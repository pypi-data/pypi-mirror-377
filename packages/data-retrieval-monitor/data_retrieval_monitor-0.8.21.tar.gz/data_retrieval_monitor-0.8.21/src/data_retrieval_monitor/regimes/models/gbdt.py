# models/gbdt.py
import numpy as np
from sklearn.cluster import KMeans
from configs import N_CLUSTERS, KMEANS_N_INIT, KMEANS_MAX_ITER

# Try GBDT libs
try:
    import lightgbm as lgb
    LGB_OK = True
except Exception:
    LGB_OK = False

try:
    import xgboost as xgb
    XGB_OK = True
except Exception:
    XGB_OK = False

try:
    from catboost import CatBoostClassifier, Pool
    CAT_OK = True
except Exception:
    CAT_OK = False

def _pseudo_labels_from_kmeans(X_train, n_clusters=N_CLUSTERS):
    km = KMeans(n_clusters=n_clusters, n_init=KMEANS_N_INIT, max_iter=KMEANS_MAX_ITER, random_state=0)
    y = km.fit_predict(X_train)
    return y

def _leaf_embed_lightgbm(X_train, y_train, X_all, n_estimators=200, num_leaves=31):
    model = lgb.LGBMClassifier(objective="multiclass", n_estimators=n_estimators,
                               num_leaves=num_leaves, random_state=0)
    model.fit(X_train, y_train)
    # leaf indices: array [n_samples, n_trees]
    leaves = model.predict(X_all, pred_leaf=True)
    # one-hot leaves per tree
    # safer dense embed: concat leaves as integers and standardize later
    return np.asarray(leaves, dtype=np.int32), model

def _leaf_embed_xgboost(X_train, y_train, X_all, n_estimators=200, max_depth=6):
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dall   = xgb.DMatrix(X_all)
    params = {"objective": "multi:softprob", "num_class": int(np.max(y_train))+1,
              "max_depth": max_depth, "eta": 0.1, "subsample": 0.9, "colsample_bytree": 0.9,
              "eval_metric": "mlogloss", "seed": 0}
    model = xgb.train(params, dtrain, num_boost_round=n_estimators)
    # leaf index embedding
    leaves = model.predict(dall, pred_leaf=True)
    return np.asarray(leaves, dtype=np.int32), model

def _leaf_embed_catboost(X_train, y_train, X_all, n_estimators=300, depth=6):
    model = CatBoostClassifier(iterations=n_estimators, depth=depth, learning_rate=0.1,
                               loss_function="MultiClass", verbose=False, random_seed=0)
    model.fit(X_train, y_train)
    # CatBoost: we can use prediction path indices via calc_leaf_indexes
    leaves_train = model.calc_leaf_indexes(Pool(X_train, label=y_train))
    leaves_all   = model.calc_leaf_indexes(Pool(X_all))
    return np.asarray(leaves_all, dtype=np.int32), model

def _cluster_from_embed(embed, name="gbdt_kmeans"):
    # Simple KMeans on embedding
    km = KMeans(n_clusters=N_CLUSTERS, n_init=KMEANS_N_INIT, max_iter=KMEANS_MAX_ITER, random_state=0)
    labels = km.fit_predict(embed)
    return labels, km

def gbdt_cluster_train(X_train, X_all, base_labels=None, backend_preference=("lightgbm", "xgboost", "catboost")):
    """
    Train a multiclass GBDT on pseudo-labels (from KMeans on train) unless base_labels given.
    Use leaf-index embeddings for X_all and cluster them with KMeans.
    Returns (labels, {"backend": str, "gbdt_model": model, "km": km})
    """
    if base_labels is None:
        y_train = _pseudo_labels_from_kmeans(X_train, n_clusters=N_CLUSTERS)
    else:
        y_train = np.asarray(base_labels[:len(X_train)])

    backend_used = None
    embed = None; model = None

    for be in backend_preference:
        if be == "lightgbm" and LGB_OK:
            embed, model = _leaf_embed_lightgbm(X_train, y_train, X_all)
            backend_used = "lightgbm"; break
        if be == "xgboost" and XGB_OK:
            embed, model = _leaf_embed_xgboost(X_train, y_train, X_all)
            backend_used = "xgboost"; break
        if be == "catboost" and CAT_OK:
            embed, model = _leaf_embed_catboost(X_train, y_train, X_all)
            backend_used = "catboost"; break

    if embed is None:
        print("[INFO] No GBDT backend available — skipping GBDT clustering.")
        return None, None

    labels, km = _cluster_from_embed(embed)
    return labels, {"backend": backend_used, "gbdt_model": model, "km": km, "embed": embed}