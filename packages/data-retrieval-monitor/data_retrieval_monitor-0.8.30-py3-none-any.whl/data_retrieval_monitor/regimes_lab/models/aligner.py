import numpy as np
from scipy.spatial.distance import cdist
from scipy.linalg import sqrtm
from scipy.stats import entropy

from .base import BaseRegimeModel, register_model

def _gauss_w2(mu1, s1, mu2, s2, eps=1e-9):
    # 2-Wasserstein between Gaussians: ||mu1-mu2||^2 + Tr(S1 + S2 - 2(S2^{1/2} S1 S2^{1/2})^{1/2})
    dmu = np.linalg.norm(mu1 - mu2)**2
    s2h = sqrtm(s2 + eps*np.eye(len(mu2)))
    prod = s2h @ s1 @ s2h
    prodh = sqrtm(prod + eps*np.eye(len(mu2)))
    tr = np.trace(s1 + s2 - 2*prodh.real)
    return float(dmu + tr)

def _gauss_kl(mu1, s1, mu2, s2, eps=1e-9):
    # KL(N1||N2)
    d = len(mu1)
    s2i = np.linalg.pinv(s2 + eps*np.eye(d))
    diff = (mu2 - mu1).reshape(-1,1)
    term = np.trace(s2i @ s1) + (diff.T @ s2i @ diff)[0,0] - d + np.log(np.linalg.det(s2 + eps*np.eye(d))/np.linalg.det(s1 + eps*np.eye(d)))
    return float(0.5 * term)

@register_model("align_cpd_to_train")
class AlignmentRegimer(BaseRegimeModel):
    """
    Given a base segmentation (e.g., CPD) and TRAIN statistics of a reference model’s regimes,
    align each segment to the nearest TRAIN regime by distributional distance (W2 or KL).
    """
    def __init__(self, base_labels_train: np.ndarray, base_labels_full: np.ndarray,
                 X_train: np.ndarray, ref_regime_labels_train: np.ndarray,
                 metric: str = "w2"):
        super().__init__("align_cpd_to_train")
        self.base_labels_train = base_labels_train
        self.base_labels_full  = base_labels_full
        self.X_train = X_train
        self.ref_labels_train = ref_regime_labels_train
        self.metric = metric
        self.map_ = None  # segment_id -> ref_regime_id

    def fit(self, X: np.ndarray):
        # Estimate Gaussian per ref regime (on TRAIN)
        ids = np.unique(self.ref_labels_train)
        ref_stats = {}
        for r in ids:
            Xr = self.X_train[self.ref_labels_train == r]
            if len(Xr) < 3: continue
            ref_stats[r] = (Xr.mean(0), np.cov(Xr.T))

        # Estimate Gaussian per CPD segment (on TRAIN portion only)
        seg_ids = np.unique(self.base_labels_train)
        mapping = {}
        for s in seg_ids:
            Xs = self.X_train[self.base_labels_train == s]
            if len(Xs) < 3: 
                mapping[s] = int(ids[0]) if len(ids) else 0
                continue
            mu_s, cov_s = Xs.mean(0), np.cov(Xs.T)
            best, best_d = None, np.inf
            for r, (mu_r, cov_r) in ref_stats.items():
                if self.metric == "kl":
                    d = _gauss_kl(mu_s, cov_s, mu_r, cov_r)
                else:
                    d = _gauss_w2(mu_s, cov_s, mu_r, cov_r)
                if d < best_d:
                    best_d, best = d, r
            mapping[s] = int(best) if best is not None else int(ids[0]) if len(ids) else 0

        self.map_ = mapping
        # produce TRAIN labels
        self.train_labels_ = np.vectorize(mapping.get)(self.base_labels_full[:len(self.base_labels_train)])
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        # Map FULL segments via learned mapping
        if self.map_ is None:
            return np.zeros(len(self.base_labels_full), dtype=int)
        return np.vectorize(self.map_.get)(self.base_labels_full)