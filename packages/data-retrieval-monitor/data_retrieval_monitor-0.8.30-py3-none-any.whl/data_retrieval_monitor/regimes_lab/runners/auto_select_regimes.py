# analytics/regimes_lab/runners/auto_select_regimes.py
import os, json, argparse
import numpy as np
import pandas as pd

from regimes_lab.data import prepare, _future_sum_returns
from regimes_lab.regimes import load_or_build_labels
from regimes_lab.configs import (
    STATS_TAB_DIR, TRAIN_FRAC, VAL_FRAC, DEFAULT_HORIZONS, SELECTOR, HAC_LAGS
)

import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_hac as _cov_hac_try

try:
    from statsmodels.stats.sandwich_covariance import cov_hac_simple as _cov_hac_simple
except Exception:
    _cov_hac_simple = None

try:
    from sklearn.linear_model import LassoCV
    SKL_OK = True
except Exception:
    SKL_OK = False

os.makedirs(STATS_TAB_DIR, exist_ok=True)

# ----------------------------- helpers -----------------------------

def _train_val_test_index(idx: pd.DatetimeIndex, train_frac, val_frac):
    T = len(idx)
    n_tr = int(train_frac * T)
    n_va = int(val_frac * T)
    te0 = n_tr + n_va
    tr = idx[:n_tr]
    va = idx[n_tr: te0]
    te = idx[te0:]
    return tr, va, te

def _cov_hac_safe(model, lags: int):
    """
    Prefer HAC with nlags; fall back to cov_hac_simple; else HC0.
    Always returns a covariance matrix (ndarray).
    """
    # 1) statsmodels >=0.13: cov_hac(model, nlags=...)
    try:
        return _cov_hac_try(model, nlags=int(lags))
    except TypeError:
        pass
    except Exception:
        pass
    # 2) older: cov_hac_simple(model, nlags=...)
    if _cov_hac_simple is not None:
        try:
            return _cov_hac_simple(model, nlags=int(lags))
        except Exception:
            pass
    # 3) HC0
    try:
        return model.get_robustcov_results(cov_type="HC0").cov_params()
    except Exception:
        p = len(model.params)
        return np.eye(p) * 1e6

def _ols_hac(y: pd.Series, X: pd.DataFrame, hac_lags: int, min_rows: int = 30):
    """
    OLS with HAC covariance (version-safe).
    Align indices, coerce numeric, drop NaNs.
    Returns: (statsmodels_results, df with coef/t_hac/se_hac)
    """
    df = pd.concat([y.rename("y"), X], axis=1, join="inner")
    for c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan).dropna(axis=0, how="any")

    if df.empty or df.shape[0] < max(min_rows, X.shape[1] + 2):
        raise ValueError(f"Not enough clean rows for OLS: n={df.shape[0]}, p={X.shape[1]}.")

    y_clean = df["y"].astype(np.float64)
    X_clean = df.drop(columns=["y"]).astype(np.float64)
    Xc = sm.add_constant(X_clean, has_constant="add")

    model = sm.OLS(y_clean, Xc, missing="drop").fit()
    cov = _cov_hac_safe(model, lags=int(hac_lags))
    se = np.sqrt(np.clip(np.diag(cov), 1e-18, np.inf))
    params = model.params.values
    tvals = params / se

    out = pd.DataFrame({"coef": params, "t_hac": tvals, "se_hac": se}, index=model.params.index)
    return model, out

def _phi_std_normal(z):
    from math import erf, sqrt
    z = np.asarray(z, dtype=float)
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))

def _score_from_row(row: pd.Series, weights: dict) -> tuple[float,float,float,float]:
    coef = float(row["coef"])
    tval = float(row["t_hac"])
    pval = float(2.0 * (1.0 - _phi_std_normal(abs(tval))))
    abs_coef = abs(coef)
    total = 0.0
    if "t_hac" in weights:    total += weights["t_hac"] * tval
    if "abs_coef" in weights: total += weights["abs_coef"] * abs_coef
    if "neg_p" in weights:    total += weights["neg_p"] * (1.0 - pval)
    return float(total), pval, abs_coef, tval

def _build_full_dummies(L: pd.DataFrame) -> pd.DataFrame:
    """
    Full set of regime dummies for every model column in L (no drop_first).
    Columns named like: <model>_R_<k>
    """
    parts = []
    for col in L.columns:
        s = pd.to_numeric(L[col], errors="coerce").astype("Int64")
        d = pd.get_dummies(s, prefix=f"{col}_R", drop_first=False, dtype=float)
        parts.append(d)
    if not parts:
        return pd.DataFrame(index=L.index)
    D = pd.concat(parts, axis=1)
    D = D.replace([np.inf, -np.inf], np.nan).dropna(axis=0, how="any")
    return D.astype(np.float64)

def _maybe_lasso_gate(X, y, random_state=0):
    if not SKL_OK or X.shape[0] < 10 or X.shape[1] < 2:
        return set(X.columns)
    X_ = (X - X.mean(0)) / (X.std(0).replace(0, 1.0))
    X_ = X_.fillna(0.0)
    y_ = y.loc[X_.index].fillna(0.0)
    lass = LassoCV(cv=5, random_state=random_state, n_jobs=-1).fit(X_.values, y_.values)
    keep = set(X_.columns[np.abs(lass.coef_) > 1e-12])
    return keep if keep else set(X.columns)

# ---------------------- selection core ----------------------

def _select_for_factor(
    R: pd.DataFrame,
    IND: pd.DataFrame,
    L: pd.DataFrame,
    factor: str,
    horizon: int,
    lags: list[int],
    include_indicators: bool,
    hac_lags: int,
    metrics: list[str],
    weights: dict,
    thresholds: dict,
    use_lasso: bool,
    min_rows: int = 30,
):
    """
    For a factor and horizon h:
      - y_t^(h) = sum_{i=0}^{h-1} r_{t+i}
      - Build full regime dummies from labels and APPLY predictive lags in 'lags'
      - (Optionally) include raw indicators as controls (no pre-shift here)
      - Score each (dummy, lag) marginally with HAC OLS on TRAIN
    Returns payload dict (like before) + a long DataFrame of all scored dummies.
    """
    # target
    y = _future_sum_returns(R[[factor]], int(horizon)).iloc[:, 0].dropna()
    if y.empty:
        return dict(
            factor=factor, horizon=int(horizon), chosen_dummies=[],
            score_table={}, metric_table={}, error="empty target"
        ), pd.DataFrame()

    # labels -> dummies (no drop_first), then lag them
    D0 = _build_full_dummies(L).reindex(y.index)
    if D0.empty:
        return dict(
            factor=factor, horizon=int(horizon), chosen_dummies=[],
            score_table={}, metric_table={}, error="no dummies"
        ), pd.DataFrame()

    # base indicators (optional)
    X_ind = IND.reindex(y.index)
    if include_indicators:
        X_ind = X_ind.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    else:
        X_ind = pd.DataFrame(index=y.index)

    # split
    tr_idx, va_idx, te_idx = _train_val_test_index(y.index, TRAIN_FRAC, VAL_FRAC)
    if len(tr_idx) < max(min_rows, 30) or len(te_idx) < 5:
        return dict(
            factor=factor, horizon=int(horizon), chosen_dummies=[],
            score_table={}, metric_table={}, error="too few rows after split"
        ), pd.DataFrame()

    # optional LASSO gate on TRAIN using all (unlagged) dummies as a proxy
    gated = list(D0.columns)
    if use_lasso:
        X_joint_tr = pd.concat([X_ind.loc[tr_idx], D0.loc[tr_idx]], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
        if not X_joint_tr.empty:
            y_tr_align = y.loc[X_joint_tr.index]
            keep = _maybe_lasso_gate(X_joint_tr, y_tr_align)
            gated = [c for c in gated if c in keep]

    # coverage constraint
    cov_min = int(thresholds.get("coverage_min", 0))
    if cov_min > 0:
        cover = D0.loc[tr_idx].sum(0)
        gated = [c for c in gated if int(cover.get(c, 0)) >= cov_min]

    rows = []
    chosen = []
    score_table = {}
    metric_table = {}

    # loop (dummy, lag)
    for dcol in gated:
        for LAG in lags:
            dlag = D0[dcol].shift(int(LAG))  # predictive lag: use only info available at t-LAG
            Z_tr = pd.concat([X_ind.loc[tr_idx], dlag.loc[tr_idx].rename(f"{dcol}_lag{LAG}")], axis=1)

            try:
                model, ols_tr = _ols_hac(y.loc[Z_tr.index], Z_tr, hac_lags=hac_lags, min_rows=min_rows)
            except Exception:
                continue

            name = f"{dcol}_lag{LAG}"
            if name not in ols_tr.index:
                continue

            row = ols_tr.loc[name]
            score, pval, abs_c, tval = _score_from_row(row, weights)

            rows.append({
                "factor": factor,
                "horizon": int(horizon),
                "dummy": dcol,
                "lag": int(LAG),
                "coef": float(row["coef"]),
                "t_hac": float(tval),
                "se_hac": float(row["se_hac"]),
                "p_hac": float(pval),
                "score": float(score),
                "n_train": int(len(Z_tr.index)),
            })
            metric_table[name] = {
                "coef": float(row["coef"]),
                "t_hac": float(tval),
                "se_hac": float(row["se_hac"]),
                "p_hac": float(pval),
                "abs_coef": float(abs_c)
            }
            score_table[name] = float(score)

    # select by p-value threshold (and then by score)
    pmax = thresholds.get("p_hac_max", None)
    if rows:
        df_rows = pd.DataFrame(rows)
        if pmax is not None:
            df_rows = df_rows.loc[np.isfinite(df_rows["p_hac"]) & (df_rows["p_hac"] <= float(pmax))]
        if not df_rows.empty:
            df_rows = df_rows.sort_values(["score", "t_hac", "coef"], ascending=[False, False, False])
            chosen = list(df_rows["dummy"] + "_lag" + df_rows["lag"].astype(str))
        else:
            df_rows = pd.DataFrame(rows)  # keep raw rows for output
    else:
        df_rows = pd.DataFrame()

    payload = dict(
        factor=factor,
        horizon=int(horizon),
        metrics=list(metrics),
        weights={k: float(v) for k, v in weights.items()},
        thresholds=thresholds,
        chosen_dummies=chosen,
        score_table=score_table,
        metric_table=metric_table
    )
    return payload, df_rows

# ----------------------------- main -----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizons", nargs="*", type=int, default=DEFAULT_HORIZONS,
                    help="Forecast horizons used to build targets y_t^(h) via future-sum returns.")
    ap.add_argument("--lags", nargs="*", type=int, default=[1,3,5],
                    help="Predictive lags to apply to regime dummies (e.g., --lags 1 3 5).")
    ap.add_argument("--use_lasso", action="store_true",
                    help="Gate with LASSO on train (indicators + unlagged dummies).")
    ap.add_argument("--no_ind", action="store_true",
                    help="Exclude indicators from marginal regressions.")
    ap.add_argument("--metrics", nargs="*", default=SELECTOR.get("METRICS", ["t_hac","abs_coef","neg_p"]))
    ap.add_argument("--weights", type=str, default=None,
                    help='JSON string, e.g. {"t_hac":1.0,"abs_coef":0.7,"neg_p":0.5}')
    ap.add_argument("--thresholds", type=str, default=None,
                    help='JSON string, e.g. {"p_hac_max":0.10,"coverage_min":10}')
    ap.add_argument("--min_rows", type=int, default=30)
    ap.add_argument("--hac_lags", type=int, default=HAC_LAGS)
    args = ap.parse_args()

    # prepare base data (NO SHIFT on IND)
    R, IND = prepare()
    # labels from contemporaneous indicators
    L = load_or_build_labels(IND, split_tag="full")

    # weights/thresholds
    weights = dict(SELECTOR.get("WEIGHTS", {}))
    thresholds = dict(SELECTOR.get("THRESHOLDS", {}))
    if args.weights:
        weights.update(json.loads(args.weights))
    if args.thresholds:
        thresholds.update(json.loads(args.thresholds))

    os.makedirs(STATS_TAB_DIR, exist_ok=True)

    # Aggregators
    long_rows_global = []            # across all horizons and factors
    agg_per_factor = {}              # factor -> dict(summary)

    for factor in R.columns:
        agg = {
            "factor": factor,
            "horizons": sorted(set(int(h) for h in args.horizons)),
            "lags": sorted(set(int(L) for L in args.lags)),
            "metrics": list(args.metrics),
            "weights": {k: float(v) for k, v in weights.items()},
            "thresholds": thresholds,
            # selections: dict[dummy] -> {
            #    "best": {"horizon","lag","score","coef","t_hac","p_hac","se_hac"},
            #    "occurrences": [ {horizon, lag, coef, t_hac, p_hac, se_hac, score, n_train} ... ]
            # }
            "selections": {},
            # chosen_unique: flattened best entries sorted by score
            "chosen_unique": []
        }

        per_horizon_long = []  # to also write existing per-horizon long CSVs

        for h in args.horizons:
            # run selector (existing behavior)
            try:
                payload, df_rows = _select_for_factor(
                    R, IND, L, factor,
                    horizon=int(h),
                    lags=[int(x) for x in args.lags],
                    include_indicators=(not args.no_ind),
                    hac_lags=int(args.hac_lags),
                    metrics=args.metrics,
                    weights=weights,
                    thresholds=thresholds,
                    use_lasso=args.use_lasso,
                    min_rows=int(args.min_rows),
                )
            except Exception as e:
                payload = dict(factor=factor, horizon=int(h), error=str(e),
                               metrics=list(args.metrics), weights=weights, thresholds=thresholds,
                               chosen_dummies=[], score_table={}, metric_table={})
                df_rows = pd.DataFrame()

            # write per-factor-per-horizon JSON (unchanged contract)
            out = os.path.join(STATS_TAB_DIR, f"COMBINED_SELECTED_{factor}_h{h}.json")
            with open(out, "w") as fh:
                json.dump(payload, fh, indent=2)
            print(f"[auto-select] wrote {out}")

            if not df_rows.empty:
                df_rows = df_rows.copy()
                df_rows["factor"] = factor  # ensure column present (already set in builder)
                per_horizon_long.append(df_rows)
                long_rows_global.append(df_rows)

                # feed aggregator (selections across horizons & lags)
                for _, r in df_rows.iterrows():
                    name = f"{r['dummy']}_lag{int(r['lag'])}"
                    occ = {
                        "horizon": int(r["horizon"]),
                        "lag": int(r["lag"]),
                        "coef": float(r["coef"]),
                        "t_hac": float(r["t_hac"]),
                        "p_hac": float(r["p_hac"]),
                        "se_hac": float(r["se_hac"]),
                        "score": float(r["score"]),
                        "n_train": int(r["n_train"]),
                    }
                    if name not in agg["selections"]:
                        agg["selections"][name] = {"best": occ, "occurrences": [occ]}
                    else:
                        agg["selections"][name]["occurrences"].append(occ)
                        # update best by score (tie-breaker by |t|)
                        best = agg["selections"][name]["best"]
                        is_better = (occ["score"] > best["score"]) or (
                            np.isclose(occ["score"], best["score"]) and abs(occ["t_hac"]) > abs(best["t_hac"])
                        )
                        if is_better:
                            agg["selections"][name]["best"] = occ

            # also emit the per-horizon long CSV matching the original behavior
            if per_horizon_long:
                big_h = pd.concat(per_horizon_long, axis=0, ignore_index=True)
                big_path = os.path.join(STATS_TAB_DIR, f"COMBINED_SELECTED_LONG_h{h}.csv")
                big_h.to_csv(big_path, index=False)
                print(f"[auto-select] wrote {big_path}")
            per_horizon_long.clear()

        # finalize aggregated chosen_unique for this factor
        if agg["selections"]:
            best_rows = []
            for name, obj in agg["selections"].items():
                b = obj["best"]
                best_rows.append({
                    "name": name,
                    "horizon": b["horizon"],
                    "lag": b["lag"],
                    "score": b["score"],
                    "t_hac": b["t_hac"],
                    "coef": b["coef"],
                    "p_hac": b["p_hac"],
                    "se_hac": b["se_hac"],
                    "n_train": b["n_train"],
                })
            best_df = pd.DataFrame(best_rows).sort_values(["score","t_hac","coef"], ascending=[False, False, False])
            agg["chosen_unique"] = best_df["name"].tolist()

        # write aggregated JSON for the factor (new file)
        agg_path = os.path.join(STATS_TAB_DIR, f"COMBINED_SELECTED_{factor}.json")
        with open(agg_path, "w") as fh:
            json.dump(agg, fh, indent=2)
        print(f"[auto-select] wrote {agg_path}")
        agg_per_factor[factor] = agg

    # write one giant CSV across all horizons & factors
    if long_rows_global:
        giant = pd.concat(long_rows_global, axis=0, ignore_index=True)
        giant_path = os.path.join(STATS_TAB_DIR, "COMBINED_SELECTED_AGG.csv")
        giant.to_csv(giant_path, index=False)
        print(f"[auto-select] wrote {giant_path}")

if __name__ == "__main__":
    main()