import numpy as np
from sklearn.cluster import KMeans
from .base import BaseRegimeModel, register_model

@register_model("kmeans_raw")
class KMeansRaw(BaseRegimeModel):
    def __init__(self, n_clusters=12, n_init=20, random_state=0):
        super().__init__("kmeans_raw")
        self.k = n_clusters
        self.n_init = n_init
        self.random_state = random_state
        self.km_ = None

    def fit(self, X: np.ndarray):
        km = KMeans(n_clusters=self.k, n_init=self.n_init, random_state=self.random_state)
        self.train_labels_ = km.fit_predict(X)
        self.km_ = km
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.km_ is None:
            return np.zeros(len(X), dtype=int)
        return self.km_.predict(X)