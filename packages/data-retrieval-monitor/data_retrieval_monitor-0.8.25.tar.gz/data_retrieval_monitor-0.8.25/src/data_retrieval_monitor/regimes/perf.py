import os, numpy as np, pandas as pd
from utils import annualized_stats, infer_periods_per_year, professional_heatmap
from configs import SUBDIRS

class PerformanceEvaluator:
    def __init__(self, returns_df, regimes_df):
        self.R = returns_df; self.reg = regimes_df
        self.ann = infer_periods_per_year(self.R.index)

    def _perf(self, ret_subset, rseries):
        labs = pd.Series(rseries).astype("Int64").values
        uniq = [int(u) for u in np.unique(labs[~pd.isna(labs)]) if u>=0]
        mu = pd.DataFrame(index=ret_subset.columns, columns=[f"Regime {s}" for s in uniq])
        vo = mu.copy(); sh = mu.copy()
        for s in uniq:
            m = labs==s
            if m.sum()==0: continue
            stats = annualized_stats(ret_subset.loc[m], self.ann)
            mu[f"Regime {s}"] = stats["mean"]; vo[f"Regime {s}"] = stats["vol"]; sh[f"Regime {s}"] = stats["sharpe"]
        return mu, vo, sh

    def save_split(self, train_slice, test_slice):
        ret_tr = self.R.iloc[train_slice]; ret_te = self.R.iloc[test_slice]
        for col in self.reg.columns:
            mu_tr, vo_tr, sh_tr = self._perf(ret_tr, self.reg[col].iloc[train_slice])
            mu_te, vo_te, sh_te = self._perf(ret_te, self.reg[col].iloc[test_slice])
            for split, (mu,vo,sh) in {"train":(mu_tr,vo_tr,sh_tr), "test":(mu_te,vo_te,sh_te)}.items():
                root = SUBDIRS["perf"]
                mu.to_csv(os.path.join(root, split, "mean",   f"{col}.csv"))
                vo.to_csv(os.path.join(root, split, "vol",    f"{col}.csv"))
                sh.to_csv(os.path.join(root, split, "sharpe", f"{col}.csv"))
                professional_heatmap(mu, f"{col} — {split} Mean",   os.path.join(root, split, "mean",   f"{col}_heatmap.png"), fmt=".2%")
                professional_heatmap(vo, f"{col} — {split} Vol",    os.path.join(root, split, "vol",    f"{col}_heatmap.png"), fmt=".2%")
                professional_heatmap(sh, f"{col} — {split} Sharpe", os.path.join(root, split, "sharpe", f"{col}_heatmap.png"), fmt=".2f", center_zero=True, cbar_label="Sharpe")