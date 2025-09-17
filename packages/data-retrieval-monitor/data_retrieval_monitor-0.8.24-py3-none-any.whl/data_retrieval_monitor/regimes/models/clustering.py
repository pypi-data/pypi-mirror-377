# models/clustering.py
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.neighbors import NearestNeighbors
from configs import N_CLUSTERS, KMEANS_N_INIT, KMEANS_MAX_ITER, KNN_K
from utils import plot_timeline_chunked

def _safe_k(n_samples, desired):
    return max(1, min(desired, n_samples))

def kmeans_labels(X, dates, name="kmeans"):
    X = np.asarray(X)
    n = X.shape[0]
    if n == 0:
        lab = np.array([], dtype=int)
        return lab, None
    k = _safe_k(n, N_CLUSTERS)  # n_clusters ≤ n_samples
    km = KMeans(n_clusters=k, n_init=min(KMEANS_N_INIT, n), max_iter=KMEANS_MAX_ITER, random_state=0)
    lab = km.fit_predict(X)
    if dates is not None and len(lab) > 0:
        plot_timeline_chunked(lab, dates, title=f"Regimes — {name}", fname=f"exhibit4_{name}")
    return lab, km.cluster_centers_

def gmm_labels(X, dates, name="gmm"):
    X = np.asarray(X)
    n = X.shape[0]
    if n < 2:
        # Not enough samples for GMM; mark as unknown (-1)
        lab = np.full(n, -1, dtype=int)
        return lab, (None, None)
    # GMM requires n_components ≤ n_samples - 1
    k = max(1, min(N_CLUSTERS, n - 1))
    gmm = GaussianMixture(n_components=k, covariance_type="full", random_state=0)
    lab = gmm.fit_predict(X)
    if dates is not None and len(lab) > 0:
        plot_timeline_chunked(lab, dates, title=f"Regimes — {name}", fname=f"exhibit4_{name}")
    return lab, (gmm.means_, gmm.covariances_)

def knn_refine(embeddings, base_labels, k=KNN_K, name_suffix="knn", dates=None):
    E = np.asarray(embeddings)
    n = E.shape[0]
    if n < 2:
        refined = np.asarray(base_labels, dtype=int)
        return refined
    kk = max(2, min(k, n - 1))
    nbrs = NearestNeighbors(n_neighbors=kk)
    nbrs.fit(E)
    neigh = nbrs.kneighbors(return_distance=False)
    refined = []
    base_labels = np.asarray(base_labels)
    for idxs in neigh:
        vals, cnt = np.unique(base_labels[idxs], return_counts=True)
        refined.append(vals[np.argmax(cnt)])
    refined = np.asarray(refined, dtype=int)
    if dates is not None and len(refined) > 0:
        plot_timeline_chunked(refined, dates, title=f"Regimes — {name_suffix}", fname=f"exhibit4_{name_suffix}")
    return refined