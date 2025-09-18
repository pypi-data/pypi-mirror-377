# regimes_lab/features.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def scale_indicators(IND: pd.DataFrame):
    sc = StandardScaler()
    X = sc.fit_transform(IND.values.astype(float))
    return X, sc