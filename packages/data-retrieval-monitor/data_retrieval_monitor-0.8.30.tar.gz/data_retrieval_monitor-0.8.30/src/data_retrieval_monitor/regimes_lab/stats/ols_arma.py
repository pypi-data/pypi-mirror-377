# analytics/regimes_lab/stats/ols_arma.py
import os, numpy as np, pandas as pd, statsmodels.api as sm
from scipy.stats import chi2, f
from statsmodels.regression.linear_model import GLSAR
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
import matplotlib.pyplot as plt

def ols_hac(y: pd.Series, X: pd.DataFrame, maxlags: int = 5):
    X = sm.add_constant(X, has_constant="add")
    model = sm.OLS(y, X, missing="drop")
    res   = model.fit(cov_type="HAC", cov_kwds={"maxlags": maxlags})
    return dict(
        coefs = res.params, tvals = res.tvalues, pvals = res.pvalues,
        r2 = res.rsquared, r2_adj = res.rsquared_adj, aic = res.aic, bic = res.bic,
        resid = res.resid, cov = res.cov_params(), df_resid = res.df_resid, X_cols = X.columns
    )

def glsar_iter(y: pd.Series, X: pd.DataFrame, order: int = 1, iters: int = 8):
    X = sm.add_constant(X, has_constant="add")
    model = GLSAR(y, X, rho=order)
    res = model.iterative_fit(maxiter=iters)
    cov = res.cov_params()  # (classic, not HAC)
    return dict(
        coefs = pd.Series(res.params, index=X.columns),
        tvals = pd.Series(res.tvalues, index=X.columns),
        pvals = pd.Series(res.pvalues, index=X.columns),
        aic = res.aic, bic = res.bic, resid = pd.Series(res.resid, index=y.index),
        cov = cov, df_resid = res.df_resid, X_cols = X.columns
    )

def ols_arima_errors(y: pd.Series, X: pd.DataFrame, ar: int = 1, ma: int = 1):
    X = sm.add_constant(X, has_constant="add")
    mod = sm.tsa.SARIMAX(y, exog=X, order=(ar,0,ma),
                         enforce_stationarity=False, enforce_invertibility=False)
    res = mod.fit(disp=False)
    return dict(
        coefs = pd.Series(res.params, index=res.model.param_names),
        tvals = pd.Series(res.tvalues, index=res.model.param_names),
        pvals = pd.Series(res.pvalues, index=res.model.param_names),
        aic = res.aic, bic = res.bic, resid = pd.Series(res.resid, index=y.index)
    )

def wald_test_manual(params: pd.Series, cov: pd.DataFrame, R: np.ndarray, r: np.ndarray, df_resid: float):
    # W = (R b - r)' (R Σ R')^{-1} (R b - r)
    b = params.values.reshape(-1,1)
    diff = R @ b - r.reshape(-1,1)
    RS = R @ cov.values @ R.T
    try:
        RS_inv = np.linalg.pinv(RS)
    except Exception:
        return dict(stat=np.nan, df=len(r), p_chi2=np.nan, f_stat=np.nan, p_f=np.nan)
    stat = float((diff.T @ RS_inv @ diff).ravel()[0])
    df_h = R.shape[0]
    p_chi2 = 1 - chi2.cdf(stat, df_h)
    # F version
    if df_resid > 0:
        f_stat = (stat/df_h) / (1.0)
        p_f = 1 - f.cdf(f_stat, df_h, df_resid)
    else:
        f_stat, p_f = np.nan, np.nan
    return dict(stat=stat, df=df_h, p_chi2=p_chi2, f_stat=f_stat, p_f=p_f)

def joint_wald_test(res_ols: dict, cols: list[str]):
    if not cols: return None
    params = res_ols["coefs"].reindex(res_ols["X_cols"], fill_value=0.0)
    cov    = res_ols["cov"].reindex(index=res_ols["X_cols"], columns=res_ols["X_cols"]).fillna(0.0)
    R = np.zeros((len(cols), len(res_ols["X_cols"])))
    for i, c in enumerate(cols):
        if c in res_ols["X_cols"]:
            R[i, list(res_ols["X_cols"]).index(c)] = 1.0
    r = np.zeros(len(cols))
    return wald_test_manual(params, cov, R, r, df_resid=res_ols.get("df_resid", np.nan))

def residual_diagnostics(y: pd.Series, name: str, out_dir: str, lags: int = 24):
    os.makedirs(out_dir, exist_ok=True)
    # ACF/PACF
    fig, ax = plt.subplots(2,1, figsize=(10,6))
    plot_acf(y.dropna(), lags=lags, ax=ax[0]); ax[0].set_title(f"{name} — ACF")
    plot_pacf(y.dropna(), lags=lags, ax=ax[1]); ax[1].set_title(f"{name} — PACF")
    fig.tight_layout(); fig.savefig(os.path.join(out_dir, f"{name}_acf_pacf.png"), dpi=140); plt.close(fig)
    # Ljung-Box
    lb = acorr_ljungbox(y.dropna(), lags=[lags], return_df=True)
    lb.to_csv(os.path.join(out_dir, f"{name}_ljungbox.csv"))
    # basic gate: p>0.05 => “white-ish”
    valid = bool(lb["lb_pvalue"].iloc[0] > 0.05)
    return dict(ljungbox=lb.to_dict(orient="list"), valid=valid)