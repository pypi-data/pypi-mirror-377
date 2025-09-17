#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Regime Analysis Pipeline — FULL + ADD-ONS (outputs -> ./output2)

What it does
------------
1) Reads factor PRICE LEVELS and 4 INDICATORS (CSV with date index).
2) Computes LOG RETURNS; shifts indicators by +2 business days (no leakage).
3) Sign-based analysis per indicator (Positive vs Negative):
   - Annualized Mean, Volatility, Sharpe
   - Professional heatmaps
4) Systematic regime models on ALL 4 indicators (scaled + PCA):
   - KMeans (raw), Gaussian Mixture (raw), Bayesian GMM (raw),
   - Agglomerative (on PCA), KMeans (on PCA), Spectral Clustering (on PCA),
   - Optional HMM (raw indicators) if hmmlearn is installed
5) Per-regime factor performance (Mean, Vol, Sharpe) + professional heatmaps
6) Exhibit-4-style multi-row timeline (colored timepoints by regimes)
7) Factor time series with translucent regime bands (midpoint method — no gaps)
8) Dummy variables for every model’s regimes + indicator sign dummies
9) Optional CHANGePOINT DETECTION (via ruptures): Binseg / PELT / KernelCPD

ADD-ONS (requested)
-------------------
A) VQ-VAE on indicators → regime labels via codebook indices (PyTorch optional)
B) SAINT-style transformer embeddings + nearest-neighbor voting for regimes (PyTorch optional)
C) Deterministic distances between Gaussians on rolling windows:
   - KL(N_old || N_new), KL(N_new || N_old), Wasserstein-2 (squared) — no sampling
D) Inductive Conformal Prediction over a base regime model to produce coverage-controlled regimes

CSV formats expected
--------------------
- levels.csv:  date index in first column; remaining columns are factor PRICE LEVELS
- indicators.csv: date index; EXACTLY 4 indicator columns

All outputs are written to ./output2
"""

import os
import math
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import ListedColormap

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, AgglomerativeClustering, SpectralClustering
from sklearn.mixture import GaussianMixture, BayesianGaussianMixture
from sklearn.neighbors import NearestNeighbors

# Optional HMM
try:
    from hmmlearn import hmm
    HMM_AVAILABLE = True
except Exception:
    HMM_AVAILABLE = False

# Optional changepoint detection
try:
    import ruptures as rpt
    CPD_AVAILABLE = True
except Exception:
    CPD_AVAILABLE = False

# Optional PyTorch for VQ-VAE & SAINT add-ons
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False


# ============================ CONFIG ============================
LEVELS_CSV = "levels.csv"           # price levels (date index, factor columns)
INDICATORS_CSV = "indicators.csv"   # 4 indicators (date index, 4 columns)
OUTPUT_DIR = "output2"              # <— per your request

# Models / embeddings
N_CLUSTERS = 4
PCA_COMPONENTS = 3
SPECTRAL_KNN = 15  # for spectral clustering nearest-neighbor affinity

# Plotting presets
TIMELINE_ROWS = 5                    # rows in Exhibit-4 style timeline
BANDS_ALPHA = 0.18                   # opacity of regime bands on time series

# Add-ons config
SEED = 7
np.random.seed(SEED)

# VQ-VAE
VQVAE_CODEBOOK_K = 16
VQVAE_EMBED_DIM  = 8
VQVAE_HIDDEN     = 32
VQVAE_EPOCHS     = 20
VQVAE_LR         = 1e-3
VQVAE_BETA       = 0.25   # commitment cost

# SAINT encoder (simplified) + kNN on embeddings
SAINT_D_MODEL  = 64
SAINT_NHEAD    = 4
SAINT_NLAYERS  = 2
SAINT_DFF      = 128
SAINT_DROPOUT  = 0.1
KNN_K          = 10

# Gaussian rolling windows (add-on C)
OLD_WIN = 252 * 4  # ~4y of old data
NEW_WIN = 63       # ~3m of new data

# Conformal prediction (add-on D)
CONF_BASE_MODEL = "kmeans_ind"  # which base regime series to conformalize
CONF_CAL_FRAC   = 0.3           # fraction for calibration (oldest chunk)
CONF_ALPHA      = 0.1           # miscoverage level (90% coverage)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================ UTILITIES ============================

def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()


def infer_periods_per_year(dates_index: pd.DatetimeIndex) -> int:
    """Infer annualization factor from timestamp spacing."""
    if len(dates_index) < 3:
        return 252
    diffs = np.diff(dates_index.values.astype("datetime64[ns]")).astype("timedelta64[D]").astype(int)
    median_days = np.median(diffs)
    if median_days <= 2:   # ~daily business days
        return 252
    elif median_days <= 10:
        return 52          # weekly
    elif median_days <= 40:
        return 12          # monthly
    else:
        return 1


def annualized_stats(returns_df: pd.DataFrame, ann_factor: int) -> dict:
    """Annualized mean, vol, sharpe for each column."""
    mu = returns_df.mean() * ann_factor
    vol = returns_df.std() * math.sqrt(ann_factor)
    sharpe = (returns_df.mean() / returns_df.std()) * math.sqrt(ann_factor)
    return {"mean": mu, "vol": vol, "sharpe": sharpe}


def save_table(df: pd.DataFrame, name: str):
    path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    df.to_csv(path)
    return path

# -------------------- Pretty plotting helpers --------------------

def _regime_palette(n):
    # Distinct, readable colors (10-cycle if needed)
    base = plt.get_cmap("tab10")
    return [base(i % 10) for i in range(n)]


def _format_pct(x, pos):
    return f"{x*100:.0f}%"


def professional_heatmap(df, title, fname=None, fmt=".2%", center_zero=True,
                         cbar_label=None):
    """
    Clean, presentation-ready heatmap:
    - white gridlines
    - bold title, tight layout
    - optional zero-centering (good for Sharpe/alpha)
    - percent formatting default
    """
    values = df.values.astype(float)
    if center_zero:
        vmax = np.nanmax(np.abs(values))
        vmin = -vmax
        cmap = "coolwarm"
    else:
        vmin, vmax = np.nanmin(values), np.nanmax(values)
        cmap = "viridis"

    fig_h = max(3.8, 0.34 * len(df))
    fig, ax = plt.subplots(figsize=(11, fig_h))
    im = ax.imshow(values, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)

    # gridlines
    ax.set_xticks(np.arange(values.shape[1]+1)-0.5, minor=True)
    ax.set_yticks(np.arange(values.shape[0]+1)-0.5, minor=True)
    ax.grid(which="minor", color="w", linestyle="-", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)

    ax.set_xticks(np.arange(values.shape[1]))
    ax.set_yticks(np.arange(values.shape[0]))
    ax.set_xticklabels(df.columns, rotation=0)
    ax.set_yticklabels(df.index)

    # annotate cells
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            val = values[i, j]
            try:
                txt = format(val, fmt)
            except Exception:
                txt = f"{val:.2f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8, color="black")

    # colorbar
    formatter = FuncFormatter(_format_pct) if "%" in fmt else None
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, format=formatter)
    if cbar_label:
        cbar.set_label(cbar_label)

    ax.set_title(title, fontsize=13, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    if fname:
        plt.savefig(os.path.join(OUTPUT_DIR, f"{fname}.png"), dpi=160, bbox_inches="tight")
    plt.close()


def plot_timeline_chunked(labels, dates, title="Regimes Through Time",
                          n_rows=5, fname=None):
    """
    Exhibit-4 style: split the full sample into n_rows horizontal strips and
    color each timepoint by regime.
    """
    labels = np.asarray(labels).ravel()
    dates = pd.to_datetime(dates)
    mask = ~pd.isna(dates)
    labels = labels[mask]
    dates = dates[mask]

    # split into contiguous chunks by time
    chunks = np.array_split(np.arange(len(dates)), n_rows)
    K = int(labels.max()) + 1
    colors = _regime_palette(K)

    fig, axes = plt.subplots(n_rows, 1, figsize=(12, 1.2 * n_rows), sharex=False)
    if n_rows == 1:
        axes = [axes]

    for ax, idx in zip(axes, chunks):
        if len(idx) == 0:
            continue
        arr = labels[idx].reshape(1, -1)
        cmap = ListedColormap(colors[:K])
        ax.imshow(arr, aspect="auto", cmap=cmap, vmin=-0.5, vmax=K-0.5)
        ax.set_yticks([])
        # year ticks
        sub_dates = dates[idx]
        years = sorted({d.year for d in sub_dates})
        step = max(1, len(years)//8)
        ticks, labs = [], []
        for y in years[::step]:
            j = idx[np.argmax(sub_dates.year == y)]
            ticks.append(j - idx[0])
            labs.append(str(y))
        ax.set_xticks(ticks)
        ax.set_xticklabels(labs)
        # remove borders
        for spine in ax.spines.values():
            spine.set_visible(False)

    counts = pd.Series(labels).value_counts(normalize=True).sort_index()
    legend_handles = [
        patches.Patch(facecolor=colors[k], edgecolor="none",
                      label=f"Regime {k}, {counts.get(k,0):.0%}")
        for k in range(K)
    ]
    fig.legend(handles=legend_handles, ncol=min(4, K), loc="upper center",
               bbox_to_anchor=(0.5, 1.05))
    fig.suptitle(title, y=1.08, fontsize=13, fontweight="bold")
    fig.tight_layout()
    if fname:
        plt.savefig(os.path.join(OUTPUT_DIR, f"{fname}.png"), dpi=160, bbox_inches="tight")
    plt.close()


def plot_series_with_regime_bands(dates, series, regime_labels, title=None, fname=None, alpha=BANDS_ALPHA):
    """
    Continuous shading (no white gaps): uses midpoints between timestamps as regime edges.
    """
    dates = pd.to_datetime(dates)
    s = pd.Series(series, index=dates).dropna()
    r = pd.Series(regime_labels, index=dates).reindex(s.index).ffill().bfill().astype(int)

    t = s.index.view('int64') # ns since epoch
    if len(t) < 2:
        return
    mids = (t[:-1] + t[1:]) // 2
    left_edge  = t[0] - (mids[0] - t[0])        if len(mids) else t[0]
    right_edge = t[-1] + (t[-1] - mids[-1])     if len(mids) else t[-1]
    edges = np.concatenate([[left_edge], mids, [right_edge]])
    dt_edges = pd.to_datetime(edges, unit="ns")

    reg = r.to_numpy()
    K = int(reg.max()) + 1
    colors = _regime_palette(K)

    fig, ax = plt.subplots(figsize=(12, 3.2))
    ax.plot(s.index, s.values, lw=1.5, zorder=10)
    ax.set_xlim(s.index.min(), s.index.max())
    ax.grid(axis="y", alpha=0.25)

    for k in range(len(reg)):
        ax.axvspan(dt_edges[k], dt_edges[k+1],
                   facecolor=colors[reg[k]], alpha=alpha, linewidth=0)

    handles = [patches.Patch(facecolor=colors[k], alpha=alpha, edgecolor="none", label=f"Regime {k}")
               for k in range(K)]
    ax.legend(handles=handles, ncol=min(4, K), loc="upper left", frameon=False)

    if title:
        ax.set_title(title, fontsize=12, fontweight="bold")
    fig.tight_layout()
    if fname:
        plt.savefig(os.path.join(OUTPUT_DIR, f"{fname}.png"), dpi=160, bbox_inches="tight")
    plt.close()


# ============================ DATA LOADING (with simulation fallback) ============================

def load_or_simulate():
    if os.path.exists(LEVELS_CSV) and os.path.exists(INDICATORS_CSV):
        levels = ensure_datetime_index(pd.read_csv(LEVELS_CSV, index_col=0))
        indicators = ensure_datetime_index(pd.read_csv(INDICATORS_CSV, index_col=0))
        return levels, indicators, True

    # Simulate realistic data (daily, 20 factors, 4 indicators)
    rng = np.random.default_rng(42)
    dates = pd.bdate_range("2017-01-03", "2024-12-31")
    n, n_assets, n_ind = len(dates), 20, 4

    t = np.arange(n)
    indicators = pd.DataFrame({
        "Ind1_Growth": 0.5*np.sin(2*np.pi*t/260) + 0.3*rng.standard_normal(n),
        "Ind2_Infl":   0.6*np.cos(2*np.pi*t/500) + 0.3*rng.standard_normal(n),
        "Ind3_Stress": 0.4*np.sin(2*np.pi*t/780 + 1.0) + 0.4*rng.standard_normal(n),
        "Ind4_Liq":    0.6*np.cos(2*np.pi*t/390 + 0.7) + 0.3*rng.standard_normal(n),
    }, index=dates)

    B = rng.normal(0, 0.1, size=(n_ind, n_assets))
    base_mu = rng.normal(0.04/252, 0.02/252, size=n_assets)
    base_sigma = rng.uniform(0.12/np.sqrt(252), 0.3/np.sqrt(252), size=n_assets)

    eps = rng.standard_normal((n, n_assets)) * base_sigma
    drift = (indicators.values @ B) / 252.0
    rets = base_mu + drift + eps
    levels = 100 * np.exp(np.cumsum(rets, axis=0))
    cols = [f"Factor_{i+1:02d}" for i in range(n_assets)]
    levels = pd.DataFrame(levels, index=dates, columns=cols)

    print(">> CSVs not found; generated a synthetic dataset to demonstrate the pipeline.")
    return levels, indicators, False


# ============================ SIGN-BASED ANALYSIS ============================

def sign_based_analysis(returns: pd.DataFrame, indicators_shifted: pd.DataFrame, ann_factor: int):
    for ind in indicators_shifted.columns:
        pos = indicators_shifted[ind] > 0
        neg = ~pos

        stats_pos = annualized_stats(returns.loc[pos], ann_factor)
        stats_neg = annualized_stats(returns.loc[neg], ann_factor)

        df_mean = pd.DataFrame({"Positive": stats_pos["mean"], "Negative": stats_neg["mean"]})
        df_vol  = pd.DataFrame({"Positive": stats_pos["vol"],  "Negative": stats_neg["vol"]})
        df_sharpe = pd.DataFrame({"Positive": stats_pos["sharpe"], "Negative": stats_neg["sharpe"]})

        save_table(df_mean, f"{ind}_mean_by_sign")
        save_table(df_vol,  f"{ind}_vol_by_sign")
        save_table(df_sharpe, f"{ind}_sharpe_by_sign")

        professional_heatmap(df_mean,   f"{ind}: Annualized Mean (Pos/Neg)",   f"{ind}_mean_heatmap",   fmt=".2%")
        professional_heatmap(df_vol,    f"{ind}: Annualized Vol (Pos/Neg)",    f"{ind}_vol_heatmap",    fmt=".2%")
        professional_heatmap(df_sharpe, f"{ind}: Sharpe (Pos/Neg)",            f"{ind}_sharpe_heatmap", fmt=".2f", center_zero=True, cbar_label="Sharpe")


# ============================ SYSTEMATIC REGIME MODELS ============================

def fit_regime_models(ind_scaled: np.ndarray, dates: pd.DatetimeIndex) -> dict:
    labels = {}

    # KMeans on indicators
    labels["kmeans_ind"] = KMeans(n_clusters=N_CLUSTERS, n_init=10, random_state=0).fit_predict(ind_scaled)

    # GMM on indicators
    labels["gmm_ind"] = GaussianMixture(n_components=N_CLUSTERS, covariance_type="full", random_state=0)\
                        .fit_predict(ind_scaled)

    # Bayesian GMM (estimates component usage; N_CLUSTERS is an upper bound)
    labels["bayes_gmm_ind"] = BayesianGaussianMixture(n_components=N_CLUSTERS, covariance_type="full",
                                                      random_state=0).fit_predict(ind_scaled)

    # PCA embedding
    pca = PCA(n_components=min(PCA_COMPONENTS, ind_scaled.shape[1]))
    Xp = pca.fit_transform(ind_scaled)

    # Agglomerative on PCA
    labels["agg_pca"] = AgglomerativeClustering(n_clusters=N_CLUSTERS).fit_predict(Xp)

    # KMeans on PCA
    labels["kmeans_pca"] = KMeans(n_clusters=N_CLUSTERS, n_init=10, random_state=0).fit_predict(Xp)

    # Spectral clustering using k-NN affinity on PCA space
    n_neighbors = max(2, min(SPECTRAL_KNN, Xp.shape[0]-1))
    labels["spectral_pca"] = SpectralClustering(n_clusters=N_CLUSTERS, affinity="nearest_neighbors",
                                                n_neighbors=n_neighbors,
                                                random_state=0, assign_labels="kmeans")\
                             .fit_predict(Xp)

    # Optional HMM on indicators
    if HMM_AVAILABLE:
        ghmm = hmm.GaussianHMM(n_components=N_CLUSTERS, covariance_type="full", n_iter=200, random_state=0)
        ghmm.fit(ind_scaled)
        labels["hmm_ind"] = ghmm.predict(ind_scaled)

    # Save timeline plots
    for name, lab in labels.items():
        plot_timeline_chunked(lab, dates, title=f"Highest-Probability Market Conditions — {name}",
                              n_rows=TIMELINE_ROWS, fname=f"exhibit4_{name}")

    return labels


# ============================ CHANGEPOINT DETECTION (optional) ============================

def fit_changepoint_models(ind_scaled: np.ndarray, dates: pd.DatetimeIndex, n_bkps: int = 6) -> dict:
    """
    Multivariate changepoint detection on scaled indicators.
    Returns dict of labels per date (segment IDs), one series per algorithm.
    n_bkps is the *maximum* number of breakpoints (segments = n_bkps+1).
    """
    labels = {}
    if not CPD_AVAILABLE or ind_scaled.shape[0] < 10:
        return labels

    T = ind_scaled.shape[0]
    n_bkps = max(1, min(n_bkps, T // 50))  # avoid overfitting on short samples

    # 1) Binary Segmentation (l2)
    try:
        algo = rpt.Binseg(model="l2").fit(ind_scaled)
        bkps = algo.predict(n_bkps=n_bkps)
        seg = np.zeros(T, dtype=int)
        start = 0
        for seg_id, end in enumerate(bkps):
            seg[start:end] = seg_id
            start = end
        labels[f"cpd_binseg_{n_bkps}"] = seg
    except Exception:
        pass

    # 2) PELT (rbf) with dynamic penalty
    try:
        pen = 10.0 * np.log(T) * (ind_scaled.shape[1] ** 0.5)
        algo = rpt.Pelt(model="rbf").fit(ind_scaled)
        bkps = algo.predict(pen=pen)
        seg = np.zeros(T, dtype=int)
        start = 0
        for seg_id, end in enumerate(bkps):
            seg[start:end] = seg_id
            start = end
        labels["cpd_pelt_rbf"] = seg
    except Exception:
        pass

    # 3) KernelCPD (rbf)
    try:
        algo = rpt.KernelCPD(kernel="rbf").fit(ind_scaled)
        bkps = algo.predict(n_bkps=n_bkps)
        seg = np.zeros(T, dtype=int)
        start = 0
        for seg_id, end in enumerate(bkps):
            seg[start:end] = seg_id
            start = end
        labels[f"cpd_kernel_{n_bkps}"] = seg
    except Exception:
        pass

    # Exhibit-4 timelines for CPD
    for name, lab in labels.items():
        plot_timeline_chunked(lab, dates, title=f"Changepoint Segments — {name}",
                              n_rows=TIMELINE_ROWS, fname=f"exhibit4_{name}")
    return labels


# ============================ EVALUATION / EXPORT ============================

def per_regime_factor_stats(returns: pd.DataFrame, ann_factor: int, regime_labels: dict, dates: pd.DatetimeIndex):
    regimes_df = pd.DataFrame(regime_labels, index=dates)
    save_table(regimes_df, "regimes_by_model")

    for model_name in regimes_df.columns:
        labs = regimes_df[model_name].values
        uniq = np.unique(labs)

        out_mean   = pd.DataFrame(index=returns.columns, columns=[f"Regime {int(s)}" for s in uniq])
        out_vol    = out_mean.copy()
        out_sharpe = out_mean.copy()

        for s in uniq:
            mask = labs == s
            if mask.sum() == 0:
                continue
            stats = annualized_stats(returns.loc[mask], ann_factor)
            out_mean[f"Regime {int(s)}"]   = stats["mean"]
            out_vol[f"Regime {int(s)}"]    = stats["vol"]
            out_sharpe[f"Regime {int(s)}"] = stats["sharpe"]

        save_table(out_mean,   f"{model_name}_annualized_mean_by_regime")
        save_table(out_vol,    f"{model_name}_annualized_vol_by_regime")
        save_table(out_sharpe, f"{model_name}_sharpe_by_regime")

        professional_heatmap(out_mean,   f"{model_name}: Annualized Mean by Regime",
                             f"{model_name}_mean_heatmap",   fmt=".2%")
        professional_heatmap(out_vol,    f"{model_name}: Annualized Vol by Regime",
                             f"{model_name}_vol_heatmap",    fmt=".2%")
        professional_heatmap(out_sharpe, f"{model_name}: Sharpe by Regime",
                             f"{model_name}_sharpe_heatmap", fmt=".2f", center_zero=True, cbar_label="Sharpe")

    return regimes_df


def make_dummies(regimes_df: pd.DataFrame, indicators_shifted: pd.DataFrame) -> pd.DataFrame:
    """One-hot dummies for regimes of each model + sign dummies for indicators."""
    parts = []
    for col in regimes_df.columns:
        onehot = pd.get_dummies(regimes_df[col], prefix=f"{col}_R")
        parts.append(onehot)

    for ind in indicators_shifted.columns:
        parts.append(pd.Series((indicators_shifted[ind] > 0).astype(int), name=f"{ind}_POS"))
        parts.append(pd.Series((indicators_shifted[ind] <= 0).astype(int), name=f"{ind}_NEG"))

    dummies = pd.concat(parts, axis=1)
    save_table(dummies, "regime_and_sign_dummies")
    return dummies


# ============================ ADD-ONS: Deterministic Gaussian distances ============================

def _spd_project(S, eps=1e-9):
    """Project symmetric matrix to nearest SPD by eigenvalue clipping."""
    S = 0.5 * (S + S.T)
    w, V = np.linalg.eigh(S)
    w = np.clip(w, eps, None)
    return (V * w) @ V.T


def kl_gaussian(m0, C0, m1, C1):
    """KL(N0||N1) closed-form for d-dimensional Gaussians."""
    d = m0.shape[0]
    C0 = _spd_project(C0)
    C1 = _spd_project(C1)
    L1 = np.linalg.cholesky(C1)
    invC1_C0 = np.linalg.solve(L1, np.linalg.solve(L1.T, C0))
    diff = (m1 - m0)
    quad = diff.T @ np.linalg.solve(L1, np.linalg.solve(L1.T, diff))
    logdetC0 = 2.0 * np.sum(np.log(np.diag(np.linalg.cholesky(C0))))
    logdetC1 = 2.0 * np.sum(np.log(np.diag(L1)))
    return 0.5 * (logdetC1 - logdetC0 - d + np.trace(invC1_C0) + quad)


def w2_gaussian(m0, C0, m1, C1):
    """2-Wasserstein distance (squared) between Gaussians."""
    C0 = _spd_project(C0)
    C1 = _spd_project(C1)
    diff2 = float(np.dot(m0 - m1, m0 - m1))
    w1, V1 = np.linalg.eigh(C1)
    S1h = (V1 * np.sqrt(np.clip(w1, 0, None))) @ V1.T
    M = _spd_project(S1h @ C0 @ S1h)
    wm, Vm = np.linalg.eigh(M)
    tr_sqrt = np.sum(np.sqrt(np.clip(wm, 0, None)))
    return diff2 + np.trace(C0 + C1) - 2.0 * tr_sqrt


def rolling_gaussian_distances(X, dates, old_win=OLD_WIN, new_win=NEW_WIN):
    """Compute rolling KL(N_old||N_new), KL(N_new||N_old), and W2^2 between old and new windows."""
    X = np.asarray(X)
    T, d = X.shape
    out = []
    for t in range(T):
        if t < old_win + new_win:
            out.append((np.nan, np.nan, np.nan))
            continue
        Xold = X[t - old_win - new_win : t - new_win]
        Xnew = X[t - new_win : t]
        m0 = Xold.mean(axis=0)
        m1 = Xnew.mean(axis=0)
        C0 = np.cov(Xold.T, bias=False)
        C1 = np.cov(Xnew.T, bias=False)
        try:
            d01 = kl_gaussian(m0, C0, m1, C1)
            d10 = kl_gaussian(m1, C1, m0, C0)
            w2 = w2_gaussian(m0, C0, m1, C1)
        except np.linalg.LinAlgError:
            d01 = d10 = w2 = np.nan
        out.append((d01, d10, w2))
    df = pd.DataFrame(out, index=pd.to_datetime(dates), columns=["KL_old_to_new", "KL_new_to_old", "W2_sq"])
    df.to_csv(os.path.join(OUTPUT_DIR, "rolling_gaussian_distances.csv"))
    return df


# ============================ ADD-ONS: VQ-VAE (optional, PyTorch) ============================

if TORCH_AVAILABLE:
    torch.manual_seed(SEED)

    class VectorQuantizer(nn.Module):
        def __init__(self, K, D, beta=0.25):
            super().__init__()
            self.K = K
            self.D = D
            self.beta = beta
            self.codebook = nn.Parameter(torch.randn(K, D))

        def forward(self, z_e):
            # z_e: (T, D)
            with torch.no_grad():
                d = (z_e.pow(2).sum(1, keepdim=True)
                     - 2 * z_e @ self.codebook.T
                     + self.codebook.pow(2).sum(1))  # (T,K)
                indices = torch.argmin(d, dim=1)
            z_q = F.embedding(indices, self.codebook)
            # losses
            commit = self.beta * F.mse_loss(z_e.detach(), z_q)
            code = F.mse_loss(z_e, z_q.detach())
            loss = code + commit
            # Straight-through estimator
            z_q_st = z_e + (z_q - z_e).detach()
            return z_q_st, indices, loss

    class VQVAE(nn.Module):
        def __init__(self, x_dim, hidden=32, z_dim=8, K=16, beta=0.25):
            super().__init__()
            self.enc = nn.Sequential(
                nn.Linear(x_dim, hidden), nn.ReLU(),
                nn.Linear(hidden, z_dim)
            )
            self.vq = VectorQuantizer(K, z_dim, beta)
            self.dec = nn.Sequential(
                nn.Linear(z_dim, hidden), nn.ReLU(),
                nn.Linear(hidden, x_dim)
            )
        def forward(self, x):
            z_e = self.enc(x)
            z_q, idx, vq_loss = self.vq(z_e)
            x_hat = self.dec(z_q)
            recon = F.mse_loss(x_hat, x)
            loss = recon + vq_loss
            return x_hat, idx, loss

    def fit_vqvae_on_rows(X, epochs=VQVAE_EPOCHS, z_dim=VQVAE_EMBED_DIM, K=VQVAE_CODEBOOK_K,
                           hidden=VQVAE_HIDDEN, lr=VQVAE_LR, beta=VQVAE_BETA):
        X_t = torch.tensor(X, dtype=torch.float32)
        model = VQVAE(X.shape[1], hidden, z_dim, K, beta)
        opt = torch.optim.Adam(model.parameters(), lr=lr)
        model.train()
        for _ in range(epochs):
            opt.zero_grad()
            _, _, loss = model(X_t)
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            _, idx, _ = model(X_t)
        return model, idx.cpu().numpy()


# ============================ ADD-ONS: SAINT-style Transformer (optional, PyTorch) ==============

if TORCH_AVAILABLE:
    class SAINTEncoder(nn.Module):
        def __init__(self, d_in, d_model=64, nhead=4, nlayers=2, dff=128, dropout=0.1):
            super().__init__()
            self.inp = nn.Linear(d_in, d_model)
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model, nhead=nhead, dim_feedforward=dff,
                dropout=dropout, batch_first=True, activation='gelu'
            )
            self.tf = nn.TransformerEncoder(encoder_layer, num_layers=nlayers)
            self.norm = nn.LayerNorm(d_model)
        def forward(self, x):
            # x: (B, 1, d_in) -> (B, d_model)
            h = self.inp(x)
            h = self.tf(h)
            h = self.norm(h)[:, 0, :]
            return h

    def fit_saint_embeddings(X, epochs=10, d_model=SAINT_D_MODEL):
        X_t = torch.tensor(X, dtype=torch.float32)
        model = SAINTEncoder(X.shape[1], d_model=d_model, nhead=SAINT_NHEAD,
                             nlayers=SAINT_NLAYERS, dff=SAINT_DFF, dropout=SAINT_DROPOUT)
        dec = nn.Sequential(nn.Linear(d_model, X.shape[1]))
        opt = torch.optim.Adam(list(model.parameters()) + list(dec.parameters()), lr=1e-3)
        for _ in range(epochs):
            opt.zero_grad()
            emb = model(X_t.unsqueeze(1))
            x_hat = dec(emb)
            loss = F.mse_loss(x_hat, X_t)
            loss.backward()
            opt.step()
        model.eval(); dec.eval()
        with torch.no_grad():
            emb = model(X_t.unsqueeze(1)).cpu().numpy()
        return emb


# ============================ ADD-ONS: Conformal Prediction ============================

def conformalize_regimes(X, base_labels, dates, alpha=CONF_ALPHA, cal_frac=CONF_CAL_FRAC):
    """
    Inductive conformal classification using nonconformity from class-conditional Gaussian density.
    Returns: (pvalue_df, hard_labels)
    """
    X = np.asarray(X)
    T, d = X.shape
    labels = np.asarray(base_labels).astype(int)
    K = labels.max() + 1
    n_cal = max(50, int(T * cal_frac))

    X_cal, y_cal = X[:n_cal], labels[:n_cal]

    # Fit per-class Gaussian (full cov or diag fallback)
    class_models = {}
    for k in range(K):
        Xm = X_cal[y_cal == k]
        if len(Xm) < d + 2:
            mu = Xm.mean(0) if len(Xm) else X_cal.mean(0)
            cov = np.diag(np.var(X_cal, axis=0) + 1e-6)
        else:
            mu = Xm.mean(0)
            cov = np.cov(Xm.T, bias=False)
        class_models[k] = (mu, _spd_project(cov))

    # Calibration nonconformity = −loglik
    cal_scores = {k: [] for k in range(K)}
    for k in range(K):
        mu, cov = class_models[k]
        L = np.linalg.cholesky(cov)
        ld = 2.0 * np.sum(np.log(np.diag(L)))
        for x in X_cal:
            r = x - mu
            quad = np.sum(np.square(np.linalg.solve(L, r)))
            ll = -0.5 * (quad + ld + d * np.log(2*np.pi))
            cal_scores[k].append(-ll)

    # P-values for each t, k
    P = np.zeros((T, K))
    for t, x in enumerate(X):
        for k in range(K):
            mu, cov = class_models[k]
            L = np.linalg.cholesky(cov)
            ld = 2.0 * np.sum(np.log(np.diag(L)))
            r = x - mu
            quad = np.sum(np.square(np.linalg.solve(L, r)))
            ll = -0.5 * (quad + ld + d * np.log(2*np.pi))
            a = -ll
            P[t, k] = (np.sum(np.array(cal_scores[k]) >= a) + 1.0) / (len(cal_scores[k]) + 1.0)

    p_df = pd.DataFrame(P, index=pd.to_datetime(dates), columns=[f"Regime_{k}" for k in range(K)])
    p_df.to_csv(os.path.join(OUTPUT_DIR, "conformal_pvalues.csv"))

    # Hard labels: smallest set achieving sum p >= 1 - alpha; here we take the first in that set
    hard = []
    for t in range(T):
        order = np.argsort(-P[t])
        cum = 0.0
        sel = []
        for k in order:
            sel.append(k)
            cum += P[t, k]
            if cum >= 1 - alpha:
                break
        hard.append(sel[0])
    hard = np.array(hard)

    plot_timeline_chunked(hard, dates, title=f"Highest-Probability Market Conditions — conformal",
                          n_rows=TIMELINE_ROWS, fname="exhibit4_conformal")
    return p_df, hard


# ============================ ADD-ONS: Export helpers (match original naming) ====================

def export_regime_artifacts(model_name: str, labels: np.ndarray, returns: pd.DataFrame, dates: pd.DatetimeIndex):
    """Append to regimes_by_model.csv, create per-regime stats CSVs + heatmaps, and timeline."""
    labels = np.asarray(labels).astype(int)

    # 1) regimes_by_model.csv
    path = os.path.join(OUTPUT_DIR, "regimes_by_model.csv")
    new_col = pd.Series(labels, index=pd.to_datetime(dates), name=model_name)
    if os.path.exists(path):
        rbm = pd.read_csv(path, index_col=0, parse_dates=True)
        rbm = rbm.reindex(new_col.index).copy()
        rbm[model_name] = new_col.values
    else:
        rbm = pd.DataFrame({model_name: new_col.values}, index=new_col.index)
    rbm.to_csv(path)

    # 2) Per-regime stats + heatmaps
    ann_factor = infer_periods_per_year(returns.index)
    labs = labels
    uniq = np.unique(labs)
    out_mean   = pd.DataFrame(index=returns.columns, columns=[f"Regime {int(s)}" for s in uniq])
    out_vol    = out_mean.copy()
    out_sharpe = out_mean.copy()
    for s in uniq:
        mask = labs == s
        if mask.sum() == 0:
            continue
        stats = annualized_stats(returns.loc[mask], ann_factor)
        out_mean[f"Regime {int(s)}"]   = stats["mean"]
        out_vol[f"Regime {int(s)}"]    = stats["vol"]
        out_sharpe[f"Regime {int(s)}"] = stats["sharpe"]
    out_mean.to_csv(os.path.join(OUTPUT_DIR, f"{model_name}_annualized_mean_by_regime.csv"))
    out_vol.to_csv(os.path.join(OUTPUT_DIR, f"{model_name}_annualized_vol_by_regime.csv"))
    out_sharpe.to_csv(os.path.join(OUTPUT_DIR, f"{model_name}_sharpe_by_regime.csv"))
    professional_heatmap(out_mean,   f"{model_name}: Annualized Mean by Regime",   f"{model_name}_mean_heatmap",   fmt=".2%")
    professional_heatmap(out_vol,    f"{model_name}: Annualized Vol by Regime",    f"{model_name}_vol_heatmap",    fmt=".2%")
    professional_heatmap(out_sharpe, f"{model_name}: Sharpe by Regime",            f"{model_name}_sharpe_heatmap", fmt=".2f", center_zero=True, cbar_label="Sharpe")

    # 3) Timeline
    plot_timeline_chunked(labels, dates,
                          title=f"Highest-Probability Market Conditions — {model_name}",
                          n_rows=TIMELINE_ROWS, fname=f"exhibit4_{model_name}")

    # 4) Dummies augmentation
    d_path = os.path.join(OUTPUT_DIR, "regime_and_sign_dummies.csv")
    new_dummies = pd.get_dummies(labels, prefix=f"{model_name}_R")
    if os.path.exists(d_path):
        ddf = pd.read_csv(d_path, index_col=0, parse_dates=True)
        ddf = ddf.reindex(pd.to_datetime(dates))
        ddf = pd.concat([ddf, new_dummies.set_index(pd.to_datetime(dates))], axis=1)
    else:
        ddf = new_dummies.set_index(pd.to_datetime(dates))
    ddf.to_csv(d_path)


# ============================ MAIN ============================

def main():
    # Load or simulate data
    levels, indicators, loaded = load_or_simulate()

    # Compute log returns from price levels
    logp = np.log(levels)
    returns = logp.diff().dropna()

    # Shift indicators by +2 days to avoid look-ahead leakage
    ind_shifted = indicators.shift(2)

    # Align & drop NaNs
    data = returns.join(ind_shifted, how="inner").dropna()
    returns_aligned = data[returns.columns]
    indicators_aligned = data[ind_shifted.columns]

    # Save bases
    save_table(returns_aligned, "returns_computed")
    save_table(indicators_aligned, "indicators_shifted_by2d")

    # Annualization factor
    ann_factor = infer_periods_per_year(returns_aligned.index)
    print(f"Annualization factor inferred: {ann_factor}")

    # ---------- Analysis 1: Sign-based ----------
    sign_based_analysis(returns_aligned, indicators_aligned, ann_factor)

    # ---------- Analysis 2: Systematic regime modeling ----------
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(indicators_aligned.values)

    regime_labels = fit_regime_models(X_scaled, indicators_aligned.index)

    # ---------- Optional: Changepoint detection ----------
    cpd_labels = fit_changepoint_models(X_scaled, indicators_aligned.index, n_bkps=6)
    regime_labels.update(cpd_labels)

    regimes_df = per_regime_factor_stats(returns_aligned, ann_factor, regime_labels, indicators_aligned.index)

    # ===== Gather ALL clusters by timepoint and save train/test slices =====
    # Start from the baseline regimes_by_model already built
    clusters = regimes_df.copy()

    # Try to merge add-on regimes if present
    addon_path = os.path.join(OUTPUT_DIR, "addon_regimes.csv")
    if os.path.exists(addon_path):
        addon = pd.read_csv(addon_path, index_col=0, parse_dates=True)
        # avoid duplicate columns if any names overlap
        for col in addon.columns:
            if col not in clusters.columns:
                clusters[col] = addon[col]

    # Ensure integer type for labels where possible
    for col in clusters.columns:
        try:
            clusters[col] = clusters[col].astype("Int64")
        except Exception:
            pass

    # Chronological split consistent with the regime prediction module
    dates_all = clusters.index
    T = len(dates_all)
    n_train = int(0.6 * T)
    n_val   = int(0.2 * T)   # we skip exporting val per your request
    # train = first 60%; test = last 20%
    train_slice = slice(0, n_train)
    test_slice  = slice(n_train + n_val, T)

    train_clusters = clusters.iloc[train_slice].copy()
    test_clusters  = clusters.iloc[test_slice].copy()

    # Save
    train_clusters.to_csv(os.path.join(OUTPUT_DIR, "train_clusters.csv"))
    test_clusters.to_csv(os.path.join(OUTPUT_DIR, "test_clusters.csv"))

    print("[Clusters] Saved train_clusters.csv and test_clusters.csv")
    # ---------- Dummies ----------
    _ = make_dummies(regimes_df, indicators_aligned)

    # ---------- Example “highlight timepoints” figure on one factor ----------
    try:
        # Prefer kmeans_ind if present; else take first model
        example_model = "kmeans_ind" if "kmeans_ind" in regimes_df.columns else regimes_df.columns[0]
        example_factor = returns_aligned.columns[0]
        cumret = (returns_aligned[example_factor]).cumsum().pipe(np.exp) - 1.0
        plot_series_with_regime_bands(
            returns_aligned.index, cumret, regimes_df[example_model].values,
            title=f"{example_factor} cumulative return — colored by {example_model}",
            fname=f"{example_factor}_{example_model}_bands"
        )
    except Exception as e:
        print(f"Skipped banded series example due to: {e}")

    # ====================== ADD-ONS START ======================
    # Scale indicators for add-ons
    X_scaler = StandardScaler().fit(indicators_aligned.values)
    X = X_scaler.transform(indicators_aligned.values)
    dates = indicators_aligned.index

    # ===== Regime Prediction Module =====
    # Choose a base label to predict (next-period); default to kmeans_ind
    if "kmeans_ind" in regime_labels:
        base_for_pred = np.asarray(regime_labels["kmeans_ind"]).astype(int)
    else:
        # fallback: any existing column
        base_for_pred = np.asarray(next(iter(regime_labels.values()))).astype(int)

    K_pred = int(np.max(base_for_pred)) + 1
    _ = run_regime_prediction_module(
        X, dates, base_for_pred, K_pred, OUTPUT_DIR, alpha=CONF_ALPHA, train_frac=0.6, val_frac=0.2
    )
    # C) Rolling deterministic Gaussian distances
    _ = rolling_gaussian_distances(X, dates, OLD_WIN, NEW_WIN)

    # A) VQ-VAE regimes
    vq_labels = None
    if TORCH_AVAILABLE:
        _, vq_idx = fit_vqvae_on_rows(X)
        vq_labels = vq_idx.astype(int)
        export_regime_artifacts("vqvae_ind", vq_labels, returns_aligned, dates)
    else:
        print("[INFO] PyTorch not available — skipping VQ-VAE add-on.")

    # B) SAINT embeddings + k-NN regimes
    saint_labels = None
    if TORCH_AVAILABLE:
        saint_emb = fit_saint_embeddings(X, epochs=12)
        km = KMeans(n_clusters=min(8, max(2, X.shape[1]*2)), n_init=10, random_state=SEED).fit(saint_emb)
        nbrs = NearestNeighbors(n_neighbors=min(KNN_K, max(2, len(saint_emb)-1))).fit(saint_emb)
        neigh = nbrs.kneighbors(return_distance=False)
        base = km.labels_
        lab = []
        for idxs in neigh:
            vals, counts = np.unique(base[idxs], return_counts=True)
            lab.append(vals[np.argmax(counts)])
        saint_labels = np.array(lab, dtype=int)
        export_regime_artifacts("saint_knn", saint_labels, returns_aligned, dates)
    else:
        print("[INFO] PyTorch not available — skipping SAINT add-on.")

    # D) Conformal prediction over a base regime model
    if CONF_BASE_MODEL in regimes_df.columns:
        base_series = regimes_df[CONF_BASE_MODEL].reindex(dates).ffill().bfill().astype(int).values
    elif vq_labels is not None:
        base_series = vq_labels
    elif saint_labels is not None:
        base_series = saint_labels
    else:
        base_series = KMeans(n_clusters=4, n_init=10, random_state=SEED).fit_predict(X)

    p_df, hard = conformalize_regimes(X, base_series, dates, alpha=CONF_ALPHA, cal_frac=CONF_CAL_FRAC)
    pd.Series(hard, index=dates, name="conformal_regime").to_csv(os.path.join(OUTPUT_DIR, "conformal_regimes.csv"))
    p_df.to_csv(os.path.join(OUTPUT_DIR, "conformal_pvalues.csv"))
    export_regime_artifacts("conformal", hard, returns_aligned, dates)

    # Add-on master table
    out = {"conformal_regime": hard, "base_for_conformal": base_series}
    if vq_labels is not None:
        out["vqvae_ind"] = vq_labels
    if saint_labels is not None:
        out["saint_knn"] = saint_labels
    addon_df = pd.DataFrame(out, index=dates)
    addon_df.to_csv(os.path.join(OUTPUT_DIR, "addon_regimes.csv"))
    # ====================== ADD-ONS END ======================

    print(f"Done. Outputs saved under: {os.path.abspath(OUTPUT_DIR)}")

# ============================ PREDICTION: ranking + conformity ============================
# Try LightGBM for LambdaMART; fallback to heuristic if unavailable.
try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except Exception:
    LGB_AVAILABLE = False

def _fit_class_gaussians(X_train, y_train, K):
    """Fit class-conditional Gaussians on X_train for regimes 0..K-1."""
    class_models = {}
    d = X_train.shape[1]
    for k in range(K):
        Xk = X_train[y_train == k]
        if len(Xk) < d + 2:
            mu = Xk.mean(0) if len(Xk) else X_train.mean(0)
            cov = np.diag(np.var(X_train, axis=0) + 1e-6)
        else:
            mu = Xk.mean(0)
            cov = np.cov(Xk.T, bias=False)
        class_models[k] = (mu, _spd_project(cov))
    return class_models

def _loglik_under_class(x, mu, cov):
    """Gaussian log-likelihood of x under N(mu, cov)."""
    d = x.shape[0]
    L = np.linalg.cholesky(cov)
    ld = 2.0 * np.sum(np.log(np.diag(L)))
    r = x - mu
    quad = np.sum(np.square(np.linalg.solve(L, r)))
    ll = -0.5 * (quad + ld + d * np.log(2*np.pi))
    return ll

def _kmeans_centroids_on_X(X, y, K):
    """Compute KMeans centroids implied by labels y on X; if a class is empty, use overall mean."""
    d = X.shape[1]
    cents = []
    mean_all = X.mean(0)
    for k in range(K):
        Xk = X[y == k]
        cents.append(Xk.mean(0) if len(Xk) else mean_all)
    return np.vstack(cents)

def _build_candidate_table(X, dates, y_next, K, class_models, centroids, pvals_df=None):
    """
    Build per-time, per-candidate features for ranking.
    y_next: next-period true label aligned to X_t (predict t+1 from X_t).
    pvals_df: DataFrame of conformal p-values (index=dates, cols=Regime_0..)
    """
    rows = []
    for i, (x, dt) in enumerate(zip(X, dates)):
        if np.isnan(y_next[i]):
            continue
        for k in range(K):
            mu, cov = class_models[k]
            ll = _loglik_under_class(x, mu, cov)
            # distance to pseudo-centroid k in X-space
            dist = float(np.linalg.norm(x - centroids[k]))
            feat = {
                "t_index": i,
                "date": pd.to_datetime(dt),
                "regime_k": k,
                "ll_k": ll,
                "dist_centroid_k": dist,
            }
            if pvals_df is not None:
                col = f"Regime_{k}"
                feat["conf_p_k"] = float(pvals_df.loc[dt, col]) if dt in pvals_df.index else 0.0
            rows.append(feat)
    cand = pd.DataFrame(rows)
    # label: 1 if candidate equals true next label else 0
    truth = pd.Series(y_next, index=np.arange(len(y_next)))
    cand["y"] = (cand.apply(lambda r: r["regime_k"] == truth.loc[int(r["t_index"])], axis=1)).astype(int)
    # groups: each time index is a query for ranking
    groups = cand.groupby("t_index").size().values
    return cand, groups

def _train_ranker_and_predict(cand_train, groups_train, cand_test, groups_test):
    feature_cols = [c for c in cand_train.columns if c in ("ll_k", "dist_centroid_k", "conf_p_k")]
    if LGB_AVAILABLE and len(feature_cols) > 0:
        ranker = lgb.LGBMRanker(
            objective="lambdarank",
            n_estimators=300,
            learning_rate=0.05,
            max_depth=-1,
            num_leaves=31,
            random_state=42
        )
        ranker.fit(
            cand_train[feature_cols], cand_train["y"],
            group=groups_train,
            eval_set=[(cand_test[feature_cols], cand_test["y"])],
            eval_group=[groups_test],
            eval_at=[1, 3, 5],
            verbose=False
        )
        cand_test["score"] = ranker.predict(cand_test[feature_cols])
        cand_train["score"] = ranker.predict(cand_train[feature_cols])
        model_used = "lightgbm_lambdamart"
    else:
        # Heuristic fallback: higher is better
        # score = ll_k  -  lambda * dist ; add p-value if present
        lam = 0.2
        cand_train["score"] = cand_train["ll_k"] - lam * cand_train["dist_centroid_k"] + cand_train.get("conf_p_k", 0.0)
        cand_test["score"]  = cand_test["ll_k"]  - lam * cand_test["dist_centroid_k"]  + cand_test.get("conf_p_k", 0.0)
        model_used = "heuristic_ll_minus_dist_plus_p"
    return cand_train, cand_test, model_used

def _topk_metrics(cand, K, alpha=0.1):
    # Top-1 accuracy and MRR
    accs, mrrs = [], []
    preds, setsizes, cover = [], [], []
    for t, grp in cand.groupby("t_index"):
        grp = grp.sort_values("score", ascending=False)
        true_k = int(grp.loc[grp["y"] == 1, "regime_k"].iloc[0]) if (grp["y"] == 1).any() else None
        # top-1
        top1 = int(grp.iloc[0]["regime_k"])
        preds.append({"t_index": t, "pred_top1": top1, "true": true_k})
        accs.append(1.0 if top1 == true_k else 0.0)
        # MRR
        rank_true = np.where(grp["regime_k"].values == true_k)[0]
        r = rank_true[0] + 1 if len(rank_true) else K
        mrrs.append(1.0 / r)
        # conformity set: use conf_p_k if present; else convert score to p-like by rank
        if "conf_p_k" in grp.columns:
            grp["p_like"] = grp["conf_p_k"]
        else:
            # monotone transform: higher score -> higher p_like
            ranks = np.arange(1, len(grp) + 1)
            grp = grp.assign(p_like=(len(grp) - ranks + 1) / len(grp))
        # smallest set whose sum p >= 1 - alpha
        cum, chosen = 0.0, []
        for _, row in grp.iterrows():
            chosen.append(int(row["regime_k"]))
            cum += float(row["p_like"])
            if cum >= 1 - alpha:
                break
        setsizes.append(len(chosen))
        cover.append(1.0 if (true_k in chosen) else 0.0)
    return {
        "top1_acc": float(np.mean(accs)) if accs else np.nan,
        "mrr": float(np.mean(mrrs)) if mrrs else np.nan,
        "coverage": float(np.mean(cover)) if cover else np.nan,
        "avg_set_size": float(np.mean(setsizes)) if setsizes else np.nan,
        "n_points": int(len(accs))
    }, pd.DataFrame(preds)

def run_regime_prediction_module(
    X, dates, base_labels, K, output_dir, alpha=0.1, train_frac=0.6, val_frac=0.2
):
    """
    Predict next-period regime using ranking over K candidates.
    Features: Gaussian log-likelihood per class, centroid distance, (optional) conformal p-values.
    Saves metrics and per-time predictions.
    """
    dates = pd.to_datetime(dates)
    T = len(X)
    # Build next-period label
    y = np.asarray(base_labels).astype(float)
    y_next = np.roll(y, -1); y_next[-1] = np.nan  # predict t+1 from X_t
    # Calibration for class Gaussians on the first chunk (train)
    n_train = int(T * train_frac)
    n_val   = int(T * val_frac)
    n_test  = T - n_train - n_val
    idx_train = slice(0, n_train)
    idx_val   = slice(n_train, n_train + n_val)
    idx_test  = slice(n_train + n_val, T)

    # Fit class Gaussians & centroids on TRAIN only
    class_models = _fit_class_gaussians(X[idx_train], y[idx_train].astype(int), K)
    cents = _kmeans_centroids_on_X(X[idx_train], y[idx_train].astype(int), K)

    # Optional: conformal p-values as features (fit using train as calibration)
    # We reuse the same class Gaussians for p-values (consistent).
    # Build p-values DataFrame for the whole period:
    P = np.zeros((T, K))
    for t in range(T):
        for k in range(K):
            mu, cov = class_models[k]
            # Use -loglik as nonconformity; calibrate on train
            # Convert to p by empirical tail on train
            a_t = -_loglik_under_class(X[t], mu, cov)
            A_cal = []
            for tt in range(n_train):
                A_cal.append(-_loglik_under_class(X[tt], mu, cov))
            P[t, k] = (np.sum(np.array(A_cal) >= a_t) + 1.0) / (len(A_cal) + 1.0)
    pvals_df = pd.DataFrame(P, index=dates, columns=[f"Regime_{k}" for k in range(K)])

    # Build candidate tables
    cand_train, g_train = _build_candidate_table(X[idx_train], dates[idx_train], y_next[idx_train], K, class_models, cents, pvals_df)
    cand_val,   g_val   = _build_candidate_table(X[idx_val],   dates[idx_val],   y_next[idx_val],   K, class_models, cents, pvals_df)
    cand_test,  g_test  = _build_candidate_table(X[idx_test],  dates[idx_test],  y_next[idx_test],  K, class_models, cents, pvals_df)

    # Train ranker (LambdaMART if available) and score
    _ , cand_val,  model_used = _train_ranker_and_predict(cand_train, g_train, cand_val, g_val)
    cand_train, cand_test, _  = _train_ranker_and_predict(cand_train, g_train, cand_test, g_test)

    # Metrics
    m_train, preds_train = _topk_metrics(cand_train, K, alpha=alpha)
    m_val,   preds_val   = _topk_metrics(cand_val,   K, alpha=alpha)
    m_test,  preds_test  = _topk_metrics(cand_test,  K, alpha=alpha)

    # Save
    metrics = pd.DataFrame(
        [m_train, m_val, m_test],
        index=["train", "val", "test"]
    )
    metrics["model"] = model_used
    metrics.to_csv(os.path.join(output_dir, "regime_prediction_metrics.csv"))

    preds = []
    for split_name, df in [("train", preds_train), ("val", preds_val), ("test", preds_test)]:
        df = df.copy()
        df["split"] = split_name
        preds.append(df)
    preds = pd.concat(preds, axis=0, ignore_index=True)
    preds.to_csv(os.path.join(output_dir, "regime_predictions.csv"), index=False)

    print(f"[RegimePrediction] model={model_used} | metrics:\n{metrics}")
    return metrics, preds
if __name__ == "__main__":
    main()
