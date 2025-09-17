import numpy as np
from models.base import BaseRegimeModel
try:
    from hmmlearn import hmm
    HMM_OK = True
except Exception:
    HMM_OK = False

class HMMRegimes(BaseRegimeModel):
    def __init__(self, name="hmm", n_states=4):
        super().__init__(name); self.n_states=n_states; self._m=None
    def fit(self, Xw):
        if not HMM_OK or Xw.shape[0] < 10:
            self._m=None; return np.zeros(len(Xw), int)
        k = max(1, min(self.n_states, max(1, len(Xw)//5)))
        self._m = hmm.GaussianHMM(n_components=k, covariance_type="full", n_iter=200, random_state=0)
        try:
            lab = self._m.fit_predict(Xw)
            return lab
        except Exception:
            self._m=None; return np.zeros(len(Xw), int)
    def label_last(self, Xw):
        if self._m is None: return 0
        return int(self._m.predict(Xw)[-1])