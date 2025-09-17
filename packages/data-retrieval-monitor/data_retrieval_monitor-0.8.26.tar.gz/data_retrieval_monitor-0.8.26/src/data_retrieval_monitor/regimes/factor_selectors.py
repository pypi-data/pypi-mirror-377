import os, numpy as np, pandas as pd
from configs import SUBDIRS, ROLL_WINDOW

try:
    import lightgbm as lgb
    LGB_OK=True
except Exception:
    LGB_OK=False

try:
    import torch, torch.nn as nn
    TORCH_OK=True
except Exception:
    TORCH_OK=False

def _panelize(R, X):
    y_next = R.shift(-1); frames=[]
    for f in R.columns:
        df = X.copy(); df["factor"]=f; df["y_next"]=y_next[f]; frames.append(df)
    P = pd.concat(frames, axis=0).sort_index()
    F = pd.get_dummies(P["factor"], prefix="F", dtype=int)
    return pd.concat([P.drop(columns=["factor"]), F], axis=1)

def _relevance(panel):
    panel = panel.dropna(subset=["y_next"]).copy()
    parts=[]
    for d,g in panel.groupby(panel.index):
        ord_asc = g["y_next"].rank(method="first", ascending=True).astype(int)-1
        rel = ord_asc.max() - ord_asc
        gg = g.copy(); gg["y_rel"]=rel.astype(int); parts.append(gg)
    return pd.concat(parts) if parts else panel.iloc[0:0].assign(y_rel=np.nan)

class LambdaMARTSelector:
    def __init__(self): pass
    def run(self, R, X):
        if not LGB_OK: return None
        P = _relevance(_panelize(R,X))
        if P.empty: return None
        feat = [c for c in P.columns if c not in ("y_next","y_rel")]
        dates = P.index.unique().sort_values(); picks=[]
        for i,d in enumerate(dates):
            past = dates[max(0, i-ROLL_WINDOW):i]
            if len(past)<5: continue
            tr = P.loc[past].dropna(subset=["y_rel"])
            te = P.loc[[d]].dropna(subset=["y_next"])
            if tr.empty or te.empty: continue
            group = tr.index.value_counts().loc[past].values.tolist()
            Xtr, ytr = tr[feat], tr["y_rel"].astype(int)

            m = lgb.LGBMRanker(
                objective="lambdarank",
                n_estimators=300,
                learning_rate=0.05,
                num_leaves=63,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=0,
            )

            # OPTIONAL: set label_gain as a MODEL PARAM (not in fit)
            # If you want DCG-style gains, provide a nondecreasing int list:
            # e.g., [0, 1, 3, 7, 15] up to max(ytr)
            # Otherwise you can skip this entirely.
            max_rel = int(ytr.max()) if ytr.size else 0
            if max_rel > 0:
                label_gain = list(range(max_rel + 1))   # simple linear gain; customize if you like
                m.set_params(label_gain=label_gain)

            m.fit(Xtr, ytr, group=group)
            score = m.predict(te[feat])
            fac_cols = [c for c in feat if c.startswith("F_")]; facs=[c.replace("F_","") for c in fac_cols]
            pick = facs[int(np.argmax(score))] if fac_cols else None
            realized = R.loc[d, pick] if pick is not None else np.nan
            picks.append((d, pick, float(realized)))
        if not picks: return None
        out = pd.DataFrame(picks, columns=["date","selected_factor","realized_ret"]).set_index("date")
        out.to_csv(os.path.join(SUBDIRS["selectors"], "selector_lambdamart_choices.csv"))
        rets = out["realized_ret"].dropna()
        perf = {"count":int(rets.shape[0]),
                "mean_ann":float(rets.mean()*252),
                "vol_ann": float(rets.std()*(252**0.5)),
                "sharpe":  float((rets.mean()/(rets.std()+1e-12))*(252**0.5))}
        pd.DataFrame([perf]).to_csv(os.path.join(SUBDIRS["selectors"], "selector_lambdamart_performance.csv"), index=False)
        return out

class SaintMLPSelector:
    def __init__(self, epochs=8, lr=1e-3): self.epochs=epochs; self.lr=lr
    def run(self, R, X):
        if not TORCH_OK: return None
        P = _panelize(R,X).dropna(subset=["y_next"])
        if P.empty: return None
        cols=[c for c in P.columns if c!="y_next"]
        dates = P.index.unique().sort_values(); picks=[]
        import torch
        class MLP(nn.Module):
            def __init__(self, d): super().__init__(); 
            # tiny head
            def __init__(self, d):
                super().__init__()
                self.net = nn.Sequential(nn.Linear(d,128), nn.ReLU(), nn.LayerNorm(128),
                                         nn.Linear(128,128), nn.ReLU(), nn.LayerNorm(128),
                                         nn.Linear(128,1))
            def forward(self,x): return self.net(x)
        for i,d in enumerate(dates):
            past = dates[max(0,i-ROLL_WINDOW):i]
            if len(past)<5: continue
            tr=P.loc[past]; te=P.loc[[d]]
            Xtr = torch.tensor(tr[cols].values, dtype=torch.float32); ytr=torch.tensor(tr["y_next"].values, dtype=torch.float32).view(-1,1)
            Xte = torch.tensor(te[cols].values, dtype=torch.float32)
            m=MLP(Xtr.shape[1]); opt=torch.optim.AdamW(m.parameters(), lr=self.lr); lossf=nn.MSELoss()
            m.train()
            for _ in range(self.epochs):
                opt.zero_grad(); pred=m(Xtr); loss=lossf(pred,ytr); loss.backward(); opt.step()
            m.eval()
            with torch.no_grad(): score=m(Xte).squeeze(1).numpy()
            fac_cols=[c for c in cols if c.startswith("F_")]; facs=[c.replace("F_","") for c in fac_cols]
            pick=facs[int(np.argmax(score))] if fac_cols else None
            realized = R.loc[d, pick] if pick is not None else np.nan
            picks.append((d,pick,float(realized)))
        if not picks: return None
        out = pd.DataFrame(picks, columns=["date","selected_factor","realized_ret"]).set_index("date")
        out.to_csv(os.path.join(SUBDIRS["selectors"], "selector_saint_choices.csv"))
        return out