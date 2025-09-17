# src/analytics/regimes2/regimes_rolling.py
__all__ = ["rolling_regimes"]

import numpy as np, pandas as pd
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering, MiniBatchKMeans
from sklearn.mixture import GaussianMixture, BayesianGaussianMixture
from sklearn.decomposition import PCA
from configs import (N_CLUSTERS, ROLL_WINDOW, ROLL_STEP, CLUSTER_VARIANTS,
                     PCA_COMPONENTS, CAUSAL_KNN_K, CAUSAL_KNN_TIME_DECAY, CAUSAL_KNN_METRIC)
from models.label_align import align_labels
from models.knn_causal import causal_knn_refine

def _tiny_jitter(X, eps=1e-8):
    # add tiny noise only if rows are identical / zero variance along some dims
    if X.ndim != 2 or len(X) == 0: return X
    # check degeneracy
    if np.linalg.matrix_rank(X - X.mean(0)) < min(X.shape)-0:
        rng = np.random.default_rng(0)
        return X + rng.normal(0, eps, size=X.shape)
    return X

def _n_unique_rows(X):
    if len(X) == 0: return 0
    return np.unique(np.round(X, decimals=12), axis=0).shape[0]

def _cap_k_by_uniques(k, X):
    nuniq = _n_unique_rows(X)
    return max(1, min(int(k), max(1, nuniq)))

def _safe_pca_fit_transform(X_tr, X_all):
    # cap components by min(n_samples-1, n_features)
    max_comp = max(1, min(PCA_COMPONENTS, X_tr.shape[1], max(1, X_tr.shape[0]-1)))
    pca = PCA(n_components=max_comp, random_state=0)
    Z_tr = pca.fit_transform(X_tr)
    Z_all = pca.transform(X_all)
    return Z_tr, Z_all

def _safe_kmeans(X, k, init="k-means++", n_init=20, max_iter=1000, minibatch=False, batch_size=64):
    X = _tiny_jitter(X)
    k = _cap_k_by_uniques(k, X)
    warnings.filterwarnings("ignore", category=ConvergenceWarning)
    if minibatch:
        km = MiniBatchKMeans(n_clusters=k, n_init=min(10, n_init), batch_size=batch_size,
                             random_state=0, max_iter=max_iter)
    else:
        km = KMeans(n_clusters=k, n_init=n_init, max_iter=max_iter, random_state=0, init=init, algorithm="lloyd")
    try:
        lab = km.fit_predict(X)
        ctr = km.cluster_centers_
        return lab, ctr
    except Exception:
        # fallback: reduce k to distinct rows /2
        k2 = max(1, min(k-1, _cap_k_by_uniques(k-1, X)))
        if k2 < k:
            if minibatch:
                km2 = MiniBatchKMeans(n_clusters=k2, n_init=5, batch_size=batch_size, random_state=0, max_iter=max_iter)
            else:
                km2 = KMeans(n_clusters=k2, n_init=10, max_iter=max_iter, random_state=0)
            lab = km2.fit_predict(X)
            ctr = km2.cluster_centers_
            return lab, ctr
        # ultimate fallback: single cluster
        return np.zeros(len(X), dtype=int), X.mean(0, keepdims=True)

def _safe_gmm(X, k, cov="full"):
    if len(X) < 2:
        return np.zeros(len(X), dtype=int), X.mean(0, keepdims=True) if len(X)>0 else None
    X = _tiny_jitter(X)
    k = _cap_k_by_uniques(k, X)
    try:
        gm = GaussianMixture(n_components=k, covariance_type=cov, random_state=0)
        lab = gm.fit_predict(X); ctr = gm.means_
        return lab, ctr
    except Exception:
        # reduce k
        k2 = max(1, k-1)
        try:
            gm2 = GaussianMixture(n_components=k2, covariance_type=cov, random_state=0)
            lab = gm2.fit_predict(X); ctr = gm2.means_
            return lab, ctr
        except Exception:
            return np.zeros(len(X), dtype=int), X.mean(0, keepdims=True)

def _safe_bayes_gmm(X, k, cov="full"):
    if len(X) < 2:
        return np.zeros(len(X), dtype=int), X.mean(0, keepdims=True) if len(X)>0 else None
    X = _tiny_jitter(X)
    k = _cap_k_by_uniques(k, X)
    try:
        bg = BayesianGaussianMixture(n_components=k, covariance_type=cov, random_state=0)
        lab = bg.fit_predict(X); ctr = bg.means_
        return lab, ctr
    except Exception:
        return np.zeros(len(X), dtype=int), X.mean(0, keepdims=True)

def _safe_spectral_on_pca(X, k, base_neighbors=10):
    """
    PCA -> kNN graph; ensure connectivity by growing neighbors.
    Fallback: RBF affinity; Final fallback: Agglomerative on PCA.
    Returns labels (len(X),) and centers in PCA space.
    """
    if len(X) <= 1:
        return np.zeros(len(X), dtype=int), X.mean(0, keepdims=True) if len(X)>0 else None
    # PCA reduce
    d = max(1, min(3, X.shape[1], max(1, X.shape[0]-1)))
    Z = PCA(n_components=d, random_state=0).fit_transform(_tiny_jitter(X))
    k_eff = _cap_k_by_uniques(k, Z)
    # try growing neighbors until connected or we hit limit
    N = len(Z)
    for nn in range(min(base_neighbors, max(2, N-1)), max(2, N), 2):
        G = kneighbors_graph(Z, n_neighbors=min(nn, N-1), mode='connectivity', include_self=False)
        n_comp, labels_cc = connected_components(G, directed=False)
        if n_comp == 1:
            try:
                sp = SpectralClustering(n_clusters=k_eff, affinity="nearest_neighbors",
                                        n_neighbors=min(nn, N-1), random_state=0, assign_labels="kmeans")
                lab = sp.fit_predict(Z)
                ctr = np.vstack([Z[lab==j].mean(axis=0) if np.any(lab==j) else np.zeros(d) for j in range(k_eff)])
                return lab, ctr
            except Exception:
                pass
    # Fallback: RBF kernel (fully connected)
    try:
        sp = SpectralClustering(n_clusters=k_eff, affinity="rbf", gamma=None, random_state=0, assign_labels="kmeans")
        lab = sp.fit_predict(Z)
        ctr = np.vstack([Z[lab==j].mean(axis=0) if np.any(lab==j) else np.zeros(d) for j in range(k_eff)])
        return lab, ctr
    except Exception:
        # Final fallback: Agglomerative on PCA
        try:
            ag = AgglomerativeClustering(n_clusters=k_eff, linkage="ward")
            lab = ag.fit_predict(Z)
            ctr = np.vstack([Z[lab==j].mean(axis=0) if np.any(lab==j) else np.zeros(d) for j in range(k_eff)])
            return lab, ctr
        except Exception:
            return np.zeros(len(Z), dtype=int), Z.mean(0, keepdims=True)

def _fit_variant(name, X_tr):
    meta = CLUSTER_VARIANTS[name]
    algo = meta["algo"]; kw = meta.get("kwargs", {})
    k = _cap_k_by_uniques(N_CLUSTERS, X_tr)

    if algo == "kmeans":
        init = kw.get("init", "k-means++")
        return _safe_kmeans(X_tr, k, init=init, n_init=20, max_iter=1000, minibatch=False)

    if algo == "mbkmeans":
        bs = kw.get("batch_size", 64)
        return _safe_kmeans(X_tr, k, minibatch=True, batch_size=bs)

    if algo == "gmm":
        cov = kw.get("covariance_type", "full")
        return _safe_gmm(X_tr, k, cov=cov)

    if algo == "bayes_gmm":
        cov = kw.get("covariance_type", "full")
        return _safe_bayes_gmm(X_tr, k, cov=cov)

    if algo == "spectral_pca":
        nn = kw.get("n_neighbors", 15)
        return _safe_spectral_on_pca(X_tr, k, base_neighbors=nn)

    if algo == "agg_pca":
        # PCA + Agglomerative
        d = max(1, min(3, X_tr.shape[1], max(1, X_tr.shape[0]-1)))
        Z = PCA(n_components=d, random_state=0).fit_transform(_tiny_jitter(X_tr))
        k_eff = _cap_k_by_uniques(k, Z)
        ag = AgglomerativeClustering(n_clusters=k_eff, linkage=kw.get("linkage","ward"))
        lab = ag.fit_predict(Z)
        ctr = np.vstack([Z[lab==j].mean(axis=0) if np.any(lab==j) else np.zeros(d) for j in range(k_eff)])
        return lab, ctr

    # fallback to kmeans
    return _safe_kmeans(X_tr, k, init="k-means++", n_init=20, max_iter=1000, minibatch=False)

def rolling_regimes(X_all: np.ndarray, dates) -> pd.DataFrame:
    """
    Rolling-window labeling for a suite of variants defined in CONFIG.
    Returns a DataFrame of shape (T, num_models) with columns like 'rw_kmeans_raw', ...
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
            aligned, _ = align_labels(prev_centers[f"rw_{name}"], ctr, lab)
            prev_centers[f"rw_{name}"] = ctr
            outputs[f"rw_{name}"][t] = aligned[-1]

        # --- PCA + KMeans (+ refine later)
        Z_tr, Z_all = _safe_pca_fit_transform(X_tr, X_all)
        km = KMeans(n_clusters=max(1, min(N_CLUSTERS, len(Z_tr))), n_init=20, random_state=0)
        lab_p = km.fit_predict(Z_tr); ctr_p = km.cluster_centers_
        aligned_p, _ = align_labels(prev_centers["rw_pca_kmeans"], ctr_p, lab_p)
        prev_centers["rw_pca_kmeans"] = ctr_p
        outputs["rw_pca_kmeans"][t] = aligned_p[-1]
        Z_cache[t,:Z_all.shape[1]] = Z_all[t]

    outputs["rw_pca_kmeans_knn"] = causal_knn_refine(
        embeddings=np.where(np.isfinite(Z_cache), Z_cache, 0.0),
        base_labels=outputs["rw_pca_kmeans"],
        k=CAUSAL_KNN_K,
        time_decay=CAUSAL_KNN_TIME_DECAY,
        metric=CAUSAL_KNN_METRIC
    )
    return pd.DataFrame(outputs, index=pd.to_datetime(dates))