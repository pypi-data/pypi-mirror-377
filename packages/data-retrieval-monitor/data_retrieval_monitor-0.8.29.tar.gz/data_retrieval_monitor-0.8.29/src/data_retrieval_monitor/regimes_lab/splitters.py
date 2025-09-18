# regimes_lab/splitters.py
import pandas as pd
from typing import Tuple
from .configs import TRAIN_FRAC, VAL_FRAC

def single_split(index: pd.DatetimeIndex) -> Tuple[pd.DatetimeIndex, pd.DatetimeIndex, pd.DatetimeIndex]:
    T = len(index)
    n_tr = int(TRAIN_FRAC*T)
    n_va = int(VAL_FRAC*T)
    return index[:n_tr], index[n_tr:n_tr+n_va], index[n_tr+n_va:]

def future_sum_returns(R, h: int):
    S = R.shift(-1).rolling(window=h).sum()
    return S.shift(-(h-1))