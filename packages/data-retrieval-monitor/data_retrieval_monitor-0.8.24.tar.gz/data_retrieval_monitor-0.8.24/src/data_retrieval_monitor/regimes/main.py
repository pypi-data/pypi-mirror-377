# main.py
import os, numpy as np, pandas as pd
from configs import SUBDIRS, OUTPUT_DIR, SEED, TRAIN_FRAC, VAL_FRAC
from data import prepare_data, tvt_slices
from utils import infer_periods_per_year
# main.py (top of file)
from regimes_rolling import rolling_regimes
from perf import compute_regime_perf_split
from stats import run_ols_per_model

# Optional selectors (retain your previous imports if needed)
from selector_rank_lambdamart import lambdamart_rank_rolling
from selector_saint import saint_selector_rolling
from selector_conformal import conformal_selector_rolling
from stats import build_indicator_sign_dummies  # if you need sign dummies elsewhere

def main():
    np.random.seed(SEED)

    # Data (returns_aligned already no-look-ahead; indicators lagged +2BD inside your data prep)
    returns_aligned, indicators_aligned, X_all, dates = prepare_data()

    T = len(X_all)
    idx_train, idx_val, idx_test = tvt_slices(T)
    n_train = idx_train.stop
    n_val = idx_val.stop - idx_val.start
    train_slice = idx_train
    test_slice  = slice(n_train + n_val, T)

    # ---------------- Rolling regimes across many variants ----------------
    regimes_df = rolling_regimes(X_all, dates)
    regimes_df.to_csv(os.path.join(SUBDIRS["regimes"], "regimes_by_model.csv"))

    # ---------------- Train vs Test performance (split/metric folders) ----------------
    compute_regime_perf_split(returns_aligned, regimes_df, train_slice, test_slice)

    # ---------------- Selectors (optional; all rolling) ----------------
    # Build features = indicators + (optionally) regime dummies of all models
    # For ranking selectors, we keep it simple: indicators only; you can concatenate any regime dummies you like.
    X_features = indicators_aligned.copy()
    # Example: add sign dummies (optional)
    X_features = pd.concat([X_features, build_indicator_sign_dummies(indicators_aligned)], axis=1)

    # LambdaMART rolling ranker
    _ = lambdamart_rank_rolling(returns_aligned, X_features)
    # SAINT-style tiny MLP selector (skips if torch not present)
    _ = saint_selector_rolling(returns_aligned, X_features, epochs=10, lr=1e-3)
    # Conformal (residual-based)
    _ = conformal_selector_rolling(returns_aligned, X_features)

    # ---------------- Statistical tests per model ----------------
    # For each regime model column: returns ~ lagged indicators (+ sign dummies) + that model's dummies
    run_ols_per_model(returns_aligned, indicators_aligned, regimes_df, include_sign_dummies=True, with_interactions=False)

    print(f"Done. Outputs saved under: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    main()