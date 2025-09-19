import numpy as np, warnings
from sklearn.cluster import KMeans, MiniBatchKMeans, AgglomerativeClustering, SpectralClustering
from sklearn.mixture import GaussianMixture, BayesianGaussianMixture
from sklearn.decomposition import PCA
from sklearn.neighbors import kneighbors_graph
from sklearn.exceptions import ConvergenceWarning
from scipy.sparse.csgraph import connected_components
from models.base import BaseRegimeModel

def _tiny_jitter(X, eps=1e-8):
    if X.ndim!=2 or len(X)==0: return X
    import numpy as np
    if np.linalg.matrix_rank(X - X.mean(0)) < min(X.shape):
        rng = np.random.default_rng(0); return X + rng.normal(0, eps, size=X.shape)
    return X

def _cap_k_by_uniques(k, X):
    import numpy as np
    if len(X)==0: return 1
    nuniq = np.unique(np.round(X,12), axis=0).shape[0]
    return max(1, min(int(k), max(1, nuniq)))

class KMeansPCA(BaseRegimeModel):
    def __init__(self, name="pca_kmeans", n_clusters=4, pca_dim=3):
        super().__init__(name); self.n_clusters=n_clusters; self.pca_dim=pca_dim
        self._centers=None; self._pca=None; self._km=None; self._Z_all=None

    def fit(self, Xw):
        from sklearn.decomposition import PCA
        Xw = _tiny_jitter(Xw)
        d = max(1, min(self.pca_dim, Xw.shape[1], max(1, Xw.shape[0]-1)))
        self._pca = PCA(n_components=d, random_state=0)
        Zw = self._pca.fit_transform(Xw)
        k = _cap_k_by_uniques(self.n_clusters, Zw)
        self._km = KMeans(n_clusters=k, n_init=20, random_state=0)
        lab = self._km.fit_predict(Zw); self._centers = self._km.cluster_centers_
        return lab

    def label_last(self, Xw):
        Zw = self._pca.transform(Xw)
        lab = self._km.predict(Zw)
        return int(lab[-1])

    def forward_embed(self, Xw, X_all):
        self._Z_all = self._pca.transform(X_all)
        return self._Z_all

    def get_alignment_key(self): return self._centers

class GMMRaw(BaseRegimeModel):
    def __init__(self, name="gmm_raw", n_clusters=4, cov_type="full"):
        super().__init__(name); self.n_clusters=n_clusters; self.cov_type=cov_type
        self._means=None; self._gmm=None

    def fit(self, Xw):
        Xw = _tiny_jitter(Xw)
        k = _cap_k_by_uniques(self.n_clusters, Xw)
        try:
            self._gmm = GaussianMixture(n_components=k, covariance_type=self.cov_type, random_state=0)
            lab = self._gmm.fit_predict(Xw); self._means = self._gmm.means_
            return lab
        except Exception:
            return np.zeros(len(Xw), int)

    def label_last(self, Xw):
        return int(self._gmm.predict(Xw)[-1]) if self._gmm is not None else 0

    def get_alignment_key(self): return self._means

class BayesGMMRaw(BaseRegimeModel):
    def __init__(self, name="bayes_gmm_raw", n_clusters=4, cov_type="full"):
        super().__init__(name); self.n_clusters=n_clusters; self.cov_type=cov_type
        self._means=None; self._bgmm=None

    def fit(self, Xw):
        Xw = _tiny_jitter(Xw)
        k = _cap_k_by_uniques(self.n_clusters, Xw)
        try:
            self._bgmm = BayesianGaussianMixture(n_components=k, covariance_type=self.cov_type, random_state=0)
            lab = self._bgmm.fit_predict(Xw); self._means = self._bgmm.means_
            return lab
        except Exception:
            return np.zeros(len(Xw), int)

    def label_last(self, Xw):
        return int(self._bgmm.predict(Xw)[-1]) if self._bgmm is not None else 0

    def get_alignment_key(self): return self._means