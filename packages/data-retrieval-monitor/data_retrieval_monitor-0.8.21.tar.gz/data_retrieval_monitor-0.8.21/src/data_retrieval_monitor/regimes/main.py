# main.py
import numpy as np, pandas as pd, os
from configs import SUBDIRS, OUTPUT_DIR, SEED, RECURSIVE_ESTIMATION
from data import prepare_data, tvt_slices
from utils import infer_periods_per_year
from regimes import build_all_regimes
from changepoints import cpd_all
from alignment import align_cpd_to_regimes
from stats import build_designs, run_ols_panel, run_statistical_tests_subset
from viz_utils import plot_all_timelines
from selector import selector_best_factor
# from models.selector_gbdt import gbdt_selector_rank
from perf import compute_regime_perf_split
from models.selector_gbdt import gbdt_selector_rank_all
from stats import plot_significance_annotated

def main():
    np.random.seed(SEED)
    returns_aligned, indicators_aligned, X_all, dates = prepare_data()
    T = len(X_all); idx_train, idx_val, idx_test = tvt_slices(T)
    n_train = idx_train.stop; n_val = idx_val.stop - idx_val.start
    train_slice = idx_train
    test_slice  = slice(n_train + n_val, T)

    ann_factor = infer_periods_per_year(returns_aligned.index)
    print(f"[MODE] Recursive estimation = {RECURSIVE_ESTIMATION}")

    # ---------- Regimes ----------
    X_train = X_all[idx_train]
    regimes_df = build_all_regimes(X_train, X_all, dates, returns_aligned)

    # ---------- CPD + Alignment ----------
    cpd_labels = cpd_all(X_all, n_bkps=6)
    if cpd_labels:
        for name, lab in cpd_labels.items():
            regimes_df[name] = lab
    aligned_df = align_cpd_to_regimes(cpd_labels, regimes_df)
    for col in aligned_df.columns:
        regimes_df[col] = aligned_df[col]

    regimes_df.to_csv(os.path.join(SUBDIRS["regimes"], "regimes_by_model.csv"))

    # ---------- Train/Test clusters export ----------
    regimes_df.iloc[train_slice].to_csv(os.path.join(SUBDIRS["regimes"], "train_clusters.csv"))
    regimes_df.iloc[test_slice].to_csv(os.path.join(SUBDIRS["regimes"], "test_clusters.csv"))
    print("[Clusters] Saved to regimes/")

    # ---------- Selector (rule-based) ----------
    selection = selector_best_factor(returns_aligned, regimes_df)

    # ---------- GBDT Selector (ranking to top pick) ----------
    from stats import build_designs
    X_clusters_only, X_full = build_designs(returns_aligned, indicators_aligned, regimes_df, interactions=True)
    _ = gbdt_selector_rank_all(returns_aligned, X_full)

    # ---------- Per-regime stats (ALL models) — TRAIN vs TEST ----------
    compute_regime_perf_split(returns_aligned, regimes_df, train_slice, test_slice)

    # ---------- OLS (full) ----------
    coefs2, tstats2, pvals2, fits2 = run_ols_panel(returns_aligned, X_full, ann_factor,
                                                   prefix="ols_indicators_regimes_interactions")

    # ---------- Subset statistical test example ----------
    # You can pick any subset of dummy prefixes, e.g., only aligned CPD:
    aligned_prefixes = [c + "_R" for c in regimes_df.columns if c.endswith("_aligned")]
    if len(aligned_prefixes):
         co_s, ts_s, pv_s, ft_s  = run_statistical_tests_subset(returns_aligned, indicators_aligned, regimes_df,
                                         subset_dummy_prefixes=aligned_prefixes,
                                         interactions=True,
                                         prefix="ols_subset_aligned")
    # co_s, ts_s, pv_s, ft_s = run_statistical_tests_subset(returns_aligned, indicators_aligned, regimes_df,
    #                                      subset_dummy_prefixes=aligned_prefixes, prefix="ols_subset_aligned")
    plot_significance_annotated(co_s, pv_s, alpha=0.05, coef_quantile=0.75,
                                fname=os.path.join(SUBDIRS["stat_tests"], "ols_subset_aligned_significance_annotated"))
    # ---------- Visuals ----------
    plot_all_timelines(regimes_df)
    print(f"Done. Outputs saved under: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    main()