# models/pca_cluster.py
import numpy as np
from sklearn.decomposition import PCA
from models.clustering import kmeans_labels, gmm_labels, knn_refine
from configs import PCA_COMPONENTS

def _safe_pca_fit_transform(X_train, X_all):
    X_train = np.asarray(X_train); X_all = np.asarray(X_all)
    n_samples, n_features = X_train.shape
    max_comps = min(PCA_COMPONENTS, max(1, n_samples - 1), n_features)
    if n_samples <= 1 or max_comps < 1:
        # Not enough data for PCA; identity embedding
        return X_all.copy(), None
    pca = PCA(n_components=max_comps, random_state=0)
    pca.fit(X_train)
    Z_all = pca.transform(X_all)
    return Z_all, pca

def pca_cluster(X_train, X_all, dates, method="kmeans"):
    Z_all, _ = _safe_pca_fit_transform(X_train, X_all)
    name_root = f"{method}_pca"
    if method == "kmeans":
        base, _ = kmeans_labels(Z_all, dates, name=name_root)
    else:
        base, _ = gmm_labels(Z_all, dates, name=name_root)
    refined = knn_refine(Z_all, base, name_suffix=f"{name_root}_knn", dates=dates)
    return base, refined, Z_all