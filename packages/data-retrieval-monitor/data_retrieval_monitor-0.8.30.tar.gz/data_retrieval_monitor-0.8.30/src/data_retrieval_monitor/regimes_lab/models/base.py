from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np

# Simple registry so regimes.py can “discover” models centrally
_REGISTRY = {}

def register_model(name: str):
    def deco(cls):
        _REGISTRY[name] = cls
        return cls
    return deco

def get_registry():
    return dict(_REGISTRY)

class BaseRegimeModel(ABC):
    """
    Minimal interface for all regime models.
    Fit/predict on numpy arrays (aligned to horizon-specific X_h).
    """
    def __init__(self, name: str):
        self.name = name
        self.train_labels_ = None

    @abstractmethod
    def fit(self, X: np.ndarray):
        ...

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        ...

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        if self.train_labels_ is None:
            self.train_labels_ = self.predict(X)
        return self.train_labels_