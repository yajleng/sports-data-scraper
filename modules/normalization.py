# modules/normalization.py
import numpy as np
import pandas as pd

METRIC_COLS = [
    "epa_off", "epa_def",
    "success_rate_off", "success_rate_def",
    "explosiveness"
]

def _zscore(series: pd.Series) -> pd.Series:
    mu = series.mean()
    sd = series.std(ddof=0)
    # safe z-score (avoid div-by-zero)
    return (series - mu) / (sd if sd and sd > 0 else 1.0)

def normalize_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input: df with columns ['team', METRIC_COLS...]
    Output: same + *_z (z-scores) + composite_score
    """
    df = df.copy()

    # ensure numeric, coerce bad/missing to NaN->0 (stable for weekly ops)
    for col in METRIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # compute z for each metric across ALL teams (key fix for your zeros)
    for col in METRIC_COLS:
        df[f"{col}_z"] = _zscore(df[col])

    # simple, tunable composite: offense weight 0.6, defense 0.3, explosiveness 0.1
    df["composite_score"] = (
        0.30 * df["epa_off_z"] +
        0.30 * df["success_rate_off_z"] +
        0.10 * df["explosiveness_z"] +
        0.20 * (-df["epa_def_z"]) +          # lower EPA allowed is better
        0.10 * (-df["success_rate_def_z"])
    )

    # keep only what we need outward
    keep = ["team", "composite_score"] + [f"{c}_z" for c in METRIC_COLS]
    return df[keep].sort_values("composite_score", ascending=False).reset_index(drop=True)
