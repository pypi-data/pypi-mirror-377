# selector_conformal.py
import os, numpy as np, pandas as pd
from numpy.linalg import lstsq
from configs import SUBDIRS, ROLL_WINDOW

def _design_simple(X_features: pd.DataFrame):
    # add const; X_features already has indicators + dummies
    X = X_features.copy()
    if "const" not in X.columns:
        X = pd.concat([pd.Series(1.0, index=X.index, name="const"), X], axis=1)
    return X

def conformal_selector_rolling(returns_df: pd.DataFrame, X_features: pd.DataFrame):
    """
    Rolling split: for each date t, fit baseline linear model on [t-W..t-1],
    compute calibration residual distribution, then compute p-values for each
    factor at t based on its predicted error vs calibration residuals.
    Pick factor with highest p-value (smallest expected error).
    """
    X = _design_simple(X_features).reindex(returns_df.index)
    R = returns_df.copy()
    uniq_dates = X.index

    picks = []
    pval_records = []
    for i, d in enumerate(uniq_dates):
        if i < ROLL_WINDOW: continue
        tr_idx = uniq_dates[i-ROLL_WINDOW:i]
        te_idx = d

        Xtr = X.loc[tr_idx].values
        # For each factor, fit same coefs (common beta); multiple targets -> independent fits
        # We'll fit per-factor to keep it simple.
        for_factors = []
        for f in R.columns:
            ytr = R.loc[tr_idx, f].values
            # fit beta via least squares
            beta, *_ = lstsq(Xtr, ytr, rcond=None)
            # calibration residuals (absolute)
            yhat_tr = Xtr @ beta
            cal = np.abs(ytr - yhat_tr)
            # test score
            xt = X.loc[[te_idx]].values[0]
            yhat_t = float(xt @ beta)
            # we don't know y_{t}, but for p-values ranking we can use |yhat_t| (proxy risk) or use scores to rank;
            # Proper CP would need candidate labels; here we produce p-values by comparing |yhat_t| against calibration
            pval = float((cal >= np.abs(yhat_t)).mean()) if cal.size else 0.0
            pval_records.append((d, f, pval))
            for_factors.append((f, pval, yhat_t))

        # pick factor with highest p-value (tie -> highest yhat)
        if for_factors:
            for_factors.sort(key=lambda x: (x[1], x[2]), reverse=True)
            best_f = for_factors[0][0]
            realized = R.loc[d, best_f]
            picks.append((d, best_f, float(realized)))

    if picks:
        out = pd.DataFrame(picks, columns=["date","selected_factor","realized_ret"]).set_index("date")
        out.to_csv(os.path.join(SUBDIRS["selectors"], "selector_conformal_choices.csv"))
        rets = out["realized_ret"].dropna()
        perf = {
            "count": int(rets.shape[0]),
            "mean_ann": float(rets.mean()*252),
            "vol_ann":  float(rets.std()*(252**0.5)),
            "sharpe":   float((rets.mean()/(rets.std()+1e-12))*(252**0.5)),
            "backend": "conformal_residual",
        }
        pd.DataFrame([perf]).to_csv(os.path.join(SUBDIRS["selectors"], "selector_conformal_performance.csv"), index=False)

    if pval_records:
        pdf = pd.DataFrame(pval_records, columns=["date","factor","pval"]).set_index("date")
        pdf.to_csv(os.path.join(SUBDIRS["selectors"], "selector_conformal_pvals.csv"))