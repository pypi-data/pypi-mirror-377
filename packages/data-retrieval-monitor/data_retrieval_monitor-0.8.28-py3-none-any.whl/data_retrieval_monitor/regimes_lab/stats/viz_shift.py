import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import ListedColormap
from matplotlib import gridspec
from .viz import _savefig

def _palette(K: int):
    base = plt.get_cmap("tab10")
    return [base(i % 10) for i in range(max(1, K))]

def shift_labels_for_horizon(labels: pd.Series, h: int, full_index: pd.DatetimeIndex) -> pd.Series:
    lab = pd.Series(labels).copy()
    return lab.shift(h).reindex(full_index)

def _mask_to_keep(lab: pd.Series, keep_ids: set[int] | None) -> pd.Series:
    if not keep_ids:
        return lab
    m = lab.copy()
    m[~m.isin(list(keep_ids))] = np.nan
    return m

def _raster_extent(idx: pd.DatetimeIndex):
    return [mdates.date2num(idx[0]), mdates.date2num(idx[-1]), 0.0, 1.0]

def _draw_raster(ax, labels: pd.Series, title: str | None):
    vals = labels.to_numpy(dtype=float)              # keep NaNs
    finite = vals[np.isfinite(vals)]
    K = int(finite.max()) + 1 if finite.size else 1
    # masked array so NaNs are transparent
    arr = np.ma.masked_invalid(vals.reshape(1, -1))
    cmap = ListedColormap(_palette(K))
    cmap.set_bad((1, 1, 1, 0.0))
    ax.imshow(arr, aspect="auto", cmap=cmap, vmin=-0.5, vmax=K-0.5,
              extent=_raster_extent(labels.index))
    ax.set_yticks([])
    if title:
        ax.set_ylabel(title, rotation=0, labelpad=40, ha="right", va="center", fontsize=9)
    for s in ax.spines.values():
        s.set_visible(False)

def _draw_split(ax, split_date: pd.Timestamp | None):
    if split_date is None:
        return
    x = mdates.date2num(split_date)
    ax.axvline(x, color="k", linestyle="--", linewidth=1.2, alpha=0.85)
    ymax = ax.get_ylim()[1]
    ax.text(x, ymax, " train→test ", ha="left", va="top", fontsize=9,
            bbox=dict(fc="white", ec="none", alpha=0.65, pad=1.5), color="k")

def plot_cumret_with_shifted_regime(
    dates: pd.DatetimeIndex,
    cumret: pd.Series,
    labels: pd.Series,
    horizon: int,
    model_name: str,
    title: str,
    fname: str,
    alpha: float = 0.18,
    keep_regimes: set[int] | None = None,
    split_date: pd.Timestamp | None = None,
):
    s = pd.Series(cumret).reindex(dates).dropna()
    if s.empty:
        plt.figure(figsize=(12, 4), constrained_layout=True)
        plt.title(f"{title}\n(model={model_name}) — no data")
        _savefig(fname); return

    lab_sh = shift_labels_for_horizon(labels, horizon, dates)
    lab_sh = _mask_to_keep(lab_sh, keep_regimes).reindex(s.index)

    fig = plt.figure(figsize=(12.5, 4.3), constrained_layout=True)
    ax = fig.add_subplot(1,1,1)
    ax.plot(s.index, s.values, lw=1.7, color="black", zorder=10)
    # shade bands per step where label is finite
    t = s.index.view("int64")
    if len(t) > 1:
        mids = (t[:-1] + t[1:]) // 2
        left, right = t[0] - (mids[0] - t[0]), t[-1] + (t[-1] - mids[-1])
        edges = np.concatenate([[left], mids, [right]])
        edges = pd.to_datetime(edges, unit="ns")
        colors = _palette(int(np.nanmax(lab_sh.values)) + 1 if np.isfinite(lab_sh.values).any() else 1)
        rvals = lab_sh.to_numpy()
        for k in range(len(rvals)):
            v = rvals[k]
            if np.isfinite(v):
                ax.axvspan(edges[k], edges[k+1], facecolor=colors[int(v)], alpha=alpha, linewidth=0)

    _draw_split(ax, split_date)
    ax.set_title(f"{title}\n(model={model_name}, labels shifted by +{horizon})", fontsize=12)
    ax.grid(axis="y", alpha=0.25)
    fig.autofmt_xdate()
    _savefig(fname)

def plot_cumret_with_multi_model_rasters(
    dates: pd.DatetimeIndex,
    cumret: pd.Series,
    labels_by_model: dict,
    horizon: int,
    title: str,
    fname: str,
    raster_height: float = 0.42,
    keep_by_model: dict | None = None,
    split_date: pd.Timestamp | None = None,
):
    s = pd.Series(cumret).reindex(dates).dropna()
    if s.empty:
        plt.figure(figsize=(12, 3), constrained_layout=True)
        plt.title(f"{title} — no data")
        _savefig(fname); return

    n_models = len(labels_by_model)
    fig_h = 4.0 + n_models * raster_height
    fig = plt.figure(figsize=(13.0, fig_h), constrained_layout=True)
    gs = gridspec.GridSpec(n_models + 1, 1, height_ratios=[3.0] + [raster_height]*n_models, hspace=0.05)

    ax0 = fig.add_subplot(gs[0, 0])
    ax0.plot(s.index, s.values, lw=1.7, color="black")
    ax0.grid(axis="y", alpha=0.25)
    _draw_split(ax0, split_date)
    ax0.set_title(f"{title}\n(labels shifted by +{horizon})", fontsize=12)

    for i, (model_name, lab) in enumerate(labels_by_model.items(), start=1):
        keep_ids = keep_by_model.get(model_name) if keep_by_model else None
        lab_sh = shift_labels_for_horizon(pd.Series(lab), horizon, dates)
        lab_sh = _mask_to_keep(lab_sh, keep_ids).reindex(s.index)
        ax = fig.add_subplot(gs[i, 0], sharex=ax0)
        _draw_raster(ax, lab_sh, title=model_name)
        if i < n_models:
            ax.set_xticklabels([])
        ax.tick_params(axis="x", which="both", length=0)

    fig.autofmt_xdate()
    _savefig(fname)