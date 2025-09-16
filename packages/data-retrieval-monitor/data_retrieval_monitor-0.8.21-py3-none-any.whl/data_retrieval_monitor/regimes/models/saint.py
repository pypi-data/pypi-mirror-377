# models/saint.py
import numpy as np
from configs import (SAINT_D_MODEL, SAINT_NHEAD, SAINT_NLAYERS, SAINT_DFF, SAINT_DROPOUT,
                     SAINT_EPOCHS, SAINT_LR, SAINT_WD, SAINT_BS)
try:
    import torch, torch.nn as nn, torch.nn.functional as F
    TORCH = True
except Exception:
    TORCH = False

class SAINTFeatureEncoder(nn.Module if TORCH else object):
    def __init__(self, d_in, d_model=64, nhead=4, nlayers=2, dff=128, dropout=0.1):
        if not TORCH: return
        super().__init__()
        self.d_in = d_in; self.d_model = d_model
        self.feat_proj = nn.Linear(1, d_model)
        self.col_embed = nn.Parameter(torch.randn(d_in, d_model)*0.02)
        self.cls = nn.Parameter(torch.randn(1,1,d_model)*0.02)
        enc_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=dff,
                                               dropout=dropout, activation='gelu', batch_first=True)
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=nlayers)
        self.norm = nn.LayerNorm(d_model)
        self.dec = nn.Linear(d_model, 1)
    def forward(self, X):
        B, d = X.shape
        feat_tokens = self.feat_proj(X.view(B,d,1)) + self.col_embed.unsqueeze(0)
        cls_tok = self.cls.expand(B,1,self.d_model)
        tokens = torch.cat([cls_tok, feat_tokens], dim=1)
        H = self.encoder(tokens); H = self.norm(H)
        cls_emb = H[:,0,:]
        x_hat = self.dec(H[:,1:,:]).squeeze(-1)
        return cls_emb, x_hat

def fit_saint_embeddings_train(X_train, X_all, epochs=SAINT_EPOCHS, d_model=SAINT_D_MODEL,
                               nhead=SAINT_NHEAD, nlayers=SAINT_NLAYERS, dff=SAINT_DFF,
                               dropout=SAINT_DROPOUT, lr=SAINT_LR, wd=SAINT_WD, bs=SAINT_BS):
    if not TORCH:
        print("[INFO] PyTorch not available — skipping SAINT.")
        return None
    torch.manual_seed(7)
    Xtr = torch.tensor(X_train, dtype=torch.float32)
    Xal = torch.tensor(X_all, dtype=torch.float32)
    model = SAINTFeatureEncoder(X_train.shape[1], d_model=d_model, nhead=nhead, nlayers=nlayers,
                                dff=dff, dropout=dropout)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    model.train(); N = Xtr.shape[0]
    for _ in range(epochs):
        perm = torch.randperm(N)
        for i in range(0, N, bs):
            idx = perm[i:i+bs]; xb = Xtr[idx]
            opt.zero_grad()
            emb, x_hat = model(xb)
            loss = F.mse_loss(x_hat, xb)
            loss.backward(); opt.step()
    model.eval()
    with torch.no_grad():
        emb_all, _ = model(Xal)
    return emb_all.cpu().numpy()