import numpy as np
try:
    import ruptures as rpt
    _RUPTURES = True
except Exception:
    _RUPTURES = False

from .base import BaseRegimeModel, register_model

def _segments_to_labels(T: int, bkps: list[int]) -> np.ndarray:
    """Given breakpoints in 1..T, map each index to a segment id."""
    z = np.zeros(T, dtype=int)
    start = 0
    for s, end in enumerate(bkps):
        z[start:end] = s
        start = end
    if start < T:
        z[start:T] = len(bkps)
    return z

@register_model("cpd_binseg")
class RupturesCPD(BaseRegimeModel):
    """
    Binary segmentation (l2) with max segments = n_bkps+1.
    Produces segment labels (0..S-1).
    """
    def __init__(self, n_bkps=6, model="l2"):
        super().__init__("cpd_binseg")
        self.n_bkps = n_bkps
        self.model = model
        self.bkps_ = None

    def fit(self, X: np.ndarray):
        T = len(X)
        if not _RUPTURES or T < 10:
            self.train_labels_ = np.zeros(T, dtype=int)
            return self
        n_bkps = max(1, min(self.n_bkps, T // 50))
        algo = rpt.Binseg(model=self.model).fit(X)
        bkps = algo.predict(n_bkps=n_bkps)
        self.bkps_ = bkps
        self.train_labels_ = _segments_to_labels(T, bkps)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        # For consistency, just re-fit on X; CPD usually depends on full series
        return self.fit(X).train_labels_