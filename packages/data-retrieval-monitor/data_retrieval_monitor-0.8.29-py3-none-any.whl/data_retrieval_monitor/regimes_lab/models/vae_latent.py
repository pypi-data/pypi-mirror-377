# regimes_lab/models/vae_latent.py
import numpy as np
from .base import BaseRegimeModel
from sklearn.cluster import KMeans

try:
    import torch
    import torch.nn as nn
    _TORCH = True
except Exception:
    _TORCH = False

class VAERegimes(BaseRegimeModel):
    def __init__(self, d_in, d_lat=8, k=8, **kw):
        super().__init__("vae", **kw)
        self.d_in=d_in; self.d_lat=d_lat; self.k=k
        self._torch=_TORCH
        if _TORCH:
            self.enc = nn.Sequential(nn.Linear(d_in,64), nn.ReLU())
            self.mu  = nn.Linear(64, d_lat)
            self.lv  = nn.Linear(64, d_lat)
            self.dec = nn.Sequential(nn.Linear(d_lat,64), nn.ReLU(), nn.Linear(64,d_in))
            self.opt = torch.optim.Adam(list(self.enc.parameters())+list(self.mu.parameters())+list(self.lv.parameters())+list(self.dec.parameters()), lr=1e-3)

    def fit(self, X):
        if not self._torch:
            # degrade: PCA-like random projection
            rng = np.random.default_rng(2)
            W = rng.normal(size=(self.d_in, self.d_lat))/np.sqrt(self.d_in)
            Z = X @ W
            self.km = KMeans(n_clusters=self.k, n_init=5, random_state=0).fit(Z)
            self._Z_tr = Z
            return
        # One quick epoch VAE to get mu/sigma
        self.enc.train(); self.mu.train(); self.lv.train(); self.dec.train()
        X_t = torch.from_numpy(X).float()
        for _ in range(1):
            h = self.enc(X_t)
            mu = self.mu(h); lv = self.lv(h)
            std = (0.5*lv).exp()
            eps = torch.randn_like(std)
            z = mu + eps*std
            xhat = self.dec(z)
            recon = ((X_t - xhat)**2).mean()
            kld = -0.5*(1 + lv - mu.pow(2) - lv.exp()).mean()
            loss = recon + 1e-3*kld
            self.opt.zero_grad(); loss.backward(); self.opt.step()
        with torch.no_grad():
            Z = self.mu(self.enc(X_t)).cpu().numpy()
        self.km = KMeans(n_clusters=self.k, n_init=5, random_state=0).fit(Z)
        self._Z_tr = Z

    def predict(self, X):
        if not hasattr(self, "km"):
            return np.zeros(len(X), dtype=int)
        if not self._torch:
            rng = np.random.default_rng(2)
            W = rng.normal(size=(self.d_in, self.d_lat))/np.sqrt(self.d_in)
            Z = X @ W
        else:
            self.enc.eval(); self.mu.eval()
            with torch.no_grad():
                Z = self.mu(self.enc(torch.from_numpy(X).float())).cpu().numpy()
        return self.km.predict(Z)