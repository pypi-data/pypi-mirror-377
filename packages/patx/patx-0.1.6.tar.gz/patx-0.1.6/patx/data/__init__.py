"""Data module for PatX package."""

import os
import pandas as pd
import numpy as np
from pathlib import Path

def get_data_path():
    """Get the path to the data directory."""
    return Path(__file__).parent

def load_mitbih_data():
    """
    Load the MIT-BIH Arrhythmia Database data.
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing the processed MIT-BIH data
    """
    data_path = get_data_path() / "mitbih_processed.csv"
    return pd.read_csv(data_path)

def load_remc_data(series=("H3K4me3", "H3K4me1")):
    """
    Load the REMC data as separate numpy arrays per series (multiple time series).
    Only the requested series are returned, defaulting to two: H3K4me3, H3K4me1.
    """
    data_path = get_data_path() / "E003.parquet"
    df = pd.read_parquet(data_path)

    y = df['target'].to_numpy()
    X_list = []
    series_names = []
    for s in series:
        cols = [c for c in df.columns if c.startswith(f"{s}_")]
        if not cols:
            continue
        cols.sort(key=lambda x: int(x.split('_')[1]))
        X_list.append(df[cols].to_numpy())
        series_names.append(s)

    # Combined matrix for convenience (concatenate requested series)
    X_combined = np.concatenate(X_list, axis=1) if X_list else np.empty((len(y), 0))

    return {
        'X_list': X_list,
        'y': y,
        'X': X_combined,
        'series_names': series_names,
    }
