import numpy as np
from models.base import BaseRegimeModel

try:
    import torch, torch.nn as nn, torch.nn.functional as F
    TORCH_OK = True
except Exception:
    TORCH_OK = False

# ===== SAINT-like encoder (tiny) =====
class _TabEncoder(nn.Module):
    def __init__(self, d_in, d_h=128, d_emb=32, n_layers=2, n_heads=4):
        super().__init__()
        self.proj = nn.Linear(d_in, d_h)
        enc = nn.TransformerEncoderLayer(d_model=d_h, nhead=n_heads,
                                         dim_feedforward=2*d_h, batch_first=True, norm_first=True, activation="gelu")
        self.enc = nn.TransformerEncoder(enc, num_layers=n_layers)
        self.head = nn.Linear(d_h, d_emb)
        self.recon = nn.Linear(d_emb, d_in)

    def forward(self, x):
        h = self.proj(x); h = self.enc(h); z = self.head(h)[:,0,:]
        xr = self.recon(z)
        return z, xr

class SaintKMeans(BaseRegimeModel):
    def __init__(self, name="saint_kmeans", n_clusters=4, epochs=8, lr=1e-3):
        super().__init__(name); self.n_clusters=n_clusters; self.epochs=epochs; self.lr=lr
        self._model=None; self._centers=None; self._pca_km=None; self._Z_all=None

    def fit(self, Xw):
        if not TORCH_OK or Xw.shape[0] < 8:
            self._centers=None; return np.zeros(len(Xw), int)
        import torch
        d = Xw.shape[1]
        self._model = _TabEncoder(d_in=d)
        opt = torch.optim.AdamW(self._model.parameters(), lr=self.lr, weight_decay=1e-4)
        lossf = nn.SmoothL1Loss()
        Xt = torch.tensor(Xw, dtype=torch.float32)[:,None,:]
        self._model.train()
        for _ in range(self.epochs):
            opt.zero_grad()
            z, xr = self._model(Xt)
            loss = lossf(xr, Xt[:,0,:])
            loss.backward(); opt.step()
        self._model.eval()
        with torch.no_grad():
            z, _ = self._model(Xt)
            Z = z.cpu().numpy()
        from sklearn.cluster import KMeans
        k = max(1, min(self.n_clusters, max(1, np.unique(np.round(Z,12), axis=0).shape[0])))
        km = KMeans(n_clusters=k, n_init=20, random_state=0).fit(Z)
        self._centers = km.cluster_centers_
        return km.labels_

    def label_last(self, Xw):
        if not TORCH_OK or self._model is None: return 0
        import torch
        with torch.no_grad():
            z,_ = self._model(torch.tensor(Xw, dtype=torch.float32)[:,None,:])
            from sklearn.cluster import KMeans
            km = KMeans(n_clusters=self._centers.shape[0], n_init=1, random_state=0)
            km.cluster_centers_ = self._centers
            lab = km.predict(z.cpu().numpy())
        return int(lab[-1])

    def forward_embed(self, Xw, X_all):
        if not TORCH_OK or self._model is None: return None
        import torch
        with torch.no_grad():
            z,_ = self._model(torch.tensor(X_all, dtype=torch.float32)[:,None,:])
        self._Z_all = z.cpu().numpy()
        return self._Z_all

    def get_alignment_key(self): return self._centers

# ===== VQ-VAE =====
class _VectorQuant(nn.Module):
    def __init__(self, n_codes=16, d_code=16, beta=0.25):
        super().__init__()
        self.codebook = nn.Embedding(n_codes, d_code)
        nn.init.uniform_(self.codebook.weight, -1/np.sqrt(d_code), 1/np.sqrt(d_code))
        self.beta = beta
    def forward(self, z_e):
        with torch.no_grad():
            cb = self.codebook.weight
            dist = (z_e.pow(2).sum(1,keepdim=True) - 2*z_e @ cb.T + cb.pow(2).sum(1))
            idx = dist.argmin(1)
        z_q = self.codebook(idx)
        z_q_st = z_e + (z_q - z_e).detach()
        loss = F.mse_loss(z_e, z_q.detach()) + self.beta*F.mse_loss(z_e.detach(), z_q)
        return z_q_st, idx, loss

class _VQVAE(nn.Module):
    def __init__(self, d_in, d_h=128, d_lat=16, n_codes=16, beta=0.25):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(d_in,d_h), nn.ReLU(), nn.Linear(d_h,d_lat))
        self.vq = _VectorQuant(n_codes=n_codes, d_code=d_lat, beta=beta)
        self.dec = nn.Sequential(nn.Linear(d_lat,d_h), nn.ReLU(), nn.Linear(d_h,d_in))
    def forward(self, x):
        z_e = self.enc(x)
        z_q, idx, vq_loss = self.vq(z_e)
        xr = self.dec(z_q)
        loss = F.smooth_l1_loss(xr, x) + vq_loss
        return xr, idx, z_e, z_q, loss

class VQVAERegimes(BaseRegimeModel):
    def __init__(self, name="vqvae_codes", n_codes=16, epochs=25, lr=2e-3):
        super().__init__(name); self.n_codes=n_codes; self.epochs=epochs; self.lr=lr
        self._model=None; self._Z_all=None

    def fit(self, Xw):
        if not TORCH_OK or Xw.shape[0] < 20:
            return np.zeros(len(Xw), int)
        import torch
        d = Xw.shape[1]
        self._model = _VQVAE(d_in=d, d_h=128, d_lat=16, n_codes=self.n_codes, beta=0.25)
        opt = torch.optim.AdamW(self._model.parameters(), lr=self.lr, weight_decay=1e-4)
        Xt = torch.tensor(Xw, dtype=torch.float32)
        for _ in range(self.epochs):
            opt.zero_grad(); _,_,_,_,loss = self._model(Xt); loss.backward(); opt.step()
        with torch.no_grad():
            _, idx, z_e, _, _ = self._model(Xt)
        return idx.cpu().numpy().astype(int)

    def label_last(self, Xw):
        if not TORCH_OK or self._model is None: return 0
        import torch
        with torch.no_grad():
            _, idx, _, _, _ = self._model(torch.tensor(Xw, dtype=torch.float32))
        return int(idx[-1].cpu().item())

    def forward_embed(self, Xw, X_all):
        if not TORCH_OK or self._model is None: return None
        import torch
        with torch.no_grad():
            _, _, z_e, _, _ = self._model(torch.tensor(X_all, dtype=torch.float32))
        self._Z_all = z_e.cpu().numpy(); return self._Z_all

class MaskedDAERegimes(BaseRegimeModel):
    def __init__(self, name="maskeddae_kmeans", d_emb=32, epochs=15, lr=1e-3, n_clusters=4):
        super().__init__(name); self.d_emb=d_emb; self.epochs=epochs; self.lr=lr; self.n_clusters=n_clusters
        self._enc=None; self._Z_all=None; self._centers=None

    def fit(self, Xw):
        if not TORCH_OK or Xw.shape[0] < 20:
            return np.zeros(len(Xw), int)
        import torch, numpy as np
        class Enc(nn.Module):
            def __init__(self, d_in, d_h=128, d_emb=32):
                super().__init__()
                self.enc = nn.Sequential(nn.Linear(d_in,d_h), nn.GELU(), nn.Linear(d_h,d_h), nn.GELU(), nn.Linear(d_h,d_emb))
                self.dec = nn.Sequential(nn.Linear(d_emb,d_h), nn.GELU(), nn.Linear(d_h,d_in))
            def forward(self, x, mask):
                xm = x.clone(); xm[mask]=0.0; z = self.enc(xm); xr = self.dec(z); return z, xr
        d = Xw.shape[1]; self._enc = Enc(d)
        opt = torch.optim.AdamW(self._enc.parameters(), lr=self.lr, weight_decay=1e-4)
        lossf = nn.SmoothL1Loss()
        Xt = torch.tensor(Xw, dtype=torch.float32)
        for _ in range(self.epochs):
            mask = (torch.rand_like(Xt) < 0.2)
            z, xr = self._enc(Xt, mask); loss = lossf(xr, Xt); opt.zero_grad(); loss.backward(); opt.step()
        with torch.no_grad():
            m = torch.zeros_like(Xt, dtype=torch.bool); z,_ = self._enc(Xt, m)
        Z = z.cpu().numpy()
        from sklearn.cluster import KMeans
        k = max(1, min(self.n_clusters, max(1, np.unique(np.round(Z,12), axis=0).shape[0])))
        km = KMeans(n_clusters=k, n_init=20, random_state=0).fit(Z)
        self._centers = km.cluster_centers_
        return km.labels_

    def label_last(self, Xw):
        if not TORCH_OK or self._enc is None: return 0
        import torch
        with torch.no_grad():
            m = torch.zeros((len(Xw), Xw.shape[1]), dtype=torch.bool)
            z,_ = self._enc(torch.tensor(Xw, dtype=torch.float32), m)
        from sklearn.cluster import KMeans
        km = KMeans(n_clusters=self._centers.shape[0], n_init=1, random_state=0)
        km.cluster_centers_ = self._centers
        lab = km.predict(z.cpu().numpy())
        return int(lab[-1])

    def forward_embed(self, Xw, X_all):
        if not TORCH_OK or self._enc is None: return None
        import torch
        with torch.no_grad():
            m = torch.zeros((len(X_all), X_all.shape[1]), dtype=torch.bool)
            z,_ = self._enc(torch.tensor(X_all, dtype=torch.float32), m)
        self._Z_all = z.cpu().numpy(); return self._Z_all

    def get_alignment_key(self): return self._centers