# regimes_lab/runners/run_rolling.py
from regimes_lab.data import prepare
from regimes_lab.regimes import load_or_build_labels, make_dummies
from regimes_lab.stats.rolling_timeseries import rolling_timeseries_suite
from regimes_lab.configs import FORECAST_LAGS

def main():
    R, IND, _ = prepare()
    # For rolling/recursive *regression* diagnostics we just need a dummy matrix aligned to R
    L = load_or_build_labels(IND, split_tag="full")  # labels on full IND; no leakage in regression testing
    D = make_dummies(L, full_index=R.index)
    models = sorted(set(c.split("_R")[0] for c in D.columns)) + ["COMBINED"]
    rolling_timeseries_suite(R, D, IND, horizons=FORECAST_LAGS, models=models, top_k_per_model=8)
    print("[rolling] Done. See output2/stats/{tables,figures}/")

if __name__ == "__main__":
    main()