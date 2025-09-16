# perf.py
import os
import numpy as np
import pandas as pd
from configs import SUBDIRS
from utils import annualized_stats, professional_heatmap, infer_periods_per_year

def _perf_one_split(returns_df: pd.DataFrame, regime_series: pd.Series, ann: int):
    labs = pd.Series(regime_series).astype("Int64").values
    uniq = [int(u) for u in np.unique(labs[~pd.isna(labs)])]
    mu_df = pd.DataFrame(index=returns_df.columns, columns=[f"Regime {s}" for s in uniq])
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

def compute_regime_perf_split(returns_df: pd.DataFrame,
                              regimes_df: pd.DataFrame,
                              train_slice: slice,
                              test_slice: slice):
    """
    For every regime column, compute train vs test mean/vol/Sharpe and save:
      perf_train/<col>_{mean,vol,sharpe}.csv + heatmaps
      perf_test/<col>_{mean,vol,sharpe}.csv  + heatmaps
    """
    ann = infer_periods_per_year(returns_df.index)
    ret_train = returns_df.iloc[train_slice]
    ret_test  = returns_df.iloc[test_slice]

    for col in regimes_df.columns:
        r = regimes_df[col]
        r_tr = r.iloc[train_slice]
        r_te = r.iloc[test_slice]

        mu_tr, vol_tr, shr_tr = _perf_one_split(ret_train, r_tr, ann)
        mu_te, vol_te, shr_te = _perf_one_split(ret_test,  r_te, ann)

        # CSVs
        mu_tr.to_csv(os.path.join(SUBDIRS["perf_train"], f"{col}_mean.csv"))
        vol_tr.to_csv(os.path.join(SUBDIRS["perf_train"], f"{col}_vol.csv"))
        shr_tr.to_csv(os.path.join(SUBDIRS["perf_train"], f"{col}_sharpe.csv"))
        mu_te.to_csv(os.path.join(SUBDIRS["perf_test"],  f"{col}_mean.csv"))
        vol_te.to_csv(os.path.join(SUBDIRS["perf_test"],  f"{col}_vol.csv"))
        shr_te.to_csv(os.path.join(SUBDIRS["perf_test"],  f"{col}_sharpe.csv"))

        # Heatmaps
        professional_heatmap(mu_tr, f"{col} — Train Mean",   os.path.join("..", SUBDIRS["perf_train"], f"{col}_mean_heatmap"),   fmt=".2%")
        professional_heatmap(vol_tr, f"{col} — Train Vol",    os.path.join("..", SUBDIRS["perf_train"], f"{col}_vol_heatmap"),    fmt=".2%")
        professional_heatmap(shr_tr, f"{col} — Train Sharpe", os.path.join("..", SUBDIRS["perf_train"], f"{col}_sharpe_heatmap"), fmt=".2f", center_zero=True, cbar_label="Sharpe")

        professional_heatmap(mu_te, f"{col} — Test Mean",     os.path.join("..", SUBDIRS["perf_test"], f"{col}_mean_heatmap"),   fmt=".2%")
        professional_heatmap(vol_te, f"{col} — Test Vol",      os.path.join("..", SUBDIRS["perf_test"], f"{col}_vol_heatmap"),    fmt=".2%")
        professional_heatmap(shr_te, f"{col} — Test Sharpe",   os.path.join("..", SUBDIRS["perf_test"], f"{col}_sharpe_heatmap"), fmt=".2f", center_zero=True, cbar_label="Sharpe")