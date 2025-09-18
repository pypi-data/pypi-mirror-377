# regimes_lab/models/base.py
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd

class BaseRegimeModel(ABC):
    name: str

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.kw = kwargs

    @abstractmethod
    def fit(self, X: np.ndarray): ...
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray: ...
    def predict_proba(self, X: np.ndarray) -> np.ndarray | None: return None

    def fit_predict(self, X: np.ndarray):
        self.fit(X)
        return self.predict(X)