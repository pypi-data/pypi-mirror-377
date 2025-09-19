# -*- coding: utf-8 -*-
import os, math, re, json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_hac

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash import Dash, dcc, html, Input, Output, State, ALL
import dash_bootstrap_components as dbc

# --------------------- project imports ---------------------
from regimes_lab.data import prepare  # returns (R, IND, X_by_h)
from regimes_lab.regimes import load_or_build_labels
from regimes_lab.configs import (
    TRAIN_FRAC, VAL_FRAC, HAC_LAGS, DEFAULT_HORIZONS,
    STATS_FIG_DIR,
)

# --------------------- data & dirs -------------------------
os.makedirs(STATS_FIG_DIR, exist_ok=True)
# tables dir (where COMBINED_SELECTED_{factor}_h{h}.json lives)
STATS_TAB_DIR = os.path.join("regimes_lab", "output", "stats", "tables")
os.makedirs(STATS_TAB_DIR, exist_ok=True)

# Load once at server boot
R, IND, X_by_h = prepare(horizons=DEFAULT_HORIZONS)   # R: returns df indexed by date
L_full = load_or_build_labels(IND, split_tag="full")  # wide df of label columns (one column per model)

ALL_MODELS = list(L_full.columns)
ALL_FACTORS = list(R.columns)

# --------------------- utils: split & future returns -------------------------
def future_sum_returns(R: pd.DataFrame, h: int) -> pd.DataFrame:
    """Sum of next-h daily log-returns aligned at t."""
    if h is None or int(h) <= 1:
        return R.copy()
    h = int(h)
    return R.rolling(h).sum().shift(-h + 1)

def split_date(idx: pd.DatetimeIndex, train_frac: float, val_frac: float):
    T = len(idx)
    n_tr = int(train_frac * T)
    n_va = int(val_frac * T)
    te0 = n_tr + n_va
    if te0 <= 0 or te0 >= T:
        return None
    return idx[te0]

# ----------------- expression parser (AND/OR/XOR/NOT, ==, in {…}) -----------------
_TOKEN_SPEC = [
    ("WS",       r"[ \t\n\r]+"),
    ("LP",       r"\("),
    ("RP",       r"\)"),
    ("AND",      r"AND\b"),
    ("OR",       r"OR\b"),
    ("XOR",      r"XOR\b"),
    ("NOT",      r"NOT\b"),
    ("IN",       r"in\b"),
    ("EQ",       r"=="),
    ("LBRACE",   r"\{"),
    ("RBRACE",   r"\}"),
    ("COMMA",    r","),
    ("NUM",      r"-?\d+"),
    ("NAME",     r"[A-Za-z_][A-Za-z0-9_]*"),
]
_TOKEN_RE = re.compile("|".join(f"(?P<{n}>{p})" for n, p in _TOKEN_SPEC))

class _Tok:
    def __init__(self, typ, val):
        self.typ, self.val = typ, val

def _lex(s: str):
    pos = 0
    while pos < len(s):
        m = _TOKEN_RE.match(s, pos)
        if not m:
            raise ValueError(f"Unexpected char at {pos}: {s[pos:pos+20]!r}")
        typ = m.lastgroup; val = m.group()
        pos = m.end()
        if typ == "WS":
            continue
        yield _Tok(typ, val)

def _parse_expr(tokens_iter):
    tokens = list(tokens_iter)
    i = 0

    def peek():
        return tokens[i] if i < len(tokens) else None

    def eat(kind):
        nonlocal i
        if i < len(tokens) and tokens[i].typ == kind:
            i += 1
            return True
        return False

    def expect(kind):
        if not eat(kind):
            raise ValueError(f"Expected {kind} at token {i}, got {peek()}")

    def parse_num_list():
        nonlocal i
        vals = []
        expect("LBRACE")
        first = True
        while True:
            tok = peek()
            if tok is None:
                raise ValueError("Unclosed { ... }")
            if tok.typ == "RBRACE":
                eat("RBRACE")
                break
            if not first:
                expect("COMMA")
            tok = peek()
            if tok is None or tok.typ != "NUM":
                raise ValueError("Expected number in { ... }")
            vals.append(int(tok.val))
            eat("NUM")
            first = False
        return vals

    def atom():
        if eat("LP"):
            node = expr()
            expect("RP")
            return ("group", node)
        tok = peek()
        if tok and tok.typ == "NAME":
            name = tok.val; eat("NAME")
            if eat("EQ"):
                tok2 = peek()
                if tok2 is None or tok2.typ != "NUM":
                    raise ValueError("Expected number after '=='")
                val = int(tok2.val); eat("NUM")
                return ("eq", name, val)
            if eat("IN"):
                vals = parse_num_list()
                return ("in", name, vals)
            raise ValueError("Expected '==' or 'in' after model name")
        raise ValueError(f"Bad atom at token {i}: {peek()}")

    def unary():
        if eat("NOT"):
            return ("not", unary())
        return atom()

    def and_term():
        node = unary()
        while eat("AND"):
            node = ("and", node, unary())
        return node

    def xor_term():
        node = and_term()
        while eat("XOR"):
            node = ("xor", node, and_term())
        return node

    def expr():
        node = xor_term()
        while eat("OR"):
            node = ("or", node, xor_term())
        return node

    node = expr()
    if i != len(tokens):
        raise ValueError("Extra tokens at end")
    return node

def eval_expr_mask(node, L_by_model: dict, shift: int, index: pd.DatetimeIndex) -> pd.Series:
    """Evaluate parsed AST to boolean mask."""
    idx = index

    def ev(n):
        typ = n[0]
        if typ == "group":
            return ev(n[1])
        if typ == "eq":
            _, name, val = n
            if name not in L_by_model: return pd.Series(False, index=idx)
            s = L_by_model[name].shift(shift).reindex(idx)
            return s.eq(val).fillna(False)
        if typ == "in":
            _, name, vals = n
            if name not in L_by_model: return pd.Series(False, index=idx)
            s = L_by_model[name].shift(shift).reindex(idx)
            return s.isin(set(int(v) for v in vals)).fillna(False)
        if typ == "not":
            return ~ev(n[1])
        if typ == "and":
            return ev(n[1]) & ev(n[2])
        if typ == "or":
            return ev(n[1]) | ev(n[2])
        if typ == "xor":
            a = ev(n[1]); b = ev(n[2]); return a ^ b
        raise ValueError(f"Unknown node {typ}")
    return ev(node).astype(bool)

# ----------------- picks & masks -----------------
def read_combined_picks(factor: str, h: int) -> dict:
    """
    Read COMBINED_SELECTED_{factor}_h{h}.json and convert to:
      {model: {"regimes":[...], "lag": h}, ...}
    """
    path = os.path.join(STATS_TAB_DIR, f"COMBINED_SELECTED_{factor}_h{int(h)}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r") as fh:
        dd = json.load(fh)
    chosen = dd.get("chosen_dummies", []) or []
    out = {}
    for name in chosen:
        # e.g. "hmm_gauss_R_9" or "cpd_binseg_R_3"
        m = re.match(r"^([A-Za-z0-9_]+)_R_(-?\d+)$", str(name))
        if not m:
            continue
        model, rid = m.group(1), int(m.group(2))
        out.setdefault(model, {"regimes": [], "lag": int(h)})
        if rid not in out[model]["regimes"]:
            out[model]["regimes"].append(rid)
    return out

def picks_from_ui(models: list[str], regime_lists: list[list[int]], h: int) -> dict:
    """UI picker -> {model:{regimes:[...], lag:h}}; ignore empty."""
    out = {}
    for m, vals in zip(models or [], regime_lists or []):
        if not vals:
            continue
        out[m] = {"regimes": [int(v) for v in vals], "lag": int(h)}
    return out

def mask_from_picks(L_by_model: dict[str, pd.Series], picks: dict, logic: str,
                    index: pd.DatetimeIndex) -> pd.Series:
    """Combine model/regime+lag picks into a boolean mask on 'index'."""
    idx = index
    if not picks:
        return pd.Series(False, index=idx)
    acc = None
    for m, cfg in picks.items():
        if m not in L_by_model:
            continue
        regimes = set(cfg.get("regimes", []))
        lag = int(cfg.get("lag", 0))
        s = L_by_model[m].shift(lag).reindex(idx)
        msk = s.isin(regimes).fillna(False)
        if acc is None:
            acc = msk
        else:
            if logic == "AND":
                acc = acc & msk
            elif logic == "XOR":
                acc = acc ^ msk
            else:
                acc = acc | msk
    return acc if acc is not None else pd.Series(False, index=idx)

# ----------------- design & OLS(HAC) -----------------
def design_from_mask_and_indicators(X: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    Z = X.copy()
    Z = Z.apply(pd.to_numeric, errors="coerce")
    Z["Z"] = mask.astype(float)
    Z = Z.replace([np.inf, -np.inf], np.nan).dropna(axis=0, how="any")
    nunique = Z.nunique(dropna=False)
    Z = Z.loc[:, nunique > 1]
    return Z

def ols_hac_full(y: pd.Series, X: pd.DataFrame, hac_lags: int):
    """
    OLS with HAC cov. Returns (res, res_hac) where res_hac has robust cov.
    Works across statsmodels versions by passing both keys.
    """
    df = pd.concat([y.rename("y"), X], axis=1, join="inner").dropna()
    if df.shape[0] < max(20, X.shape[1] + 2):
        return None, None
    yv = df["y"].astype("float64")
    Xv = sm.add_constant(df.drop(columns=["y"]).astype("float64"), has_constant="add")
    res = sm.OLS(yv, Xv).fit()

    # Compute HAC covariance and attach; and also try robustcov wrapper for pretty summaries.
    cov = cov_hac(res, nlags=int(hac_lags))
    try:
        # newer statsmodels accepts 'nlags', older wants 'maxlags'
        res_hac = res.get_robustcov_results(
            cov_type="HAC",
            use_correction=True,
            cov_kwds={"maxlags": int(hac_lags), "nlags": int(hac_lags)}
        )
        # force the HAC cov we computed (preserve param names if possible)
        res_hac.cov_params_default = cov
        return res, res_hac
    except Exception:
        # fall back: create a shallow wrapper with cov set
        res.cov_params_default = cov
        return res, res  # summary will still show (non-robust), but we keep cov for Z

# ----------------- background shading -----------------
def subplot_axis_ids(row: int, col: int, ncols: int):
    """
    Return (xref, yref) like ('x','y') or ('x2','y2') for a subplot position.
    Plotly numbers subplots row-wise: idx = (row-1)*ncols + col, first has no suffix.
    """
    idx = (row - 1) * ncols + col
    suf = "" if idx == 1 else str(idx)
    return f"x{suf}", f"y{suf}"

def add_background_bands(fig: go.Figure, r: int, c: int, ncols: int,
                         x: pd.DatetimeIndex, mask: pd.Series, y_min: float, y_max: float,
                         color: str):
    """
    Shade THIS subplot's background where mask==True.
    Shapes are bound to the subplot's x/y axes so they always show.
    """
    if mask is None or x is None or len(x) == 0:
        return

    xref, yref = subplot_axis_ids(r, c, ncols)

    m = mask.reindex(x).fillna(False).to_numpy()
    if m.size == 0:
        return

    starts, ends, start = [], [], None
    for i, val in enumerate(m):
        if val and start is None:
            start = i
        if (not val or i == len(m) - 1) and start is not None:
            end_i = i if val else i - 1
            if end_i >= start:
                starts.append(start)
                ends.append(end_i)
            start = None

    # vertical range: small padding
    if np.isfinite(y_min) and np.isfinite(y_max):
        pad = 0.02 * (y_max - y_min if y_max != y_min else 1.0)
        y0 = y_min - pad
        y1 = y_max + pad
    else:
        y0, y1 = -1.0, 1.0

    for s, e in zip(starts, ends):
        x0 = x[max(0, s)]
        x1 = x[min(e + 1, len(x) - 1)]
        fig.add_shape(
            type="rect",
            xref=xref, yref=yref,
            x0=x0, x1=x1, y0=y0, y1=y1,
            fillcolor=color, opacity=0.22,
            line=dict(width=0),
            layer="below",
        )

# ----------------- Dash UI -----------------
app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
server = app.server

controls = dbc.Card([
    html.H5("Controls", className="card-title"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Factors"),
            dcc.Dropdown(
                id="factors", options=[{"label": c, "value": c} for c in ALL_FACTORS],
                value=ALL_FACTORS[:6], multi=True
            ),
        ], md=6),
        dbc.Col([
            dbc.Label("Rows"),
            dbc.Input(id="nrows", type="number", value=2, min=1, step=1),
        ], md=2),
        dbc.Col([
            dbc.Label("Cols"),
            dbc.Input(id="ncols", type="number", value=3, min=1, step=1),
        ], md=2),
        dbc.Col([
            dbc.Label("Horizon (shift, integer)"),
            dbc.Input(id="horizon", type="number", value=(DEFAULT_HORIZONS[0] if DEFAULT_HORIZONS else 1), min=0, step=1),
        ], md=2),
    ], className="mb-2"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Combine"),
            dcc.Dropdown(id="logic", options=[{"label": k, "value": k} for k in ["OR", "AND", "XOR"]],
                         value="OR"),
        ], md=3),
        dbc.Col([
            dbc.Label("Apply to all panels?"),
            dcc.Dropdown(id="apply_all", options=[{"label": "Yes", "value": "yes"}, {"label": "No", "value": "no"}],
                         value="yes"),
        ], md=3),
        dbc.Col([
            dbc.Label("Models"),
            dcc.Dropdown(id="models", options=[{"label": m, "value": m} for m in ALL_MODELS],
                         value=ALL_MODELS[:3], multi=True),
        ], md=6),
    ], className="mb-2"),

    html.Div(id="regime_pickers_container"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Custom regime expression (optional)"),
            dcc.Input(id="expr", placeholder="e.g. gmm_raw in {2,3} AND NOT hmm_gauss==1", style={"width":"100%"}),
            dbc.FormText("Use model names as shown in 'Models'. Operators: AND/OR/XOR/NOT, ==, in {…}, parentheses."),
        ]),
    ], className="mb-2"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Focus factor for OLS"),
            dcc.Dropdown(id="focus_factor", options=[{"label": c, "value": c} for c in ALL_FACTORS],
                         value=(ALL_FACTORS[0] if ALL_FACTORS else None))
        ], md=6),
        dbc.Col([
            dbc.Button("Run OLS & Save (for focus factor)", id="run_ols", color="primary", className="mt-4")
        ], md=6),
    ], className="mb-2"),
], body=True, style={"maxWidth":"360px"})

grid = dbc.Card([
    html.H5("Regime-shaded cumulative returns (h=1)", id="grid_title", className="card-title"),
    dcc.Graph(id="grid_fig", config={"displayModeBar": True}),
], body=True)

# stats panels aligned to the grid (one per subplot)
stats_grid = dbc.Card([
    html.H5("Per-subplot Performance & OLS(HAC)", className="card-title"),
    html.Div(id="stats_panels"),
], body=True)

detail = dbc.Card([
    html.H5("Detailed OLS (HAC) for Focus Factor", className="card-title"),
    html.Div(id="ols_detail", style={"whiteSpace":"normal"}),
], body=True)

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(controls, width=3),
        dbc.Col([
            html.H2("Regime-aware Factor Explorer"),
            grid,
            html.Br(),
            stats_grid,
            html.Br(),
            detail,
        ], width=9),
    ], className="g-2"),
], fluid=True)

# ------------- dynamic per-model regime pickers -------------
@app.callback(
    Output("regime_pickers_container", "children"),
    Input("models", "value"),
    Input("horizon", "value"),
)
def render_pickers(models, h):
    models = models or []
    h = int(h) if h is not None else 0
    rows = []
    for m in models:
        if m not in L_full.columns:
            continue
        vals = pd.Series(L_full[m]).dropna().astype(int).unique()
        opts = [{"label": f"R{int(v)}", "value": int(v)} for v in sorted(vals)]
        rows.append(
            dbc.Row([
                dbc.Col(dbc.Badge(m, color="secondary"), width=3),
                dbc.Col(dcc.Dropdown(
                    id={"type":"regime_picker","model":m}, options=opts, value=[], multi=True,
                    placeholder=f"Pick regimes for {m}"
                ), width=9),
            ], className="mb-1")
        )
    if not rows:
        return dbc.Alert("Pick one or more models above to select regimes (or leave empty to use COMBINED defaults per factor/h).", color="light")
    return rows

# helper: per-panel perf quick stats
def _ret_stats(series: pd.Series):
    if series is None or len(series) == 0:
        return (np.nan, np.nan, np.nan, 0)
    mu = series.mean() * 252.0
    sd = series.std(ddof=1) * math.sqrt(252.0)
    sh = (mu / sd) if (sd and math.isfinite(sd)) else float("nan")
    return sh, mu, sd, len(series)

# ------------- main render (grid + per-subplot stats) -------------
@app.callback(
    Output("grid_fig", "figure"),
    Output("grid_title", "children"),
    Output("stats_panels", "children"),
    Input("factors", "value"),
    Input("nrows", "value"),
    Input("ncols", "value"),
    Input("horizon", "value"),
    Input("logic", "value"),
    Input("apply_all", "value"),
    Input("models", "value"),
    Input({"type":"regime_picker","model":ALL}, "value"),
    Input("expr", "value"),
)
def render_grid(factors, nrows, ncols, h, logic, apply_all, models, regime_lists, expr):
    factors = factors or []
    try:
        nrows = int(nrows); ncols = int(ncols)
    except Exception:
        nrows, ncols = 1, max(1, len(factors))
    h = int(h) if h is not None else 0
    logic = logic or "OR"

    fig = make_subplots(rows=max(1,nrows), cols=max(1,ncols), shared_xaxes=False, shared_yaxes=False)
    color = "#D4E6F1"  # background shading color (pale blue)
    stats_cards = []

    # consistent split date on full sample index
    split_dt = split_date(R.index, TRAIN_FRAC, VAL_FRAC)

    # build model label dict
    L_by_model_full = {m: L_full[m] for m in (models or []) if m in L_full.columns}

    # Build a *global* mask builder according to UI; if no picks/expr, we'll fall back to COMBINED per factor
    def mask_from_ui_or_combined(factor: str, index: pd.DatetimeIndex) -> tuple[pd.Series, str]:
        # 1) expression wins
        if isinstance(expr, str) and expr.strip():
            try:
                ast = _parse_expr(_lex(expr.strip()))
                msk = eval_expr_mask(ast, L_by_model_full, shift=h, index=index)
                return msk, f"expr[{expr.strip()}]"
            except Exception as e:
                # fall back to COMBINED if expression fails
                pass
        # 2) picks from pickers
        ui_picks = picks_from_ui(models, regime_lists, h)
        if ui_picks:
            desc = " ; ".join(f"{m}(R{','.join(map(str, cfg['regimes']))}, lag={cfg['lag']})" for m,cfg in ui_picks.items())
            msk = mask_from_picks(L_by_model_full, ui_picks, logic=logic, index=index)
            return msk, desc
        # 3) combined per factor/h
        cmb = read_combined_picks(factor, h)
        if cmb:
            # we need corresponding labels present
            L_use = {m:L_full[m] for m in cmb.keys() if m in L_full.columns}
            desc = " ; ".join(f"{m}(R{','.join(map(str,cfg['regimes']))}, lag={cfg['lag']})" for m,cfg in cmb.items())
            msk = mask_from_picks(L_use, cmb, logic=logic, index=index)
            return msk, f"COMBINED: {desc}"
        # 4) no filter
        return pd.Series(False, index=index), "(no filter)"

    # render each subplot
    for k, factor in enumerate(factors):
        r = k // max(1, ncols) + 1
        c = k % max(1, ncols) + 1

        # cumulative series
        rr = R.get(factor, pd.Series(index=R.index, dtype=float)).dropna()
        cum = rr.cumsum().pipe(np.exp) - 1.0
        fig.add_trace(go.Scatter(x=cum.index, y=cum.values, mode="lines",
                                 name=factor, line=dict(width=1.7)), row=r, col=c)

        # mask for this factor (UI -> else COMBINED defaults)
        mask, desc = mask_from_ui_or_combined(factor, cum.index)

        # shading on this subplot
        ymin = float(np.nanmin(cum.values)) if len(cum) else -1
        ymax = float(np.nanmax(cum.values)) if len(cum) else  1
        add_background_bands(fig, r, c, ncols, cum.index, mask, ymin, ymax, color)

        # vertical split line
        if split_dt is not None:
            fig.add_vline(x=split_dt, line_width=1, line_dash="dash", line_color="#666", opacity=0.7,
                          row=r, col=c)

        # quick stats (TEST only, masked vs unmasked) on h-shifted returns
        Yh = future_sum_returns(R, h)
        y = Yh[factor].dropna().reindex(cum.index)
        if split_dt is not None and len(y) > 0:
            te = y.loc[y.index >= split_dt]
            m_te = mask.reindex(te.index).fillna(False)
            sh_m, mu_m, sd_m, n_m = _ret_stats(te[m_te])
            sh_u, mu_u, sd_u, n_u = _ret_stats(te[~m_te])
        else:
            sh_m = mu_m = sd_m = np.nan; n_m = 0
            sh_u = mu_u = sd_u = np.nan; n_u = 0

        # card under subplot
        stats_cards.append(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(f"{factor} (h={h}) — Panel {k+1}"),
                    dbc.CardBody([
                        html.Div(f"Filter: {desc}", style={"fontSize":"12px","color":"#666","marginBottom":"4px"}),
                        dbc.Row([
                            dbc.Col(html.Div([
                                html.Div("Masked (TEST)", style={"fontWeight":"600"}),
                                html.Div(f"Sharpe: {sh_m:.3f}"),
                                html.Div(f"Ret: {mu_m:.3f}"),
                                html.Div(f"Vol: {sd_m:.3f}"),
                                html.Div(f"N: {n_m}"),
                            ]), width=6),
                            dbc.Col(html.Div([
                                html.Div("Unmasked (TEST)", style={"fontWeight":"600"}),
                                html.Div(f"Sharpe: {sh_u:.3f}"),
                                html.Div(f"Ret: {mu_u:.3f}"),
                                html.Div(f"Vol: {sd_u:.3f}"),
                                html.Div(f"N: {n_u}"),
                            ]), width=6),
                        ])
                    ], style={"padding":"8px"})
                ], style={"marginBottom":"8px"}),
                width=int(12 / max(1,ncols))
            )
        )

    fig.update_layout(
        height=max(420, 280 * nrows),
        template="plotly_white",
        margin=dict(l=30, r=20, t=40, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    title = f"Regime-shaded cumulative returns (h={h})"

    # pack stats cards into rows of ncols
    rows = []
    for i in range(0, len(stats_cards), max(1,ncols)):
        rows.append(dbc.Row(stats_cards[i:i+max(1,ncols)], className="g-1"))
    stats_children = rows if rows else html.Div("No panels to summarize.", style={"color":"#666"})

    return fig, title, stats_children

# ------------- “Run OLS & Save” detailed stats -------------
@app.callback(
    Output("ols_detail", "children"),
    Input("run_ols", "n_clicks"),
    State("focus_factor", "value"),
    State("horizon", "value"),
    State("logic", "value"),
    State("models", "value"),
    State({"type":"regime_picker","model":ALL}, "value"),
    State("expr", "value"),
    prevent_initial_call=True
)
def run_ols(n, factor, h, logic, models, regime_lists, expr):
    if not factor or factor not in R.columns:
        return html.Div("Select a valid focus factor first.", style={"color":"#a33"})
    h = int(h) if h is not None else 0
    logic = logic or "OR"

    # build mask (UI expr/picks else COMBINED for this factor/h)
    L_by_model = {m: L_full[m] for m in (models or []) if m in L_full.columns}
    # try expr
    mask = None; desc = ""
    if isinstance(expr, str) and expr.strip():
        try:
            ast = _parse_expr(_lex(expr.strip()))
            mask = eval_expr_mask(ast, L_by_model, shift=h, index=R.index).reindex(R.index).fillna(False)
            desc = f"expr[{expr.strip()}]"
        except Exception:
            mask = None
    if mask is None:
        ui_picks = picks_from_ui(models, regime_lists, h)
        if ui_picks:
            mask = mask_from_picks(L_by_model, ui_picks, logic=logic, index=R.index).reindex(R.index).fillna(False)
            desc = " ; ".join(f"{m}(R{','.join(map(str,cfg['regimes']))}, lag={cfg['lag']})" for m,cfg in ui_picks.items())
        else:
            cmb = read_combined_picks(factor, h)
            if cmb:
                L_use = {m:L_full[m] for m in cmb.keys() if m in L_full.columns}
                mask = mask_from_picks(L_use, cmb, logic=logic, index=R.index).reindex(R.index).fillna(False)
                desc = "COMBINED: " + " ; ".join(f"{m}(R{','.join(map(str,cfg['regimes']))}, lag={cfg['lag']})" for m,cfg in cmb.items())
            else:
                mask = pd.Series(False, index=R.index)
                desc = "(no filter)"

    # data at horizon
    Yh = future_sum_returns(R, h)
    y = Yh[factor].dropna()
    Xh = X_by_h[h] if h in X_by_h else IND.copy()
    if isinstance(Xh, pd.DataFrame) and h:
        Xh = Xh.copy()
        # rename indicators to include lag suffix per your requirement
        Xh.columns = [f"{c}_lag{h}" for c in Xh.columns]

    Z = design_from_mask_and_indicators(Xh, mask).reindex(y.index).dropna()
    y = y.loc[Z.index]

    sd = split_date(y.index, TRAIN_FRAC, VAL_FRAC)
    if sd is None:
        return html.Div("Not enough data to split train/test.", style={"color":"#a33"})
    tr_idx = y.index[y.index < sd]
    te_idx = y.index[y.index >= sd]
    if len(tr_idx) < 20 or len(te_idx) < 10:
        return html.Div("Too few observations after cleaning.", style={"color":"#a33"})

    res_tr, res_tr_hac = ols_hac_full(y.loc[tr_idx], Z.loc[tr_idx], HAC_LAGS)
    res_te, res_te_hac = ols_hac_full(y.loc[te_idx], Z.loc[te_idx], HAC_LAGS)

    # Save robust summaries (TRAIN/TEST)
    def save_res(reslike, tag):
        if reslike is None: return None
        path = os.path.join(STATS_TAB_DIR, f"dash_ols_{factor}_{tag}_h{h}.html")
        try:
            with open(path, "w") as fh:
                fh.write(reslike.summary().as_html())
        except Exception:
            with open(path.replace(".html", ".txt"), "w") as fh:
                fh.write(str(reslike.summary()))
        return path

    p_tr = save_res(res_tr_hac if hasattr(res_tr_hac, "summary") else res_tr, "train")
    p_te = save_res(res_te_hac if hasattr(res_te_hac, "summary") else res_te, "test")

    header = html.Div([
        html.Div(f"Focus factor: {factor}   |   h={h}", style={"fontWeight":"600"}),
        html.Div("Selection used: " + desc, style={"fontSize":"12px", "color":"#555"}),
        html.Hr()
    ])

    def summary_block(title, reslike):
        if reslike is None:
            return html.Div([html.H6(title), html.Div("OLS could not be estimated (too few rows).")])
        # Inline statsmodels HTML (allow HTML)
        return html.Div([
            html.H6(title),
            dcc.Markdown(reslike.summary().as_html(), dangerously_allow_html=True),
        ], style={"overflowX":"auto", "border":"1px solid #eee", "padding":"8px", "borderRadius":"6px", "background":"#fafafa", "marginBottom":"8px"})

    # quick diagnostics masked/unmasked on train/test (at horizon)
    def perf(series):
        if series is None or len(series) == 0:
            return (np.nan, np.nan, np.nan, 0)
        mu = series.mean() * 252.0
        sd = series.std(ddof=1) * math.sqrt(252.0)
        sh = (mu / sd) if (sd and math.isfinite(sd)) else float("nan")
        return sh, mu, sd, len(series)

    m_tr = mask.reindex(tr_idx).fillna(False)
    m_te = mask.reindex(te_idx).fillna(False)
    sh_m_tr, mu_m_tr, sd_m_tr, n_m_tr = perf(y.loc[tr_idx][m_tr])
    sh_u_tr, mu_u_tr, sd_u_tr, n_u_tr = perf(y.loc[tr_idx][~m_tr])
    sh_m_te, mu_m_te, sd_m_te, n_m_te = perf(y.loc[te_idx][m_te])
    sh_u_te, mu_u_te, sd_u_te, n_u_te = perf(y.loc[te_idx][~m_te])

    diag = pd.DataFrame({
        "dataset": ["train", "test"],
        "sharpe_masked": [sh_m_tr, sh_m_te], "ret_masked": [mu_m_tr, mu_m_te], "vol_masked": [sd_m_tr, sd_m_te], "N_masked": [n_m_tr, n_m_te],
        "sharpe_unmask": [sh_u_tr, sh_u_te], "ret_unmask": [mu_u_tr, mu_u_te], "vol_unmask": [sd_u_tr, sd_u_te], "N_unmask": [n_u_tr, n_u_te],
    })
    diag_path = os.path.join(STATS_TAB_DIR, f"dash_diag_{factor}_h{h}.csv")
    try:
        diag.to_csv(diag_path, index=False)
        diag_msg = html.Div(f"Diagnostics CSV saved -> {diag_path}", style={"fontSize":"12px","color":"#666"})
    except Exception:
        diag_msg = html.Div("", style={"display":"none"})

    blocks = [
        header,
        summary_block("OLS(HAC) — TRAIN", res_tr_hac if hasattr(res_tr_hac, "summary") else res_tr),
        summary_block("OLS(HAC) — TEST",  res_te_hac if hasattr(res_te_hac, "summary") else res_te),
        dbc.Alert(
            f"TRAIN masked: Sharpe={sh_m_tr:.3f}, Ret={mu_m_tr:.3f}, Vol={sd_m_tr:.3f}, N={n_m_tr} | "
            f"TRAIN unmasked: Sharpe={sh_u_tr:.3f}, Ret={mu_u_tr:.3f}, Vol={sd_u_tr:.3f}, N={n_u_tr} | "
            f"TEST masked: Sharpe={sh_m_te:.3f}, Ret={mu_m_te:.3f}, Vol={sd_m_te:.3f}, N={n_m_te} | "
            f"TEST unmasked: Sharpe={sh_u_te:.3f}, Ret={mu_u_te:.3f}, Vol={sd_u_te:.3f}, N={n_u_te}",
            color="light"
        ),
        diag_msg
    ]
    if p_tr or p_te:
        paths = " | ".join([p for p in [p_tr, p_te] if p])
        blocks.append(html.Div(f"Saved summaries: {paths}", style={"fontSize":"12px","color":"#666"}))

    return html.Div(blocks)

# ----------------- main -----------------
if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1", port=8052)