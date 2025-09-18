# regimes_lab/rolling.py
import numpy as np
import pandas as pd
from typing import Dict
from .configs import CADENCE, RECURSIVE
from .regimes import build_models
from .features import scale_indicators

def rolling_or_recursive_labels(IND: pd.DataFrame, train_end_idx: int) -> pd.DataFrame:
    """
    Train on [0:train_end), then either recursive (use all past) or rolling (last window),
    refitting every CADENCE steps to label post-train dates.
    """
    X_all, sc = scale_indicators(IND)
    dates = IND.index
    models = build_models(d_in=X_all.shape[1])
    out = {m.name: pd.Series(index=dates, dtype="Int64") for m in models}

    last_fit_t = None
    for t in range(train_end_idx, len(dates)):
        if (last_fit_t is None) or ((t - (last_fit_t or 0)) >= CADENCE):
            # training slice
            if RECURSIVE:
                sl = slice(0, t)  # all past
            else:
                # use a rolling window of max 2000 (or all past if shorter)
                start = max(0, t-2000)
                sl = slice(start, t)
            X_tr = X_all[sl]
            for m in models:
                try:
                    m.fit(X_tr)
                except Exception as e:
                    print(f"[WARN] rolling fit {m.name} failed at t={t}: {e}")
            last_fit_t = t
        X_te = X_all[t:t+CADENCE]
        for m in models:
            try:
                labs = m.predict(X_te)
            except Exception:
                labs = np.zeros(len(X_te), dtype=int)
            out[m.name].iloc[t:t+CADENCE] = labs
    return pd.DataFrame(out, index=dates)