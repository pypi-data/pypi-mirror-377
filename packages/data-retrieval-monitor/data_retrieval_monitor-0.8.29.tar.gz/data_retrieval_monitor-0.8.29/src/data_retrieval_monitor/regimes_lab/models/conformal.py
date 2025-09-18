# regimes_lab/models/conformal.py
import numpy as np
from sklearn.neighbors import KernelDensity
from .base import BaseRegimeModel
from sklearn.cluster import KMeans

class ConformalRegimes(BaseRegimeModel):
    """
    Simple split-conformal assignment:
    - Fit KMeans to training X -> provisional regimes.
    - For each regime, fit KDE on its cluster points.
    - p-value for a new x is rank of its likelihood among calibration points (per regime).
    - Assign regime = argmax p-value.
    """
    def __init__(self, k=8, **kw):
        super().__init__("conformal", **kw)
        self.k = k

    def fit(self, X):
        km = KMeans(n_clusters=self.k, n_init=5, random_state=0).fit(X)
        self.km = km
        self.kdes = []
        for c in range(self.k):
            pts = X[km.labels_==c]
            if len(pts) < 5:
                self.kdes.append(None)
            else:
                kde = KernelDensity(kernel="gaussian", bandwidth=0.5).fit(pts)
                self.kdes.append(kde)
        self._cal = X

    def _pvals(self, X):
        p = np.zeros((len(X), self.k))
        for c in range(self.k):
            kde = self.kdes[c]
            if kde is None:
                continue
            # nonconformity: -log density
            s = -kde.score_samples(X)
            s_cal = -kde.score_samples(self._cal[self.km.labels_==c]) if np.any(self.km.labels_==c) else np.array([np.inf])
            # p-value = fraction of calibration nonconformities >= new one
            p[:, c] = np.array([(s_cal >= si).mean() for si in s])
        return p

    def predict(self, X):
        P = self._pvals(X)
        # fallback to kmeans if all zeros
        mask = (P.sum(axis=1)==0)
        labs = P.argmax(axis=1)
        if mask.any():
            labs[mask] = self.km.predict(X[mask])
        return labs