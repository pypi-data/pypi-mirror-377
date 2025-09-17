# perf.py
import os
import numpy as np
import pandas as pd
from configs import SUBDIRS
from utils import annualized_stats, professional_heatmap, infer_periods_per_year

def _perf_one_split(returns_df: pd.DataFrame, regime_series: pd.Series, ann: int):
    labs = pd.Series(regime_series).astype("Int64").values
    uniq = [int(u) for u in np.unique(labs[~pd.isna(labs)])]
    if len(uniq) == 0:
        cols = []
    else:
        cols = [f"Regime {s}" for s in uniq]
    mu_df = pd.DataFrame(index=returns_df.columns, columns=cols)
    vol_df = mu_df.copy(); shr_df = mu_df.copy()
    for s in uniq:
        m = labs == s
        if m.sum() == 0: 
            continue
        stats = annualized_stats(returns_df.loc[m], ann)
        mu_df[f"Regime {s}"] = stats["mean"]
        vol_df[f"Regime {s}"] = stats["vol"]
        shr_df[f"Regime {s}"] = stats["sharpe"]
    return mu_df, vol_df, shr_df

def _save_perf(model_col: str, split: str, mu_df, vol_df, shr_df):
    root = SUBDIRS["perf"]
    # CSVs
    mu_df.to_csv(os.path.join(root, split, "mean",   f"{model_col}.csv"))
    vol_df.to_csv(os.path.join(root, split, "vol",    f"{model_col}.csv"))
    shr_df.to_csv(os.path.join(root, split, "sharpe", f"{model_col}.csv"))
    # Heatmaps
    professional_heatmap(mu_df,  f"{model_col} — {split.capitalize()} Mean",
                         os.path.join("..", root, split, "mean",   f"{model_col}_heatmap"), fmt=".2%")
    professional_heatmap(vol_df, f"{model_col} — {split.capitalize()} Vol",
                         os.path.join("..", root, split, "vol",    f"{model_col}_heatmap"), fmt=".2%")
    professional_heatmap(shr_df, f"{model_col} — {split.capitalize()} Sharpe",
                         os.path.join("..", root, split, "sharpe", f"{model_col}_heatmap"),
                         fmt=".2f", center_zero=True, cbar_label="Sharpe")

def compute_regime_perf_split(returns_df: pd.DataFrame,
                              regimes_df: pd.DataFrame,
                              train_slice: slice,
                              test_slice: slice):
    """For every regime column, compute train vs test mean/vol/Sharpe and save to perf/<split>/<metric>/"""
    ann = infer_periods_per_year(returns_df.index)
    ret_train = returns_df.iloc[train_slice]
    ret_test  = returns_df.iloc[test_slice]
    for col in regimes_df.columns:
        r = regimes_df[col]
        mu_tr, vol_tr, shr_tr = _perf_one_split(ret_train, r.iloc[train_slice], ann)
        mu_te, vol_te, shr_te = _perf_one_split(ret_test,  r.iloc[test_slice],  ann)
        _save_perf(col, "train", mu_tr, vol_tr, shr_tr)
        _save_perf(col, "test",  mu_te, vol_te, shr_te)