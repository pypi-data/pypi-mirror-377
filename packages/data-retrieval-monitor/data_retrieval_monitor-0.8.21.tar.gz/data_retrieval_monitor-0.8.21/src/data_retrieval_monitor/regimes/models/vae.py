# models/vae.py
import numpy as np
from configs import VAE_Z_DIM, VAE_H, VAE_EPOCHS, VAE_LR
try:
    import torch, torch.nn as nn, torch.nn.functional as F
    TORCH = True
except Exception:
    TORCH = False

class VAE(nn.Module if TORCH else object):
    def __init__(self, x_dim, h=64, z_dim=8):
        if not TORCH: return
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(x_dim, h), nn.ReLU())
        self.mu = nn.Linear(h, z_dim); self.logvar = nn.Linear(h, z_dim)
        self.dec = nn.Sequential(nn.Linear(z_dim, h), nn.ReLU(), nn.Linear(h, x_dim))
    def encode(self, x):
        h = self.enc(x); return self.mu(h), self.logvar(h)
    def reparam(self, mu, logvar):
        std = torch.exp(0.5*logvar); eps = torch.randn_like(std); return mu + eps*std
    def forward(self, x):
        mu, lv = self.encode(x); z = self.reparam(mu, lv); x_hat = self.dec(z)
        recon = F.mse_loss(x_hat, x, reduction='mean')
        kl = -0.5 * torch.mean(1 + lv - mu.pow(2) - lv.exp())
        return recon + kl, recon, kl

def fit_vae_train(X_train, X_all):
    if not TORCH:
        print("[INFO] PyTorch not available — skipping VAE.")
        return None, None, None
    torch.manual_seed(7)
    Xt = torch.tensor(X_train, dtype=torch.float32)
    Xa = torch.tensor(X_all, dtype=torch.float32)
    vae = VAE(X_train.shape[1], h=VAE_H, z_dim=VAE_Z_DIM)
    opt = torch.optim.Adam(vae.parameters(), lr=VAE_LR); vae.train()
    for _ in range(VAE_EPOCHS):
        opt.zero_grad(); loss, _, _ = vae(Xt); loss.backward(); opt.step()
    vae.eval()
    with torch.no_grad():
        mu_all, logvar_all = vae.encode(Xa)
    mu = mu_all.cpu().numpy(); var = np.exp(logvar_all.cpu().numpy())
    return vae, mu, var