# regimes_lab/runners/run_single_split.py
from regimes_lab.data import prepare
from regimes_lab.regimes import load_or_build_labels, make_dummies
from regimes_lab.stats.testpanel import single_split_suite
from regimes_lab.configs import FORECAST_LAGS

def main():
    R, IND, dates = prepare()
    L = load_or_build_labels(IND, split_tag="full")
    D = make_dummies(L, full_index=R.index)
    single_split_suite(R, D, IND, horizons=FORECAST_LAGS, combine_significant_only=True)
    print("[single] Done. See output2/stats/{tables,figures}/")

if __name__ == "__main__":
    main()