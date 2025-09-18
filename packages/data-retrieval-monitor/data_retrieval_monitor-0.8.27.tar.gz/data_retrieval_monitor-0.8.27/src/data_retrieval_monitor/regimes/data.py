import numpy as np, pandas as pd, os
from configs import LEVELS_CSV, INDICATORS_CSV, IND_LAG_BDAYS
from utils import ensure_datetime_index

class DataModule:
    def __init__(self, levels_csv=LEVELS_CSV, indicators_csv=INDICATORS_CSV, lag_bdays=IND_LAG_BDAYS):
        self.levels_csv = levels_csv
        self.indicators_csv = indicators_csv
        self.lag_bdays = lag_bdays

    def _bday_lag(self, df, bdays): return df.shift(bdays)

    def load_or_simulate(self):
        if os.path.exists(self.levels_csv) and os.path.exists(self.indicators_csv):
            levels = ensure_datetime_index(pd.read_csv(self.levels_csv, index_col=0))
            ind = ensure_datetime_index(pd.read_csv(self.indicators_csv, index_col=0))
            return levels, ind, True
        rng = np.random.default_rng(42)
        dates = pd.bdate_range("2017-01-03", "2024-12-31")
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
        eps = rng.standard_normal((n, n_assets)) * base_sigma
        drift = (ind.values @ B) / 252.0
        rets = base_mu + drift + eps
        levels = 100 * np.exp(np.cumsum(rets, axis=0))
        cols = [f"Factor_{i+1:02d}" for i in range(n_assets)]
        levels = pd.DataFrame(levels, index=dates, columns=cols)
        return levels, ind, False

    def prepare(self):
        levels, indicators, _ = self.load_or_simulate()
        logp = np.log(levels); returns = logp.diff().dropna()
        ind_lag = self._bday_lag(indicators, self.lag_bdays)
        data = returns.join(ind_lag, how="inner").dropna()
        returns_aligned = data[returns.columns]
        indicators_aligned = data[ind_lag.columns]
        X_all = (indicators_aligned - indicators_aligned.mean()) / (indicators_aligned.std() + 1e-12)
        return returns_aligned, indicators_aligned, X_all.values, returns_aligned.index