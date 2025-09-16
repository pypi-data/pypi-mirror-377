# utils.py
import os, math, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import ListedColormap
from configs import OUTPUT_DIR

def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()

def infer_periods_per_year(dates_index: pd.DatetimeIndex) -> int:
    if len(dates_index) < 3:
        return 252
    diffs = np.diff(dates_index.values.astype("datetime64[ns]")).astype("timedelta64[D]").astype(int)
    median_days = np.median(diffs)
    if median_days <= 2: return 252
    elif median_days <= 10: return 52
    elif median_days <= 40: return 12
    else: return 1

def annualized_stats(returns_df: pd.DataFrame, ann_factor: int) -> dict:
    mu = returns_df.mean() * ann_factor
    vol = returns_df.std() * math.sqrt(ann_factor)
    sharpe = (returns_df.mean() / returns_df.std()) * math.sqrt(ann_factor)
    return {"mean": mu, "vol": vol, "sharpe": sharpe}

def save_table(df: pd.DataFrame, name: str):
    path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    df.to_csv(path)
    return path

def _regime_palette(n):
    base = plt.get_cmap("tab10")
    return [base(i % 10) for i in range(max(1, n))]

def professional_heatmap(df, title, fname=None, fmt=".2%", center_zero=True, cbar_label=None):
    values = df.values.astype(float)
    if center_zero:
        vmax = np.nanmax(np.abs(values)); vmin = -vmax; cmap = "coolwarm"
    else:
        vmin, vmax = np.nanmin(values), np.nanmax(values); cmap = "viridis"
    fig_h = max(3.8, 0.34 * len(df))
    fig, ax = plt.subplots(figsize=(11, fig_h))
    im = ax.imshow(values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(np.arange(values.shape[1]+1)-0.5, minor=True)
    ax.set_yticks(np.arange(values.shape[0]+1)-0.5, minor=True)
    ax.grid(which="minor", color="w", linestyle="-", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.set_xticks(np.arange(values.shape[1]))
    ax.set_yticks(np.arange(values.shape[0]))
    ax.set_xticklabels(df.columns, rotation=0)
    ax.set_yticklabels(df.index)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            val = values[i, j]
            try: txt = format(val, fmt)
            except: txt = f"{val:.2f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8, color="black")
    formatter = FuncFormatter(lambda x, pos: f"{x*100:.0f}%") if "%" in fmt else None
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, format=formatter)
    if cbar_label: cbar.set_label(cbar_label)
    ax.set_title(title, fontsize=13, fontweight="bold")
    for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout()
    if fname: plt.savefig(os.path.join(OUTPUT_DIR, f"{fname}.png"), dpi=160, bbox_inches="tight")
    plt.close()

def plot_timeline_chunked(labels, dates, title="Regimes Through Time", n_rows=5, fname=None):
    labels = np.asarray(labels).ravel()
    dates = pd.to_datetime(dates)
    mask = ~pd.isna(dates)
    labels = labels[mask]; dates = dates[mask]
    chunks = np.array_split(np.arange(len(dates)), n_rows)
    K = int(np.nanmax(labels)) + 1 if len(labels) else 1
    colors = _regime_palette(K)
    fig, axes = plt.subplots(n_rows, 1, figsize=(12, 1.2 * n_rows), sharex=False)
    if n_rows == 1: axes = [axes]
    for ax, idx in zip(axes, chunks):
        if len(idx) == 0: continue
        arr = labels[idx].reshape(1, -1)
        cmap = ListedColormap(colors[:K])
        ax.imshow(arr, aspect="auto", cmap=cmap, vmin=-0.5, vmax=K-0.5)
        ax.set_yticks([])
        sub_dates = dates[idx]; years = sorted({d.year for d in sub_dates})
        step = max(1, len(years)//8); ticks, labs = [], []
        for y in years[::step]:
            where = np.where(sub_dates.year == y)[0]
            if len(where): ticks.append(where[0]); labs.append(str(y))
        ax.set_xticks(ticks); ax.set_xticklabels(labs)
        for s in ax.spines.values(): s.set_visible(False)
    counts = pd.Series(labels).value_counts(normalize=True).sort_index()
    legend_handles = [patches.Patch(facecolor=colors[k], edgecolor="none", label=f"Regime {k}, {counts.get(k,0):.0%}")
                      for k in range(K)]
    fig.legend(handles=legend_handles, ncol=min(4, K), loc="upper center", bbox_to_anchor=(0.5, 1.05))
    fig.suptitle(title, y=1.08, fontsize=13, fontweight="bold"); fig.tight_layout()
    if fname: plt.savefig(os.path.join(OUTPUT_DIR, f"{fname}.png"), dpi=160, bbox_inches="tight")
    plt.close()

def spd_project(S, eps=1e-9):
    S = 0.5*(S+S.T); w, V = np.linalg.eigh(S); w = np.clip(w, eps, None); return (V*w)@V.T

def kl_gaussian(m0, C0, m1, C1):
    d = m0.shape[0]
    C0 = spd_project(C0); C1 = spd_project(C1)
    L1 = np.linalg.cholesky(C1)
    invC1_C0 = np.linalg.solve(L1, np.linalg.solve(L1.T, C0))
    diff = (m1 - m0)
    quad = diff.T @ np.linalg.solve(L1, np.linalg.solve(L1.T, diff))
    logdetC0 = 2.0*np.sum(np.log(np.diag(np.linalg.cholesky(C0))))
    logdetC1 = 2.0*np.sum(np.log(np.diag(L1)))
    return 0.5*(logdetC1 - logdetC0 - d + np.trace(invC1_C0) + quad)

def w2_gaussian(m0, C0, m1, C1):
    C0 = spd_project(C0); C1 = spd_project(C1)
    diff2 = float(np.dot(m0 - m1, m0 - m1))
    w1, V1 = np.linalg.eigh(C1)
    S1h = (V1*np.sqrt(np.clip(w1,0,None)))@V1.T
    M = spd_project(S1h @ C0 @ S1h)
    wm, Vm = np.linalg.eigh(M)
    tr_sqrt = np.sum(np.sqrt(np.clip(wm,0,None)))
    return diff2 + np.trace(C0 + C1) - 2.0*tr_sqrt