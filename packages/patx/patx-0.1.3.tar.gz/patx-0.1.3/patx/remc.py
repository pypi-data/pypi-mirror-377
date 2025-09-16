import pandas as pd
import numpy as np
import os
import time
import warnings
from sklearn.metrics import roc_auc_score
from patx import PatternOptimizer, get_model
warnings.filterwarnings('ignore')

def load_remc_data(cell_line):
    """Load preprocessed REMC data for a specific cell line."""
    data_file = f"../data/{cell_line}.parquet"
    
    df = pd.read_parquet(data_file)
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
    
    # Combined X for CV splitting and CNN/TSFRESH (which expect single matrix)
    X_combined = df[feature_cols].values
    
    return {'X_list': X_list, 'y': y, 'X': X_combined}

# Get cell lines from processed data
processed_files = [f for f in os.listdir('../data') if f.endswith('.parquet')]
cell_lines = [f.replace('.parquet', '') for f in processed_files]
cell_lines.sort()

results_file = '../results/remc.csv'
results = []
processed_cell_lines = set()


for cell_line in cell_lines:
    print(f"Processing {cell_line}")
    
    data_dict = load_remc_data(cell_line)
    
    X_list = data_dict['X_list']
    y = data_dict['y']
    X_combined = data_dict['X']
    for fold, (train_idx, val_idx) in enumerate(skf.split(X_combined, y)):
        y_train, y_val = y[train_idx], y[val_idx]
        
        t0 = time.time()
        X_train_list = [X_s[train_idx] for X_s in X_list]
        X_val_list = [X_s[val_idx] for X_s in X_list]
        
        model = get_model('lightgbm', 'classification', 'REMC')
        optimizer = PatternOptimizer(X_train_list, y_train, model=model, max_n_trials=300, 
                                    show_progress=True, test_size=0.3, n_jobs=-1, 
                                    dataset='REMC', multiple_series=True, 
                                    X_test_data=X_val_list, polynomial_degree=3, 
                                    metric='auc', val_size=0.3, initial_features=None)
        result = optimizer.feature_extraction()
        if fold == 0:
            optimizer.save_parameters_to_json(f'../json_files/REMC/{cell_line}')
        model = result['model']
        test_preds = model.predict_proba_positive(result['X_test'])
        n_features = len(result['patterns'])
        
        t1 = time.time()
        score = roc_auc_score(y_val, test_preds)
        print(f"{cell_line} fold {fold+1}: {score:.4f}")
