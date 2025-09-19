import os

# I/O
BASE_DIR = './regimes_lab/'
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LABELS_DIR = os.path.join(OUTPUT_DIR, "labels")
STATS_DIR  = os.path.join(OUTPUT_DIR, "stats")
STATS_TAB_DIR = os.path.join(STATS_DIR, "tables")
STATS_FIG_DIR = os.path.join(STATS_DIR, "figures")

for d in [OUTPUT_DIR, LABELS_DIR, STATS_DIR, STATS_TAB_DIR, STATS_FIG_DIR]:
    os.makedirs(d, exist_ok=True)

# Data
LEVELS_CSV = os.path.join(BASE_DIR, "levels.csv")
INDICATORS_CSV = os.path.join(BASE_DIR, "indicators.csv")

# Regime counts
N_CLUSTERS = 12

# Splits (single split used by runners; rolling handled elsewhere)
TRAIN_FRAC = 0.6
VAL_FRAC   = 0.2   # test = 1 - train - val

# HMM config (safe fallback if hmmlearn missing)
HMM = dict(
    N_COMPONENTS=N_CLUSTERS,
    COVARIANCE_TYPE="full",
    N_INIT=8,
    N_ITER=800,
    TOL=1e-4,
    REG_COVAR=1e-3,
    RANDOM_STATE=0,
    PREINIT_KMEANS=True,
    WHITEN_PCA=False,
)

# VQ-VAE robust config
VQVAE = dict(
    CODEBOOK_K=N_CLUSTERS,
    EMBED_DIM=32,
    COMMIT_BETA=0.25,
    EMA_UPDATE=True,
    EMA_DECAY=0.99,
    ENTROPY_W=0.02,
    DEAD_CODE_EVERY=5,
    LR=1e-3,
    EPOCHS=80,
    BATCH_SIZE=256,
    DROPOUT=0.1,
    INPUT_NORM="standard",
    SEED=0,
)

# SAINT config (true inter/intra attention)
SAINT = dict(
    EMBED_DIM=64, DEPTH=4, HEADS=4, DROPOUT=0.1,
    MASK_P=0.15, EPOCHS=60, LR=1e-3, BATCH_SIZE=256, SEED=0,
    K_NEIGHBORS=7,
)

# Stats config
HAC_LAGS = 5   # Newey-West maxlags
LJUNGBOX_LAGS = 10

# Default horizons to process (runners can override)
DEFAULT_HORIZONS = [1, 5, 10]

# add at end (or near other model configs)
CPD = dict(
    BINSEG_N_BKPS=6,
    MODEL="l2",
)

# Scoring config for auto selector
# configs.py
SELECTOR = dict(
    METRICS    = ["t_hac", "abs_coef", "neg_p"],    # add neg_p to reward small p
    WEIGHTS    = {"t_hac": 1.0, "abs_coef": 1.0, "neg_p": 1.0},
    THRESHOLDS = {"p_hac_max": 0.05, "coverage_min": 10},  # discard weak/rare dummies
    HAC_LAGS   = 5
)