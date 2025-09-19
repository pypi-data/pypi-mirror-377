import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
from sklearn.cluster import KMeans

def _make_attn(d_model: int, nhead: int, dropout: float):
    return nn.TransformerEncoderLayer(
        d_model=d_model, nhead=nhead,
        dim_feedforward=4 * d_model,
        dropout=dropout, batch_first=True,
        activation="gelu", norm_first=True,
    )

class SaintBlock(nn.Module):
    def __init__(self, n_features, d_model, nhead, dropout):
        super().__init__()
        self.n_features = n_features
        self.col_pos = nn.Parameter(torch.randn(1, n_features, d_model) * 0.02)
        self.col_attn = _make_attn(d_model, nhead, dropout)
        self.row_pe   = nn.Parameter(torch.randn(1, 1, d_model) * 0.02)
        self.row_attn = _make_attn(d_model, nhead, dropout)
    def forward(self, z):
        B, F, D = z.shape
        zc = z + self.col_pos[:, :F, :]
        zc = self.col_attn(zc)
        zr = zc.transpose(0, 1)
        zr = zr + self.row_pe
        zr = self.row_attn(zr)
        zr = zr.transpose(0, 1)
        return zr

class SaintEncoder(nn.Module):
    def __init__(self, n_features, d_model, depth, nhead, dropout):
        super().__init__()
        self.input_proj = nn.Linear(1, d_model)
        self.blocks = nn.ModuleList([SaintBlock(n_features, d_model, nhead, dropout) for _ in range(depth)])
        self.norm = nn.LayerNorm(d_model)
    def forward(self, x):
        z = self.input_proj(x.unsqueeze(-1))
        for blk in self.blocks: z = blk(z)
        return self.norm(z)

class SaintRegimes:
    def __init__(self, n_features, d_model=64, depth=4, nhead=4, dropout=0.1, mask_p=0.15,
                 lr=1e-3, epochs=60, batch_size=256, seed=0, n_clusters=12, knn_k=7, knn_refine=True, device=None):
        self.n_features=n_features; self.d_model=d_model; self.depth=depth; self.nhead=nhead
        self.dropout=dropout; self.mask_p=mask_p; self.lr=lr; self.epochs=epochs; self.batch=batch_size
        self.seed=seed; self.n_clusters=n_clusters; self.knn_k=knn_k; self.knn_refine=knn_refine
        self.device=device or ("cuda" if torch.cuda.is_available() else "cpu")
        torch.manual_seed(seed); np.random.seed(seed)
        self.enc = SaintEncoder(n_features, d_model, depth, nhead, dropout).to(self.device)
        self.head = nn.Linear(d_model, 1).to(self.device)
        self.kmeans_ = None; self.centroids_=None
        self.train_embed_=None; self.train_labels_=None

    def _mask(self, X):
        B,F = X.shape; m = torch.rand(B,F, device=X.device) < self.mask_p
        Xm = X.clone(); Xm[m]=0.0; return Xm, m

    def _embed(self, X):
        xs = torch.tensor(X, dtype=torch.float32, device=self.device); em=[]
        self.enc.eval()
        with torch.no_grad():
            for i in range(0, len(xs), 4096):
                xb = xs[i:i+4096]; zb = self.enc(xb).mean(1)
                em.append(zb.cpu().numpy())
        return np.vstack(em)

    def fit(self, X_train):
        self.enc.train()
        opt = torch.optim.AdamW(list(self.enc.parameters())+list(self.head.parameters()), lr=self.lr)
        X = torch.tensor(X_train, dtype=torch.float32, device=self.device)
        for ep in range(self.epochs):
            perm = torch.randperm(len(X), device=self.device); X = X[perm]
            total=0.0
            for i in range(0, len(X), self.batch):
                xb = X[i:i+self.batch]
                xm, m = self._mask(xb)
                z = self.enc(xm)
                pred = self.head(z).squeeze(-1)
                loss = F.mse_loss(pred[m], xb[m])
                opt.zero_grad(); loss.backward(); opt.step()
                total += loss.item()
            if (ep+1)%10==0: print(f"[SAINT] {ep+1}/{self.epochs} loss={total:.4f}")
        E = self._embed(X_train)
        km = KMeans(n_clusters=self.n_clusters, n_init=20, random_state=self.seed).fit(E)
        self.kmeans_=km; self.centroids_=km.cluster_centers_
        self.train_embed_=E; self.train_labels_=km.labels_
        return self

    def _assign_kmeans(self, E):
        C=self.centroids_; d2=((E[:,None,:]-C[None,:,:])**2).sum(-1)
        return d2.argmin(1)

    def _past_only_knn(self, E):
        labels = self._assign_kmeans(E)
        if not self.knn_refine or self.knn_k<1: return labels
        ref = labels.copy()
        for t in range(len(labels)):
            if t<1: continue
            d2 = ((E[:t]-E[t])**2).sum(1)
            k = min(self.knn_k, len(d2))
            idx = np.argpartition(d2, k-1)[:k]
            vals, cnt = np.unique(labels[idx], return_counts=True)
            ref[t] = vals[cnt.argmax()]
        return ref

    def predict(self, X):
        E = self._embed(X)
        labs = self._assign_kmeans(E)
        labs_ref = self._past_only_knn(E)
        return labs_ref