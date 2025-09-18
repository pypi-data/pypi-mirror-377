# regimes_lab/runners/run_select_and_test.py
from regimes_lab.data import prepare
from regimes_lab.regimes import load_or_build_labels, make_dummies
from regimes_lab.configs import FORECAST_LAGS
from regimes_lab.stats.select_and_test import select_and_test_best_combination

def main():
    # Load aligned returns (R), indicators lagged +2 (IND), dates
    R, IND, _ = prepare()

    # Load or build regime labels, then build dummies over full index
    L = load_or_build_labels(IND, split_tag="full")
    D = make_dummies(L, full_index=R.index)

    # Run selection + significance tests
    select_and_test_best_combination(
        R=R, D=D, IND=IND,
        horizons=FORECAST_LAGS,
        alpha_sig=0.05,
        save_prefix="COMBINED_SELECTED"
    )
    print("[select_and_test] Done. See output/stats/tables/ for selections and full stats.")

if __name__ == "__main__":
    main()