# regimes_lab/stats/testpanel.py
import os
import numpy as np
import pandas as pd
from .diag import ols_hac, lasso_cv
from .viz import heatmap_panel, bar_significance, pvalue_hist
from ..configs import (
    STATS_DIR, STATS_TAB_DIR, HAC_LAGS, TRAIN_FRAC, VAL_FRAC, DW_TOL, LB_ALPHA
)
from ..splitters import future_sum_returns
from ..io_utils import save_df

def _split_on_support(y: pd.Series, train_frac, val_frac):
    idx = y.dropna().index
    T = len(idx); n_tr = int(train_frac*T); n_va = int(val_frac*T)
    return idx[:n_tr], idx[n_tr+n_va:]

def _table_path(*names):
    os.makedirs(STATS_TAB_DIR, exist_ok=True)
    return os.path.join(STATS_TAB_DIR, "_".join(names))

def _joint_pvalue(y: pd.Series, X_te: pd.DataFrame):
    from statsmodels.regression.linear_model import OLS
    from statsmodels.tools import add_constant
    y_, X_ = y.align(X_te, join="inner")
    if X_.shape[1]==0 or len(y_) < X_.shape[1]+2: return np.nan
    Xc = add_constant(X_, has_constant="add"); m = OLS(y_, Xc).fit()
    cols = [c for c in Xc.columns if c!="const"]
    if not cols: return np.nan
    hyp = " + ".join(cols) + " = 0"
    try: return float(m.f_test(hyp).pvalue)
    except Exception: return np.nan

def _build_design(D: pd.DataFrame, IND: pd.DataFrame, model: str, train_idx, test_idx,
                  selected_cols_train: list[str] | None):
    """
    Return (X_tr, X_te) with IND controls + chosen dummy columns.
    If model == 'COMBINED':
        - If selected_cols_train provided, use those (significant-only mode).
        - Else use all dummies (COMBINED baseline).
    Else:
        - Use only that model's dummy columns.
    """
    # indicators as controls (already lagged upstream)
    C_tr = IND.reindex(train_idx).astype(float)
    C_te = IND.reindex(test_idx).astype(float)

    if model == "COMBINED":
        Z = D if selected_cols_train is None else D[selected_cols_train]
    else:
        Z = D.filter(like=model + "_R")

    X_tr = pd.concat([C_tr, Z.reindex(train_idx).fillna(0).astype(float)], axis=1)
    X_te = pd.concat([C_te, Z.reindex(test_idx).fillna(0).astype(float)], axis=1)
    return X_tr, X_te

def single_split_suite(R: pd.DataFrame,
                       D: pd.DataFrame,
                       IND: pd.DataFrame,
                       horizons,
                       alpha_sig: float = 0.05,
                       combine_significant_only: bool = True):
    """
    Train/test once-only stats with indicators as controls.
    If combine_significant_only=True, the COMBINED regression uses only dummies
    that were significant (p<alpha_sig) in each model's TRAIN regression.
    """
    models = sorted(set(c.split("_R")[0] for c in D.columns)) + ["COMBINED"]

    for h in horizons:
        Rh = future_sum_returns(R, h)
        panel_maxabs_t = pd.DataFrame(index=R.columns, columns=models, dtype=float)
        panel_joint_p  = pd.DataFrame(index=R.columns, columns=models, dtype=float)
        panel_maxabs_t_f = panel_maxabs_t.copy()
        panel_joint_p_f  = panel_joint_p.copy()

        for f in R.columns:
            y = Rh[f]
            tr_idx, te_idx = _split_on_support(y, TRAIN_FRAC, VAL_FRAC)

            # --- Determine significant dummies on TRAIN per model (for COMBINED selection) ---
            train_sig_cols = []
            if combine_significant_only:
                for m0 in models:
                    if m0 == "COMBINED": 
                        continue
                    Xtr0, Xte0 = _build_design(D, IND, m0, tr_idx, te_idx, None)
                    res0 = ols_hac(y, Xtr0, Xte0, hac_lags=HAC_LAGS, refit_test=False)
                    pt = res0["p_train"].drop(index="const", errors="ignore")
                    sig_cols = [c for c, p in pt.items() if (c in Xtr0.columns) and (p < alpha_sig)]
                    train_sig_cols.extend(sig_cols)
                train_sig_cols = sorted(set(train_sig_cols)) if train_sig_cols else None
            else:
                train_sig_cols = None  # all dummies

            for m in models:
                X_tr, X_te = _build_design(D, IND, m, tr_idx, te_idx, train_sig_cols if m=="COMBINED" else None)
                res = ols_hac(y, X_tr, X_te, hac_lags=HAC_LAGS, refit_test=True)

                # --- Save detailed tables (TRAIN / TEST) ---
                save_df(pd.DataFrame({"coef":res["coef_train"],"t":res["t_train"],"p":res["p_train"]}),
                        _table_path(f"TRAIN_OLS_{f}_{m}_h{h}.csv"))
                if "coef_test" in res:
                    save_df(pd.DataFrame({"coef":res["coef_test"],"t":res["t_test"],"p":res["p_test"]}),
                            _table_path(f"TEST_OLS_{f}_{m}_h{h}.csv"))

                # --- Per-model bar chart + p-value histogram (TEST) ---
                if "coef_test" in res:
                    bar_significance(
                        coef=res["coef_test"],
                        t=res["t_test"],
                        p=res["p_test"],
                        title=f"{f} — {m} (TEST, h={h})",
                        fname=f"{f}_{m}_TEST_h{h}.png",
                    )
                    pvalue_hist(
                        p=res["p_test"].drop(index="const", errors="ignore"),
                        title=f"p-value histogram: {f} — {m} (TEST, h={h})",
                        fname=f"pval_hist_{f}_{m}_TEST_h{h}.png"
                    )

                # --- Panel metrics (TEST) ---
                max_abs_t = np.nan
                if "t_test" in res:
                    ttest = res["t_test"].drop(index="const", errors="ignore")
                    if ttest.size>0: max_abs_t = float(ttest.abs().max())
                panel_maxabs_t.loc[f,m] = max_abs_t

                keep = ("dw_test" in res and "lb_p_test" in res and
                        pd.notna(res.get("dw_test",np.nan)) and pd.notna(res.get("lb_p_test",np.nan)) and
                        abs(res["dw_test"]-2.0)<=DW_TOL and res["lb_p_test"]>=LB_ALPHA)
                panel_maxabs_t_f.loc[f,m] = max_abs_t if keep else np.nan

                pjoint = _joint_pvalue(y.loc[te_idx], X_te)
                panel_joint_p.loc[f,m] = pjoint
                panel_joint_p_f.loc[f,m] = pjoint if keep else np.nan

        # --- Save panel tables ---
        save_df(panel_maxabs_t, _table_path(f"PANEL_OOS_MAXABS_T_h{h}.csv"))
        save_df(panel_maxabs_t_f, _table_path(f"PANEL_OOS_MAXABS_T_FILTERED_h{h}.csv"))
        save_df(panel_joint_p,  _table_path(f"PANEL_JOINTF_P_h{h}.csv"))
        save_df(panel_joint_p_f,_table_path(f"PANEL_JOINTF_P_FILTERED_h{h}.csv"))

        # --- Panel figures ---
        from .viz import heatmap_panel
        heatmap_panel(panel_maxabs_t,
                      title=f"Max |OOS HAC t| per Factor × Model with IND controls (h={h})",
                      fname=f"panel_oos_maxabs_t_h{h}.png",
                      cmap="magma", fmt=".2f")
        heatmap_panel(panel_maxabs_t_f,
                      title=f"[Filtered] Max |OOS HAC t| (DW≈2 & LB p≥{LB_ALPHA}) (h={h})",
                      fname=f"panel_oos_maxabs_t_filtered_h{h}.png",
                      cmap="magma", fmt=".2f")
        heatmap_panel(-np.log10(panel_joint_p).replace([np.inf, -np.inf], np.nan),
                      title=f"Joint F-test (−log10 p) with IND controls (h={h})",
                      fname=f"panel_jointF_neglogp_h{h}.png",
                      cmap="rocket", fmt=".2f")
        heatmap_panel(-np.log10(panel_joint_p_f).replace([np.inf, -np.inf], np.nan),
                      title=f"[Filtered] Joint F-test (−log10 p) (h={h})",
                      fname=f"panel_jointF_neglogp_filtered_h{h}.png",
                      cmap="rocket", fmt=".2f")