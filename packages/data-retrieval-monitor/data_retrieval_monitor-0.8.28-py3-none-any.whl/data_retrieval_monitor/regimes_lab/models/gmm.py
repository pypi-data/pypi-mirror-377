# regimes_lab/models/gmm.py
import numpy as np
from sklearn.mixture import GaussianMixture, BayesianGaussianMixture
from .base import BaseRegimeModel

class GMM(BaseRegimeModel):
    def __init__(self, k=8, **kw):
        super().__init__("gmm", k=k, **kw)
        self.m = GaussianMixture(n_components=k, covariance_type="full", random_state=0)

    def fit(self, X): self.m.fit(X)
    def predict(self, X): return self.m.predict(X)
    def predict_proba(self, X): return self.m.predict_proba(X)

class BayesGMM(BaseRegimeModel):
    def __init__(self, k=8, **kw):
        super().__init__("bayesgmm", k=k, **kw)
        self.m = BayesianGaussianMixture(n_components=k, covariance_type="full", random_state=0)

    def fit(self, X): self.m.fit(X)
    def predict(self, X): return self.m.predict(X)
    def predict_proba(self, X): return self.m.predict_proba(X)