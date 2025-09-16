# data.py
import numpy as np, pandas as pd, os
from sklearn.preprocessing import StandardScaler
from configs import LEVELS_CSV, INDICATORS_CSV, IND_LAG, TRAIN_FRAC, VAL_FRAC
from utils import ensure_datetime_index

def load_or_simulate():
    if os.path.exists(LEVELS_CSV) and os.path.exists(INDICATORS_CSV):
        levels = ensure_datetime_index(pd.read_csv(LEVELS_CSV, index_col=0))
        indicators = ensure_datetime_index(pd.read_csv(INDICATORS_CSV, index_col=0))
        return levels, indicators, True
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2017-01-03", "2024-12-31")
    n, n_assets, n_ind = len(dates), 20, 4
    t = np.arange(n)
    indicators = pd.DataFrame({
        "Ind1_Growth": 0.5*np.sin(2*np.pi*t/260) + 0.3*rng.standard_normal(n),
        "Ind2_Infl":   0.6*np.cos(2*np.pi*t/500) + 0.3*rng.standard_normal(n),
        "Ind3_Stress": 0.4*np.sin(2*np.pi*t/780 + 1.0) + 0.4*rng.standard_normal(n),
        "Ind4_Liq":    0.6*np.cos(2*np.pi*t/390 + 0.7) + 0.3*rng.standard_normal(n),
    }, index=dates)
    B = rng.normal(0, 0.1, size=(n_ind, n_assets))
    base_mu = rng.normal(0.04/252, 0.02/252, size=n_assets)
    base_sigma = rng.uniform(0.12/np.sqrt(252), 0.3/np.sqrt(252), size=n_assets)
    eps = rng.standard_normal((n, n_assets)) * base_sigma
    drift = (indicators.values @ B) / 252.0
    rets = base_mu + drift + eps
    levels = 100 * np.exp(np.cumsum(rets, axis=0))
    cols = [f"Factor_{i+1:02d}" for i in range(n_assets)]
    levels = pd.DataFrame(levels, index=dates, columns=cols)
    print(">> CSVs not found; generated synthetic dataset.")
    return levels, indicators, False

def prepare_data():
    levels, indicators, loaded = load_or_simulate()
    logp = np.log(levels); returns = logp.diff().dropna()
    ind_shifted = indicators.shift(IND_LAG)
    data = returns.join(ind_shifted, how="inner").dropna()
    returns_aligned   = data[returns.columns]
    indicators_aligned = data[ind_shifted.columns]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(indicators_aligned.values)
    dates = indicators_aligned.index
    return returns_aligned, indicators_aligned, X_scaled, dates

def tvt_slices(T):
    n_train = int(TRAIN_FRAC*T)
    n_val = int(VAL_FRAC*T)
    return slice(0, n_train), slice(n_train, n_train+n_val), slice(n_train+n_val, T)