# models/vqvae.py
import numpy as np
from configs import VQVAE_CODEBOOK_K, VQVAE_EMBED_DIM, VQVAE_HIDDEN, VQVAE_EPOCHS, VQVAE_LR, VQVAE_BETA
try:
    import torch, torch.nn as nn, torch.nn.functional as F
    TORCH = True
except Exception:
    TORCH = False

class VectorQuantizer(nn.Module if TORCH else object):
    def __init__(self, K, D, beta=0.25):
        if not TORCH: return
        super().__init__(); self.K, self.D, self.beta = K, D, beta
        self.codebook = nn.Parameter(torch.randn(K, D))
    def forward(self, z_e):
        with torch.no_grad():
            d = (z_e.pow(2).sum(1, keepdim=True) - 2*z_e@self.codebook.T + self.codebook.pow(2).sum(1))
            idx = torch.argmin(d, dim=1)
        z_q = F.embedding(idx, self.codebook)
        commit = self.beta * F.mse_loss(z_e.detach(), z_q)
        code = F.mse_loss(z_e, z_q.detach()); loss = code + commit
        z_st = z_e + (z_q - z_e).detach()
        return z_st, idx, loss

class VQVAE(nn.Module if TORCH else object):
    def __init__(self, x_dim, hidden=32, z_dim=8, K=16, beta=0.25):
        if not TORCH: return
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(x_dim, hidden), nn.ReLU(), nn.Linear(hidden, z_dim))
        self.vq  = VectorQuantizer(K, z_dim, beta)
        self.dec = nn.Sequential(nn.Linear(z_dim, hidden), nn.ReLU(), nn.Linear(hidden, x_dim))
    def forward(self, x):
        z_e = self.enc(x); z_q, idx, vq_loss = self.vq(z_e)
        x_hat = self.dec(z_q)
        recon = F.mse_loss(x_hat, x)
        return x_hat, idx, recon + vq_loss

def fit_vqvae_train(X_train, X_all):
    if not TORCH:
        print("[INFO] PyTorch not available — skipping VQ-VAE.")
        return None, None
    torch.manual_seed(7)
    Xt = torch.tensor(X_train, dtype=torch.float32)
    Xa = torch.tensor(X_all, dtype=torch.float32)
    model = VQVAE(X_train.shape[1], VQVAE_HIDDEN, VQVAE_EMBED_DIM, VQVAE_CODEBOOK_K, VQVAE_BETA)
    opt = torch.optim.Adam(model.parameters(), lr=VQVAE_LR); model.train()
    for _ in range(VQVAE_EPOCHS):
        opt.zero_grad(); _, _, loss = model(Xt); loss.backward(); opt.step()
    model.eval()
    with torch.no_grad():
        _, idx_all, _ = model(Xa)
    return model, idx_all.cpu().numpy()