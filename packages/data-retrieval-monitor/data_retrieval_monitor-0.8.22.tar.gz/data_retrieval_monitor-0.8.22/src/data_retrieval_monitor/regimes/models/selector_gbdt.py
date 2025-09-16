# models/selector_gbdt.py
import os
import numpy as np
import pandas as pd
from configs import SUBDIRS, TRAIN_FRAC, VAL_FRAC

# Backends
try:
    import lightgbm as lgb
    LGB_OK = True
except Exception:
    LGB_OK = False

try:
    import xgboost as xgb
    XGB_OK = True
except Exception:
    XGB_OK = False

try:
    from catboost import CatBoostClassifier, Pool
    CAT_OK = True
except Exception:
    CAT_OK = False


def list_available_backends():
    backends = []
    if LGB_OK: backends.append("lightgbm")
    if XGB_OK: backends.append("xgboost")
    if CAT_OK: backends.append("catboost")
    return backends

def _as_frame(X, ref_index, ref_columns):
    if isinstance(X, pd.DataFrame): return X
    return pd.DataFrame(X, index=ref_index, columns=ref_columns)

def _train_backend(Xtr_df, ytr, backend):
    if backend == "lightgbm":
        model = lgb.LGBMClassifier(objective="multiclass", n_estimators=400, num_leaves=63,
                                   learning_rate=0.05, subsample=0.9, colsample_bytree=0.9,
                                   random_state=0)
        model.fit(Xtr_df, ytr)
        return model
    if backend == "xgboost":
        dtrain = xgb.DMatrix(Xtr_df.values, label=ytr, feature_names=[str(c) for c in Xtr_df.columns])
        params = {"objective": "multi:softprob",
                  "num_class": int(np.max(ytr))+1,
                  "max_depth": 7, "eta": 0.05, "subsample": 0.9, "colsample_bytree": 0.9,
                  "eval_metric": "mlogloss", "seed": 0}
        model = xgb.train(params, dtrain, num_boost_round=500)
        model._feature_names = [str(c) for c in Xtr_df.columns]
        return model
    if backend == "catboost":
        model = CatBoostClassifier(iterations=500, depth=7, learning_rate=0.05,
                                   loss_function="MultiClass", verbose=False, random_seed=0)
        model.fit(Xtr_df, ytr)
        return model
    return None

def _predict_backend(model, X_df, backend):
    if backend == "lightgbm":
        P = model.predict_proba(X_df)
        P = np.asarray(P)
        if P.ndim == 1:  # binary edge case
            P = np.column_stack([1 - P, P])
        return P
    if backend == "xgboost":
        dm = xgb.DMatrix(X_df.values, feature_names=getattr(model, "_feature_names", [str(c) for c in X_df.columns]))
        return np.asarray(model.predict(dm))
    if backend == "catboost":
        return np.asarray(model.predict_proba(Pool(X_df)))
    return None

def _evaluate_picks(returns_df, picks, start_offset):
    names = list(returns_df.columns)
    realized_idx = returns_df.index[start_offset + 1 : start_offset + 1 + len(picks)]
    realized_vals = []
    for i, d in enumerate(realized_idx):
        fidx = int(picks[i])
        if 0 <= fidx < len(names):
            realized_vals.append(returns_df.loc[d, names[fidx]])
        else:
            realized_vals.append(np.nan)
    return realized_idx, realized_vals, names

def gbdt_selector_rank_all(returns_df: pd.DataFrame, X_df: pd.DataFrame):
    """
    Train & evaluate ALL available GBDT backends.
    Writes:
      selectors/selector_gbdt_<backend>_choices.csv
      selectors/selector_gbdt_<backend>_performance.csv
      selectors/selector_gbdt_leaderboard.csv
    """
    backends = list_available_backends()
    if not backends:
        print("[INFO] No GBDT backend available — skipping GBDT selector.")
        return None

    # Align X with returns (features at t predict t+1 argmax)
    X_df = X_df.reindex(returns_df.index).copy()
    R = returns_df.copy()

    # Target classes from t+1 argmax (drop last row)
    y_factors = R.shift(-1).idxmax(axis=1).iloc[:-1]
    classes = {f: i for i, f in enumerate(R.columns)}
    y = y_factors.map(classes).values
    # Features at t (drop last row to align with y)
    X_all = X_df.iloc[:-1, :]
    X_all = _as_frame(X_all, X_all.index, X_all.columns)

    Tm1 = len(X_all)
    n_train = min(int(TRAIN_FRAC * len(R)), Tm1)
    idx_train = slice(0, n_train)
    idx_oos   = slice(n_train, Tm1)
    if (idx_oos.stop - idx_oos.start) <= 0:
        print("[INFO] Not enough OOS samples for GBDT selector.")
        return None

    leaderboard = []
    for be in backends:
        Xtr_df = X_all.iloc[idx_train, :]
        ytr    = y[idx_train]
        Xoos_df = X_all.iloc[idx_oos, :]

        model = _train_backend(Xtr_df, ytr, be)
        if model is None:
            print(f"[INFO] Training failed for {be}")
            continue

        P = _predict_backend(model, Xoos_df, be)
        if P is None or P.ndim != 2:
            print(f"[INFO] Prediction failed for {be}")
            continue

        picks = P.argmax(axis=1)
        realized_idx, realized_vals, names = _evaluate_picks(returns_df, picks, start_offset=n_train)

        # save choices
        out = pd.DataFrame(
            {
                "selected_factor": [names[int(c)] if 0 <= int(c) < len(names) else None for c in picks],
                "realized_ret": realized_vals,
            },
            index=realized_idx,
        )
        out.index.name = "date"
        out.to_csv(os.path.join(SUBDIRS["selectors"], f"selector_gbdt_{be}_choices.csv"))

        # performance
        rets = pd.Series(realized_vals, index=realized_idx).dropna()
        perf = {
            "backend": be,
            "count": int(rets.shape[0]),
            "mean_ann": float(rets.mean() * 252),
            "vol_ann":  float(rets.std() * (252 ** 0.5)),
            "sharpe":   float((rets.mean() / (rets.std() + 1e-12)) * (252 ** 0.5)),
        }
        pd.DataFrame([perf]).to_csv(os.path.join(SUBDIRS["selectors"], f"selector_gbdt_{be}_performance.csv"), index=False)
        leaderboard.append(perf)

    if leaderboard:
        lb = pd.DataFrame(leaderboard).sort_values("sharpe", ascending=False)
        lb.to_csv(os.path.join(SUBDIRS["selectors"], "selector_gbdt_leaderboard.csv"), index=False)
    return None