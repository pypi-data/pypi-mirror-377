# regimes_lab/configs.py
import os

# Paths
OUTPUT_DIR = "./regimes_lab/output"
CACHE_DIR  = os.path.join(OUTPUT_DIR, "cache")
FIG_DIR    = os.path.join(OUTPUT_DIR, "figures")   # global figs (if any)
REG_DIR    = os.path.join(OUTPUT_DIR, "regimes")

# Stats subfolders
STATS_DIR      = os.path.join(OUTPUT_DIR, "stats")
STATS_TAB_DIR  = os.path.join(STATS_DIR, "tables")
STATS_FIG_DIR  = os.path.join(STATS_DIR, "figures")

for d in [OUTPUT_DIR, CACHE_DIR, FIG_DIR, REG_DIR, STATS_DIR, STATS_TAB_DIR, STATS_FIG_DIR]:
    os.makedirs(d, exist_ok=True)

# Data files (levels & indicators)
LEVELS_CSV     = "levels.csv"
INDICATORS_CSV = "indicators.csv"

# Splits / horizons
TRAIN_FRAC  = 0.7
VAL_FRAC    = 0.15
FORECAST_LAGS = [1, 5, 20]   # horizons (days)

# Rolling / recursive
ROLL_WINDOW = 500
ROLL_STEP   = 20
CADENCE     = 5
RECURSIVE   = False

# Models hyperparams
N_CLUSTERS = 8
PCA_DIM    = 3

# HAC & residual diagnostics
HAC_LAGS   = 5
DW_TOL     = 0.5
LB_ALPHA   = 0.05