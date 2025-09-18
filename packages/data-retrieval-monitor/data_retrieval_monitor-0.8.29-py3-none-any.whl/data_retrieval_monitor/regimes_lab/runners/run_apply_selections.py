# regimes_lab/runners/run_apply_selections.py
from regimes_lab.data import prepare
from regimes_lab.regimes import load_or_build_labels, make_dummies
from regimes_lab.stats.apply_selections import apply_and_test_all_selections

def main():
    # Load aligned returns (R), indicators lagged +2 (IND)
    R, IND, _ = prepare()

    # If you already have cached labels/dummies, this just rebuilds the dummy frame aligned to R.index
    L = load_or_build_labels(IND, split_tag="full")
    D = make_dummies(L, full_index=R.index)

    # Read all selection JSONs and run statsmodels tests; write tables & text reports
    apply_and_test_all_selections(R=R, D=D, IND=IND)

    print("[apply selections] Done. See output2/stats/tables/ for CSVs and .txt summaries.")

if __name__ == "__main__":
    main()