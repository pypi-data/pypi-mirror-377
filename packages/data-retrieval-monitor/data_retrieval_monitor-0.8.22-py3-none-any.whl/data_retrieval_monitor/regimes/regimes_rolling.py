# regimes_rolling.py
import numpy as np, pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering, MiniBatchKMeans
from sklearn.mixture import GaussianMixture, BayesianGaussianMixture
from sklearn.decomposition import PCA
from configs import (N_CLUSTERS, ROLL_WINDOW, ROLL_STEP, CLUSTER_VARIANTS,
                     PCA_COMPONENTS, CAUSAL_KNN_K, CAUSAL_KNN_TIME_DECAY, CAUSAL_KNN_METRIC)
from models.label_align import align_labels
from models.knn_causal import causal_knn_refine

def _safe_pca_fit_transform(X_tr, X_all):
    d = min(PCA_COMPONENTS, X_tr.shape[1], max(1, X_tr.shape[0]-1))
    if d <= 0: d = 1
    pca = PCA(n_components=d, random_state=0)
    Z_tr = pca.fit_transform(X_tr)
    Z_all = pca.transform(X_all)
    return Z_tr, Z_all

def _fit_variant(name, X_tr):
    k = max(1, min(N_CLUSTERS, max(1, len(X_tr)-1)))
    meta = CLUSTER_VARIANTS[name]
    algo = meta["algo"]; kw = meta.get("kwargs", {})
    if algo == "kmeans":
        km = KMeans(n_clusters=k, n_init=20, max_iter=500, random_state=0, **kw)
        lab = km.fit_predict(X_tr); ctr = km.cluster_centers_
        return lab, ctr
    if algo == "mbkmeans":
        mb = MiniBatchKMeans(n_clusters=k, batch_size=kw.get("batch_size", 64), n_init=5, random_state=0)
        lab = mb.fit_predict(X_tr); ctr = mb.cluster_centers_
        return lab, ctr
    if algo == "gmm":
        if len(X_tr) < 2: return np.full(len(X_tr), -1, int), None
        gm = GaussianMixture(n_components=k, random_state=0, **kw)
        lab = gm.fit_predict(X_tr); ctr = gm.means_
        return lab, ctr
    if algo == "bayes_gmm":
        if len(X_tr) < 2: return np.full(len(X_tr), -1, int), None
        bg = BayesianGaussianMixture(n_components=k, random_state=0, **kw)
        lab = bg.fit_predict(X_tr); ctr = bg.means_
        return lab, ctr
    if algo == "spectral_pca":
        # do PCA then spectral clustering on window
        d = min(3, X_tr.shape[1], max(1, X_tr.shape[0]-1))
        if d <= 0: d = 1
        Z = PCA(n_components=d, random_state=0).fit_transform(X_tr)
        nn = min(kw.get("n_neighbors", 10), max(2, len(X_tr)-1))
        sp = SpectralClustering(n_clusters=k, affinity="nearest_neighbors", n_neighbors=nn, random_state=0, assign_labels="kmeans")
        lab = sp.fit_predict(Z)
        # centers in PCA space (mean of Z per label)
        ctr = np.vstack([Z[lab==j].mean(axis=0) if np.any(lab==j) else np.zeros(d) for j in range(k)])
        return lab, ctr
    if algo == "agg_pca":
        d = min(3, X_tr.shape[1], max(1, X_tr.shape[0]-1))
        Z = PCA(n_components=d, random_state=0).fit_transform(X_tr)
        ag = AgglomerativeClustering(n_clusters=k, linkage=kw.get("linkage","ward"))
        lab = ag.fit_predict(Z)
        ctr = np.vstack([Z[lab==j].mean(axis=0) if np.any(lab==j) else np.zeros(d) for j in range(k)])
        return lab, ctr
    # fallback
    km = KMeans(n_clusters=k, n_init=10, random_state=0)
    lab = km.fit_predict(X_tr); ctr = km.cluster_centers_
    return lab, ctr

def rolling_regimes(X_all: np.ndarray, dates) -> pd.DataFrame:
    """
    Rolling-window labeling for a suite of variants defined in CONFIG.
    For PCA-based variants, label t using window [t-W, t), then optionally causal kNN refine (past-only).
    """
    T = X_all.shape[0]
    outputs = { f"rw_{name}": np.full(T, -1, int) for name in CLUSTER_VARIANTS.keys() }
    outputs["rw_pca_kmeans"] = np.full(T, -1, int)
    outputs["rw_pca_kmeans_knn"] = np.full(T, -1, int)

    prev_centers = { f"rw_{name}": None for name in CLUSTER_VARIANTS.keys() }
    prev_centers["rw_pca_kmeans"] = None

    Z_cache = np.zeros((T, min(PCA_COMPONENTS, X_all.shape[1])))

    for t in range(ROLL_WINDOW, T, ROLL_STEP):
        win = slice(t-ROLL_WINDOW, t)
        X_tr = X_all[win]

        # --- raw variants
        for name in CLUSTER_VARIANTS.keys():
            lab, ctr = _fit_variant(name, X_tr)
            aligned, perm = align_labels(prev_centers[f"rw_{name}"], ctr, lab)
            prev_centers[f"rw_{name}"] = ctr
            outputs[f"rw_{name}"][t] = aligned[-1]

        # --- PCA + KMeans (+ refine)
        Z_tr, Z_all = _safe_pca_fit_transform(X_tr, X_all)
        km = KMeans(n_clusters=max(1, min(N_CLUSTERS, len(Z_tr))), n_init=20, random_state=0)
        lab_p = km.fit_predict(Z_tr); ctr_p = km.cluster_centers_
        aligned_p, perm_p = align_labels(prev_centers["rw_pca_kmeans"], ctr_p, lab_p)
        prev_centers["rw_pca_kmeans"] = ctr_p
        outputs["rw_pca_kmeans"][t] = aligned_p[-1]
        Z_cache[t,:Z_all.shape[1]] = Z_all[t]

    # --- causal kNN refine for PCA labels (past-only)
    outputs["rw_pca_kmeans_knn"] = causal_knn_refine(
        embeddings=np.where(np.isfinite(Z_cache), Z_cache, 0.0),
        base_labels=outputs["rw_pca_kmeans"],
        k=CAUSAL_KNN_K,
        time_decay=CAUSAL_KNN_TIME_DECAY
    )
    return pd.DataFrame(outputs, index=pd.to_datetime(dates))