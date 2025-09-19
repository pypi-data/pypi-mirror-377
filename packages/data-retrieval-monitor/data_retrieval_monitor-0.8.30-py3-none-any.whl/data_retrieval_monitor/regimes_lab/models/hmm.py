import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

try:
    from hmmlearn.hmm import GaussianHMM  # type: ignore
    HMMLEARN_AVAILABLE = True
except Exception:
    GaussianHMM = None  # type: ignore
    HMMLEARN_AVAILABLE = False

class HMMGaussian:
    def __init__(self, n_components=12, covariance_type="full", n_init=8, n_iter=800, tol=1e-4,
                 reg_covar=1e-3, random_state=0, preinit_kmeans=True, whiten_pca=False):
        self.n_components = n_components
        self.covariance_type = covariance_type
        self.n_init = n_init; self.n_iter = n_iter
        self.tol = tol; self.reg_covar = reg_covar
        self.random_state = random_state
        self.preinit_kmeans = preinit_kmeans
        self.whiten_pca = whiten_pca
        self.scaler_ = StandardScaler()
        self.pca_ = None
        self.hmm_ = None
        self._km_centers = None
        self.train_labels_ = None

    def _prep_fit(self, X):
        Xs = self.scaler_.fit_transform(X)
        if self.whiten_pca:
            self.pca_ = PCA(whiten=True, random_state=self.random_state)
            Xs = self.pca_.fit_transform(Xs)
        return Xs

    def _prep_apply(self, X):
        Xs = self.scaler_.transform(X)
        if self.pca_ is not None:
            Xs = self.pca_.transform(Xs)
        return Xs

    def _kmeans_init(self, Xs):
        km = KMeans(n_clusters=self.n_components, n_init=10, random_state=self.random_state).fit(Xs)
        z = km.labels_; means = km.cluster_centers_
        A = np.ones((self.n_components, self.n_components))
        for i in range(len(z)-1): A[z[i], z[i+1]] += 1
        A /= A.sum(1, keepdims=True)
        pi = (np.bincount(z, minlength=self.n_components) + 1).astype(float)
        pi /= pi.sum()
        return pi, A, means

    def fit(self, X):
        Xs = self._prep_fit(X)
        if not HMMLEARN_AVAILABLE:
            km = KMeans(n_clusters=self.n_components, n_init=20, random_state=self.random_state).fit(Xs)
            self._km_centers = km.cluster_centers_
            self.train_labels_ = km.labels_
            return self

        best, best_score = None, -np.inf
        pi0 = A0 = m0 = None
        if self.preinit_kmeans: pi0, A0, m0 = self._kmeans_init(Xs)
        for r in range(self.n_init):
            hmm = GaussianHMM(n_components=self.n_components, covariance_type=self.covariance_type,
                              n_iter=self.n_iter, tol=self.tol, random_state=self.random_state+r,
                              params="stmc", init_params="")
            hmm.reg_covar = self.reg_covar
            if self.preinit_kmeans:
                hmm.startprob_ = pi0; hmm.transmat_ = A0; hmm.means_ = m0
                if self.covariance_type == "full":
                    cov = np.cov(Xs.T) + self.reg_covar*np.eye(Xs.shape[1])
                    hmm.covars_ = np.stack([cov]*self.n_components)
                else:
                    v = np.clip(np.var(Xs, axis=0), self.reg_covar, None)
                    hmm.covars_ = np.tile(v, (self.n_components,1))
            hmm.fit(Xs)
            z = hmm.predict(Xs)
            if len(np.unique(z)) <= 1: continue
            score = hmm.score(Xs)
            if score > best_score: best_score, best = score, hmm
        if best is None:
            km = KMeans(n_clusters=self.n_components, n_init=20, random_state=self.random_state).fit(Xs)
            self._km_centers = km.cluster_centers_
            self.train_labels_ = km.labels_
            return self
        self.hmm_ = best
        self.train_labels_ = self.hmm_.predict(Xs)
        return self

    def predict(self, X):
        Xs = self._prep_apply(X)
        if self.hmm_ is None:
            if self._km_centers is None: return np.zeros(len(Xs), dtype=int)
            d2 = ((Xs[:,None,:] - self._km_centers[None,:,:])**2).sum(-1)
            return d2.argmin(1)
        return self.hmm_.predict(Xs)