import os
import numpy as np
import pandas as pd
from .configs import LEVELS_CSV, INDICATORS_CSV

def _ensure_dt(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()

def _simulate():
    rng = np.random.default_rng(7)
    dates = pd.bdate_range("2018-01-02", "2024-12-31")
    n, n_assets, n_ind = len(dates), 20, 4

    t = np.arange(n)
    IND = pd.DataFrame({
        "Ind1_Growth": 0.5*np.sin(2*np.pi*t/260) + 0.3*rng.standard_normal(n),
        "Ind2_Infl":   0.6*np.cos(2*np.pi*t/500) + 0.3*rng.standard_normal(n),
        "Ind3_Stress": 0.4*np.sin(2*np.pi*t/780 + 1.0) + 0.4*rng.standard_normal(n),
        "Ind4_Liq":    0.6*np.cos(2*np.pi*t/390 + 0.7) + 0.3*rng.standard_normal(n),
    }, index=dates)

    B   = rng.normal(0, 0.1, size=(n_ind, n_assets))
    mu  = rng.normal(0.04/252, 0.02/252, size=n_assets)
    sig = rng.uniform(0.12/np.sqrt(252), 0.3/np.sqrt(252), size=n_assets)

    eps    = rng.standard_normal((n, n_assets)) * sig
    drift  = (IND.values @ B) / 252.0
    rets   = mu + drift + eps
    levels = 100 * np.exp(np.cumsum(rets, axis=0))
    cols   = [f"Factor_{i+1:02d}" for i in range(n_assets)]
    LEVELS = pd.DataFrame(levels, index=dates, columns=cols)
    return LEVELS, IND

def _future_sum_returns(R: pd.DataFrame, h: int) -> pd.DataFrame:
    """Sum of next h daily log-returns aligned to t (predict t→t+h-1)."""
    h = int(h)
    if h <= 1:
        return R.copy()
    return R.rolling(h).sum().shift(-h + 1)

def prepare(horizons=None):
    """
    Returns
    -------
    R : (T x F) log-returns
    IND : (T x K) indicators (NO pre-shift)

    Notes
    -----
    - We do not shift indicators here. Leakage control is handled by lagging
      the predictors (e.g., regime dummies) downstream.
    - Horizon 'h' is only used downstream to build targets via _future_sum_returns.
    - If CSVs aren’t found, simulated data are used.
    - `horizons` is accepted for backward compatibility with older callers but is not used here.
    """
    if os.path.exists(LEVELS_CSV) and os.path.exists(INDICATORS_CSV):
        LEVELS = _ensure_dt(pd.read_csv(LEVELS_CSV, index_col=0))
        IND0   = _ensure_dt(pd.read_csv(INDICATORS_CSV, index_col=0))
    else:
        LEVELS, IND0 = _simulate()

    # log-returns
    R = np.log(LEVELS).diff().dropna()

    # NO SHIFT HERE — use as-is
    IND = IND0.copy()

    # align & drop NaNs
    base = R.join(IND, how="inner").dropna()
    R   = base[R.columns]
    IND = base[IND.columns]
    return R, IND