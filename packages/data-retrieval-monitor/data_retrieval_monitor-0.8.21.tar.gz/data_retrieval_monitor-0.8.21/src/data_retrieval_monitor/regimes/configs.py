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
    "perf_train":   os.path.join(OUTPUT_DIR, "perf_train"),
    "perf_test":    os.path.join(OUTPUT_DIR, "perf_test"),
    "stat_tests":   os.path.join(OUTPUT_DIR, "stat_tests"),
    "designs":      os.path.join(OUTPUT_DIR, "designs"),
    "figures":      os.path.join(OUTPUT_DIR, "figures"),
}
os.makedirs(OUTPUT_DIR, exist_ok=True)
for p in SUBDIRS.values():
    os.makedirs(p, exist_ok=True)

# Randomness
SEED = 7

# Splits (chronological)
TRAIN_FRAC = 0.60
VAL_FRAC   = 0.20   # test is the rest (0.20)

# Leakage guard
IND_LAG = 2  # business days

# Clustering
N_CLUSTERS = 4
KMEANS_N_INIT = 50
KMEANS_MAX_ITER = 1000

# kNN refinement
KNN_K = 10

# PCA
PCA_COMPONENTS = 3

# Rolling windows for distributional distances
OLD_WIN = 252 * 4
NEW_WIN = 63

# SAINT hyperparams (if you use it)
SAINT_D_MODEL  = 64
SAINT_NHEAD    = 4
SAINT_NLAYERS  = 2
SAINT_DFF      = 128
SAINT_DROPOUT  = 0.1
SAINT_EPOCHS   = 30
SAINT_LR       = 1e-3
SAINT_WD       = 1e-4
SAINT_BS       = 256

# VQ-VAE
VQVAE_CODEBOOK_K = 16
VQVAE_EMBED_DIM  = 8
VQVAE_HIDDEN     = 32
VQVAE_EPOCHS     = 20
VQVAE_LR         = 1e-3
VQVAE_BETA       = 0.25

# VAE latent
VAE_Z_DIM = 8
VAE_H     = 64
VAE_EPOCHS = 25
VAE_LR     = 1e-3

# Estimation mode
RECURSIVE_ESTIMATION = False     # <- per your latest request (batch only)
REFIT_STEP = 20
RECURSIVE_INCLUDE_DEEP = False