from typing import Dict, Optional, Set, Iterable
import numpy as np, pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def _regime_runs(labels: pd.Series, keep_ids: Optional[Set[int]]) -> Iterable[tuple[pd.Timestamp, pd.Timestamp, int]]:
    s = labels.copy()
    if keep_ids is not None:
        s[~s.isin(list(keep_ids))] = np.nan
    s = s.dropna().astype(int)
    if s.empty: return []
    idx = s.index; vals = s.values
    runs=[]; start=0
    for i in range(1, len(vals)+1):
        if i==len(vals) or vals[i]!=vals[i-1] or (idx[i]-idx[i-1]).days>7:
            runs.append((idx[start], idx[i-1], vals[i-1])); start=i
    return runs

def _shift_for_horizon(labels: pd.Series, h: int, full_index: pd.DatetimeIndex) -> pd.Series:
    return labels.shift(h).reindex(full_index)

def plot_combined_plotly(dates, cumret, labels_by_model: Dict[str, pd.Series], keep_only: Dict[str, Set[int]],
                         horizon=1, split_train=None, split_valid=None, split_test=None,
                         title="Cumulative Return with Selected Regimes (interactive)") -> go.Figure:
    s = pd.Series(cumret).reindex(dates).dropna()
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
    fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", name="Cumulative Return", line=dict(width=2)), 1,1)
    palette = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"]
    color_cache={}; ci=0
    for model, lab in labels_by_model.items():
        keep = keep_only.get(model, set())
        if not keep: continue
        sh = _shift_for_horizon(pd.Series(lab), horizon, s.index)
        for (start,end,rid) in _regime_runs(sh, keep):
            key=(model,rid)
            if key not in color_cache:
                color_cache[key]=palette[ci%len(palette)]; ci+=1
            col=color_cache[key]
            fig.add_vrect(x0=start, x1=end, fillcolor=col, opacity=0.18, line_width=0,
                          layer="below", annotation_text=f"{model}: R{rid}",
                          annotation_position="top left",
                          annotation=dict(font=dict(size=9, color="#333"), bgcolor="rgba(255,255,255,0.6)"))
    def _add_split(x,label):
        if x is None: return
        fig.add_vline(x=x, line_width=1.5, line_dash="dash", line_color="black",
                      annotation_text=label, annotation_position="top right")
    if (split_valid is not None): _add_split(split_valid, "train→valid")
    if (split_test  is not None): _add_split(split_test,  "valid→test")
    fig.update_layout(title=title, hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                      margin=dict(l=40,r=10,t=60,b=40), template="plotly_white", height=500)
    return fig