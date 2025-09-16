# models/hmm_model.py
import numpy as np
try:
    from hmmlearn import hmm
    HMM = True
except Exception:
    HMM = False

def hmm_labels_train(X_train, X_all, n_comp):
    if not HMM:
        print("[INFO] hmmlearn not available — skipping HMM.")
        return None, None
    X_train = np.asarray(X_train); X_all = np.asarray(X_all)
    n = X_train.shape[0]
    # Need at least n_components observations; be generous:
    k = min(n_comp, max(1, n - 1))
    if n < 2 or k < 1:
        return np.full(X_all.shape[0], -1, dtype=int), None
    model = hmm.GaussianHMM(n_components=k, covariance_type="full", n_iter=200, random_state=0)
    model.fit(X_train)
    lab = model.predict(X_all)
    return lab, model