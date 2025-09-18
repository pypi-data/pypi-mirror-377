# regimes_lab/models/hmm_.py
import numpy as np
from .base import BaseRegimeModel
try:
    from hmmlearn import hmm
    _HMMOK = True
except Exception:
    _HMMOK = False

class HMMGaussian(BaseRegimeModel):
    def __init__(self, k=8, **kw):
        super().__init__("hmm", k=k, **kw)
        if _HMMOK:
            self.m = hmm.GaussianHMM(n_components=k, covariance_type="full", n_iter=200, random_state=0)
        else:
            self.m = None

    def fit(self, X):
        if self.m is None:
            raise RuntimeError("hmmlearn not installed")
        self.m.fit(X)

    def predict(self, X):
        if self.m is None:
            return np.zeros(len(X), dtype=int)
        return self.m.predict(X)