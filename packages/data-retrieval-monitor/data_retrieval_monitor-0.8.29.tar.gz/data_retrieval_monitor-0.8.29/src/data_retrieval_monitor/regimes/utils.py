import os, math, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()

def infer_periods_per_year(dates_index: pd.DatetimeIndex) -> int:
    if len(dates_index) < 3: return 252
    diffs = np.diff(dates_index.values.astype("datetime64[ns]")).astype("timedelta64[D]").astype(int)
    md = np.median(diffs)
    return 252 if md<=2 else 52 if md<=10 else 12 if md<=40 else 1

def annualized_stats(returns_df: pd.DataFrame, ann_factor: int) -> dict:
    mu = returns_df.mean() * ann_factor
    vol = returns_df.std() * math.sqrt(ann_factor)
    sharpe = (returns_df.mean() / (returns_df.std() + 1e-12)) * math.sqrt(ann_factor)
    return {"mean": mu, "vol": vol, "sharpe": sharpe}

def professional_heatmap(df: pd.DataFrame, title: str, out_png: str,
                         fmt=".2%", center_zero=True, cbar_label=None):
    values = df.values.astype(float) if df.size else np.zeros((1,1))
    if center_zero:
        vmax = np.nanmax(np.abs(values)) if np.isfinite(values).any() else 1.0
        vmin = -vmax; cmap = "coolwarm"
    else:
        vmin, vmax = (np.nanmin(values), np.nanmax(values)) if df.size else (0,1)
        cmap = "viridis"
    fig_h = max(3.8, 0.34 * max(1, len(df)))
    fig, ax = plt.subplots(figsize=(11, fig_h))
    im = ax.imshow(values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(values.shape[1])); ax.set_yticks(range(values.shape[0]))
    ax.set_xticklabels(df.columns, rotation=90); ax.set_yticklabels(df.index)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            try: txt = format(values[i,j], fmt)
            except Exception: txt = f"{values[i,j]:.2f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7, color="black")
    formatter = FuncFormatter(lambda x,_: f"{x*100:.0f}%") if "%" in fmt else None
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, format=formatter)
    if cbar_label: cbar.set_label(cbar_label)
    ax.set_title(title, fontsize=12, fontweight="bold")
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.savefig(out_png, dpi=160, bbox_inches="tight")
    plt.close()

def save_csv(df: pd.DataFrame, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path)