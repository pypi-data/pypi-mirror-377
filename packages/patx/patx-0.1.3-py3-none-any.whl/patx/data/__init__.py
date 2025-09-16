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

def load_remc_data():
    """
    Load the REMC (Roadmap Epigenomics Consortium) data for multiple time series example.
    
    This dataset contains chromatin modification data with 5 different histone marks
    (H3K4me3, H3K4me1, H3K36me3, H3K9me3, H3K27me3) measured across 200 genomic positions.
    
    Returns
    -------
    dict
        Dictionary containing:
        - 'X_list': List of numpy arrays, one for each time series
        - 'y': Target labels (numpy array)
        - 'X': Combined feature matrix (numpy array)
        - 'series_names': List of time series identifiers
    """
    data_path = get_data_path() / "E003.parquet"
    df = pd.read_parquet(data_path)
    
    feature_cols = [col for col in df.columns if col != 'target']
    y = df['target'].values
    
    # Separate the multiple time series
    TIME_SERIES_IDENTIFIERS = ['H3K4me3', 'H3K4me1', 'H3K36me3', 'H3K9me3', 'H3K27me3']
    X_list = []
    
    for series_id in TIME_SERIES_IDENTIFIERS:
        series_cols = [col for col in feature_cols if col.startswith(f"{series_id}_")]
        if series_cols:
            series_cols.sort(key=lambda x: int(x.split('_')[1]))  # Sort by time point
            X_series = df[series_cols].values
            X_list.append(X_series)
    
    # Combined X for methods that expect single matrix
    X_combined = df[feature_cols].values
    
    return {
        'X_list': X_list, 
        'y': y, 
        'X': X_combined,
        'series_names': TIME_SERIES_IDENTIFIERS
    }
