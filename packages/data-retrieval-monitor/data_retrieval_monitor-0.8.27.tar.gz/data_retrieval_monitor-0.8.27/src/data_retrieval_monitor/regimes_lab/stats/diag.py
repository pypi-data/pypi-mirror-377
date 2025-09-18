# regimes_lab/stats/diag.py
import numpy as np
import pandas as pd
from typing import Tuple, Dict
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from statsmodels.stats.sandwich_covariance import cov_hac
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.linear_model import LassoCV
from sklearn.metrics import r2_score
from scipy.stats import t as student_t

def _align(y: pd.Series, X: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
    y_, X_ = y.align(X, join="inner")
    # drop rows with any NaN
    mask = y_.notna() & ~X_.isna().any(axis=1)
    return y_[mask], X_[mask]

def _pvals_from_t(tvals, df):
    return 2.0*student_t.sf(np.abs(np.asarray(tvals)), df=df) if df>0 else np.full_like(np.asarray(tvals), np.nan, dtype=float)

def _add_back_missing_params(params_idx, full_cols):
    """Return list of columns that were dropped by OLS due to singularity."""
    return [c for c in full_cols if c not in params_idx]

def ols_hac(y: pd.Series, X_train: pd.DataFrame, X_test: pd.DataFrame, hac_lags=5, refit_test=True) -> Dict:
    y_tr, X_tr = _align(y, X_train)
    y_te, X_te = _align(y, X_test)

    # constant + safe finite
    Xtr_c = add_constant(X_tr, has_constant="add")
    mtr = OLS(y_tr, Xtr_c).fit()
    cov = cov_hac(mtr, nlags=hac_lags)
    se = np.sqrt(np.maximum(np.diag(cov), 1e-12))
    t = mtr.params / se
    p = _pvals_from_t(t, df=float(mtr.df_resid))
    # detect dropped train columns
    dropped_tr = _add_back_missing_params(list(mtr.params.index), list(Xtr_c.columns))
    out = {
        "coef_train": mtr.params, "t_train": pd.Series(t, index=mtr.params.index), "p_train": pd.Series(p, index=mtr.params.index),
        "dropped_train": dropped_tr
    }

    # R2s using train fit
    try:
        yhat_tr = mtr.predict(Xtr_c)
        r2tr = r2_score(y_tr, yhat_tr) if len(y_tr)>0 else np.nan
    except Exception:
        r2tr = np.nan
    try:
        Xte_c = add_constant(X_te, has_constant="add")
        yhat_te = mtr.predict(Xte_c) if len(X_te)>0 else np.array([])
        r2te = r2_score(y_te, yhat_te) if len(y_te)>0 and np.isfinite(yhat_te).all() else np.nan
    except Exception:
        r2te = np.nan
    out.update({"r2_train": r2tr, "r2_test": r2te})

    # DW/LB on train
    try:
        dw_tr = float(durbin_watson(mtr.resid))
        lb_tr = acorr_ljungbox(mtr.resid, lags=[min(20, max(2, len(mtr.resid)//10))], return_df=True)["lb_pvalue"].iloc[0]
        out.update({"dw_train": dw_tr, "lb_p_train": float(lb_tr)})
    except Exception:
        pass

    # Refit on test for ex-post t,p
    if refit_test and len(y_te) > 3 and X_te.shape[1] > 0:
        Xte_c = add_constant(X_te, has_constant="add")
        mte = OLS(y_te, Xte_c).fit()
        covt = cov_hac(mte, nlags=hac_lags)
        sete = np.sqrt(np.maximum(np.diag(covt), 1e-12))
        tt = mte.params/sete; pp = _pvals_from_t(tt, df=float(mte.df_resid))
        out.update({
            "coef_test": mte.params, "t_test": pd.Series(tt, index=mte.params.index), "p_test": pd.Series(pp, index=mte.params.index),
            "dropped_test": _add_back_missing_params(list(mte.params.index), list(Xte_c.columns))
        })
        try:
            dw_te = float(durbin_watson(mte.resid))
            lb_te = acorr_ljungbox(mte.resid, lags=[min(20, max(2, len(mte.resid)//10))], return_df=True)["lb_pvalue"].iloc[0]
            out.update({"dw_test": dw_te, "lb_p_test": float(lb_te)})
        except Exception:
            pass

    return out

def lasso_cv(y: pd.Series, X_train: pd.DataFrame, X_test: pd.DataFrame) -> Dict:
    y_tr, X_tr = _align(y, X_train); y_te, X_te = _align(y, X_test)
    if X_tr.shape[1]==0 or len(y_tr)<10: return {"coef": pd.Series(dtype=float), "r2_train": np.nan, "r2_test": np.nan}
    model = LassoCV(alphas=np.logspace(-3,1,24), cv=5, random_state=0).fit(X_tr, y_tr)
    coef = pd.Series(model.coef_, index=X_tr.columns)
    yhat_tr = model.predict(X_tr); yhat_te = model.predict(X_te) if len(X_te)>0 else np.array([])
    r2tr = r2_score(y_tr, yhat_tr)
    r2te = r2_score(y_te, yhat_te) if len(y_te)>0 and np.isfinite(yhat_te).all() else np.nan
    return {"coef": coef, "r2_train": r2tr, "r2_test": r2te}