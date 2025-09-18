# regimes_lab/stats/apply_selections.py
import os
import re
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from statsmodels.stats.sandwich_covariance import cov_hac
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.diagnostic import acorr_ljungbox
from sklearn.metrics import r2_score
from scipy.stats import t as student_t

from ..configs import STATS_TAB_DIR, HAC_LAGS, TRAIN_FRAC, VAL_FRAC
from ..splitters import future_sum_returns
from ..io_utils import save_df


# ------------------------- small utilities -------------------------

def _align(y: pd.Series, X: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    y_, X_ = y.align(X, join="inner")
    mask = y_.notna() & ~X_.isna().any(axis=1)
    return y_[mask], X_[mask]

def _split_on_support(y: pd.Series, train_frac: float, val_frac: float) -> tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    idx = y.dropna().index
    T = len(idx)
    n_tr = int(train_frac * T)
    n_va = int(val_frac * T)
    return idx[:n_tr], idx[n_tr + n_va:]

def _pvals_from_t(tvals: np.ndarray, df_resid: float) -> np.ndarray:
    return 2.0 * student_t.sf(np.abs(tvals), df=df_resid) if df_resid > 0 else np.full_like(tvals, np.nan, dtype=float)

def _ols_hac_full(y: pd.Series, X: pd.DataFrame, hac_lags: int = 5) -> dict:
    """
    statsmodels OLS fit + HAC covariance; returns coef/t/p, R2, DW, Ljung-Box p, summary text.
    """
    y_, X_ = _align(y, X)
    Xc = add_constant(X_, has_constant="add")
    res = {
        "coef": pd.Series(dtype=float),
        "t": pd.Series(dtype=float),
        "p": pd.Series(dtype=float),
        "r2": np.nan,
        "dw": np.nan,
        "lb_p": np.nan,
        "summary": "",
        "n": len(y_),
    }
    if X_.shape[1] == 0 or len(y_) < 5:
        return res

    model = OLS(y_, Xc).fit()
    # HAC cov + robust t/p
    cov = cov_hac(model, nlags=hac_lags)
    se = np.sqrt(np.maximum(np.diag(cov), 1e-12))
    tvals = model.params.values / se
    pvals = _pvals_from_t(tvals, float(model.df_resid))
    res["coef"] = pd.Series(model.params.values, index=model.params.index)
    res["t"]    = pd.Series(tvals, index=model.params.index)
    res["p"]    = pd.Series(pvals, index=model.params.index)

    try:
        res["r2"] = r2_score(y_, model.predict(Xc))
    except Exception:
        pass

    try:
        res["dw"] = float(durbin_watson(model.resid))
        lb = acorr_ljungbox(model.resid, lags=[min(20, max(2, len(model.resid)//10))], return_df=True)["lb_pvalue"].iloc[0]
        res["lb_p"] = float(lb)
    except Exception:
        pass

    try:
        res["summary"] = model.summary().as_text()
    except Exception:
        res["summary"] = ""

    return res

def _joint_F_pvalue(y: pd.Series, X: pd.DataFrame) -> float:
    """
    Joint F-test that *all regressors* (excluding const) are zero.
    """
    y_, X_ = _align(y, X)
    if X_.shape[1] == 0 or len(y_) < (X_.shape[1] + 2):
        return np.nan
    Xc = add_constant(X_, has_constant="add")
    try:
        m = OLS(y_, Xc).fit()
        cols = [c for c in Xc.columns if c != "const"]
        if not cols:
            return np.nan
        return float(m.f_test(" + ".join(cols) + " = 0").pvalue)
    except Exception:
        return np.nan


# ------------------------- selection I/O -------------------------

def _discover_selection_jsons(prefix: str = "COMBINED_SELECTED_SELECTED_") -> list[str]:
    os.makedirs(STATS_TAB_DIR, exist_ok=True)
    files = [f for f in os.listdir(STATS_TAB_DIR) if f.startswith(prefix) and f.endswith(".json")]
    files.sort()
    return [os.path.join(STATS_TAB_DIR, f) for f in files]

def _parse_factor_horizon(fname: str) -> tuple[str, int]:
    # pattern: COMBINED_SELECTED_SELECTED_<factor>_h<h>.json
    base = os.path.basename(fname)
    m = re.match(r"^COMBINED_SELECTED_SELECTED_(.+?)_h(\d+)\.json$", base)
    if not m:
        return base, -1
    return m.group(1), int(m.group(2))

def _load_selection(fname: str) -> dict:
    with open(fname, "r") as fh:
        return json.load(fh)


# ------------------------- main driver -------------------------

def apply_and_test_all_selections(
    R: pd.DataFrame,         # factor returns
    D: pd.DataFrame,         # all regime dummies
    IND: pd.DataFrame,       # indicators (controls)
    hac_lags: int = HAC_LAGS,
    prefix_in: str = "COMBINED_SELECTED_SELECTED_",
    prefix_out: str = "COMBINED_SELECTED_APPLIED"
) -> None:
    """
    Read all saved selections (JSON), refit OLS/HAC for TRAIN / TEST / ALL,
    save full coef/t/p tables (CSV), model summaries (.txt), and a per-horizon summary CSV.
    """
    sel_files = _discover_selection_jsons(prefix=prefix_in)
    if not sel_files:
        print(f"[apply] No selection JSONs found in {STATS_TAB_DIR} (prefix={prefix_in}).")
        return

    # Group by horizon to emit a compact summary per-h
    grouped: dict[int, list[tuple[str, str]]] = {}
    for path in sel_files:
        factor, h = _parse_factor_horizon(path)
        grouped.setdefault(h, []).append((factor, path))

    for h, items in grouped.items():
        rows = []
        for factor, path in items:
            payload = _load_selection(path)
            chosen = payload.get("chosen_dummies", [])
            if not chosen:
                print(f"[apply] {os.path.basename(path)} → no chosen dummies; skipping {factor}, h={h}")
                continue

            # Build y and splits
            Rh = future_sum_returns(R, h)
            y = Rh[factor]
            tr_idx, te_idx = _split_on_support(y, TRAIN_FRAC, VAL_FRAC)

            # Designs
            X_tr = pd.concat([IND.reindex(tr_idx).astype(float),
                              D[chosen].reindex(tr_idx).fillna(0.0).astype(float)], axis=1)
            X_te = pd.concat([IND.reindex(te_idx).astype(float),
                              D[chosen].reindex(te_idx).fillna(0.0).astype(float)], axis=1)
            X_all = pd.concat([IND, D[chosen]], axis=1).reindex(R.index).fillna(0.0).astype(float)

            # Train / Test / All fits
            res_tr  = _ols_hac_full(y.reindex(tr_idx), X_tr, hac_lags=hac_lags)
            res_te  = _ols_hac_full(y.reindex(te_idx), X_te, hac_lags=hac_lags)
            res_all = _ols_hac_full(y.reindex(R.index), X_all.reindex(R.index), hac_lags=hac_lags)

            # Save detailed coef tables
            save_df(pd.DataFrame({"coef":res_tr["coef"], "t":res_tr["t"], "p":res_tr["p"]}).sort_index(),
                    os.path.join(STATS_TAB_DIR, f"{prefix_out}_TRAIN_{factor}_h{h}.csv"))
            save_df(pd.DataFrame({"coef":res_te["coef"], "t":res_te["t"], "p":res_te["p"]}).sort_index(),
                    os.path.join(STATS_TAB_DIR, f"{prefix_out}_TEST_{factor}_h{h}.csv"))
            save_df(pd.DataFrame({"coef":res_all["coef"], "t":res_all["t"], "p":res_all["p"]}).sort_index(),
                    os.path.join(STATS_TAB_DIR, f"{prefix_out}_ALL_{factor}_h{h}.csv"))

            # Save model summaries as text for easy reading
            with open(os.path.join(STATS_TAB_DIR, f"{prefix_out}_TRAIN_{factor}_h{h}.txt"), "w") as fh:
                fh.write(res_tr["summary"] or "(no summary)")
            with open(os.path.join(STATS_TAB_DIR, f"{prefix_out}_TEST_{factor}_h{h}.txt"), "w") as fh:
                fh.write(res_te["summary"] or "(no summary)")
            with open(os.path.join(STATS_TAB_DIR, f"{prefix_out}_ALL_{factor}_h{h}.txt"), "w") as fh:
                fh.write(res_all["summary"] or "(no summary)")

            # Model-level joint F (excluding const)
            Fp_tr  = _joint_F_pvalue(y.reindex(tr_idx), X_tr)
            Fp_te  = _joint_F_pvalue(y.reindex(te_idx), X_te)
            Fp_all = _joint_F_pvalue(y.reindex(R.index), X_all.reindex(R.index))

            rows.append({
                "factor": factor, "h": h,
                "n_train": res_tr["n"], "n_test": res_te["n"], "n_all": res_all["n"],
                "R2_train": res_tr["r2"], "R2_test": res_te["r2"], "R2_all": res_all["r2"],
                "F_p_train": Fp_tr, "F_p_test": Fp_te, "F_p_all": Fp_all,
                "DW_train": res_tr["dw"], "DW_test": res_te["dw"], "DW_all": res_all["dw"],
                "LBp_train": res_tr["lb_p"], "LBp_test": res_te["lb_p"], "LBp_all": res_all["lb_p"],
                "n_dummies": len(chosen)
            })

            print(f"[apply] factor={factor:>12s} h={h:>2d} | "
                  f"R2(tr/te/all)=({res_tr['r2']:.3f}/{res_te['r2']:.3f}/{res_all['r2']:.3f}) "
                  f"F_p(tr/te/all)=({Fp_tr:.3g}/{Fp_te:.3g}/{Fp_all:.3g})")

        # Save compact summary for this horizon
        if rows:
            summary = pd.DataFrame(rows).set_index(["factor", "h"]).sort_index()
            save_df(summary, os.path.join(STATS_TAB_DIR, f"{prefix_out}_SUMMARY_h{h}.csv"))