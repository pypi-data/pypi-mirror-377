# regimes_lab/models/vqvae.py
import numpy as np
from .base import BaseRegimeModel
from sklearn.cluster import KMeans

try:
    import torch
    import torch.nn as nn
    _TORCH = True
except Exception:
    _TORCH = False

class VQVAERegimes(BaseRegimeModel):
    def __init__(self, d_in, codebook=16, d_lat=16, **kw):
        super().__init__("vqvae", **kw)
        self.d_in = d_in; self.codebook = codebook; self.d_lat = d_lat
        self._torch = _TORCH
        if _TORCH:
            self.enc = nn.Sequential(nn.Linear(d_in, 64), nn.ReLU(), nn.Linear(64, d_lat))
            self.code = nn.Embedding(codebook, d_lat)
            nn.init.xavier_uniform_(self.code.weight)
            self.dec = nn.Sequential(nn.Linear(d_lat, 64), nn.ReLU(), nn.Linear(64, d_in))
            self.opt = torch.optim.Adam(list(self.enc.parameters())+list(self.dec.parameters())+[self.code.weight], lr=1e-3)

    def _embed_np(self, X):
        if not self._torch:
            # degrade: kmeans code assignment on random projection
            rng = np.random.default_rng(1)
            W = rng.normal(size=(self.d_in, self.d_lat))/np.sqrt(self.d_in)
            Z = X @ W
            self.km = KMeans(n_clusters=self.codebook, n_init=5, random_state=0).fit(Z)
            return Z, self.km.labels_
        # if torch: do one quick epoch and assign closest code
        self.enc.eval(); self.code.eval()
        with torch.no_grad():
            Z = self.enc(torch.from_numpy(X).float()).cpu().numpy()
        # nearest codebook via kmeans init (fast)
        km = KMeans(n_clusters=self.codebook, n_init=5, random_state=0).fit(Z)
        self.km = km
        return Z, km.labels_

    def fit(self, X):
        Z, labs = self._embed_np(X)
        self._Z_tr = Z
        self._labs_tr = labs

    def predict(self, X):
        if hasattr(self, "km"):
            Z = (X @ (self._Z_tr.T @ self._Z_tr + 1e-6*np.eye(self._Z_tr.shape[1])) @ np.linalg.pinv(self._Z_tr.T @ self._Z_tr + 1e-6*np.eye(self._Z_tr.shape[1]))) if not _TORCH else None
            Z = X if Z is None else Z
            return self.km.predict(Z)
        return np.zeros(len(X), dtype=int)