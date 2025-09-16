# selector.py
import os
import numpy as np, pandas as pd
from configs import TRAIN_FRAC, VAL_FRAC, SUBDIRS

def _combo_key(row: pd.Series) -> str:
    return "|".join([f"{c}:{int(row[c])}" for c in row.index])

def selector_best_factor(returns_df: pd.DataFrame, regimes_df: pd.DataFrame) -> pd.DataFrame:
    T = len(returns_df)
    n_train = int(TRAIN_FRAC * T)
    n_val   = int(VAL_FRAC * T)

    idx_train = slice(0, n_train)
    idx_test  = slice(n_train + n_val, T)

    combo_cols = list(regimes_df.columns)
    combos = regimes_df.apply(_combo_key, axis=1)

    mapping = {}
    train_df = pd.concat([returns_df.iloc[idx_train], combos.iloc[idx_train].rename("combo")], axis=1)
    for combo, grp in train_df.groupby("combo"):
        mu = grp[returns_df.columns].mean()
        mapping[combo] = {"best_factor": mu.idxmax(), "mean": float(mu.max())}

    mapping_df = pd.DataFrame(mapping).T
    mapping_df.index.name = "combo"
    mapping_df.to_csv(os.path.join(SUBDIRS["selectors"], "selector_mapping.csv"))

    global_mu = train_df[returns_df.columns].mean()
    fallback_factor = global_mu.idxmax()

    picks = []
    for t in range(n_train, T - 1):
        combo_t = combos.iloc[t]
        pick = mapping.get(combo_t, {"best_factor": fallback_factor})["best_factor"]
        realized = returns_df.iloc[t + 1][pick]
        picks.append((returns_df.index[t + 1], combo_t, pick, realized))

    picks_df = pd.DataFrame(picks, columns=["date", "combo", "selected_factor", "realized_ret"]).set_index("date")
    picks_df.to_csv(os.path.join(SUBDIRS["selectors"], "selector_choices.csv"))

    rets = picks_df["realized_ret"]
    perf = {
        "count": len(rets),
        "mean_ann": rets.mean() * 252,
        "vol_ann":  rets.std() * (252 ** 0.5),
        "sharpe":   (rets.mean()/(rets.std()+1e-12))*(252 ** 0.5),
    }
    pd.DataFrame([perf]).to_csv(os.path.join(SUBDIRS["selectors"], "selector_performance.csv"), index=False)
    return picks_df