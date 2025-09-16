# alignment.py
import numpy as np, pandas as pd
from collections import Counter

def align_cpd_to_regimes(cpd_labels: dict, regime_df: pd.DataFrame) -> pd.DataFrame:
    """
    For each CPD series (segments), label each time t with the MODE of all regime
    models at t (majority vote across regime_df columns). Returns DataFrame with
    aligned labels per CPD model, e.g., 'cpd_binseg_6_aligned'.
    """
    if not cpd_labels: return pd.DataFrame(index=regime_df.index)
    # vote base regime among all models per t
    votes = []
    for t in range(len(regime_df)):
        row = regime_df.iloc[t].dropna().astype(int).values
        if len(row)==0: votes.append(np.nan)
        else:
            c = Counter(row); votes.append(c.most_common(1)[0][0])
    voted = np.asarray(votes)
    out = {}
    for name, seg in cpd_labels.items():
        # assign aligned label equals voted regime per t (or per segment-mean vote)
        aligned = []
        for s in np.unique(seg):
            idx = np.where(seg==s)[0]
            if len(idx):
                seg_vote = Counter(voted[idx[~np.isnan(voted[idx])].astype(int)]).most_common(1)
                label = seg_vote[0][0] if seg_vote else -1
                aligned.extend([(i, label) for i in idx])
        aligned = sorted(aligned, key=lambda x: x[0])
        arr = np.full_like(seg, fill_value=-1)
        for i,l in aligned: arr[i]=l
        out[f"{name}_aligned"] = arr
    return pd.DataFrame(out, index=regime_df.index)