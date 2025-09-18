# regimes_lab/data.py
import os
import numpy as np
import pandas as pd
from .configs import LEVELS_CSV, INDICATORS_CSV

def _ensure_dt(df):
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()

def load_or_simulate():
    if os.path.exists(LEVELS_CSV) and os.path.exists(INDICATORS_CSV):
        levels = _ensure_dt(pd.read_csv(LEVELS_CSV, index_col=0))
        ind    = _ensure_dt(pd.read_csv(INDICATORS_CSV, index_col=0))
        return levels, ind, True
    # simulate
    rng   = np.random.default_rng(7)
    dates = pd.bdate_range("2018-01-02", "2024-12-31")
    n, n_assets, n_ind = len(dates), 20, 4
    t = np.arange(n)
    ind = pd.DataFrame({
        "Ind1_Growth": 0.5*np.sin(2*np.pi*t/260) + 0.3*rng.standard_normal(n),
        "Ind2_Infl":   0.6*np.cos(2*np.pi*t/500) + 0.3*rng.standard_normal(n),
        "Ind3_Stress": 0.4*np.sin(2*np.pi*t/780 + 1.0) + 0.4*rng.standard_normal(n),
        "Ind4_Liq":    0.6*np.cos(2*np.pi*t/390 + 0.7) + 0.3*rng.standard_normal(n),
    }, index=dates)
    B = rng.normal(0, 0.1, size=(n_ind, n_assets))
    base_mu = rng.normal(0.04/252, 0.02/252, size=n_assets)
    base_sigma = rng.uniform(0.12/np.sqrt(252), 0.3/np.sqrt(252), size=n_assets)
    eps = rng.standard_normal((n, n_assets))*base_sigma
    drift = (ind.values @ B)/252.0
    rets  = base_mu + drift + eps
    levels = 100*np.exp(np.cumsum(rets, axis=0))
    cols = [f"Factor_{i+1:02d}" for i in range(n_assets)]
    levels = pd.DataFrame(levels, index=dates, columns=cols)
    return levels, ind, False

def prepare():
    levels, ind, _ = load_or_simulate()
    logp = np.log(levels)
    R = logp.diff().dropna()
    # lag indicators by +2BD
    IND = ind.shift(2)
    df = R.join(IND, how="inner").dropna()
    R = df[levels.columns]
    IND = df[ind.columns]
    # canonicalize index
    R.index = pd.to_datetime(R.index).tz_localize(None)
    IND.index = R.index
    return R, IND, R.index