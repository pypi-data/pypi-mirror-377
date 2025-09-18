import numpy as np
from sklearn.neighbors import NearestNeighbors

def causal_knn_refine(embeddings, base_labels, k=10, time_decay=0.0, metric="euclidean"):
    E = np.asarray(embeddings); L = np.asarray(base_labels).astype(int)
    T = E.shape[0]; out = L.copy()
    nbrs = NearestNeighbors(n_neighbors=max(1, min(k, max(1, T-1))), metric=metric).fit(E)
    for t in range(T):
        if t==0: out[t] = L[t] if L[t]>=0 else 0; continue
        inds = nbrs.kneighbors(E[t:t+1], n_neighbors=min(k*3, t), return_distance=False)[0]
        past = inds[inds < t]
        if past.size==0: out[t] = L[t] if L[t]>=0 else out[t-1]; continue
        use = past[:min(k, len(past))]
        votes = L[use]; mask = votes>=0
        if not np.any(mask): out[t] = L[t] if L[t]>=0 else out[t-1]; continue
        votes = votes[mask]
        if time_decay>0:
            ages = (t - use[mask]).astype(float); w = np.exp(-time_decay*ages)
        else:
            w = np.ones_like(votes, float)
        uniq = np.unique(votes)
        best, bw = 0, -1.0
        for u in uniq:
            sw = w[votes==u].sum()
            if sw>bw: best, bw = int(u), float(sw)
        out[t] = best
    return out