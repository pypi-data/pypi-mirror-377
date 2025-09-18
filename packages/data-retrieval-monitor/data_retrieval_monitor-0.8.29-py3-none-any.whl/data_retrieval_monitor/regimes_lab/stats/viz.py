# regimes_lab/stats/viz.py
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from ..configs import STATS_FIG_DIR

plt.rcParams.update({"axes.titlesize": 12, "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9})

def _savefig(fname: str):
    import os
    os.makedirs(STATS_FIG_DIR, exist_ok=True)
    path = os.path.join(STATS_FIG_DIR, fname)
    # No tight_layout here (some axes are imshow with gridspec). Let constrained_layout handle it.
    plt.savefig(path, dpi=170)  # regular save
    plt.close()

def heatmap_panel(df: pd.DataFrame, title: str, fname: str, center=None, cmap="viridis", fmt=".2f"):
    plt.figure(figsize=(max(10, 0.6 * df.shape[1]), max(4.5, 0.4 * df.shape[0])))
    sns.heatmap(df, annot=True, fmt=fmt, cmap=cmap, center=center, linewidths=0.4, cbar=True)
    plt.title(title)
    _savefig(fname)

def bar_significance(coef: pd.Series, t: pd.Series|None, p: pd.Series|None, title: str, fname: str, top_n: int = 30):
    df = pd.DataFrame({"coef": coef})
    if t is not None: df["tstat"] = t
    if p is not None: df["pval"]  = p
    if "const" in df.index: df = df.drop(index="const")
    df = df.reindex(df["coef"].abs().sort_values(ascending=False).head(top_n).index)
    plt.figure(figsize=(min(24, 0.8 * max(10, len(df))), 7))
    ax = sns.barplot(x=df.index, y=df["coef"], palette="coolwarm", edgecolor="k", linewidth=0.4)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=80, ha="right")
    for i, idx in enumerate(df.index):
        labels=[]
        if "tstat" in df.columns and pd.notna(df.loc[idx, "tstat"]): labels.append(f"t={df.loc[idx,'tstat']:.2f}")
        if "pval"  in df.columns and pd.notna(df.loc[idx, "pval" ]): labels.append(f"p={df.loc[idx,'pval']:.3f}")
        if labels:
            y = df.loc[idx, "coef"]; va = "bottom" if y > 0 else "top"
            ax.text(i, y, "\n".join(labels), ha="center", va=va, fontsize=8)
    plt.title(title)
    _savefig(fname)

def pvalue_hist(p: pd.Series, title: str, fname: str, bins: int = 20):
    pv = p.dropna().values
    if pv.size == 0:
        return
    plt.figure(figsize=(7,4.5))
    plt.hist(pv, bins=bins, edgecolor="k")
    plt.title(title); plt.xlabel("p-value"); plt.ylabel("count")
    _savefig(fname)

def line_over_windows(df_stat: pd.DataFrame, title: str, fname: str):
    plt.figure(figsize=(12.5, 4.8))
    for c in df_stat.columns:
        plt.plot(df_stat.index, df_stat[c], label=c, linewidth=1.2, marker='.', markersize=3, alpha=0.9)
    plt.legend(ncol=3, fontsize=8, frameon=False)
    plt.title(title)
    _savefig(fname)

def plot_cumret_bands(dates, series, labels: pd.Series, title: str, fname: str, alpha=0.18):
    """Plot cumulative return with translucent regime bands (labels indexed by dates)."""
    import matplotlib.patches as patches
    dates = pd.to_datetime(dates)
    s = pd.Series(series, index=dates).dropna()
    r = labels.reindex(s.index).ffill().bfill().astype(int)
    t = s.index.view('int64').to_numpy()
    if len(t) < 2: return
    mids = (t[:-1] + t[1:]) // 2
    left  = t[0] - (mids[0] - t[0]) if len(mids) else t[0]
    right = t[-1] + (t[-1] - mids[-1]) if len(mids) else t[-1]
    edges = np.concatenate([[left], mids, [right]])
    dt_edges = pd.to_datetime(edges, unit="ns")
    K = int(r.max()) + 1 if len(r) else 1
    base = plt.get_cmap("tab10"); colors = [base(i%10) for i in range(K)]
    plt.figure(figsize=(12,4))
    plt.plot(s.index, s.values, lw=1.5, zorder=10)
    for k in range(len(r)):
        plt.axvspan(dt_edges[k], dt_edges[k+1], facecolor=colors[r.iloc[k]], alpha=alpha, linewidth=0)
    handles = [patches.Patch(facecolor=colors[k], alpha=alpha, edgecolor="none", label=f"Regime {k}") for k in range(K)]
    plt.legend(handles=handles, ncol=min(4,K), frameon=False)
    plt.title(title)
    _savefig(fname)