# configs.py
import os

# IO
OUTPUT_DIR = "output2"
LEVELS_CSV = "levels.csv"
INDICATORS_CSV = "indicators.csv"

# Organized subdirs
SUBDIRS = {
    "regimes":      os.path.join(OUTPUT_DIR, "regimes"),
    "selectors":    os.path.join(OUTPUT_DIR, "selectors"),
    "perf":         os.path.join(OUTPUT_DIR, "perf"),           # root; split/metric will live under this
    "stat_tests":   os.path.join(OUTPUT_DIR, "stat_tests"),
    "designs":      os.path.join(OUTPUT_DIR, "designs"),
    "figures":      os.path.join(OUTPUT_DIR, "figures"),
}
for p in SUBDIRS.values():
    os.makedirs(p, exist_ok=True)

# (split, metric) folders: perf/<train|test>/<sharpe|mean|vol>/
PERF_SPLITS  = ["train", "test"]
PERF_METRICS = ["sharpe", "mean", "vol"]
for split in PERF_SPLITS:
    for metric in PERF_METRICS:
        os.makedirs(os.path.join(SUBDIRS["perf"], split, metric), exist_ok=True)

# Randomness
SEED = 7

# Splits (chronological)
TRAIN_FRAC = 0.60
VAL_FRAC   = 0.20   # test is the rest (0.20)

# Leakage guard
IND_LAG = 2  # business days

# Rolling window (estimation)
ROLL_WINDOW = 252
ROLL_STEP   = 1

# Clustering configs
N_CLUSTERS = 4
KMEANS_N_INIT = 50
KMEANS_MAX_ITER = 1000

# Extra variants
CLUSTER_VARIANTS = {
    "kmeans_raw":        {"algo": "kmeans", "kwargs": {"init": "k-means++"}},
    "kmeans_raw_he":     {"algo": "kmeans", "kwargs": {"init": "random"}},  # different init
    "kmeans_minibatch":  {"algo": "mbkmeans", "kwargs": {"batch_size": 64}},
    "gmm_full":          {"algo": "gmm", "kwargs": {"covariance_type": "full"}},
    "gmm_diag":          {"algo": "gmm", "kwargs": {"covariance_type": "diag"}},
    "gmm_spherical":     {"algo": "gmm", "kwargs": {"covariance_type": "spherical"}},
    "bayes_gmm":         {"algo": "bayes_gmm", "kwargs": {"covariance_type": "full"}},
    "spectral_pca":      {"algo": "spectral_pca", "kwargs": {"n_neighbors": 15}},
    "agg_pca":           {"algo": "agg_pca", "kwargs": {"linkage": "ward"}},
}

# PCA
PCA_COMPONENTS = 3

# Causal kNN refine
CAUSAL_KNN_K = 10
CAUSAL_KNN_TIME_DECAY = 0.01   # 0 -> no decay
CAUSAL_KNN_METRIC = "euclidean"  # or "cosine"

# SAINT selector (if torch present)
SAINT_EPOCHS   = 10
SAINT_LR       = 1e-3

# Estimation mode
RECURSIVE_ESTIMATION = False
REFIT_STEP = 20
RECURSIVE_INCLUDE_DEEP = False