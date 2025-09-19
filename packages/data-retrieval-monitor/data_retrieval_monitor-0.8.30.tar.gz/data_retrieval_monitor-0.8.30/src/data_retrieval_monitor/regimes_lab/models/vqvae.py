import math, numpy as np, pandas as pd, torch
import torch.nn as nn, torch.nn.functional as F
from sklearn.cluster import KMeans

class Encoder(nn.Module):
    def __init__(self, d_in, d_hidden=64, d_latent=32, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, d_hidden), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(d_hidden, d_hidden), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(d_hidden, d_latent)
        )
    def forward(self, x): return self.net(x)

class Decoder(nn.Module):
    def __init__(self, d_latent, d_hidden=64, d_out=4, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_latent, d_hidden), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(d_hidden, d_hidden), nn.ReLU(), nn.Dropout(dropout),
            nn.Linear(d_hidden, d_out)
        )
    def forward(self, z): return self.net(z)

class VectorQuantizerEMA(nn.Module):
    def __init__(self, K, D, decay=0.99, eps=1e-5):
        super().__init__()
        self.K, self.D = K, D
        self.decay, self.eps = decay, eps
        embed = torch.randn(K, D)
        self.register_buffer("embed", embed)
        self.register_buffer("cluster_size", torch.zeros(K))
        self.register_buffer("embed_avg", embed.clone())

    @torch.no_grad()
    def _ema_update(self, x, one_hot):
        self.cluster_size.mul_(self.decay).add_(one_hot.sum(0), alpha=1 - self.decay)
        embed_sum = x.t() @ one_hot
        self.embed_avg.mul_(self.decay).add_(embed_sum.t(), alpha=1 - self.decay)
        n = self.cluster_size.sum()
        cluster_size = ((self.cluster_size + self.eps) / (n + self.K * self.eps)) * n
        embed_normalized = self.embed_avg / cluster_size.unsqueeze(1)
        self.embed.copy_(embed_normalized)

    def forward(self, z_e):
        d = (z_e.pow(2).sum(1, keepdim=True) - 2 * z_e @ self.embed.t() + self.embed.pow(2).sum(1))
        idx = torch.argmin(d, dim=1)
        one_hot = F.one_hot(idx, self.K).type_as(z_e)
        z_q = one_hot @ self.embed
        return z_q, idx, one_hot

class VQVAERegimes:
    def __init__(self, k=12, embed_dim=32, commit_beta=0.25, ema_update=True, ema_decay=0.99,
                 entropy_w=0.02, dead_code_every=5, lr=1e-3, epochs=80, batch_size=256,
                 dropout=0.1, input_norm="standard", seed=0, device=None):
        self.k, self.embed_dim = k, embed_dim
        self.commit_beta = commit_beta
        self.ema_update, self.ema_decay = ema_update, ema_decay
        self.entropy_w = entropy_w
        self.dead_code_every = dead_code_every
        self.lr, self.epochs, self.batch = lr, epochs, batch_size
        self.dropout, self.input_norm = dropout, input_norm
        self.seed = seed
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.enc = self.dec = self.vq = None
        self.scaler_ = None
        torch.manual_seed(seed); np.random.seed(seed)
        self.train_labels_ = None

    def _scale(self, X):
        X = pd.DataFrame(X).astype(float)
        if self.input_norm == "standard":
            mu, sig = X.mean(0), X.std(0).replace(0, 1.0)
            self.scaler_ = (mu, sig)
            return ((X - mu) / sig).values.astype(np.float32)
        return X.values.astype(np.float32)

    def fit(self, X_train):
        X = self._scale(X_train)
        n, d = X.shape
        self.enc = Encoder(d, 64, self.embed_dim, self.dropout).to(self.device)
        self.dec = Decoder(self.embed_dim, 64, d, self.dropout).to(self.device)
        self.vq  = VectorQuantizerEMA(self.k, self.embed_dim, decay=self.ema_decay).to(self.device)
        opt = torch.optim.Adam(list(self.enc.parameters()) + list(self.dec.parameters()), lr=self.lr)

        with torch.no_grad():
            Zp = []
            Xt = torch.tensor(X, device=self.device)
            for i in range(0, n, 4096):
                Zp.append(self.enc(Xt[i:i+4096]).cpu().numpy())
            Zp = np.vstack(Zp)
        km = KMeans(n_clusters=self.k, n_init=10, random_state=self.seed).fit(Zp)
        centers = torch.tensor(km.cluster_centers_ + 1e-4*np.random.randn(*km.cluster_centers_.shape),
                               dtype=torch.float32, device=self.device)
        self.vq.embed.copy_(centers); self.vq.embed_avg.copy_(centers.clone())

        X_t = torch.tensor(X, device=self.device)
        nb = math.ceil(n / self.batch)
        for ep in range(self.epochs):
            perm = torch.randperm(n, device=self.device); X_t = X_t[perm]
            epoch_usage = torch.zeros(self.k, device=self.device)
            for b in range(nb):
                xb = X_t[b*self.batch:(b+1)*self.batch]
                z_e = self.enc(xb)
                z_q, idx, one_hot = self.vq(z_e)
                recon = self.dec(z_q)
                recon_loss = F.mse_loss(recon, xb)
                commit = self.commit_beta * F.mse_loss(z_e.detach(), z_q)
                usage = one_hot.mean(0)
                epoch_usage += one_hot.sum(0)
                p = usage + 1e-8
                entropy = -torch.sum(p * torch.log(p))
                entropy_loss = - self.entropy_w * entropy
                loss = recon_loss + commit + entropy_loss
                opt.zero_grad(); loss.backward(); opt.step()
                if self.ema_update:
                    with torch.no_grad():
                        self.vq._ema_update(z_e.detach(), one_hot.detach())
            if (ep+1) % self.dead_code_every == 0:
                with torch.no_grad():
                    dead = (epoch_usage == 0).nonzero(as_tuple=True)[0]
                    if len(dead) > 0:
                        sel = torch.randint(0, n, (len(dead),), device=self.device)
                        z_seed = self.enc(X_t[sel])
                        self.vq.embed[dead] = z_seed
                        self.vq.embed_avg[dead] = z_seed
        self.train_labels_ = self.predict(X_train)
        return self

    @torch.no_grad()
    def predict(self, X):
        Xs = X if self.scaler_ is None else self._scale(X)
        Xt = torch.tensor(Xs, device=self.device)
        idx_all = []
        for i in range(0, len(Xt), 4096):
            z_e = self.enc(Xt[i:i+4096])
            _, idx, _ = self.vq(z_e)
            idx_all.append(idx.cpu().numpy())
        return np.concatenate(idx_all)