import numpy as np
from sklearn.mixture import GaussianMixture

class GMMRaw:
    def __init__(self, n_components=12, covariance_type="full", random_state=0):
        self.gmm = GaussianMixture(n_components=n_components, covariance_type=covariance_type, random_state=random_state)
        self.train_labels_ = None
    def fit(self, X): 
        self.gmm.fit(X)
        self.train_labels_ = self.gmm.predict(X)
        return self
    def predict(self, X): 
        return self.gmm.predict(X)