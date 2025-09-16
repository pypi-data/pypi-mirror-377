# stats.py
import os, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from configs import SUBDIRS
from utils import infer_periods_per_year

# Try statsmodels, else fall back to NumPy+HAC
try:
    import statsmodels.api as sm
    STATSM = True
except Exception:
    STATSM = False

def build_indicator_sign_dummies(indicators_df: pd.DataFrame) -> pd.DataFrame:
    outs = {}
    for ind in indicators_df.columns:
        pos = (indicators_df[ind] > 0).astype(int)
        outs[f"{ind}_POS"] = pos
        outs[f"{ind}_NEG"] = (1 - pos)
    return pd.DataFrame(outs, index=indicators_df.index)

def dummies_for_model(regime_col: pd.Series, prefix: str) -> pd.DataFrame:
    s = regime_col.astype("Int64")
    return pd.get_dummies(s, prefix=f"{prefix}_R", dtype=int)

def _add_constant(X: pd.DataFrame) -> pd.DataFrame:
    if "const" in X.columns: return X
    return pd.concat([pd.Series(1.0, index=X.index, name="const"), X], axis=1)

def _nw_lags(ann): return max(1, int(round((ann) ** (1/3))))

def _ols_numpy(y: np.ndarray, X: np.ndarray):
    XtX = X.T @ X
    XtX_inv = np.linalg.pinv(XtX)
    beta = XtX_inv @ (X.T @ y)
    resid = y - X @ beta
    ss_tot = np.sum((y - y.mean())**2)
    ss_res = np.sum(resid**2)
    n, p = X.shape
    r2 = 1 - (ss_res / ss_tot if ss_tot > 0 else 0.0)
    r2_adj = 1 - (1-r2)*(n-1)/max(1,n-p)
    return beta, resid, r2, r2_adj, XtX_inv

def _hac_cov(resid: np.ndarray, X: np.ndarray, XtX_inv: np.ndarray, lags: int):
    n, p = X.shape
    u = resid.reshape(-1,1)
    S = (X*u).T @ (X*u)
    for h in range(1, min(lags, n-1)+1):
        w = 1.0 - h/(lags+1.0)
        Z0 = (X[:-h]*u[:-h]); Zh = (X[h:]*u[h:])
        G = Z0.T @ Zh
        S += w*(G + G.T)
    return XtX_inv @ S @ XtX_inv

def _norm_cdf(x): return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
def _p_from_t(t): return 2.0 * (1.0 - _norm_cdf(abs(t)))

def run_ols_panel(returns_df: pd.DataFrame, X_df: pd.DataFrame, prefix: str):
    ann = infer_periods_per_year(returns_df.index)
    Xc = _add_constant(X_df.astype(float))
    cols = list(Xc.columns)

    coefs, tstats, pvals, fits = [], [], [], []
    lags = _nw_lags(ann)

    for fac in returns_df.columns:
        y = returns_df[fac].reindex(Xc.index).astype(float).values
        X = Xc.values
        if STATSM:
            res = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
            coefs.append(pd.Series(res.params,  index=cols, name=fac))
            tstats.append(pd.Series(res.tvalues,index=cols, name=fac))
            pvals.append(pd.Series(res.pvalues, index=cols, name=fac))
            fits.append(pd.Series({"R2": res.rsquared, "AdjR2": res.rsquared_adj}, name=fac))
        else:
            beta, resid, r2, r2a, XtX_inv = _ols_numpy(y, X)
            cov = _hac_cov(resid, X, XtX_inv, lags)
            se = np.sqrt(np.clip(np.diag(cov), 0, None)); se[se == 0] = np.nan
            t  = beta / se
            p  = np.vectorize(_p_from_t)(t)
            coefs.append(pd.Series(beta, index=cols, name=fac))
            tstats.append(pd.Series(t,    index=cols, name=fac))
            pvals.append(pd.Series(p,     index=cols, name=fac))
            fits.append(pd.Series({"R2": r2, "AdjR2": r2a}, name=fac))

    coefs_df  = pd.DataFrame(coefs)
    tstats_df = pd.DataFrame(tstats)
    pvals_df  = pd.DataFrame(pvals)
    fits_df   = pd.DataFrame(fits)

    coefs_df.to_csv(os.path.join(SUBDIRS["stat_tests"], f"{prefix}_coefs.csv"))
    tstats_df.to_csv(os.path.join(SUBDIRS["stat_tests"], f"{prefix}_tstats.csv"))
    pvals_df.to_csv(os.path.join(SUBDIRS["stat_tests"], f"{prefix}_pvals.csv"))
    fits_df.to_csv(os.path.join(SUBDIRS["stat_tests"], f"{prefix}_fit.csv"))
    return coefs_df, tstats_df, pvals_df, fits_df

def plot_significance_annotated(coefs_df, pvals_df, alpha=0.05, coef_quantile=0.75, fname="ols_significance_annotated", fmt=".3f"):
    import numpy as np
    abs_coef = coefs_df.abs()
    thresh = abs_coef.quantile(coef_quantile, axis=0).replace(0, np.nan)
    large  = abs_coef.ge(thresh, axis=1).fillna(False)
    signif = pvals_df.lt(alpha)
    mask   = (large & signif)

    order = mask.sum(axis=0).sort_values(ascending=False).index
    coefs_o = coefs_df[order]; mask_o = mask[order]

    vals = coefs_o.values; ann_mask = mask_o.values
    vmax = np.nanpercentile(np.abs(vals[ann_mask]), 95) if ann_mask.any() else np.nanmax(np.abs(vals))
    vmax = vmax if (vmax is not None and np.isfinite(vmax) and vmax>0) else 1.0

    plt.figure(figsize=(max(8, coefs_o.shape[1]*0.35), max(4, coefs_o.shape[0]*0.35)))
    im = plt.imshow(np.clip(np.abs(vals)/vmax, 0, 1), aspect="auto", cmap="Greens", vmin=0, vmax=1)
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            if ann_mask[i, j]:
                plt.text(j, i, format(vals[i, j], fmt), ha="center", va="center", fontsize=7, color="black")
    plt.xticks(range(coefs_o.shape[1]), coefs_o.columns, rotation=90)
    plt.yticks(range(coefs_o.shape[0]), coefs_o.index)
    plt.title(f"Significant & Large (p<{alpha}, |coef|≥Q{coef_quantile:.0%}) — Annotated")
    plt.colorbar(im, fraction=0.046, pad=0.04, label="|coef| (scaled)")
    plt.tight_layout()
    plt.savefig(os.path.join(SUBDIRS["stat_tests"], f"{fname}.png"), dpi=160, bbox_inches="tight")
    plt.close()

def run_ols_per_model(returns_df: pd.DataFrame,
                      indicators_df: pd.DataFrame,
                      regimes_df: pd.DataFrame,
                      include_sign_dummies: bool = True,
                      with_interactions: bool = False):
    """
    For EACH model column in regimes_df:
      returns ~ indicators (+ sign dummies optional) + that model's dummies (+ interactions optional)
    Saves: stat_tests/<model>_* csvs and a significance_annotated figure.
    """
    for model_col in regimes_df.columns:
        Dm = dummies_for_model(regimes_df[model_col], prefix=model_col)
        X = pd.concat([indicators_df], axis=1)
        if include_sign_dummies:
            X = pd.concat([X, build_indicator_sign_dummies(indicators_df)], axis=1)
        X = pd.concat([X, Dm], axis=1).reindex(returns_df.index).fillna(0)

        if with_interactions:
            inter = {}
            for ind in indicators_df.columns:
                for dcol in Dm.columns:
                    inter[f"{ind}__x__{dcol}"] = indicators_df[ind] * Dm[dcol]
            if inter:
                X = pd.concat([X, pd.DataFrame(inter, index=returns_df.index)], axis=1).fillna(0)

        prefix = f"ols_{model_col}"
        coefs, tstats, pvals, fits = run_ols_panel(returns_df, X, prefix=prefix)
        plot_significance_annotated(coefs, pvals, alpha=0.05, coef_quantile=0.75, fname=f"{prefix}_significance_annotated")