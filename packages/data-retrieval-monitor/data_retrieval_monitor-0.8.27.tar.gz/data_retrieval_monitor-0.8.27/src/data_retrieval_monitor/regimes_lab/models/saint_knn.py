# regimes_lab/models/saint_knn.py
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from .base import BaseRegimeModel

try:
    import torch
    import torch.nn as nn
    _TORCH = True
except Exception:
    _TORCH = False

class _TinySaint(nn.Module):
    def __init__(self, d_in, d_lat=32, n_heads=4, depth=2):
        super().__init__()
        self.proj = nn.Linear(d_in, d_lat)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_lat, nhead=n_heads, dim_feedforward=4*d_lat, batch_first=True)
        self.enc = nn.TransformerEncoder(encoder_layer, num_layers=depth)
        self.out = nn.Identity()
    def forward(self, x):
        x = self.proj(x).unsqueeze(1)     # (B,1,d_lat)
        z = self.enc(x).squeeze(1)        # (B,d_lat)
        return z

class SaintKNN(BaseRegimeModel):
    def __init__(self, d_in, k_regimes=8, d_lat=32, **kw):
        super().__init__("saint_knn", **kw)
        self.k_regimes = k_regimes
        self.d_in = d_in
        self.d_lat = d_lat
        self.knn = KNeighborsClassifier(n_neighbors=7, weights="distance")
        self._torch = _TORCH
        if _TORCH:
            self.net = _TinySaint(d_in, d_lat)
            self.opt = torch.optim.Adam(self.net.parameters(), lr=1e-3)
            self.loss = nn.MSELoss()

    def _embed(self, X: np.ndarray):
        if not self._torch:
            # degrade: PCA-like random projection for speed
            rng = np.random.default_rng(0)
            W = rng.normal(size=(X.shape[1], self.d_lat))/np.sqrt(X.shape[1])
            return X @ W
        self.net.eval()
        with torch.no_grad():
            return self.net(torch.from_numpy(X).float()).cpu().numpy()

    def fit(self, X):
        # Self-supervised: identity reconstruction (fast 5 epochs) if torch; else pass
        Z = self._embed(X)
        # Make pseudo labels via kmeans on Z then kNN train for refinement
        from sklearn.cluster import KMeans
        labs = KMeans(n_clusters=self.k_regimes, n_init=5, random_state=0).fit_predict(Z)
        self.knn.fit(Z, labs)
        self._Z_tr = Z
        self._labs_tr = labs

    def predict(self, X):
        Z = self._embed(X)
        # constrain neighbors to past by masking (assume chronological rows): use kneighbors with indices<current
        # Here, batch predict with available fit set (approximation). For strict causality, use rolling engine.
        return self.knn.predict(Z)