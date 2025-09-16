# selector_rank_lambdamart.py
import os
import numpy as np, pandas as pd
from configs import SUBDIRS, ROLL_WINDOW
import lightgbm as lgb
LGB_OK = True


def _make_panel_features(returns_df: pd.DataFrame, X_features: pd.DataFrame):
    """
    Expand to panel (date, factor):
      - y: next-day return of that factor
      - X: join same X_features for all factors (plus factor dummies)
    """
    R = returns_df.copy()
    y_next = R.shift(-1)  # next-day realized
    # indicator & regime features (same across factors at time t)
    X = X_features.copy()

    # panelize
    df_list = []
    for f in R.columns:
        df = X.copy()
        df["factor"] = f
        df["y"] = y_next[f]
        df_list.append(df)
    panel = pd.concat(df_list, axis=0)
    # factor one-hot
    F = pd.get_dummies(panel["factor"], prefix="F", dtype=int)
    panel = pd.concat([panel.drop(columns=["factor"]), F], axis=1)
    return panel

def lambdamart_rank_rolling(returns_df: pd.DataFrame, X_features: pd.DataFrame):
    if not LGB_OK:
        print("[INFO] LightGBM not available, skipping LambdaMART.")
        return None
    panel = _make_panel_features(returns_df, X_features).dropna()
    # group by date (query)
    dates = panel.index
    uniq_dates = panel.index.unique()
    preds = []
    for i, d in enumerate(uniq_dates):
        # rolling train on previous ROLL_WINDOW dates
        past_dates = uniq_dates[max(0, i-ROLL_WINDOW):i]
        if len(past_dates) < 5:
            continue
        train = panel.loc[past_dates]
        test  = panel.loc[[d]]

        y_tr = train["y"].values
        X_tr = train.drop(columns=["y"]).values
        q_tr = train.index.value_counts().loc[past_dates].values  # group sizes per date

        model = lgb.LGBMRanker(
            objective="lambdarank", n_estimators=200, learning_rate=0.05,
            num_leaves=63, subsample=0.9, colsample_bytree=0.9, random_state=0
        )
        model.fit(X_tr, y_tr, group=q_tr)
        # predict scores for factors on date d
        X_te = test.drop(columns=["y"]).values
        score = model.predict(X_te)
        # find best factor for date d
        test_factors = [c.replace("F_", "") for c in test.filter(like="F_").columns]
        # argmax per factor block; but test rows are one per factor already, in the same order as get_dummies columns
        pick_idx = int(np.argmax(score))
        pick_factor = test_factors[pick_idx]
        realized = returns_df.loc[d, pick_factor] if d in returns_df.index else np.nan
        preds.append((d, pick_factor, float(realized)))
    if preds:
        out = pd.DataFrame(preds, columns=["date", "selected_factor", "realized_ret"]).set_index("date")
        out.to_csv(os.path.join(SUBDIRS["selectors"], "selector_lambdamart_choices.csv"))
        rets = out["realized_ret"].dropna()
        perf = {
            "count": int(rets.shape[0]),
            "mean_ann": float(rets.mean()*252),
            "vol_ann": float(rets.std()*(252**0.5)),
            "sharpe": float((rets.mean()/(rets.std()+1e-12))*(252**0.5)),
            "backend": "lambdamart",
        }
        pd.DataFrame([perf]).to_csv(os.path.join(SUBDIRS["selectors"], "selector_lambdamart_performance.csv"), index=False)
        return out
    return None