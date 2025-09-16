# models/knn_causal.py
import numpy as np
from sklearn.neighbors import NearestNeighbors

def causal_knn_refine(embeddings: np.ndarray,
                      base_labels: np.ndarray,
                      k: int = 10,
                      time_decay: float = 0.0,
                      metric: str = "euclidean") -> np.ndarray:
    """
    Past-only kNN refine: label at t uses neighbors from {0..t-1}.
    metric: 'euclidean' or 'cosine'
    """
    E = np.asarray(embeddings)
    L = np.asarray(base_labels).astype(int)
    T = E.shape[0]
    out = L.copy()

    nbrs = NearestNeighbors(n_neighbors=min(k, max(1, T-1)), algorithm="auto", metric=metric)
    nbrs.fit(E)

    for t in range(T):
        if t == 0:
            out[t] = L[t] if L[t] != -1 else 0
            continue
        kk = min(k, t)
        inds = nbrs.kneighbors(E[t:t+1], n_neighbors=min(k*3, t), return_distance=False)[0]
        past = inds[inds < t]
        if past.size == 0:
            out[t] = L[t] if L[t] != -1 else (out[t-1] if t>0 else 0)
            continue
        use = past[:kk]
        votes = L[use]
        use_mask = votes >= 0
        if not np.any(use_mask):
            out[t] = L[t] if L[t] != -1 else (out[t-1] if t>0 else 0)
            continue
        votes = votes[use_mask]
        if time_decay > 0:
            ages = (t - use[use_mask]).astype(float)
            w = np.exp(-time_decay * ages)
        else:
            w = np.ones_like(votes, dtype=float)

        uniq = np.unique(votes)
        best_lab, best_w = None, -1.0
        for u in uniq:
            sw = w[votes == u].sum()
            if sw > best_w:
                best_lab, best_w = int(u), float(sw)
        out[t] = best_lab
    return out