import numpy as np, pandas as pd
from align import align_labels
from knn_refine import causal_knn_refine
from configs import (ROLL_WINDOW, ROLL_STEP, RECURSIVE, N_CLUSTERS,
                      CAUSAL_KNN_K, CAUSAL_KNN_TIME_DECAY, CAUSAL_KNN_METRIC)

class RegimeRollingEngine:
    """
    Orchestrates causal rolling/recursive labeling over multiple BaseRegimeModel instances.
    """
    def __init__(self, models, add_knn_on_embeddings=True):
        self.models = models
        self.add_knn = add_knn_on_embeddings

    def build(self, X_all, dates):
        T = X_all.shape[0]
        outputs = {}
        prev_keys = {m.name: None for m in self.models}
        embed_cache = {}

        for t in range(ROLL_WINDOW, T, ROLL_STEP):
            if RECURSIVE:
                win = slice(0, t)
            else:
                win = slice(t-ROLL_WINDOW, t)
            Xw = X_all[win]

            for m in self.models:
                lab_w = m.fit(Xw)           # window labels
                key = m.get_alignment_key()
                if key is not None and prev_keys[m.name] is not None and lab_w is not None and len(lab_w)>0:
                    lab_aligned = align_labels(prev_keys[m.name], key, lab_w)
                else:
                    lab_aligned = lab_w

                prev_keys[m.name] = key
                val_t = int(lab_aligned[-1]) if lab_aligned is not None and len(lab_aligned)>0 else -1
                outputs.setdefault(m.name, np.full(T, -1, int))
                outputs[m.name][t] = val_t

                Z = m.forward_embed(Xw, X_all)
                if Z is not None:
                    embed_cache[m.name] = Z

        # causal kNN refine for embedding-based models
        if self.add_knn:
            for m in self.models:
                if m.name in embed_cache:
                    refined = causal_knn_refine(
                        embeddings=embed_cache[m.name],
                        base_labels=outputs[m.name],
                        k=CAUSAL_KNN_K, time_decay=CAUSAL_KNN_TIME_DECAY, metric=CAUSAL_KNN_METRIC
                    )
                    outputs[f"{m.name}_knn"] = refined

        return pd.DataFrame(outputs, index=pd.to_datetime(dates))