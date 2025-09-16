# viz_utils.py
import pandas as pd
from utils import plot_timeline_chunked

def plot_all_timelines(regimes_df: pd.DataFrame):
    for col in regimes_df.columns:
        plot_timeline_chunked(
            regimes_df[col].values,
            regimes_df.index,
            title=f"Regimes — {col}",
            fname=f"exhibit4_{col}"
        )