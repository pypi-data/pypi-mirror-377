import numpy as np, pandas as pd

def future_sum_returns(R: pd.DataFrame, h: int) -> pd.DataFrame:
    """Sum of next h returns aligned to current timestamp index (right-closed)."""
    return R.rolling(window=h, min_periods=h).sum().shift(-h)