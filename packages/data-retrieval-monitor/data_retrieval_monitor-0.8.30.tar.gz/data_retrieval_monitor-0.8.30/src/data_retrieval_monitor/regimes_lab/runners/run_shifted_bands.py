import os, re, json, numpy as np, pandas as pd
from regimes_lab.data import prepare
from regimes_lab.regimes import load_or_build_labels
from regimes_lab.splitters import future_sum_returns
from regimes_lab.configs import STATS_TAB_DIR, STATS_FIG_DIR, TRAIN_FRAC, VAL_FRAC

# (kept as in your current environment; Plotly runner below is the new primary)
def _find_selected_jsons(prefix="COMBINED_SELECTED_SELECTED_"):
    files = [f for f in os.listdir(STATS_TAB_DIR) if f.startswith(prefix) and f.endswith(".json")]
    files.sort()
    return [os.path.join(STATS_TAB_DIR, f) for f in files]

def _parse_factor_h(base: str):
    m = re.match(r"^COMBINED_SELECTED_SELECTED_(.+?)_h(\d+)\.json$", base)
    if not m: return base, 1
    return m.group(1), int(m.group(2))

def _parse_keep_map(cols):
    keep={}
    for c in cols:
        if "_R" not in c: continue
        m, rid = c.split("_R",1)
        try: rid=int(rid)
        except: continue
        keep.setdefault(m,set()).add(rid)
    return keep

def _split_date(R, factor, h, tr, va):
    y = future_sum_returns(R,h)[factor].dropna()
    if y.empty: return None
    T=len(y); ntr=int(tr*T); nva=int(va*T); te=ntr+nva
    if te<=0 or te>=T: return None
    return y.index[te]

def main():
    sel_paths = _find_selected_jsons()
    if not sel_paths:
        print("[bands] No selection JSONs found. Skipping.")
        return
    for path in sel_paths:
        base = os.path.basename(path)
        factor, h = _parse_factor_h(base)
        R, IND, X_by_h = prepare([h])
        X_h,_ = X_by_h[h]
        L = load_or_build_labels(X_h, split_tag="full", h=h)
        with open(path,"r") as fh: payload=json.load(fh)
        chosen = payload.get("chosen_dummies", [])
        keep_raw = _parse_keep_map(chosen)
        # nothing else here; use the Plotly runner for interactive shading

if __name__=="__main__":
    main()