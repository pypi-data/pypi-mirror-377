import numpy as np
import pandas as pd
from .base import BaseRegimeModel, register_model

@register_model("sign_thresholds")
class SignThresholdRegimes(BaseRegimeModel):
    """
    Discrete regimes from indicators via simple thresholding.
    Default: sum of sign(Ind_i) in {-n..+n}, shifted to non-negative labels.
    """
    def __init__(self, colnames: list[str] | None = None, multi_thresholds: dict[str, list[float]] | None = None):
        super().__init__("sign_thresholds")
        self.colnames = colnames
        self.multi_thresholds = multi_thresholds or {}  # e.g., {"Ind1_Growth_lag5": [-1.0, 0.0, 1.0]}

    def fit(self, X: np.ndarray):
        # Not needed; purely deterministic mapping from features
        self.train_labels_ = None
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        Xdf = pd.DataFrame(X, columns=self.colnames if self.colnames else None)
        if self.multi_thresholds:
            # multi-bin per column -> combine as categorical code
            codes = []
            for c in Xdf.columns:
                thr = self.multi_thresholds.get(c)
                if thr is None:
                    codes.append((Xdf[c] > 0).astype(int))
                else:
                    # bin into len(thr)+1 buckets
                    bins = [-np.inf] + list(thr) + [np.inf]
                    codes.append(pd.cut(Xdf[c], bins=bins, labels=False).astype(int))
            # mixed radix encoding
            codes = np.stack([c.values for c in codes], axis=1)
            # normalize to contiguous labels
            # (hash row-wise)
            lab = pd.Series([hash(tuple(row)) for row in codes]).astype("category").cat.codes.values
            return lab.astype(int)
        else:
            # default: sum of signs -> shift to nonnegative
            s = np.sign(Xdf.fillna(0)).sum(1).astype(int)
            s -= s.min()
            return s.values