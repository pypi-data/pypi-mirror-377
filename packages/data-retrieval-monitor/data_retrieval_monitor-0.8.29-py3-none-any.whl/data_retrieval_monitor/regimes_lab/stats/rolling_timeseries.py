# regimes_lab/stats/rolling_timeseries.py
import os
import numpy as np
import pandas as pd
from .diag import ols_hac
from .viz import line_over_windows
from ..configs import (
    ROLL_WINDOW, ROLL_STEP, HAC_LAGS, DW_TOL, LB_ALPHA, STATS_TAB_DIR
)
from ..io_utils import save_df
from ..splitters import future_sum_returns

def rolling_timeseries_suite(R: pd.DataFrame,
                             D: pd.DataFrame,
                             IND: pd.DataFrame,
                             horizons,
                             models: list[str],
                             top_k_per_model: int = 10):
    idx = R.index
    T = len(idx)

    for h in horizons:
        Rh = future_sum_returns(R, h)

        for f in R.columns:
            y = Rh[f]
            # storage: dict[model] -> dict[column] -> list
            store_t = {m: {} for m in models}
            store_p = {m: {} for m in models}
            store_c = {m: {} for m in models}
            time_stamps = []

            # walk windows
            for start in range(0, max(0, T - ROLL_WINDOW - ROLL_STEP) + 1, ROLL_STEP):
                tr_idx = idx[start:start+ROLL_WINDOW]
                te_idx = idx[start+ROLL_WINDOW: start+ROLL_WINDOW+ROLL_STEP]
                if len(te_idx) == 0 or len(tr_idx) < 20:
                    continue

                time_stamps.append(te_idx[-1])

                for m in models:
                    Z = D if m=="COMBINED" else D.filter(like=m+"_R")
                    X_tr = pd.concat([IND.reindex(tr_idx).astype(float),
                                      Z.reindex(tr_idx).fillna(0).astype(float)], axis=1)
                    X_te = pd.concat([IND.reindex(te_idx).astype(float),
                                      Z.reindex(te_idx).fillna(0).astype(float)], axis=1)

                    res = ols_hac(y, X_tr, X_te, hac_lags=HAC_LAGS, refit_test=True)
                    if "t_test" not in res:
                        continue

                    ok = ("dw_test" in res and "lb_p_test" in res and
                          pd.notna(res.get("dw_test",np.nan)) and pd.notna(res.get("lb_p_test",np.nan)) and
                          abs(res["dw_test"]-2.0)<=DW_TOL and res["lb_p_test"]>=LB_ALPHA)

                    t_series = res["t_test"]; p_series = res["p_test"]; c_series = res.get("coef_test", pd.Series(dtype=float))

                    for col in t_series.index:
                        if col == "const":
                            continue
                        store_t[m].setdefault(col, []).append(float(t_series[col]) if ok else np.nan)
                        store_p[m].setdefault(col, []).append(float(p_series[col]) if ok else np.nan)
                        store_c[m].setdefault(col, []).append(float(c_series.get(col, np.nan)) if ok else np.nan)

            # make continuous index (every test window end) and save/plot
            if not time_stamps:
                continue
            ts_index = pd.DatetimeIndex(time_stamps)
            for m in models:
                if not store_t[m]:
                    continue
                Tmat = pd.DataFrame({k: v for k, v in store_t[m].items()}, index=ts_index)
                Pmat = pd.DataFrame({k: v for k, v in store_p[m].items()}, index=ts_index)
                Cmat = pd.DataFrame({k: v for k, v in store_c[m].items()}, index=ts_index)

                # Optional: fill small gaps linearly just for plotting readability
                Tplot = Tmat.interpolate(limit_direction="both")
                Pplot = Pmat.interpolate(limit_direction="both")
                Cplot = Cmat.interpolate(limit_direction="both")

                save_df(Tmat, os.path.join(STATS_TAB_DIR, f"ROLL_T_series_{f}_{m}_h{h}.csv"))
                save_df(Pmat, os.path.join(STATS_TAB_DIR, f"ROLL_P_series_{f}_{m}_h{h}.csv"))
                save_df(Cmat, os.path.join(STATS_TAB_DIR, f"ROLL_COEF_series_{f}_{m}_h{h}.csv"))

                # Top K by mean |t|
                mean_abs_t = Tmat.abs().mean().sort_values(ascending=False)
                top_cols = list(mean_abs_t.head(top_k_per_model).index)
                if top_cols:
                    line_over_windows(Tplot[top_cols], 
                                      title=f"{f} — {m} (TEST HAC t over time, h={h})", 
                                      fname=f"ROLL_T_series_{f}_{m}_h{h}.png")
                    line_over_windows(Pplot[top_cols], 
                                      title=f"{f} — {m} (TEST p over time, h={h})", 
                                      fname=f"ROLL_P_series_{f}_{m}_h{h}.png")
                    line_over_windows(Cplot[top_cols], 
                                      title=f"{f} — {m} (TEST coef over time, h={h})", 
                                      fname=f"ROLL_COEF_series_{f}_{m}_h{h}.png")