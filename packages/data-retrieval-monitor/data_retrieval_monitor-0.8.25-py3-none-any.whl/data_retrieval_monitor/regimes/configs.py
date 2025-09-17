import os

# IO
OUTPUT_DIR = "output2"
LEVELS_CSV = "levels.csv"
INDICATORS_CSV = "indicators.csv"

# Random / splits
SEED = 7
TRAIN_FRAC = 0.60
VAL_FRAC   = 0.20  # test = rest

# Lag (no look-ahead)
IND_LAG_BDAYS = 2

# Rolling / recursive
ROLL_WINDOW = 252
ROLL_STEP   = 1
RECURSIVE   = False  # if True use [0,t) growing window; else [t-W, t)

# Clustering
N_CLUSTERS = 4
PCA_COMPONENTS = 3
KMEANS_N_INIT = 20
KMEANS_MAX_ITER = 1000

# causal kNN refine
CAUSAL_KNN_K = 10
CAUSAL_KNN_TIME_DECAY = 0.01
CAUSAL_KNN_METRIC = "euclidean"

# SAINT / Torch defaults
SAINT_EPOCHS = 8
SAINT_LR = 1e-3

# Scoring weights & threshold
SCORE_WEIGHTS = {
    "sharpe_consistency": 0.40,
    "avg_abs_sharpe":     0.20,
    "max_abs_sharpe":     0.10,
    "sign_flip_penalty":  0.15,
    "ols_dummy_t":        0.10,
    "ols_dummy_coef":     0.05,
}
SCORE_THRESHOLD = 0.60

# Organized subdirs
SUBDIRS = {
    "regimes":    os.path.join(OUTPUT_DIR, "regimes"),
    "selectors":  os.path.join(OUTPUT_DIR, "selectors"),
    "perf":       os.path.join(OUTPUT_DIR, "perf"),
    "stat_tests": os.path.join(OUTPUT_DIR, "stat_tests"),
    "designs":    os.path.join(OUTPUT_DIR, "designs"),
    "figures":    os.path.join(OUTPUT_DIR, "figures"),
    "scores":     os.path.join(OUTPUT_DIR, "scores"),
}
for p in SUBDIRS.values():
    os.makedirs(p, exist_ok=True)
for split in ["train","test"]:
    for metric in ["sharpe","mean","vol"]:
        os.makedirs(os.path.join(SUBDIRS["perf"], split, metric), exist_ok=True)