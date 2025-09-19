import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from .base import BaseRegimeModel, register_model

@register_model("pca_kmeans")
class PCAKMeans(BaseRegimeModel):
    def __init__(self, n_clusters=12, n_components=3, n_init=20, random_state=0, whiten=False):
        super().__init__("pca_kmeans")
        self.k = n_clusters
        self.p = n_components
        self.n_init = n_init
        self.random_state = random_state
        self.whiten = whiten
        self.pca_ = None
        self.km_ = None

    def fit(self, X: np.ndarray):
        p = min(self.p, X.shape[1])
        pca = PCA(n_components=p, whiten=self.whiten, random_state=self.random_state)
        Z = pca.fit_transform(X)
        km = KMeans(n_clusters=self.k, n_init=self.n_init, random_state=self.random_state)
        self.train_labels_ = km.fit_predict(Z)
        self.pca_, self.km_ = pca, km
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.pca_ is None or self.km_ is None:
            return np.zeros(len(X), dtype=int)
        Z = self.pca_.transform(X)
        return self.km_.predict(Z)