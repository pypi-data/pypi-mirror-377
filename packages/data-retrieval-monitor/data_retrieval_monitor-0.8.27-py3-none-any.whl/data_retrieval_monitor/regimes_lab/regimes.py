# regimes_lab/regimes.py
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from .features import scale_indicators
from .caching import save_labels, try_load_labels
from .configs import N_CLUSTERS, PCA_DIM

from .models.gmm import GMM, BayesGMM
from .models.hmm import HMMGaussian
from .models.saint_knn import SaintKNN
from .models.vqvae import VQVAERegimes
from .models.vae_latent import VAERegimes
from .models.conformal import ConformalRegimes

def build_models(d_in: int):
    models = [
        GMM(k=N_CLUSTERS),
        BayesGMM(k=N_CLUSTERS),
        HMMGaussian(k=N_CLUSTERS),
        SaintKNN(d_in=d_in, k_regimes=N_CLUSTERS, d_lat=32),
        VQVAERegimes(d_in=d_in, codebook=N_CLUSTERS, d_lat=16),
        VAERegimes(d_in=d_in, d_lat=8, k=N_CLUSTERS),
        ConformalRegimes(k=N_CLUSTERS),
    ]
    return models

def fit_predict_all(IND: pd.DataFrame, split_tag: str):
    """Fit each model on IND and save labels_<model>_<split_tag>.csv"""
    X, _ = scale_indicators(IND)
    models = build_models(d_in=X.shape[1])

    labels = {}
    for m in models:
        try:
            labs = _fit_predict_one(m, X)
        except Exception as e:
            print(f"[WARN] {m.name} failed: {e}; filling zeros")
            labs = np.zeros(len(X), dtype=int)
        s = pd.Series(labs, index=IND.index, name=m.name)
        save_labels(s.to_frame(), m.name, split_tag)
        labels[m.name] = s
    return pd.DataFrame(labels, index=IND.index)

def _fit_predict_one(m, X):
    m.fit(X)
    return m.predict(X)

def make_dummies(labels_df: pd.DataFrame, full_index: pd.DatetimeIndex) -> pd.DataFrame:
    parts=[]
    for col in labels_df.columns:
        ser = labels_df[col].dropna().astype("Int64")
        oh = pd.get_dummies(ser, prefix=f"{col}_R", dtype=int)
        oh = oh.reindex(full_index).fillna(0).astype(int)
        parts.append(oh)
    if not parts:
        return pd.DataFrame(index=full_index)
    D = pd.concat(parts, axis=1)
    return D.loc[:, ~D.columns.duplicated()].astype(int)

def load_or_build_labels(IND: pd.DataFrame, split_tag: str):
    # try load all; if any missing, rebuild all for consistency
    want = ["gmm","bayesgmm","hmm","saint_knn","vqvae","vae","conformal"]
    cols=[]; dfs=[]
    for w in want:
        df = try_load_labels(w, split_tag)
        if df is None:
            return fit_predict_all(IND, split_tag)
        dfs.append(df)
        cols.append(w)
    L = pd.concat([df for df in dfs], axis=1)
    L.columns = cols
    return L.reindex(IND.index)