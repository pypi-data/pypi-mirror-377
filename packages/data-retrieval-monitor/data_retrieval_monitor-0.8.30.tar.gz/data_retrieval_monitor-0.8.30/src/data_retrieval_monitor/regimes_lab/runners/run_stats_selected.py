import os, json, numpy as np, pandas as pd, matplotlib.pyplot as plt
from regimes_lab.data import prepare
from regimes_lab.regimes import load_or_build_labels
from regimes_lab.splitters import future_sum_returns
from regimes_lab.configs import (STATS_TAB_DIR, STATS_FIG_DIR, DEFAULT_HORIZONS, TRAIN_FRAC, VAL_FRAC, SELECTOR)
from regimes_lab.stats.ols_arma import ols_hac, glsar_iter, ols_arima_errors, joint_wald_test, residual_diagnostics

def _find_selected_jsons():
    files = [f for f in os.listdir(STATS_TAB_DIR) if f.startswith("COMBINED_SELECTED_SELECTED_") and f.endswith(".json")]
    files.sort()
    return [os.path.join(STATS_TAB_DIR, f) for f in files]

def _split_idx(idx):
    T=len(idx); ntr=int(TRAIN_FRAC*T); nva=int(VAL_FRAC*T)
    return slice(0,ntr+nva), slice(ntr+nva,T)

def _build_design(X, L, chosen):
    parts=[X]
    models=set(c.split("_R")[0] for c in chosen if "_R" in c)
    for m in models:
        m_real = m if m in L.columns else next((c for c in L.columns if c.startswith(m)), None)
        if m_real is None: continue
        D = pd.get_dummies(L[m_real].astype(int), prefix=f"{m_real}_R", dtype=int)
        keep=[c for c in D.columns if c in chosen]
        if keep: parts.append(D[keep])
    return pd.concat(parts,axis=1).fillna(0)

def _save_table(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True); df.to_csv(path)

def _barplot_params_tstats(coefs, tvals, title, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    idx = list(coefs.index)
    fig, ax1 = plt.subplots(figsize=(12,5))
    ax1.bar(idx, coefs.values, alpha=0.6); ax1.set_ylabel("Coefficient")
    ax1.set_xticklabels(idx, rotation=60, ha="right"); ax1.set_title(title)
    ax2 = ax1.twinx(); ax2.plot(idx, tvals.values, marker="o"); ax2.set_ylabel("t-stat")
    fig.tight_layout(); plt.savefig(path, dpi=140); plt.close(fig)

def main():
    os.makedirs(STATS_TAB_DIR, exist_ok=True); os.makedirs(STATS_FIG_DIR, exist_ok=True)
    hac_lags = SELECTOR.get("HAC_LAGS", 5)
    sels = _find_selected_jsons()
    if not sels:
        print("[stats] No selection JSONs. Run auto_select_regimes first."); return

    for sel in sels:
        with open(sel,"r") as fh: payload=json.load(fh)
        factor = payload["factor"]; h=int(payload["horizon"]); chosen=payload.get("chosen_dummies",[])
        R, IND, X_by_h = prepare([h]); X_h,_ = X_by_h[h]; L = load_or_build_labels(X_h, split_tag="full", h=h)

        y = future_sum_returns(R,h)[factor].dropna()
        X = X_h.reindex(y.index).dropna(); L = L.reindex(X.index); y = y.reindex(L.index)
        tr, te = _split_idx(y.index)
        Z = _build_design(X, L, chosen)
        if Z.empty: print(f"[stats] WARN empty design for {factor}, h={h}"); continue

        base = f"{factor}_h{h}"

        # TRAIN OLS-HAC
        res_tr = ols_hac(y.iloc[tr], Z.iloc[tr], maxlags=hac_lags)
        _save_table(pd.DataFrame({"coef_train":res_tr["coefs"], "t_train":res_tr["tvals"], "p_train":res_tr["pvals"]}),
                    os.path.join(STATS_TAB_DIR, f"ols_hac_train_{base}.csv"))

        # TEST OLS-HAC
        res_te = ols_hac(y.iloc[te], Z.iloc[te], maxlags=hac_lags)
        _save_table(pd.DataFrame({"coef_test":res_te["coefs"], "t_test":res_te["tvals"], "p_test":res_te["pvals"]}),
                    os.path.join(STATS_TAB_DIR, f"ols_hac_test_{base}.csv"))

        # TEST GLSAR + SARIMAX(ARMA)
        res_gls = glsar_iter(y.iloc[te], Z.iloc[te].drop(columns=["const"], errors="ignore"), order=1, iters=8)
        _save_table(pd.DataFrame({"coef_test":res_gls["coefs"], "t_test":res_gls["tvals"], "p_test":res_gls["pvals"]}),
                    os.path.join(STATS_TAB_DIR, f"glsar_test_{base}.csv"))

        res_arma = ols_arima_errors(y.iloc[te], Z.iloc[te].drop(columns=["const"], errors="ignore"), ar=1, ma=1)
        _save_table(pd.DataFrame({"coef_test":res_arma["coefs"], "t_test":res_arma["tvals"], "p_test":res_arma["pvals"]}),
                    os.path.join(STATS_TAB_DIR, f"ols_arma_test_{base}.csv"))

        # Joint Wald test (OLS-HAC) for selected dummies on TEST
        dummy_cols = [c for c in Z.columns if "_R" in c]
        wald = joint_wald_test(res_te, dummy_cols)
        if wald is not None:
            with open(os.path.join(STATS_TAB_DIR, f"joint_wald_test_{base}.txt"),"w") as fh:
                fh.write(str(wald))

        # Residual diagnostics (decide validity)
        diag = residual_diagnostics(res_te["resid"], name=f"ols_hac_test_{base}",
                                    out_dir=os.path.join(STATS_FIG_DIR,"diagnostics"), lags=24)
        with open(os.path.join(STATS_TAB_DIR, f"diagnostics_valid_{base}.json"),"w") as fh:
            json.dump(diag, fh, indent=2)

        # Figures
        _barplot_params_tstats(
            res_te["coefs"].reindex(Z.columns, fill_value=np.nan),
            res_te["tvals"].reindex(Z.columns, fill_value=np.nan),
            title=f"{factor} h={h} — OLS(HAC) TEST",
            path=os.path.join(STATS_FIG_DIR, f"ols_hac_test_{base}.png")
        )
        _barplot_params_tstats(
            res_gls["coefs"].reindex(res_gls["coefs"].index, fill_value=np.nan),
            res_gls["tvals"].reindex(res_gls["tvals"].index, fill_value=np.nan),
            title=f"{factor} h={h} — GLSAR TEST",
            path=os.path.join(STATS_FIG_DIR, f"glsar_test_{base}.png")
        )
        _barplot_params_tstats(
            res_arma["coefs"].reindex(res_arma["coefs"].index, fill_value=np.nan),
            res_arma["tvals"].reindex(res_arma["tvals"].index, fill_value=np.nan),
            title=f"{factor} h={h} — OLS(ARMA errors) TEST",
            path=os.path.join(STATS_FIG_DIR, f"ols_arma_test_{base}.png")
        )

        print(f"[stats] DONE {factor} h={h}")

if __name__ == "__main__":
    main()