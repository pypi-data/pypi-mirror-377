#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plotly HTML (one plot per factor *and* per forecast horizon) with TRAIN/VALIDATION-based joint selection,
HAC covariance, **no AR controls**, and UI to toggle between 'Final selection' vs 'All candidates'.

For each (factor, horizon):
  1) y_t(h) = sum of next h log-returns, aligned at t.
  2) Build candidate dummies (model_Rk_lagL), aligned via forward shift by L.
  3) TRAIN/VALIDATION joint OLS (HAC) on **dummies only**; keep dummies with p<=p_hac_max.
  4) Refit on TRAIN/VALIDATION, TEST, and FULL with kept dummies; print per-param HAC stats and Wald.
  5) Per-dummy strategy metrics (position = sign(coef_tr/val_dummy) * 1{dummy active}) on TR/VAL, TEST, FULL.
  6) Plot cum y_t(h) with background shading for both kept and all-candidate dummies.
     UI: grouped checkboxes + buttons (Final / All / Reset to Final).

Run:
  python -m regimes_lab.runners.run_shifted_bands_plotly
"""

import os, re, json, html, argparse
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import qualitative
import statsmodels.api as sm

from regimes_lab.data import prepare, _future_sum_returns
from regimes_lab.regimes import load_or_build_labels
from regimes_lab.configs import (
    STATS_TAB_DIR, STATS_FIG_DIR, TRAIN_FRAC, VAL_FRAC, HAC_LAGS
)

# ----------------------------- small utils -----------------------------

def _palette():
    return (qualitative.Set3 + qualitative.Pastel + qualitative.Set2 +
            qualitative.Set1 + qualitative.Dark24 + qualitative.D3)

def _ensure_dt_indexed(obj):
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        out = obj.copy()
        if not isinstance(out.index, pd.DatetimeIndex):
            out.index = pd.to_datetime(out.index)
        return out.sort_index()
    return obj

def _compute_edges(dates: pd.DatetimeIndex):
    dates = pd.to_datetime(dates)
    t = dates.view("int64")
    if len(t) < 2:
        edges = np.array([t[0], t[0]], dtype=np.int64)
    else:
        mids = (t[:-1] + t[1:]) // 2
        left = t[0] - (mids[0] - t[0])
        right = t[-1] + (t[-1] - mids[-1])
        edges = np.concatenate([[left], mids, [right]])
    return pd.to_datetime(edges)

def _segments_equal(labels: pd.Series, rid: int, edges: pd.DatetimeIndex):
    v = labels.values
    segs, cur_s = [], None
    for i in range(len(v)):
        ok = False
        val = v[i]
        if val is not None and not (isinstance(val, float) and np.isnan(val)):
            try:
                ok = (int(val) == int(rid))
            except Exception:
                ok = False
        if ok:
            if cur_s is None:
                cur_s = i
        else:
            if cur_s is not None:
                segs.append((edges[cur_s], edges[i]))
                cur_s = None
    if cur_s is not None:
        segs.append((edges[cur_s], edges[len(v)]))
    return segs

def _split_indices(idx: pd.DatetimeIndex):
    T = len(idx)
    n_tr = int(TRAIN_FRAC * T)
    n_va = int(VAL_FRAC * T)
    te0 = n_tr + n_va
    tr = idx[:n_tr]
    va = idx[n_tr:te0]
    te = idx[te0:]
    return tr, va, te

def _split_bounds(idx: pd.DatetimeIndex):
    """Return the first timestamp of Validation and of Test (for vertical lines)."""
    T = len(idx)
    n_tr = int(TRAIN_FRAC * T)
    n_va = int(VAL_FRAC * T)
    val_start = idx[n_tr] if n_tr < T else None
    test_start = idx[n_tr + n_va] if (n_tr + n_va) < T else None
    return val_start, test_start

def _split_date(idx: pd.DatetimeIndex, train_frac: float, val_frac: float):
    # kept for compatibility (unused now beyond vlines)
    T = len(idx)
    n_tr = int(train_frac * T)
    n_va = int(val_frac * T)
    te0 = n_tr + n_va
    if te0 <= 0 or te0 >= T:
        return None
    return idx[te0]

def _canon_dummy_name(s: str) -> str:
    s = s.strip().replace("_R_", "_R")
    m = re.match(r"^(.+?)_R(\d+)_lag(\d+)$", s)
    if m:
        return f"{m.group(1)}_R{int(m.group(2))}_lag{int(m.group(3))}"
    m2 = re.match(r"^(.+?)_R(\d+)$", s)
    if m2:
        return f"{m2.group(1)}_R{int(m2.group(2))}_lag1"
    return s

# ----------------------------- file discovery -----------------------------

def _index_selection_files():
    """Return dict: factor -> {'agg': path|None, 'legacy': {h:path, ...}}"""
    idx = {}
    for f in os.listdir(STATS_TAB_DIR):
        if not (f.startswith("COMBINED_SELECTED_") and f.endswith(".json")):
            continue
        p = os.path.join(STATS_TAB_DIR, f)
        m = re.match(r"^COMBINED_SELECTED_(.+?)\.json$", f)
        if m:
            fac = m.group(1)
            d = idx.setdefault(fac, {"agg": None, "legacy": {}})
            d["agg"] = p
            continue
        m2 = re.match(r"^COMBINED_SELECTED_(.+?)_h(\d+)\.json$", f)
        if m2:
            fac, h = m2.group(1), int(m2.group(2))
            d = idx.setdefault(fac, {"agg": None, "legacy": {}})
            d["legacy"][h] = p
    return idx

def _read_payload(path, factor_hint=None, horizon_hint=None):
    obj = json.load(open(path, "r"))
    if "horizons" in obj and "selections" in obj:
        fac = obj.get("factor") or factor_hint
        return dict(kind="agg", factor=fac, horizons=list(map(int, obj.get("horizons", []))), payload=obj)
    fac = factor_hint
    h = int(horizon_hint) if horizon_hint is not None else None
    obj.setdefault("factor", fac)
    obj.setdefault("selections", obj.get("selections", {}))
    obj.setdefault("chosen_unique", list(obj["selections"].keys()))
    return dict(kind="legacy", factor=fac, horizons=[h] if h else [], payload=obj)

# ----------------------------- selection extraction -----------------------------

def _rows_for_horizon(payload, horizon):
    sels = payload.get("selections", {})
    chosen = payload.get("chosen_unique", []) or list(sels.keys())
    rows = []
    for raw in chosen:
        nm = _canon_dummy_name(raw)
        rec = sels.get(raw) or sels.get(nm) or {}
        stat = None
        for oc in rec.get("occurrences", []):
            if int(oc.get("horizon", -1)) == int(horizon):
                stat = oc; break
        if stat is None and int(rec.get("best", {}).get("horizon", -1)) == int(horizon):
            stat = rec["best"]
        if stat is None:
            continue
        m = re.match(r"^(.+?)_R(\d+)_lag(\d+)$", nm)
        if not m:
            continue
        model, rid, lag = m.group(1), int(m.group(2)), int(m.group(3))
        rows.append(dict(
            name=nm, model=model, rid=rid, lag=lag, horizon=int(horizon)
        ))
    return rows

# ----------------------------- data builders -----------------------------

def _build_dummy_matrix(y_index, L_full: pd.DataFrame, defs):
    cols = []
    for d in defs:
        model, rid, lag, nm = d["model"], int(d["rid"]), int(d["lag"]), d["name"]
        if model not in L_full.columns:
            continue
        lab = pd.to_numeric(L_full[model], errors="coerce")
        col = (lab.shift(lag).reindex(y_index) == rid).astype(float)
        col.name = nm
        cols.append(col)
    if not cols:
        return pd.DataFrame(index=y_index)
    return pd.concat(cols, axis=1)

# ----------------------------- statsmodels helpers -----------------------------

def _ols_hac(y: pd.Series, X: pd.DataFrame, hac_lags: int, min_rows: int = 30):
    df = pd.concat([y.rename("y"), X], axis=1, join="inner")
    df = df.replace([np.inf, -np.inf], np.nan).dropna(axis=0, how="any")
    if df.shape[0] < max(min_rows, X.shape[1] + 2):
        return None
    y_clean = df["y"].astype(float)
    Xc = sm.add_constant(df.drop(columns=["y"]).astype(float), has_constant="add")
    res = sm.OLS(y_clean, Xc, missing="drop").fit(
        cov_type="HAC", cov_kwds={"maxlags": int(hac_lags)}
    )
    return res

def _wald_all_dummies(res, dummy_cols):
    if not dummy_cols:
        return None
    names = [nm for nm in res.params.index if nm in dummy_cols]
    if not names:
        return None
    R = np.zeros((len(names), len(res.params)))
    for i, nm in enumerate(names):
        j = list(res.params.index).index(nm)
        R[i, j] = 1.0
    return res.wald_test(R)

def _per_param_table(res, keep_cols=None):
    params = res.params
    cov = res.cov_params()
    se = np.sqrt(np.clip(np.diag(cov), 1e-18, np.inf))
    tvals = params / se
    rows = []
    for nm in params.index:
        if nm == "const":
            rows.append(dict(dummy="const", model="", regime="", lag="",
                             coef=float(params[nm]), t_hac=float(tvals[nm]),
                             p_hac=float(res.pvalues[nm]), se_hac=float(se[list(params.index).index(nm)])))
            continue
        if (keep_cols is not None) and (nm not in keep_cols):
            continue
        model = re.match(r"^(.+?)_R", nm).group(1) if re.match(r"^(.+?)_R", nm) else ""
        regime = int(re.search(r"_R(\d+)", nm).group(1)) if re.search(r"_R(\d+)", nm) else ""
        lag = int(re.search(r"_lag(\d+)", nm).group(1)) if re.search(r"_lag(\d+)", nm) else ""
        rows.append(dict(dummy=nm, model=model, regime=regime, lag=lag,
                         coef=float(params[nm]), t_hac=float(tvals[nm]),
                         p_hac=float(res.pvalues[nm]), se_hac=float(se[list(params.index).index(nm)])))
    return pd.DataFrame(rows)

# ----------------------------- performance metrics -----------------------------

def _perf_metrics(y: pd.Series, signal: pd.Series):
    """
    Compute per-dummy strategy metrics using ONLY periods where the dummy is ON (signal != 0).
    Returns daily mean, daily vol (ddof=0), annualized Sharpe (sqrt(252)),
    n = number of ACTIVE observations, and total = sum over ACTIVE periods.
    """
    base = pd.concat([y.rename("y"), signal.rename("sig")], axis=1, join="inner").dropna()
    base = base[base["sig"] != 0]
    if base.empty:
        return dict(mean=np.nan, vol=np.nan, sharpe=np.nan, n=0, total=np.nan)
    r = base["sig"] * base["y"]
    mu = r.mean()
    sd = r.std(ddof=0)
    ann_scale = np.sqrt(252.0)
    sharpe = (mu / sd * ann_scale) if (sd > 0 and np.isfinite(sd)) else np.nan
    return dict(mean=float(mu), vol=float(sd), sharpe=float(sharpe),
                n=int(r.size), total=float(r.sum()))

def _strategy_sign_from_train(res_train):
    signs = {}
    for nm in res_train.params.index:
        if nm in ("const",):
            continue
        try:
            signs[nm] = float(np.sign(float(res_train.params[nm])))
        except Exception:
            signs[nm] = 0.0
    return signs

def _dummy_signal_series(Dcol: pd.Series, sign_val: float):
    return (np.where(Dcol.values > 0.5, sign_val, 0.0)).astype(float)

# ----------------------------- controls / shading -----------------------------

def _group_for_controls(names):
    by_model = {}
    for nm in names:
        m = re.match(r"^(.+?)_R(\d+)_lag(\d+)$", nm)
        if not m:
            continue
        model, rid, lag = m.group(1), int(m.group(2)), int(m.group(3))
        by_model.setdefault(model, []).append((rid, lag, nm))
    for k in by_model:
        by_model[k].sort(key=lambda x: (x[0], x[1]))
    return by_model

def _controls_html_grouped(final_names, all_names):
    fin_by = _group_for_controls(final_names)
    all_by = _group_for_controls(all_names)

    # union of models to print both sections (final + others)
    models = sorted(set(list(fin_by.keys()) + list(all_by.keys())))
    lines = [
        "<div id='regime-controls' style='margin:8px 0 10px 0;font-family:Inter,system-ui,Arial,sans-serif;font-size:12px;line-height:1.5;'>",
        "<b>Regime shading (final selected by TRAIN/VAL):</b>",
        "<div style='margin:6px 0;'>",
        "<button id='btn-final' style='margin-right:6px; font-size:12px;'>Final</button>",
        "<button id='btn-all' style='margin-right:6px; font-size:12px;'>All</button>",
        "<button id='btn-reset' style='font-size:12px;'>Reset to Final</button>",
        "</div>"
    ]
    for model in models:
        chips = []
        seen = set()
        # final first
        for rid, lag, nm in fin_by.get(model, []):
            label = f"R{rid}_lag{lag}"
            chips.append(
                f"<label style='margin:0 10px 0 10px; white-space:nowrap;'>"
                f"<input type='checkbox' class='regime-toggle' data-regname='{html.escape(nm)}' data-group='final' checked> {label}"
                f"</label>"
            )
            seen.add(nm)
        # then candidate-only
        for rid, lag, nm in all_by.get(model, []):
            if nm in seen:
                continue
            label = f"R{rid}_lag{lag}"
            chips.append(
                f"<label style='margin:0 10px 0 10px; white-space:nowrap;'>"
                f"<input type='checkbox' class='regime-toggle' data-regname='{html.escape(nm)}' data-group='candidate'> {label}"
                f"</label>"
            )
        if chips:
            lines.append(f"<div><span style='font-weight:600'>{html.escape(model)}:</span> {''.join(chips)}</div>")
    lines.append("</div>")
    # JS
    lines.append(r"""
<script>
(function(){
  function deepCopyShapes(gd){ return (gd.layout && gd.layout.shapes) ? JSON.parse(JSON.stringify(gd.layout.shapes)) : []; }
  function setShapes(gd, shapes){ Plotly.relayout(gd, {'shapes': shapes}); }
  function toggleByName(gd, name, on){
    const shapes = deepCopyShapes(gd);
    for (let i=0; i<shapes.length; ++i){
      if ((shapes[i].name || '') === name){
        shapes[i].opacity = on ? 0.28 : 0.0;
        shapes[i].visible = true;
      }
    }
    setShapes(gd, shapes);
  }
  function setGroup(gd, groupName, on){
    const panel = document.getElementById('regime-controls');
    const boxes = panel.querySelectorAll('input.regime-toggle');
    boxes.forEach(function(box){
      const grp = box.getAttribute('data-group') || '';
      if ((groupName === 'all') || (grp === groupName)){
        box.checked = on;
        const nm = box.getAttribute('data-regname');
        toggleByName(gd, nm, on);
      }
    });
  }
  function setFinalOnly(gd){
    const panel = document.getElementById('regime-controls');
    const boxes = panel.querySelectorAll('input.regime-toggle');
    boxes.forEach(function(box){
      const isFinal = (box.getAttribute('data-group') || '') === 'final';
      box.checked = isFinal;
      const nm = box.getAttribute('data-regname');
      toggleByName(gd, nm, isFinal);
    });
  }
  window.addEventListener('load', function(){
    const gd = document.querySelector('div.plotly-graph-div');
    const panel = document.getElementById('regime-controls');
    if(!gd || !panel) return;

    panel.querySelectorAll('input.regime-toggle').forEach(function(box){
      const nm = box.getAttribute('data-regname');
      // initialize based on default checked state
      toggleByName(gd, nm, box.checked);
      box.addEventListener('change', function(){ toggleByName(gd, nm, box.checked); });
    });

    document.getElementById('btn-final').addEventListener('click', function(){
      setFinalOnly(gd);
    });
    document.getElementById('btn-all').addEventListener('click', function(){
      setGroup(gd, 'all', true);
    });
    document.getElementById('btn-reset').addEventListener('click', function(){
      setFinalOnly(gd);
    });
  });
})();
</script>
""")
    return "\n".join(lines)

def _add_background_shapes(fig, idx, L_full, final_names, all_names):
    pal = _palette()
    edges = _compute_edges(idx)
    shapes = []
    color_map, ci = {}, 0

    # Same color per (model, rid) across final/candidate
    def _parse(nm):
        m = re.match(r"^(.+?)_R(\d+)_lag(\d+)$", nm)
        if not m: return None
        return (nm, m.group(1), int(m.group(2)), int(m.group(3)))

    parsed_all = [p for p in map(_parse, set(all_names) | set(final_names)) if p]
    for _, model, rid, _ in parsed_all:
        key = (model, rid)
        if key not in color_map:
            color_map[key] = pal[ci % len(pal)]
            ci += 1

    def _shapes_for(nm_list, group):
        for nm, model, rid, lag in [p for p in map(_parse, nm_list) if p]:
            if model not in L_full.columns:
                continue
            lab = pd.to_numeric(L_full[model], errors="coerce").reindex(idx)
            series = lab.shift(lag)
            for x0, x1 in _segments_equal(series, rid, edges):
                shapes.append(dict(
                    type="rect", xref="x", yref="paper",
                    x0=x0, x1=x1, y0=0.0, y1=1.0,
                    line=dict(width=0), fillcolor=color_map[(model, rid)],
                    opacity=0.28 if (group=="final") else 0.0,  # candidates start transparent
                    layer="below", name=nm
                ))

    _shapes_for(all_names, "candidate")
    _shapes_for(final_names, "final")
    if shapes:
        fig.layout.shapes = tuple(shapes)

# ----------------------------- HTML report blocks -----------------------------

def _styled_table_html(df: pd.DataFrame, title: str):
    if df is None or df.empty:
        return f"<div style='margin:8px 0 2px 0; font-weight:600;'>{html.escape(title)}</div><div style='color:#777'>[empty]</div>"
    fmt = df.copy()
    for col in ["coef","t_hac","p_hac","se_hac","mean","vol","sharpe","total"]:
        if col in fmt.columns:
            fmt[col] = pd.to_numeric(fmt[col], errors="coerce")
    for c in ["coef","t_hac","se_hac","mean","vol","sharpe","total"]:
        if c in fmt.columns:
            fmt[c] = fmt[c].map(lambda x: f"{x:.6g}" if pd.notna(x) else "")
    if "p_hac" in fmt.columns:
        fmt["p_hac"] = fmt["p_hac"].map(lambda x: f"{x:.6g}" if pd.notna(x) else "")
    preferred = [c for c in ["dummy","model","regime","lag","coef","t_hac","p_hac","se_hac","subset",
                             "mean","vol","sharpe","n","total"] if c in fmt.columns]
    fmt = fmt[preferred]
    css = """
<style>
.table-lite { border-collapse: collapse; font-size:12px; }
.table-lite th { text-align:left; padding:6px 10px; border-bottom:1px solid #ddd; background:#fafafa; }
.table-lite td { padding:6px 10px; border-top:1px solid #f2f2f2; }
</style>
"""
    return css + f"<div style='margin:10px 0 6px 0; font-weight:600;'>{html.escape(title)}</div>" + fmt.to_html(index=False, escape=False, classes="table-lite")

def _joint_block_html(res, dummy_cols, subtitle):
    if res is None:
        return f"<div style='margin-top:8px; color:#777;'>No joint model ({html.escape(subtitle)}).</div>"
    wald = _wald_all_dummies(res, dummy_cols)
    wald_html = ""
    if wald is not None:
        try:
            stat = float(wald.statistic); pval = float(wald.pvalue)
            df_num = getattr(wald, "df_num", len(dummy_cols))
            df_den = getattr(wald, "df_denom", "")
            wald_html = (f"<div><b>Joint Wald (all dummy coeffs = 0)</b>: "
                         f"stat={stat:.4g}, p={pval:.4g}, df=({df_num},{html.escape(str(df_den))})</div>")
        except Exception:
            pass
    tab = _per_param_table(res, keep_cols=set(dummy_cols) | {"const"})
    return "<div style='margin-top:8px;'>" + wald_html + _styled_table_html(tab, f"Joint OLS (HAC) — {subtitle}") + "</div>"

def _perf_block_html(perf_rows: pd.DataFrame, subtitle: str):
    return _styled_table_html(perf_rows, f"Per-dummy strategy metrics — {subtitle}")

# ----------------------------- one plot per (factor, horizon) -----------------------------

def _write_one_factor_h(R, L_full, factor, horizon, payload):
    # target
    Yh = _future_sum_returns(R, int(horizon))
    if factor not in Yh.columns:
        print(f"[plotly] WARN: factor '{factor}' not in future-sum returns (h={horizon}); skip.")
        return
    y = Yh[factor].dropna()
    if y.empty:
        print(f"[plotly] WARN: empty y for {factor}, h={horizon}; skip.")
        return

    # candidates for this horizon
    defs = _rows_for_horizon(payload, horizon)
    cand_names = [d["name"] for d in defs]
    if not defs:
        # curve-only for traceability
        cum = y.cumsum().pipe(np.exp) - 1.0
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=cum.index, y=cum.values, mode="lines",
                                 name=f"{factor} cumret (h={horizon})", line=dict(width=1.8)))
        fig.update_layout(title=f"{factor} — cumulative return of yₜ(h={horizon})",
                          xaxis_title="Date", yaxis_title="Cumulative return",
                          template="plotly_white", height=560,
                          margin=dict(l=60, r=20, t=70, b=60), showlegend=False)
        out_html = os.path.join(STATS_FIG_DIR, f"cumret_multi_{factor}_h{int(horizon)}.html")
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(fig.to_html(full_html=True, include_plotlyjs="inline"))
        print(f"[plotly] INFO: no selections for {factor}, h={horizon}; curve-only plot.")
        return

    # design matrices
    D_full = _build_dummy_matrix(y.index, L_full, defs)
    if D_full.empty:
        print(f"[plotly] INFO: no valid dummies for {factor}, h={horizon} (labels missing?); curve-only.")
        cum = y.cumsum().pipe(np.exp) - 1.0
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=cum.index, y=cum.values, mode="lines",
                                 name=f"{factor} cumret (h={horizon})", line=dict(width=1.8)))
        fig.update_layout(title=f"{factor} — cumulative return of yₜ(h={horizon})",
                          xaxis_title="Date", yaxis_title="Cumulative return",
                          template="plotly_white", height=560,
                          margin=dict(l=60, r=20, t=70, b=60), showlegend=False)
        out_html = os.path.join(STATS_FIG_DIR, f"cumret_multi_{factor}_h{int(horizon)}.html")
        with open(out_html, "w", encoding="utf-8") as f:
            f.write(fig.to_html(full_html=True, include_plotlyjs="inline"))
        return

    # split indices
    tr_idx, va_idx, te_idx = _split_indices(y.index)
    trva_idx = tr_idx.union(va_idx)
    full_idx = y.index

    # TRAIN/VALIDATION selection (joint on all candidates)
    X_sel_train = D_full.loc[trva_idx]
    res_sel = _ols_hac(y.loc[trva_idx], X_sel_train, HAC_LAGS)
    if res_sel is None:
        print(f"[plotly] WARN: not enough rows to run TRAIN/VAL OLS for {factor}, h={horizon}.")
        return

    # keep if p<=threshold (on TRAIN/VAL) for DUMMY params
    thr = 0.05
    try:
        thr = float(payload.get("thresholds", {}).get("p_hac_max", thr))
    except Exception:
        pass
    pvals_trva = res_sel.pvalues
    kept_names = [nm for nm in D_full.columns if nm in pvals_trva.index and pvals_trva[nm] <= thr]

    # Refit joint OLS without AR on TR/VAL, TEST, FULL
    def _fit_subset(idx):
        X = D_full[kept_names].loc[idx]
        return _ols_hac(y.loc[idx], X, HAC_LAGS)

    res_trva = _fit_subset(trva_idx) if kept_names else None
    res_te   = _fit_subset(te_idx)    if kept_names else None
    res_all  = _ols_hac(y, D_full[kept_names], HAC_LAGS) if kept_names else None

    # Strategy performance for kept dummies
    perf_df = pd.DataFrame()
    if kept_names and res_trva is not None:
        signs = _strategy_sign_from_train(res_trva)
        rows = []
        for nm in kept_names:
            s = float(signs.get(nm, 0.0))
            sig_full = pd.Series(_dummy_signal_series(D_full[nm], s), index=D_full.index)
            rows.append(dict(dummy=nm, model=re.match(r"^(.+?)_R", nm).group(1),
                             regime=int(re.search(r"_R(\d+)", nm).group(1)),
                             lag=int(re.search(r"_lag(\d+)", nm).group(1)),
                             subset="TRAIN/VAL", **_perf_metrics(y.loc[trva_idx], sig_full.loc[trva_idx])))
            rows.append(dict(dummy=nm, model=re.match(r"^(.+?)_R", nm).group(1),
                             regime=int(re.search(r"_R(\d+)", nm).group(1)),
                             lag=int(re.search(r"_lag(\d+)", nm).group(1)),
                             subset="TEST",  **_perf_metrics(y.loc[te_idx], sig_full.loc[te_idx])))
            rows.append(dict(dummy=nm, model=re.match(r"^(.+?)_R", nm).group(1),
                             regime=int(re.search(r"_R(\d+)", nm).group(1)),
                             lag=int(research := re.search(r"_lag(\d+)", nm).group(1)),
                             subset="FULL",  **_perf_metrics(y.loc[full_idx], sig_full.loc[full_idx])))
        perf_df = pd.DataFrame(rows)

    # Build figure (cum y_t(h))
    cum = y.cumsum().pipe(np.exp) - 1.0

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cum.index, y=cum.values, mode="lines",
        name=f"{factor} cumret (h={horizon})", line=dict(width=1.8)
    ))
    fig.update_layout(
        title=f"{factor} — cumulative return of yₜ(h={horizon})",
        xaxis_title="Date", yaxis_title="Cumulative return",
        template="plotly_white", height=600,
        margin=dict(l=60, r=20, t=70, b=60),
        showlegend=False
    )

    # Shading: include both sets; final active, candidates transparent
    _add_background_shapes(fig, cum.index, L_full, kept_names, cand_names)
    controls_html = _controls_html_grouped(kept_names, cand_names)

    # Visible split lines (Train→Validation, Validation→Test) for context only
    val_start, test_start = _split_bounds(cum.index)
    if val_start is not None:
        fig.add_vline(x=val_start, line_width=2.5, line_dash="dash", line_color="#1f77b4", opacity=0.95)
    if test_start is not None:
        fig.add_vline(x=test_start, line_width=2.5, line_dash="dash", line_color="#d62728", opacity=0.95)

    # Reports
    block_sel   = _joint_block_html(res_sel, D_full.columns.tolist(), "TRAIN/VAL (selection on all candidates)")
    block_trva  = _joint_block_html(res_trva, kept_names, "TRAIN/VAL (kept)") if kept_names else ""
    block_te    = _joint_block_html(res_te,   kept_names, "TEST (kept)")       if kept_names else ""
    block_all   = _joint_block_html(res_all,  kept_names, "FULL (kept)")       if kept_names else ""
    block_pf    = _perf_block_html(perf_df,   "TRAIN/VAL / TEST / FULL")       if kept_names else ""

    report_html = "<div style='margin-top:10px;'>" + block_sel + block_trva + block_te + block_all + block_pf + "</div>"

    # Write HTML
    os.makedirs(STATS_FIG_DIR, exist_ok=True)
    out_html = os.path.join(STATS_FIG_DIR, f"cumret_multi_{factor}_h{int(horizon)}.html")
    blob = fig.to_html(full_html=True, include_plotlyjs="inline")
    blob = blob.replace('<div id="', controls_html + '\n<div id="', 1)
    blob = blob.replace('</body>', report_html + '\n</body>', 1)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(blob)
    print(f"[plotly] wrote {out_html}")

# ----------------------------- main -----------------------------

def main():
    ap = argparse.ArgumentParser()
    args = ap.parse_args()

    os.makedirs(STATS_FIG_DIR, exist_ok=True)
    os.makedirs(STATS_TAB_DIR, exist_ok=True)

    # Data & labels
    R, IND = prepare()
    L_full = load_or_build_labels(IND, split_tag="full")
    R = _ensure_dt_indexed(R)
    L_full = _ensure_dt_indexed(L_full)

    file_index = _index_selection_files()
    if not file_index:
        print("[plotly] No COMBINED_SELECTED_*.json found.")
        return

    for factor, files in sorted(file_index.items()):
        if files.get("agg"):
            info = _read_payload(files["agg"], factor_hint=factor)
            horizons = info["horizons"] or [1]
            for h in horizons:
                _write_one_factor_h(R, L_full, factor, h, info["payload"])
            continue
        for h, path in sorted(files.get("legacy", {}).items()):
            info = _read_payload(path, factor_hint=factor, horizon_hint=h)
            for hh in (info["horizons"] or [h]):
                _write_one_factor_h(R, L_full, factor, hh, info["payload"])

    print("[plotly] Done. See", STATS_FIG_DIR)

if __name__ == "__main__":
    main()