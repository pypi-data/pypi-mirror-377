import os, math, numpy as np, pandas as pd
from configs import SUBDIRS
from utils import infer_periods_per_year

try:
    import statsmodels.api as sm
    STATSM=True
except Exception:
    STATSM=False

def build_indicator_sign_dummies(ind_df):
    outs={}
    for c in ind_df.columns:
        pos=(ind_df[c]>0).astype(int); outs[f"{c}_POS"]=pos; outs[f"{c}_NEG"]=1-pos
    return pd.DataFrame(outs, index=ind_df.index)

def dummies_for_model(reg_col, prefix):
    s = reg_col.astype("Int64")
    return pd.get_dummies(s, prefix=f"{prefix}_R", dtype=int)

def _add_constant(X):
    if "const" in X.columns: return X
    return pd.concat([pd.Series(1.0, index=X.index, name="const"), X], axis=1)

def _ols(y, X, ann):
    Xc = _add_constant(X.astype(float)); yv = y.values; Xv = Xc.values
    if STATSM:
        res = sm.OLS(yv, Xv).fit(cov_type="HAC", cov_kwds={"maxlags": max(1,int(round(ann**(1/3))))})
        return (pd.Series(res.params, index=Xc.columns),
                pd.Series(res.tvalues, index=Xc.columns),
                pd.Series(res.pvalues, index=Xc.columns),
                res.rsquared, res.rsquared_adj)
    # fallback simple
    XtX=np.linalg.pinv(Xv.T@Xv); beta=XtX@(Xv.T@yv); resid=yv-Xv@beta
    r2 = 1 - (resid@resid)/( (yv-yv.mean())@(yv-yv.mean()) + 1e-12 )
    return (pd.Series(beta, index=Xc.columns),
            pd.Series(np.zeros_like(beta), index=Xc.columns),
            pd.Series(np.ones_like(beta), index=Xc.columns),
            r2, r2)

def run_ols_per_model_split(R, IND, REG, train_slice, val_slice, include_sign=True):
    ann = infer_periods_per_year(R.index); results={}
    for mcol in REG.columns:
        D = dummies_for_model(REG[mcol], mcol)
        X = IND.copy(); 
        if include_sign: X = pd.concat([X, build_indicator_sign_dummies(IND)], axis=1)
        X = pd.concat([X, D], axis=1).reindex(R.index).fillna(0)
        res2={}
        for tag, sl in {"train":train_slice, "val":val_slice}.items():
            coefs=[]; tstats=[]; pvals=[]; fits=[]
            Xs = X.iloc[sl]
            for fac in R.columns:
                a,b,c,r2,r2a = _ols(R[fac].iloc[sl], Xs, ann)
                coefs.append(a.rename(fac)); tstats.append(b.rename(fac)); pvals.append(c.rename(fac))
                fits.append(pd.Series({"R2":r2,"AdjR2":r2a}, name=fac))
            res2[tag] = {
                "coefs": pd.DataFrame(coefs),
                "tstats": pd.DataFrame(tstats),
                "pvals": pd.DataFrame(pvals),
                "fit": pd.DataFrame(fits)
            }
            res2[tag]["coefs"].to_csv(os.path.join(SUBDIRS["stat_tests"], f"ols_{mcol}_{tag}_coefs.csv"))
            res2[tag]["tstats"].to_csv(os.path.join(SUBDIRS["stat_tests"], f"ols_{mcol}_{tag}_tstats.csv"))
            res2[tag]["pvals"].to_csv(os.path.join(SUBDIRS["stat_tests"], f"ols_{mcol}_{tag}_pvals.csv"))
            res2[tag]["fit"].to_csv(os.path.join(SUBDIRS["stat_tests"], f"ols_{mcol}_{tag}_fit.csv"))
        results[mcol]=res2
    return results

def extract_dummy_stats(model_col, tstats_df, coefs_df):
    mask = [c.startswith(f"{model_col}_R_") for c in tstats_df.columns]
    if not any(mask): return 0.0, 0.0
    t_abs = tstats_df.loc[:,mask].abs().values
    b_abs = coefs_df.loc[:,mask].abs().values
    return float(np.nanmean(t_abs)), float(np.nanmean(b_abs))