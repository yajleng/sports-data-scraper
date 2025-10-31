import pandas as pd
import numpy as np

def normalize_stat(df, column, method="zscore"):
    """
    Normalize a single stat column using a specified method.
    Supported methods: 'zscore', 'minmax', 'scale100'
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in dataframe.")
    
    if method == "zscore":
        mean = df[column].mean()
        std = df[column].std(ddof=0)
        df[f"{column}_z"] = (df[column] - mean) / std if std != 0 else 0
    
    elif method == "minmax":
        min_val = df[column].min()
        max_val = df[column].max()
        df[f"{column}_scaled"] = (df[column] - min_val) / (max_val - min_val)
    
    elif method == "scale100":
        mean = df[column].mean()
        std = df[column].std(ddof=0)
        df[f"{column}_index"] = ((df[column] - mean) / std) * 10 + 100
    
    else:
        raise ValueError(f"Unsupported normalization method: {method}")
    
    return df


def combine_metrics(df, metrics, weights=None):
    """
    Combine multiple normalized metrics into a single composite score.
    weights: dict or list of same length as metrics
    """
    if weights is None:
        weights = [1 for _ in metrics]

    weighted_sum = sum(df[m] * w for m, w in zip(metrics, weights))
    total_weight = sum(weights)
    df["composite_score"] = weighted_sum / total_weight
    return df


def preprocess_team_metrics(data):
    """
    Standardize and prepare key football analytics metrics (EPA, Success Rate, Explosiveness, etc.)
    Expects a DataFrame or dict list with at least these columns:
        team, epa_off, epa_def, success_rate_off, success_rate_def, explosiveness
    """
    df = pd.DataFrame(data)

    normalize_targets = [
        "epa_off", "epa_def", "success_rate_off", "success_rate_def", "explosiveness"
    ]

    for col in normalize_targets:
        if col in df.columns:
            df = normalize_stat(df, col, method="zscore")

    # Combine into balanced team efficiency score
    z_cols = [f"{col}_z" for col in normalize_targets if f"{col}_z" in df.columns]
    df = combine_metrics(df, z_cols, weights=[0.3, 0.2, 0.2, 0.2, 0.1])
    
    return df.round(4).to_dict(orient="records")
