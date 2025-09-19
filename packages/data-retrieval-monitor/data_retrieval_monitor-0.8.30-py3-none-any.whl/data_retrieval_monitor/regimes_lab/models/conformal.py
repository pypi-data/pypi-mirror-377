import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
from .base import BaseRegimeModel, register_model

@register_model("conformal_bins")
class ConformalRegimes(BaseRegimeModel):
    """
    Fit a simple base model on TRAIN, compute residual-based nonconformity scores on TEST,
    convert to conformal p-values, bin p into K quantile bins as regimes.
    For 'full' fit, we fit on all available and bin by in-sample p-values (still useful as a feature regime).
    """
    def __init__(self, n_bins=12, alphas=(1e-3, 1e-2, 1e-1, 1.0)):
        super().__init__("conformal_bins")
        self.n_bins = n_bins
        self.alphas = np.array(alphas)
        self.model_ = None
        self.resid_train_ = None

    def fit(self, X: np.ndarray, y: np.ndarray | None = None):
        # If y not supplied, fallback: self-train to predict a principal column (not ideal, but keeps interface simple).
        # In practice, call fit with y = future sum of a chosen factor.
        if y is None:
            # pseudo-target from first feature to keep deterministic behavior
            y = X[:, 0]
        model = RidgeCV(alphas=self.alphas, fit_intercept=True).fit(X, y)
        yhat = model.predict(X)
        resid = np.abs(y - yhat)
        self.model_ = model
        self.resid_train_ = resid
        # regimes from train p-values (optional)
        ranks = pd.Series(resid).rank(method="average").values
        p = 1.0 - ranks / (len(resid) + 1.0)
        bins = pd.qcut(p, q=self.n_bins, labels=False, duplicates="drop")
        self.train_labels_ = bins.astype(int)
        return self

    def predict(self, X: np.ndarray, y: np.ndarray | None = None) -> np.ndarray:
        if self.model_ is None or self.resid_train_ is None:
            # fit on-the-fly without y to avoid crash
            _ = self.fit(X, y=None)
            return self.train_labels_
        if y is None:
            # no target: use model predictions and compute absolute dev from pred as proxy
            yhat = self.model_.predict(X)
            resid = np.abs(yhat - yhat.mean())
        else:
            yhat = self.model_.predict(X)
            resid = np.abs(y - yhat)
        # empirical conformal p-values vs train residual distribution
        ranks = np.searchsorted(np.sort(self.resid_train_), resid, side="right")
        p = 1.0 - ranks / (len(self.resid_train_) + 1.0)
        # bin p into regimes
        q = np.quantile(p, q=np.linspace(0, 1, self.n_bins+1))
        q[0] = 0.0; q[-1] = 1.0
        bin_idx = np.clip(np.digitize(p, q[1:-1], right=True), 0, self.n_bins-1)
        return bin_idx.astype(int)