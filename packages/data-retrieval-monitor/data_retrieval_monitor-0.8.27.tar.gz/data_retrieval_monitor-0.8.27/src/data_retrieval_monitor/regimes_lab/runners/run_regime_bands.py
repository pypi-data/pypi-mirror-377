# regimes_lab/runners/run_regime_bands.py
import numpy as np
import pandas as pd
from regimes_lab.data import prepare
from regimes_lab.regimes import load_or_build_labels
from regimes_lab.stats.viz import plot_cumret_bands

def main():
    R, IND, dates = prepare()
    L = load_or_build_labels(IND, split_tag="full")

    # choose a few representative factors (or all)
    for factor in R.columns[:5]:
        cumret = (R[factor]).cumsum().pipe(np.exp) - 1.0
        for model in L.columns:
            plot_cumret_bands(
                dates=R.index,
                series=cumret,
                labels=L[model],
                title=f"{factor} cumulative return — colored by {model}",
                fname=f"cumret_{factor}_{model}.png"
            )
    print("[bands] Done. See output2/stats/figures/")

if __name__ == "__main__":
    main()