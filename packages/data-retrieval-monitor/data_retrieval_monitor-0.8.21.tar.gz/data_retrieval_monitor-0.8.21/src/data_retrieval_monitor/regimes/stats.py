# stats.py
import os, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from configs import OUTPUT_DIR, SUBDIRS
from utils import annualized_stats, save_table, professional_heatmap, infer_periods_per_year

# Try statsmodels, else fall back to our own HAC-OLS
try:
    import statsmodels.api as sm
    STATSM = True
except Exception:
    STATSM = False

def make_all_model_dummies(regimes_df: pd.DataFrame) -> pd.DataFrame:
    outs = []
    for col in regimes_df.columns:
        s = regimes_df[col].astype("Int64")
        outs.append(pd.get_dummies(s, prefix=f"{col}_R", dtype=int))
    return pd.concat(outs, axis=1) if outs else pd.DataFrame(index=regimes_df.index)

def build_indicator_sign_dummies(indicators_df: pd.DataFrame) -> pd.DataFrame:
    outs = {}
    for ind in indicators_df.columns:
        pos = (indicators_df[ind] > 0).astype(int)
        outs[f"{ind}_POS"] = pos
        outs[f"{ind}_NEG"] = (1 - pos)
    return pd.DataFrame(outs, index=indicators_df.index)

def build_designs(returns_df, indicators_df, regimes_df, interactions=True):
    D = make_all_model_dummies(regimes_df)
    S = build_indicator_sign_dummies(indicators_df)
    X_clusters_only = D.copy()
    X_full = pd.concat([indicators_df, S, D], axis=1)
    if interactions and len(S.columns) and len(D.columns):
        inter_cols, inter_vals = [], []
        for s in S.columns:
            for d in D.columns:
                inter_cols.append(f"{s}__x__{d}")
                inter_vals.append(S[s] * D[d])
        if inter_vals:
            X_inter = pd.concat(inter_vals, axis=1)
            X_inter.columns = inter_cols
            X_full = pd.concat([X_full, X_inter], axis=1)

    X_clusters_only = X_clusters_only.reindex(returns_df.index).fillna(0)
    X_full = X_full.reindex(returns_df.index).fillna(0)

    X_clusters_only.to_csv(os.path.join(SUBDIRS["designs"], "X_clusters_only.csv"))
    X_full.to_csv(os.path.join(SUBDIRS["designs"], "X_full.csv"))
    return X_clusters_only, X_full

def _nw_lags_from_freq(ann_factor: int) -> int:
    return max(1, int(round((ann_factor) ** (1/3))))

# ---------- NumPy OLS + Newey–West HAC (no statsmodels required) ----------
def _ols_fit_numpy(y: np.ndarray, X: np.ndarray):
    XtX = X.T @ X
    XtX_inv = np.linalg.pinv(XtX)
    beta = XtX_inv @ (X.T @ y)
    yhat = X @ beta
    resid = y - yhat
    ss_tot = np.sum((y - y.mean())**2)
    ss_res = np.sum(resid**2)
    r2 = 1.0 - (ss_res / ss_tot if ss_tot > 0 else 0.0)
    n, p = X.shape
    r2_adj = 1.0 - (1.0 - r2) * (n - 1) / max(1, n - p)
    return beta, resid, yhat, r2, r2_adj, XtX_inv

def _hac_cov(resid: np.ndarray, X: np.ndarray, XtX_inv: np.ndarray, lags: int):
    n, p = X.shape
    u = resid.reshape(-1, 1)
    S = np.zeros((p, p))
    Z = X * u
    S += Z.T @ Z
    for h in range(1, min(lags, n-1)+1):
        w = 1.0 - h / (lags + 1.0)
        Zh = (X[h:] * u[h:])
        Z0 = (X[:-h] * u[:-h])
        Gamma = Z0.T @ Zh
        S += w * (Gamma + Gamma.T)
    cov = XtX_inv @ S @ XtX_inv
    return cov

def _norm_cdf(x): return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
def _pvals_from_t(tvals): return 2.0 * (1.0 - np.vectorize(_norm_cdf)(np.abs(tvals)))

def _add_constant(X: pd.DataFrame) -> pd.DataFrame:
    if "const" in X.columns: return X
    return pd.concat([pd.Series(1.0, index=X.index, name="const"), X], axis=1)

def run_ols_panel(returns_df, X_df, ann_factor, prefix):
    """Writes CSVs into stat_tests/ and returns (coefs, tstats, pvals, fits)."""
    Xc = _add_constant(X_df.astype(float))
    cols = list(Xc.columns)
    coefs, tstats, pvals, fits = [], [], [], []
    lags = _nw_lags_from_freq(ann_factor)

    for fac in returns_df.columns:
        y = returns_df[fac].reindex(Xc.index).astype(float).values
        X = Xc.values

        if STATSM:
            model = sm.OLS(y, X)
            res = model.fit(cov_type="HAC", cov_kwds={"maxlags": lags})
            coefs.append(pd.Series(res.params,  index=cols, name=fac))
            tstats.append(pd.Series(res.tvalues,index=cols, name=fac))
            pvals.append(pd.Series(res.pvalues, index=cols, name=fac))
            fits.append(pd.Series({"R2": res.rsquared, "AdjR2": res.rsquared_adj}, name=fac))
        else:
            beta, resid, _, r2, r2_adj, XtX_inv = _ols_fit_numpy(y, X)
            cov = _hac_cov(resid, X, XtX_inv, lags=lags)
            se = np.sqrt(np.clip(np.diag(cov), 0, None)); se[se == 0] = np.nan
            t = beta / se; p = _pvals_from_t(t)
            coefs.append(pd.Series(beta, index=cols, name=fac))
            tstats.append(pd.Series(t,   index=cols, name=fac))
            pvals.append(pd.Series(p,    index=cols, name=fac))
            fits.append(pd.Series({"R2": r2, "AdjR2": r2_adj}, name=fac))

    coefs_df  = pd.DataFrame(coefs)
    tstats_df = pd.DataFrame(tstats)
    pvals_df  = pd.DataFrame(pvals)
    fits_df   = pd.DataFrame(fits)

    coefs_df.to_csv(os.path.join(SUBDIRS["stat_tests"], f"{prefix}_coefs.csv"))
    tstats_df.to_csv(os.path.join(SUBDIRS["stat_tests"], f"{prefix}_tstats.csv"))
    pvals_df.to_csv(os.path.join(SUBDIRS["stat_tests"], f"{prefix}_pvals.csv"))
    fits_df.to_csv(os.path.join(SUBDIRS["stat_tests"], f"{prefix}_fit.csv"))
    print(f"[OLS] Saved {prefix}_coefs/tstats/pvals/fit.csv to stat_tests/")
    return coefs_df, tstats_df, pvals_df, fits_df

# ---------- NEW: subset dummy tests ----------
def run_statistical_tests_subset(returns_df: pd.DataFrame,
                                 indicators_df: pd.DataFrame,
                                 regimes_df: pd.DataFrame,
                                 subset_dummy_prefixes=None,
                                 interactions=True,
                                 prefix="ols_subset"):
    """
    Build design matrix and, if subset_dummy_prefixes is provided, keep only those
    dummies (and their interactions, if interactions=True). Saves CSVs + figure + summary.
    """
    # Full designs
    from stats import build_designs  # safe self-import in monorepo
    X_clusters_only, X_full = build_designs(returns_df, indicators_df, regimes_df, interactions=interactions)
    X_use = X_full.copy()

    # Filter to subset
    if subset_dummy_prefixes:
        keep = ["const"]  # will be added later in run_ols_panel
        keep.extend(indicators_df.columns.tolist())
        keep.extend([c for c in X_use.columns if any(c.startswith(p) for p in subset_dummy_prefixes)])
        X_use = X_use[sorted(set(keep) & set(X_use.columns))]

    ann = infer_periods_per_year(returns_df.index)
    coefs, tstats, pvals, fits = run_ols_panel(returns_df, X_use, ann, prefix=prefix)

    # Significance figure
    plot_significance_figure(coefs, tstats, pvals, alpha=0.05, coef_quantile=0.75,
                             fname=os.path.join(SUBDIRS["stat_tests"], f"{prefix}_significance"))

    # statsmodels textual summary (first factor) if available
    if STATSM:
        fac0 = returns_df.columns[0]
        Xc = pd.concat([pd.Series(1.0, index=X_use.index, name="const"), X_use], axis=1).astype(float)
        model = sm.OLS(returns_df[fac0].values, Xc.values).fit(cov_type="HAC", cov_kwds={"maxlags": _nw_lags_from_freq(ann)})
        with open(os.path.join(SUBDIRS["stat_tests"], f"{prefix}_summary.txt"), "w") as f:
            f.write(str(model.summary()))

    return coefs, tstats, pvals, fits

# ---------- significance figure ----------
def plot_significance_figure(coefs_df: pd.DataFrame,
                             tstats_df: pd.DataFrame,
                             pvals_df: pd.DataFrame,
                             alpha: float = 0.05,
                             coef_quantile: float = 0.75,
                             fname: str = None):
    abs_coef = coefs_df.abs()
    thresh = abs_coef.quantile(coef_quantile, axis=0).replace(0, np.nan)
    large = abs_coef.ge(thresh, axis=1).fillna(False)
    signif = pvals_df.lt(alpha)
    mask = (large & signif).astype(int)

    order = mask.sum(axis=0).sort_values(ascending=False).index
    mask = mask[order]

    plt.figure(figsize=(max(8, mask.shape[1]*0.35), max(4, mask.shape[0]*0.25)))
    plt.imshow(mask.values, aspect="auto", cmap="Greens", vmin=0, vmax=1)
    plt.xticks(range(mask.shape[1]), mask.columns, rotation=90)
    plt.yticks(range(mask.shape[0]), mask.index)
    plt.title("Significant & Large Predictors (p<{}, |coef|≥Q{:.0%})".format(alpha, coef_quantile))
    plt.colorbar(fraction=0.046, pad=0.04)
    plt.tight_layout()
    if fname is None:
        fname = os.path.join(SUBDIRS["stat_tests"], "ols_significance")
    plt.savefig(fname + ".png", dpi=160, bbox_inches="tight")
    plt.close()

def plot_significance_annotated(coefs_df: pd.DataFrame,
                                pvals_df: pd.DataFrame,
                                alpha: float = 0.05,
                                coef_quantile: float = 0.75,
                                fname: str = None,
                                fmt: str = ".3f"):
    """
    Heatmap with annotations: show coefficient values for cells that are both
    significant (p<alpha) and large (|coef| >= quantile).
    Non-significant or small cells are shown faint with no text.

    Saves <fname>.png in stat_tests/ (default).
    Rows = factors, cols = predictors.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import os

    from configs import SUBDIRS

    abs_coef = coefs_df.abs()
    thresh = abs_coef.quantile(coef_quantile, axis=0).replace(0, np.nan)
    large = abs_coef.ge(thresh, axis=1).fillna(False)
    signif = pvals_df.lt(alpha)
    mask = (large & signif)

    # Order columns by how often they’re significant & large
    order = mask.sum(axis=0).sort_values(ascending=False).index
    coefs_o = coefs_df[order]
    pvals_o = pvals_df[order]
    mask_o  = mask[order]

    vals = coefs_o.values
    ann_mask = mask_o.values

    # color map: emphasize significant/large; tone down others
    # we'll use absolute value to scale color intensity
    vmax = np.nanpercentile(np.abs(vals[ann_mask]), 95) if ann_mask.any() else np.nanmax(np.abs(vals))
    vmax = vmax if vmax and np.isfinite(vmax) and vmax>0 else 1.0

    plt.figure(figsize=(max(8, coefs_o.shape[1]*0.35), max(4, coefs_o.shape[0]*0.35)))
    im = plt.imshow(np.clip(np.abs(vals)/vmax, 0, 1), aspect="auto", cmap="Greens", vmin=0, vmax=1)

    # annotate only significant & large cells
    for i in range(vals.shape[0]):
        for j in range(vals.shape[1]):
            if ann_mask[i, j]:
                plt.text(j, i, format(vals[i, j], fmt), ha="center", va="center", fontsize=7, color="black")

    plt.xticks(range(coefs_o.shape[1]), coefs_o.columns, rotation=90)
    plt.yticks(range(coefs_o.shape[0]), coefs_o.index)
    plt.title(f"Significant & Large (p<{alpha}, |coef|≥Q{coef_quantile:.0%}) — Annotated")
    plt.colorbar(im, fraction=0.046, pad=0.04, label="|coef| (scaled)")
    plt.tight_layout()
    if fname is None:
        fname = os.path.join(SUBDIRS['stat_tests'], "ols_significance_annotated")
    plt.savefig(fname + ".png", dpi=160, bbox_inches="tight")
    plt.close()