import numpy as np
import pandas as pd
import os 
from configs import (SEED, TRAIN_FRAC, VAL_FRAC, SUBDIRS)
from data import DataModule
from models.klassic import KMeansPCA, GMMRaw, BayesGMMRaw
from models.torch_models import SaintKMeans, VQVAERegimes, MaskedDAERegimes
from models.hmm_model import HMMRegimes
from rolling_engine import RegimeRollingEngine
from perf import PerformanceEvaluator
from stats import build_indicator_sign_dummies, run_ols_per_model_split
from scoring import score_models
from factor_selectors import LambdaMARTSelector, SaintMLPSelector

np.random.seed(SEED)

def tvt_slices(T, train_frac=TRAIN_FRAC, val_frac=VAL_FRAC):
    n_train = int(train_frac*T); n_val = int(val_frac*T)
    return slice(0,n_train), slice(n_train, n_train+n_val), slice(n_train+n_val, T)

def main():
    # 1) Data (+2BD lag inside)
    dm = DataModule()
    R, IND, X_all, dates = dm.prepare()

    # 2) Splits
    T = len(X_all)
    sl_tr, sl_va, sl_te = tvt_slices(T)

    # 3) Models (OOP; mix differentiable & classical)
    models = [
        KMeansPCA(name="rw_pca_kmeans", n_clusters=4, pca_dim=3),
        GMMRaw(name="rw_gmm_full", n_clusters=4, cov_type="full"),
        BayesGMMRaw(name="rw_bayes_gmm", n_clusters=4, cov_type="full"),
        SaintKMeans(name="rw_saint_kmeans", n_clusters=4, epochs=8, lr=1e-3),
        VQVAERegimes(name="rw_vqvae_codes", n_codes=16, epochs=25, lr=2e-3),
        MaskedDAERegimes(name="rw_maskeddae_kmeans", d_emb=32, epochs=15, lr=1e-3, n_clusters=4),
        HMMRegimes(name="rw_hmm", n_states=4),
    ]

    # 4) Rolling/Recursive engine (causal)
    engine = RegimeRollingEngine(models, add_knn_on_embeddings=True)
    regimes_df = engine.build(X_all, dates)
    regimes_df.to_csv(os.path.join(SUBDIRS["regimes"], "regimes_by_model.csv"))

    # 5) Train/Test perf export
    pe = PerformanceEvaluator(R, regimes_df)
    pe.save_split(sl_tr, sl_te)

    # 6) OLS train/val per model (for scoring)
    ols_split = run_ols_per_model_split(R, IND, regimes_df, sl_tr, sl_va, include_sign=True)

    # 7) Score models (train→val stability etc.) and choose production set
    prod_models = score_models(R, regimes_df, sl_tr, sl_va, ols_split)

    # 8) Selector features = indicators (+ sign dummies) + production regime dummies
    if prod_models:
        dum_all = []
        for m in prod_models:
            
            d = pd.get_dummies(regimes_df[m], prefix=f"{m}_R", dtype=int)
            dum_all.append(d)
        regime_dummies = pd.concat(dum_all, axis=1).reindex(R.index).fillna(0)
    else:
        regime_dummies = pd.get_dummies(regimes_df, dtype=int).reindex(R.index).fillna(0)

    X_features = pd.concat([IND, build_indicator_sign_dummies(IND), regime_dummies], axis=1).fillna(0)

    # 9) Selectors (LambdaMART + SAINT MLP)
    _ = LambdaMARTSelector().run(R, X_features)
    _ = SaintMLPSelector().run(R, X_features)

    print("Done. See output2/* for artifacts.")

if __name__ == "__main__":
    main()
