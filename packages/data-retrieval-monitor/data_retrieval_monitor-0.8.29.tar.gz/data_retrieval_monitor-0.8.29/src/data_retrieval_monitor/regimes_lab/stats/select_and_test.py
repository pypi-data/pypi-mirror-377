# regimes_lab/stats/select_and_test.py
import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from statsmodels.stats.sandwich_covariance import cov_hac
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.metrics import r2_score
from scipy.stats import t as student_t

from .diag import ols_hac, _align
from ..configs import (
    STATS_TAB_DIR, HAC_LAGS, TRAIN_FRAC, VAL_FRAC, DW_TOL, LB_ALPHA
)
from ..io_utils import save_df
from ..splitters import future_sum_returns


def _split_on_support(y: pd.Series, train_frac: float, val_frac: float) -> Tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    idx = y.dropna().index
    T = len(idx)
    n_tr = int(train_frac * T)
    n_va = int(val_frac * T)
    return idx[:n_tr], idx[n_tr + n_va:]


def _build_design(
    D: pd.DataFrame, IND: pd.DataFrame, chosen_dummy_cols: List[str],
    train_idx: pd.DatetimeIndex, test_idx: pd.DatetimeIndex
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Indicators (controls) + selected regime dummies."""
    Xtr = pd.concat(
        [IND.reindex(train_idx).astype(float), D[chosen_dummy_cols].reindex(train_idx).fillna(0.0).astype(float)],
        axis=1
    )
    Xte = pd.concat(
        [IND.reindex(test_idx).astype(float), D[chosen_dummy_cols].reindex(test_idx).fillna(0.0).astype(float)],
        axis=1
    )
    return Xtr, Xte


def _pvals_from_t(tvals: np.ndarray, df_resid: float) -> np.ndarray:
    return 2.0 * student_t.sf(np.abs(tvals), df=df_resid) if df_resid > 0 else np.full_like(tvals, np.nan, dtype=float)


def _ols_full(y: pd.Series, X: pd.DataFrame, hac_lags: int = 5) -> Dict:
    """Plain OLS (statsmodels) with HAC covariance, model-level metrics."""
    y_, X_ = _align(y, X)
    if X_.shape[1] == 0 or len(y_) < 5:
        return {"coef": pd.Series(dtype=float), "t": pd.Series(dtype=float), "p": pd.Series(dtype=float),
                "r2": np.nan, "dw": np.nan, "lb_p": np.nan, "model_F_p": np.nan, "n": len(y_)}
    Xc = add_constant(X_, has_constant="add")
    m = OLS(y_, Xc).fit()
    cov = cov_hac(m, nlags=hac_lags)
    se = np.sqrt(np.maximum(np.diag(cov), 1e-12))
    t = m.params.values / se
    p = _pvals_from_t(t, float(m.df_resid))
    coef = pd.Series(m.params.values, index=m.params.index)
    tser = pd.Series(t, index=m.params.index)
    pser = pd.Series(p, index=m.params.index)
    # model-level joint F on all regressors (except const)
    cols = [c for c in Xc.columns if c != "const"]
    Fp = np.nan
    if cols:
        try:
            Fp = float(m.f_test(" + ".join(cols) + " = 0").pvalue)
        except Exception:
            pass
    # residual diagnostics
    try:
        dw = float(durbin_watson(m.resid))
        lb = acorr_ljungbox(m.resid, lags=[min(20, max(2, len(m.resid)//10))], return_df=True)["lb_pvalue"].iloc[0]
        lb = float(lb)
    except Exception:
        dw, lb = np.nan, np.nan
    # fitted R2
    try:
        r2 = r2_score(y_, m.predict(Xc))
    except Exception:
        r2 = np.nan
    return {"coef": coef, "t": tser, "p": pser, "r2": r2, "dw": dw, "lb_p": lb, "model_F_p": Fp, "n": len(y_)}


def _initial_significant_from_models(
    y: pd.Series, D: pd.DataFrame, IND: pd.DataFrame,
    train_idx: pd.DatetimeIndex, alpha_sig: float
) -> List[str]:
    """
    For each model separately, keep its dummy columns with TRAIN p < alpha_sig (with IND controls).
    Return the union of selected dummy columns across models.
    """
    chosen: List[str] = []
    models = sorted(set(c.split("_R")[0] for c in D.columns))
    for m in models:
        Zm_cols = list(D.filter(like=m + "_R").columns)
        if not Zm_cols:
            continue
        Xtr = pd.concat([IND.reindex(train_idx).astype(float),
                         D[Zm_cols].reindex(train_idx).fillna(0.0).astype(float)], axis=1)
        # use ols_hac to get TRAIN p-values
        res = ols_hac(y, Xtr, Xtr, hac_lags=HAC_LAGS, refit_test=False)
        ptrain = res["p_train"].reindex(["const"] + Zm_cols).drop(index="const", errors="ignore")
        keep = [c for c, p in ptrain.items() if (pd.notna(p) and p < alpha_sig)]
        chosen.extend(keep)
    return sorted(set(chosen))


def _prune_by_train_refit(
    y: pd.Series, IND: pd.DataFrame, D: pd.DataFrame,
    train_idx: pd.DatetimeIndex, candidates: List[str], alpha_sig: float
) -> List[str]:
    """
    Refit on TRAIN with all candidates together, then drop non-significant dummy cols (p >= alpha_sig).
    Keep indicators as controls.
    """
    if not candidates:
        return []
    Xtr = pd.concat([IND.reindex(train_idx).astype(float),
                     D[candidates].reindex(train_idx).fillna(0.0).astype(float)], axis=1)
    res = _ols_full(y, Xtr, hac_lags=HAC_LAGS)
    p = res["p"].drop(index="const", errors="ignore")
    # Only consider dummy columns (exclude indicators)
    dummy_cols = [c for c in candidates if c in p.index]
    keep = [c for c in dummy_cols if (pd.notna(p.get(c)) and p.get(c) < alpha_sig)]
    return sorted(set(keep))


def select_and_test_best_combination(
    R: pd.DataFrame,              # factor returns (log) indexed by date
    D: pd.DataFrame,              # regime dummies (all models), indexed by date
    IND: pd.DataFrame,            # indicators (controls), indexed by date (already lagged +2 upstream)
    horizons: List[int],
    alpha_sig: float = 0.05,
    save_prefix: str = "COMBINED_SELECTED"
) -> None:
    """
    For each factor & forecast horizon:
      1) TRAIN selection: Gather significant per-model dummies, union them, refit & prune on TRAIN.
      2) Save the final chosen dummy list.
      3) Build designs (IND + chosen dummies), and run OLS/HAC on:
         - TRAIN only
         - TEST only (refit)
         - ALL data (entire period)
      4) Save detailed tables and a small JSON summary with model-level p-values and R².
    """
    os.makedirs(STATS_TAB_DIR, exist_ok=True)

    for h in horizons:
        Rh = future_sum_returns(R, h)
        summary_rows = []

        for f in R.columns:
            y = Rh[f]
            tr_idx, te_idx = _split_on_support(y, TRAIN_FRAC, VAL_FRAC)

            # 1) initial candidates from per-model TRAIN significance
            candidates = _initial_significant_from_models(y, D, IND, tr_idx, alpha_sig=alpha_sig)

            # 2) prune by refitting on TRAIN jointly
            chosen = _prune_by_train_refit(y, IND, D, tr_idx, candidates, alpha_sig=alpha_sig)

            # Persist selection for reproducibility
            sel_path = os.path.join(STATS_TAB_DIR, f"{save_prefix}_SELECTED_{f}_h{h}.json")
            with open(sel_path, "w") as fh:
                json.dump({"factor": f, "horizon": h, "chosen_dummies": chosen}, fh, indent=2)

            # 3) Design matrices
            X_tr, X_te = _build_design(D, IND, chosen, tr_idx, te_idx)
            X_all = pd.concat([IND, D[chosen]], axis=1).reindex(R.index).fillna(0.0).astype(float)

            # 3a) TRAIN OLS/HAC (fit on train subset)
            train_res = _ols_full(y.reindex(tr_idx), X_tr, hac_lags=HAC_LAGS)
            save_df(pd.DataFrame({
                "coef": train_res["coef"], "t": train_res["t"], "p": train_res["p"]
            }).sort_index(), os.path.join(STATS_TAB_DIR, f"{save_prefix}_TRAIN_{f}_h{h}.csv"))

            # 3b) TEST OLS/HAC (refit purely on test subset)
            test_res = _ols_full(y.reindex(te_idx), X_te, hac_lags=HAC_LAGS)
            save_df(pd.DataFrame({
                "coef": test_res["coef"], "t": test_res["t"], "p": test_res["p"]
            }).sort_index(), os.path.join(STATS_TAB_DIR, f"{save_prefix}_TEST_{f}_h{h}.csv"))

            # 3c) ALL OLS/HAC (entire period) – are chosen dummies globally significant?
            all_res = _ols_full(y.reindex(R.index), X_all.reindex(R.index), hac_lags=HAC_LAGS)
            save_df(pd.DataFrame({
                "coef": all_res["coef"], "t": all_res["t"], "p": all_res["p"]
            }).sort_index(), os.path.join(STATS_TAB_DIR, f"{save_prefix}_ALL_{f}_h{h}.csv"))

            # A small line in a summary table
            summary_rows.append({
                "factor": f, "h": h,
                "n_train": train_res.get("n", np.nan),
                "n_test":  test_res.get("n", np.nan),
                "R2_train": train_res.get("r2", np.nan),
                "R2_test":  test_res.get("r2", np.nan),
                "R2_all":   all_res.get("r2", np.nan),
                "F_p_train": train_res.get("model_F_p", np.nan),
                "F_p_test":  test_res.get("model_F_p", np.nan),
                "F_p_all":   all_res.get("model_F_p", np.nan),
                "DW_train":  train_res.get("dw", np.nan),
                "DW_test":   test_res.get("dw", np.nan),
                "DW_all":    all_res.get("dw", np.nan),
                "LBp_train": train_res.get("lb_p", np.nan),
                "LBp_test":  test_res.get("lb_p", np.nan),
                "LBp_all":   all_res.get("lb_p", np.nan),
                "n_dummies": len(chosen)
            })

        # Save a per-horizon summary table
        summary = pd.DataFrame(summary_rows).set_index(["factor", "h"]).sort_index()
        save_df(summary, os.path.join(STATS_TAB_DIR, f"{save_prefix}_SUMMARY_h{h}.csv"))