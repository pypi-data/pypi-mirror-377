import numpy as np

class BaseRegimeModel:
    """
    Abstract interface for a rolling/recursive regime model that can be optimized later.
    """
    def __init__(self, name: str):
        self.name = name

    def fit(self, X_window: np.ndarray):
        """Fit on a window [t0, t). Return any fitted state (e.g., centers)."""
        raise NotImplementedError

    def label_last(self, X_window: np.ndarray) -> int:
        """After fit(), return regime label for last index (t-1)."""
        raise NotImplementedError

    def get_alignment_key(self):
        """Return centers/means used for Hungarian alignment across windows."""
        return None

    # differentiable hooks (no-ops for sklearn; used by torch models)
    def forward_embed(self, X_window: np.ndarray, X_all: np.ndarray):
        """Optional: produce embeddings for refine/knn; returns Z_all or None."""
        return None