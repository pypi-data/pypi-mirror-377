# regimes.py
import numpy as np, pandas as pd, os
from configs import (OUTPUT_DIR, N_CLUSTERS, RECURSIVE_ESTIMATION, REFIT_STEP, RECURSIVE_INCLUDE_DEEP)
from models.clustering import kmeans_labels, gmm_labels, knn_refine
from models.pca_cluster import pca_cluster
from models.saint import fit_saint_embeddings_train
from models.vqvae import fit_vqvae_train
from models.vae import fit_vae_train
from models.distributional import (rolling_gaussian_distances, rolling_vae_distances,
                                   gmm_regimes_train, lda_qda_regimes_train)
from models.hmm_model import hmm_labels_train
from models.gbdt import gbdt_cluster_train
from utils import save_table
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


def _batch_all(X_train, X_all, dates, returns_aligned):
    regimes = {}
    # KMeans on raw (always safe)
    km_raw, _ = kmeans_labels(X_all, dates, name="kmeans_ind")
    regimes["kmeans_ind"] = km_raw

    # GMM on raw (safe-guarded inside gmm_labels)
    gmm_raw, _ = gmm_labels(X_all, dates, name="gmm_ind")
    regimes["gmm_ind"] = gmm_raw

    # PCA + clustering (PCA fit on train)
    base_pca, ref_pca, Z_all = pca_cluster(X_train, X_all, dates, method="kmeans")
    regimes["kmeans_pca"] = base_pca; regimes["kmeans_pca_knn"] = ref_pca
    base_gpc, ref_gpc, Z_all2 = pca_cluster(X_train, X_all, dates, method="gmm")
    regimes["gmm_pca"] = base_gpc; regimes["gmm_pca_knn"] = ref_gpc

    # SAINT (train on train only), then cluster & kNN refine
    saint_emb = fit_saint_embeddings_train(X_train, X_all)
    if saint_emb is not None:
        km_s = KMeans(n_clusters=N_CLUSTERS, n_init=50, max_iter=1000, random_state=0).fit_predict(saint_emb)
        regimes["saint_kmeans"] = km_s
        regimes["saint_knn"] = knn_refine(saint_emb, km_s, name_suffix="saint_knn", dates=dates)

    # VQ-VAE
    vq_model, vq_idx = fit_vqvae_train(X_train, X_all)
    if vq_idx is not None:
        regimes["vqvae_ind"] = vq_idx.astype(int)

    # VAE latent distances
    vae, MU, VAR = fit_vae_train(X_train, X_all)
    if MU is not None:
        dist_vae = rolling_vae_distances(MU, VAR, dates)
        dist_vae.to_csv(os.path.join(OUTPUT_DIR, "vae_rolling_gaussian_distances.csv"))

    # Distributional distances on raw indicators
    dist_raw = rolling_gaussian_distances(X_all, dates)
    dist_raw.to_csv(os.path.join(OUTPUT_DIR, "rolling_gaussian_distances.csv"))

    # GMM (distributional) trained on TRAIN
    dlab, _ = gmm_regimes_train(X_train, X_all, n_comp=N_CLUSTERS)
    regimes["gmm_dist_train"] = dlab

    # LDA/QDA using km_raw first |train| labels
    ytr = km_raw[:len(X_train)]
    lda_lab, _ = lda_qda_regimes_train(X_train, ytr, X_all, which="lda")
    regimes["lda_regimes"] = lda_lab
    qda_lab, _ = lda_qda_regimes_train(X_train, ytr, X_all, which="qda")
    regimes["qda_regimes"] = qda_lab

    # HMM
    hmm_lab, _ = hmm_labels_train(X_train, X_all, n_comp=N_CLUSTERS)
    if hmm_lab is not None:
        regimes["hmm_ind"] = hmm_lab

    # NEW: GBDT-based clustering (leaf embeddings -> KMeans)
    gbdt_lab, gbdt_info = gbdt_cluster_train(X_train, X_all, base_labels=ytr)
    if gbdt_lab is not None:
        regimes["gbdt_cluster"] = gbdt_lab

    regimes_df = pd.DataFrame(regimes, index=pd.to_datetime(dates))
    save_table(regimes_df, "regimes_by_model")
    return regimes_df

def _recursive_estimation(X_all, dates):
    """
    Walk-forward regime labeling.
    Refit models every REFIT_STEP using data up to t-1, then label point t.
    Always safe-guard against tiny sample counts.
    """
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    from sklearn.mixture import GaussianMixture
    from models.gbdt import gbdt_cluster_train, _pseudo_labels_from_kmeans

    T, d = X_all.shape
    labels_dict = {
        "rec_kmeans_pca": np.full(T, -1, dtype=int),
        "rec_gmm":        np.full(T, -1, dtype=int),
        "rec_gbdt":       np.full(T, -1, dtype=int),
    }

    pca_cached = None
    km_cached  = None
    gmm_cached = None
    gbdt_cached = None  # tuple (info_dict, y_tr) or None

    for t in range(1, T):
        refit = (t % REFIT_STEP == 0) or (t <= REFIT_STEP)
        if refit:
            X_tr = X_all[:t]  # strictly prior to t
            n = X_tr.shape[0]

            # ---------- SAFE PCA + KMeans ----------
            if n > 1:
                n_comps = min(3, n - 1, d)  # safe cap
                pca_cached = PCA(n_components=n_comps, random_state=0).fit(X_tr)
                Z_tr = pca_cached.transform(X_tr)
                k_km = max(1, min(N_CLUSTERS, n))  # KMeans can use k==n if needed
                km_cached = KMeans(n_clusters=k_km, n_init=min(50, n), max_iter=1000, random_state=0).fit(Z_tr)
            else:
                # too few samples for PCA; cluster raw with k=1
                pca_cached = None
                k_km = 1
                km_cached = KMeans(n_clusters=k_km, n_init=1, max_iter=100, random_state=0).fit(X_tr)

            # ---------- SAFE GMM on raw ----------
            if n >= 2:
                k_gmm = max(1, min(N_CLUSTERS, n - 1))
                gmm_cached = GaussianMixture(n_components=k_gmm, covariance_type="full", random_state=0).fit(X_tr)
            else:
                gmm_cached = None  # not enough data; skip

            # ---------- SAFE GBDT clustering ----------
            # pseudo-labels from KMeans on X_tr (safe for any n >= 1)
            k_pl = max(1, min(N_CLUSTERS, n))
            y_tr = _pseudo_labels_from_kmeans(X_tr, n_clusters=k_pl)
            try:
                gbdt_lab, gbdt_info = gbdt_cluster_train(X_tr, X_all[:t], base_labels=y_tr)
                gbdt_cached = (gbdt_info, y_tr) if gbdt_lab is not None else None
            except Exception:
                gbdt_cached = None

        # ----- infer label at time t with current caches -----
        x_t = X_all[t:t+1]

        # PCA+KMeans label
        if km_cached is not None:
            if pca_cached is not None:
                z_t = pca_cached.transform(x_t)
                labels_dict["rec_kmeans_pca"][t] = km_cached.predict(z_t)[0]
            else:
                labels_dict["rec_kmeans_pca"][t] = km_cached.predict(x_t)[0]

        # GMM label
        if gmm_cached is not None:
            labels_dict["rec_gmm"][t] = gmm_cached.predict(x_t)[0]
        else:
            labels_dict["rec_gmm"][t] = -1  # unknown until enough samples

        # GBDT cluster label
        if gbdt_cached is not None:
            info, _ = gbdt_cached
            be = info["backend"]
            try:
                if be == "lightgbm":
                    leaves = info["gbdt_model"].predict(x_t, pred_leaf=True)
                elif be == "xgboost":
                    import xgboost as xgb
                    leaves = info["gbdt_model"].predict(xgb.DMatrix(x_t), pred_leaf=True)
                elif be == "catboost":
                    from catboost import Pool
                    leaves = info["gbdt_model"].calc_leaf_indexes(Pool(x_t))
                else:
                    leaves = None
                if leaves is not None:
                    labels_dict["rec_gbdt"][t] = info["km"].predict(np.asarray(leaves))[0]
            except Exception:
                labels_dict["rec_gbdt"][t] = -1
        else:
            labels_dict["rec_gbdt"][t] = -1

    regimes_df = pd.DataFrame(labels_dict, index=pd.to_datetime(dates))
    save_table(regimes_df, "regimes_recursive_by_model")
    return regimes_df

def build_all_regimes(X_train, X_all, dates, returns_aligned):
    if RECURSIVE_ESTIMATION:
        print("[INFO] Running recursive (walk-forward) estimation...")
        regimes_df = _recursive_estimation(X_all, dates)
        # Also compute distributional distances (batch) for diagnostics
        from models.distributional import rolling_gaussian_distances
        dist_raw = rolling_gaussian_distances(X_all, dates)
        dist_raw.to_csv(os.path.join(OUTPUT_DIR, "rolling_gaussian_distances.csv"))
        return regimes_df
    else:
        print("[INFO] Running batch estimation (train → all)...")
        return _batch_all(X_train, X_all, dates, returns_aligned)