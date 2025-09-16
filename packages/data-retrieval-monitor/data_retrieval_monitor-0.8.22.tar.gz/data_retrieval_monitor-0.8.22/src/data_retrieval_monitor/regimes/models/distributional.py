# models/distributional.py
import numpy as np, pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA, QuadraticDiscriminantAnalysis as QDA
from utils import kl_gaussian, w2_gaussian, spd_project
from configs import OLD_WIN, NEW_WIN

def rolling_gaussian_distances(X, dates, old_win=OLD_WIN, new_win=NEW_WIN):
    X = np.asarray(X); T, d = X.shape; out = []
    for t in range(T):
        if t < old_win + new_win: out.append((np.nan, np.nan, np.nan)); continue
        Xold = X[t-old_win-new_win:t-new_win]; Xnew = X[t-new_win:t]
        m0, m1 = Xold.mean(0), Xnew.mean(0)
        C0, C1 = np.cov(Xold.T), np.cov(Xnew.T)
        try:
            d01 = kl_gaussian(m0, C0, m1, C1); d10 = kl_gaussian(m1, C1, m0, C0); w2 = w2_gaussian(m0, C0, m1, C1)
        except np.linalg.LinAlgError:
            d01 = d10 = w2 = np.nan
        out.append((d01, d10, w2))
    return pd.DataFrame(out, index=pd.to_datetime(dates), columns=["KL_old_to_new", "KL_new_to_old", "W2_sq"])

def gmm_regimes_train(X_train, X_all, n_comp):
    X_train = np.asarray(X_train); X_all = np.asarray(X_all)
    n = X_train.shape[0]
    if n < 2:
        # Not enough to fit GMM; return unknown labels
        return np.full(X_all.shape[0], -1, dtype=int), None
    k = max(1, min(n_comp, n - 1))
    gmm = GaussianMixture(n_components=k, covariance_type="full", random_state=0)
    gmm.fit(X_train)
    lab = gmm.predict(X_all)
    return lab, gmm

def lda_qda_regimes_train(X_train, y_train, X_all, which="lda"):
    if which == "lda":
        clf = LDA()
    else:
        clf = QDA(store_covariance=True)
    clf.fit(X_train, y_train)
    lab = clf.predict(X_all)
    return lab, clf

def aggregate_window_gaussian(mu_win, var_win_diag):
    m_bar = mu_win.mean(axis=0)
    avg_diag = var_win_diag.mean(axis=0)
    centered = mu_win - m_bar
    C_between = centered.T @ centered / max(1, mu_win.shape[0])
    C = C_between + np.diag(avg_diag)
    return m_bar, spd_project(C)

def rolling_vae_distances(mu_all, var_all, dates, old_win=OLD_WIN, new_win=NEW_WIN):
    T, d = mu_all.shape; out = []
    for t in range(T):
        if t < old_win + new_win: out.append((np.nan, np.nan, np.nan)); continue
        mu_old = mu_all[t-old_win-new_win:t-new_win]; var_old = var_all[t-old_win-new_win:t-new_win]
        mu_new = mu_all[t-new_win:t]; var_new = var_all[t-new_win:t]
        m0, C0 = aggregate_window_gaussian(mu_old, var_old)
        m1, C1 = aggregate_window_gaussian(mu_new, var_new)
        try:
            d01 = kl_gaussian(m0, C0, m1, C1); d10 = kl_gaussian(m1, C1, m0, C0); w2 = w2_gaussian(m0, C0, m1, C1)
        except np.linalg.LinAlgError:
            d01 = d10 = w2 = np.nan
        out.append((d01, d10, w2))
    return pd.DataFrame(out, index=pd.to_datetime(dates),
                        columns=["VAE_KL_old_to_new", "VAE_KL_new_to_old", "VAE_W2_sq"])