# regimes_lab/stats/joint.py
import os
import numpy as np
import pandas as pd
from ..io_utils import save_df
from ..configs import STATS_DIR, FORECAST_LAGS

def aggregate_significance(ST_dir=STATS_DIR, alpha=0.05):
    """
    Inspect TEST_OLS_* files and count how often each dummy is significant (p<alpha).
    Return per-model top regimes and save a CSV summary.
    """
    paths = []
    for h in FORECAST_LAGS:
        paths += list(_glob(os.path.join(ST_dir, f"TEST_OLS_*_h{h}.csv")))
    if not paths:
        return None
    counts = {}
    for p in paths:
        df = pd.read_csv(p, index_col=0)
        sig = df["p"].drop(index="const", errors="ignore") < alpha
        for k,v in sig.items():
            counts[k] = counts.get(k,0) + (1 if v else 0)
    s = pd.Series(counts).sort_values(ascending=False)
    save_df(s.to_frame("sig_count"), os.path.join(ST_dir,"dummy_significance_counts.csv"))
    return s

def _glob(pattern):
    import glob
    return glob.glob(pattern)