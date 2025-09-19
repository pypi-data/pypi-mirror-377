# analytics/regimes_lab/stats/testpanel.py
import numpy as np
import pandas as pd
import statsmodels.api as sm

# ---------- DESIGN MATRIX BUILDER ----------

def build_design(X: pd.DataFrame, L: pd.DataFrame,
                 selected_cols_train: list[str] | None = None,
                 keep_models: list[str] | None = None,
                 add_const: bool = False) -> pd.DataFrame:
    # as in the patch I sent earlier
    """
    Build a design: [indicators X] + [dummies from ALL (or a subset of) label columns L].
    - X : lagged indicators/features (already aligned to horizon)
    - L : labels DataFrame (each column is a model’s integer labels across time)
    - selected_cols_train : optional explicit list of dummy column names to keep (takes precedence)
    - keep_models : optional list of label column names or prefixes to include (e.g., ["gmm_raw","saint_knn"])
                    If None: include all label columns.
                    If a prefix is given and exact match not found, the first column starting with that prefix is used.
    - add_const : if True, add intercept column named "const"
    Returns a DataFrame indexed like X with indicator columns + dummy columns.
    """
    if X is None or X.empty:
        return pd.DataFrame(index=L.index if L is not None else None)

    parts = [X.copy()]

    # Decide which label columns to use
    if L is None or L.empty:
        Z = pd.concat(parts, axis=1)
        if add_const:
            Z.insert(0, "const", 1.0)
        return Z

    if keep_models is None:
        label_cols = list(L.columns)
    else:
        label_cols = []
        for key in keep_models:
            if key in L.columns:
                label_cols.append(key)
            else:
                # prefix fallback
                cand = next((c for c in L.columns if c.startswith(key)), None)
                if cand is not None:
                    label_cols.append(cand)

    # Build dummies from the chosen label columns
    for m in label_cols:
        lab = L[m].astype("Int64")  # allow NA
        D = pd.get_dummies(lab, prefix=f"{m}_R", dtype=int)
        parts.append(D)

    Z = pd.concat(parts, axis=1).reindex(X.index).fillna(0)

    # If caller provided an explicit list of columns to keep (e.g., chosen dummies),
    # respect that and drop any other dummy columns (but keep all X columns).
    if selected_cols_train is not None:
        keep = list(X.columns) + [c for c in Z.columns if c in selected_cols_train]
        keep = [c for c in keep if c in Z.columns]
        Z = Z[keep]

    if add_const and "const" not in Z.columns:
        Z.insert(0, "const", 1.0)

    return Z


# ---------- SIMPLE OLS (HAC) WRAPPER USED ELSEWHERE ----------
def ols_hac(y: pd.Series, X: pd.DataFrame, hac_lags: int = 5):
    """
    Convenience wrapper kept here for backwards compatibility (some modules import from testpanel).
    """
    X_ = sm.add_constant(X, has_constant="add")
    model = sm.OLS(y, X_, missing="drop")
    res = model.fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})
    return {
        "coefs": res.params,
        "tvals": res.tvalues,
        "pvals": res.pvalues,
        "r2": res.rsquared,
        "r2_adj": res.rsquared_adj,
        "aic": res.aic,
        "bic": res.bic,
        "resid": res.resid,
        "cov": res.cov_params(),
        "df_resid": res.df_resid,
        "X_cols": X_.columns,
    }