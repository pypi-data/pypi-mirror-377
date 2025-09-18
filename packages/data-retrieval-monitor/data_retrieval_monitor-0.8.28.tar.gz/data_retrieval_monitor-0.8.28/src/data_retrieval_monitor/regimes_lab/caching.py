# regimes_lab/caching.py
import os
import joblib
import pandas as pd
from typing import Any
from .configs import CACHE_DIR, REG_DIR

def cache_path(name: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, name)

def save_model(obj: Any, name: str):
    joblib.dump(obj, cache_path(name))

def load_model(name: str) -> Any | None:
    p = cache_path(name)
    if os.path.exists(p):
        return joblib.load(p)
    return None

def save_labels(df: pd.DataFrame, model_name: str, split_tag: str):
    os.makedirs(REG_DIR, exist_ok=True)
    df.to_csv(os.path.join(REG_DIR, f"labels_{model_name}_{split_tag}.csv"))

def try_load_labels(model_name: str, split_tag: str) -> pd.DataFrame | None:
    p = os.path.join(REG_DIR, f"labels_{model_name}_{split_tag}.csv")
    if os.path.exists(p):
        return pd.read_csv(p, index_col=0, parse_dates=True)
    return None