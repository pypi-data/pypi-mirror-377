import os, re, json
import numpy as np
import pandas as pd

from regimes_lab.data import prepare
from regimes_lab.regimes import load_or_build_labels
from regimes_lab.stats.viz_shift import (
    plot_cumret_with_shifted_regime,
    plot_cumret_with_multi_model_rasters,
)
from regimes_lab.splitters import future_sum_returns
from regimes_lab.configs import STATS_TAB_DIR, STATS_FIG_DIR, TRAIN_FRAC, VAL_FRAC

def _find_selected_jsons(prefix="COMBINED_SELECTED_SELECTED_"):
    files = [f for f in os.listdir(STATS_TAB_DIR) if f.startswith(prefix) and f.endswith(".json")]
    files.sort()
    return [os.path.join(STATS_TAB_DIR, f) for f in files]

def _parse_factor_h(base: str):
    m = re.match(r"^COMBINED_SELECTED_SELECTED_(.+?)_h(\d+)\.json$", base)
    if not m:
        return base, 1
    return m.group(1), int(m.group(2))

def _parse_keep_map(dummy_cols: list[str]) -> dict[str, set[int]]:
    keep = {}
    for c in dummy_cols:
        if "_R" not in c:
            continue
        mname, rid = c.split("_R", 1)
        try:
            rid = int(rid)
        except Exception:
            continue
        keep.setdefault(mname, set()).add(rid)
    return keep

def _resolve_label_columns(L: pd.DataFrame, keep_by_model: dict[str, set[int]]) -> tuple[dict, dict]:
    """
    Map dummy prefixes (e.g., 'bayesgmm') to the actual label column in L.
    Strategy: exact match, else best prefix match (first col that startswith prefix).
    Returns (labels_by_model, keep_by_model_aligned).
    """
    labels_by_model = {}
    resolved_keep = {}
    cols = list(L.columns)
    for key, keep_ids in keep_by_model.items():
        chosen = None
        if key in L.columns:
            chosen = key
        else:
            # prefix match
            for c in cols:
                if c.startswith(key):
                    chosen = c
                    break
        if chosen is None:
            # could not find; skip with notice
            print(f"[shifted_bands] WARN: could not resolve model '{key}' to any label column; skipping.")
            continue
        labels_by_model[chosen] = L[chosen]
        resolved_keep[chosen] = keep_ids
    return labels_by_model, resolved_keep

def _split_date_for_factor_h(R: pd.DataFrame, factor: str, h: int) -> pd.Timestamp | None:
    """Compute the train/test cut used for this (factor, h) based on support."""
    y = future_sum_returns(R, h)[factor].dropna()
    if y.empty:
        return None
    idx = y.index
    T = len(idx)
    n_tr = int(TRAIN_FRAC * T)
    n_va = int(VAL_FRAC * T)
    te_start = n_tr + n_va
    if te_start <= 0 or te_start >= T:
        return None
    return idx[te_start]  # first test timestamp

def main():
    R, IND, dates = prepare()
    L = load_or_build_labels(IND, split_tag="full")  # columns = model label series

    os.makedirs(STATS_FIG_DIR, exist_ok=True)
    sel_paths = _find_selected_jsons()

    if sel_paths:
        for path in sel_paths:
            base = os.path.basename(path)
            factor, h = _parse_factor_h(base)
            with open(path, "r") as fh:
                payload = json.load(fh)
            chosen = payload.get("chosen_dummies", [])
            keep_raw = _parse_keep_map(chosen)

            # resolve model names to L columns
            labels_by_model, keep_by_model = _resolve_label_columns(L, keep_raw)

            # cumret
            cum = (R[factor]).cumsum().pipe(np.exp) - 1.0
            split_date = _split_date_for_factor_h(R, factor, h)

            # multi-model raster (only selected regimes colored)
            plot_cumret_with_multi_model_rasters(
                dates=R.index,
                cumret=cum,
                labels_by_model=labels_by_model if labels_by_model else {m: L[m] for m in L.columns},
                horizon=h,
                title=f"{factor} — cumulative return with shifted regimes (h={h})",
                fname=f"cumret_multi_{factor}_h{h}.png",
                keep_by_model=keep_by_model if labels_by_model else None,
                split_date=split_date,
            )

            # single-model bands for each resolved model
            for m, lab in (labels_by_model if labels_by_model else {m: L[m] for m in L.columns}).items():
                keep_ids = keep_by_model.get(m, None) if labels_by_model else None
                plot_cumret_with_shifted_regime(
                    dates=R.index,
                    cumret=cum,
                    labels=lab,
                    horizon=h,
                    model_name=m,
                    title=f"{factor} — cumulative return (h={h})",
                    fname=f"cumret_{factor}_{m}_h{h}.png",
                    keep_regimes=keep_ids,
                    split_date=split_date,
                )
        print("[shifted_bands] Done. See output2/stats/figures/")
    else:
        # fallback: first few factors at h=1, no filtering
        for factor in R.columns[:5]:
            cum = (R[factor]).cumsum().pipe(np.exp) - 1.0
            split_date = _split_date_for_factor_h(R, factor, 1)
            labels_by_model = {m: L[m] for m in L.columns}
            plot_cumret_with_multi_model_rasters(
                dates=R.index, cumret=cum, labels_by_model=labels_by_model,
                horizon=1, title=f"{factor} — cumulative return with shifted regimes (h=1)",
                fname=f"cumret_multi_{factor}_h1.png", keep_by_model=None, split_date=split_date,
            )
        print("[shifted_bands] No selection JSONs found; produced default h=1 multi-model plots.")

if __name__ == "__main__":
    main()