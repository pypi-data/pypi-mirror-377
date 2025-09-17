# selector_saint.py
import os, numpy as np, pandas as pd
from configs import SUBDIRS, ROLL_WINDOW
try:
    import torch, torch.nn as nn
    TORCH_OK = True
except Exception:
    TORCH_OK = False

def _prep_panel(returns_df: pd.DataFrame, X_features: pd.DataFrame):
    R = returns_df.copy()
    y_next = R.shift(-1)
    X = X_features.copy()
    frames = []
    for f in R.columns:
        df = X.copy()
        df["factor"] = f
        df["y"] = y_next[f]
        frames.append(df)
    panel = pd.concat(frames, axis=0)
    F = pd.get_dummies(panel["factor"], prefix="F", dtype=int)
    panel = pd.concat([panel.drop(columns=["factor"]), F], axis=1)
    return panel

class TinyMLP(nn.Module):
    def __init__(self, d_in, d_h=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, d_h), nn.ReLU(), nn.LayerNorm(d_h),
            nn.Linear(d_h, d_h), nn.ReLU(), nn.LayerNorm(d_h),
            nn.Linear(d_h, 1)
        )
    def forward(self, x): return self.net(x)

def saint_selector_rolling(returns_df: pd.DataFrame, X_features: pd.DataFrame, epochs=10, lr=1e-3):
    if not TORCH_OK:
        print("[INFO] PyTorch not available; skipping SAINT selector.")
        return None
    panel = _prep_panel(returns_df, X_features).dropna()
    uniq_dates = panel.index.unique()
    preds = []
    cols = [c for c in panel.columns if c != "y"]
    for i, d in enumerate(uniq_dates):
        past = uniq_dates[max(0, i-ROLL_WINDOW):i]
        if len(past) < 5: continue
        tr = panel.loc[past]
        te = panel.loc[[d]]

        Xtr = torch.tensor(tr[cols].values, dtype=torch.float32)
        ytr = torch.tensor(tr["y"].values, dtype=torch.float32).view(-1,1)
        Xte = torch.tensor(te[cols].values, dtype=torch.float32)

        model = TinyMLP(d_in=Xtr.shape[1])
        opt = torch.optim.AdamW(model.parameters(), lr=lr)
        lossf = nn.MSELoss()
        model.train()
        for _ in range(epochs):
            opt.zero_grad()
            pred = model(Xtr)
            loss = lossf(pred, ytr)
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            score = model(Xte).squeeze(1).numpy()
        # Identify factor names from columns one-hot
        fac_cols = [c for c in cols if c.startswith("F_")]
        fac_names = [c.replace("F_", "") for c in fac_cols]
        # rows already one per factor; use argmax on scores
        pick_idx = int(np.argmax(score))
        pick_factor = fac_names[pick_idx]
        realized = returns_df.loc[d, pick_factor] if d in returns_df.index else np.nan
        preds.append((d, pick_factor, float(realized)))

    if preds:
        out = pd.DataFrame(preds, columns=["date","selected_factor","realized_ret"]).set_index("date")
        out.to_csv(os.path.join(SUBDIRS["selectors"], "selector_saint_choices.csv"))
        rets = out["realized_ret"].dropna()
        perf = {
            "count": int(rets.shape[0]),
            "mean_ann": float(rets.mean()*252),
            "vol_ann":  float(rets.std()*(252**0.5)),
            "sharpe":   float((rets.mean()/(rets.std()+1e-12))*(252**0.5)),
            "backend": "saint_mlp",
        }
        pd.DataFrame([perf]).to_csv(os.path.join(SUBDIRS["selectors"], "selector_saint_performance.csv"), index=False)
        return out
    return None