import os, numpy as np, pandas as pd
from configs import SUBDIRS, SCORE_WEIGHTS, SCORE_THRESHOLD
from utils import infer_periods_per_year, annualized_stats
from stats import extract_dummy_stats

def _sharpe_table(ret_subset, rseries, ann):
    labs = pd.Series(rseries).astype("Int64").values
    uniq = [int(u) for u in np.unique(labs[~pd.isna(labs)]) if u>=0]
    out = pd.DataFrame(index=ret_subset.columns, columns=[f"R{u}" for u in uniq])
    for s in uniq:
        m = labs==s
        if m.sum()==0: continue
        out[f"R{s}"] = annualized_stats(ret_subset.loc[m], ann)["sharpe"]
    return out

def _consistency(sh_tr, sh_va):
    common = [c for c in sh_tr.columns if c in sh_va.columns]
    if not common: return 0.0, 0.0, 0.0, 0.0
    A = sh_tr[common]; B = sh_va[common]
    diff = (A-B).abs().values; denom = (A.abs().values + B.abs().values + 1e-12)
    cons = float(1.0 - np.nanmean(diff/denom))
    avg_abs = float(np.nanmean(np.abs(B.values)))
    max_abs = float(np.nanmax(np.abs(B.values))) if np.isfinite(B.values).any() else 0.0
    flips = np.sign(A.values)*np.sign(B.values); flip_penalty = 1.0 - float(np.mean(flips<0)) if flips.size else 0.0
    return max(0.0, cons), avg_abs, max_abs, flip_penalty

def score_models(R, REG, train_slice, val_slice, ols_split_results):
    ann = infer_periods_per_year(R.index)
    ret_tr = R.iloc[train_slice]; ret_va = R.iloc[val_slice]
    rows=[]
    for m in REG.columns:
        sh_tr = _sharpe_table(ret_tr, REG[m].iloc[train_slice], ann)
        sh_va = _sharpe_table(ret_va, REG[m].iloc[val_slice], ann)
        cons, avg_abs, max_abs, flip_pen = _consistency(sh_tr, sh_va)
        t_df = ols_split_results.get(m,{}).get("val",{}).get("tstats")
        b_df = ols_split_results.get(m,{}).get("val",{}).get("coefs")
        if t_df is None or b_df is None: tnorm, bnorm = 0.0, 0.0
        else:
            
            tavg, bavg = extract_dummy_stats(m, t_df, b_df)
            tnorm = min(1.0, tavg/3.0); bnorm=min(1.0, bavg/0.01)
        score = (
          SCORE_WEIGHTS["sharpe_consistency"]*cons +
          SCORE_WEIGHTS["avg_abs_sharpe"]*np.tanh(avg_abs) +
          SCORE_WEIGHTS["max_abs_sharpe"]*np.tanh(max_abs) +
          SCORE_WEIGHTS["sign_flip_penalty"]*flip_pen +
          SCORE_WEIGHTS["ols_dummy_t"]*tnorm +
          SCORE_WEIGHTS["ols_dummy_coef"]*bnorm
        )
        rows.append({"model":m,"consistency":cons,"avg_abs_va":avg_abs,"max_abs_va":max_abs,
                     "flip_penalty":flip_pen,"ols_t_val":tnorm,"ols_b_val":bnorm,"score":score})
    df = pd.DataFrame(rows).sort_values("score", ascending=False)
    df.to_csv(os.path.join(SUBDIRS["scores"], "model_scores.csv"), index=False)
    chosen = df.loc[df["score"]>=SCORE_THRESHOLD, "model"].tolist()
    pd.DataFrame({"model":chosen}).to_csv(os.path.join(SUBDIRS["scores"], "production_models.csv"), index=False)
    return chosen