# PatX - Pattern eXtraction for Time Series Feature Engineering

[![PyPI version](https://badge.fury.io/py/patx.svg)](https://badge.fury.io/py/patx)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PatX is a Python package for extracting polynomial patterns from time series data to create meaningful features for machine learning models. It uses Optuna optimization to automatically discover patterns that are most predictive for your target variable.

## Features

- **Automatic Pattern Discovery**: Uses optimization to find the most predictive polynomial patterns in your time series data
- **Multiple Series Support**: Handle datasets with multiple time series channels
- **Flexible Models**: Built-in support for LightGBM with easy extension to custom models
- **Visualization**: Built-in tools to visualize discovered patterns
- **Easy Integration**: Simple API that works with scikit-learn workflows

## Installation

```bash
pip install patx
```

## Quick Start

Copy and paste these complete examples to get started immediately:

### Single Time Series Example (MIT-BIH)

```python
import pandas as pd
from patx import PatternExtractor, get_model, load_mitbih_data
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the included MIT-BIH Arrhythmia dataset
print("Loading MIT-BIH dataset...")
data = load_mitbih_data()
X = data.drop('target', axis=1)
y = data['target'].values

print(f"Dataset shape: {X.shape}")
print(f"Classes: {sorted(pd.unique(y))}")

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Initialize LightGBM model
n_classes = len(pd.unique(y))
model = get_model('classification', 'MITBIH', n_classes=n_classes)

# Create PatternExtractor
optimizer = PatternExtractor(
    X_train=X_train,
    y_train=y_train,
    dataset='MITBIH',
    X_test=X_test
)

# Extract features and train model
result = optimizer.feature_extraction()

# Get results
trained_model = result['model']
patterns = result['patterns']
test_predictions = trained_model.predict(result['X_test'])

# Evaluate performance
accuracy = accuracy_score(y_test, test_predictions)
print(f"\nResults:")
print(f"Discovered {len(patterns)} patterns")
print(f"Test accuracy: {accuracy:.4f}")

# Visualize patterns
optimizer.visualize_patterns()
print("Pattern visualizations saved!")
```

### Pattern Visualization Example

```python

# Visualize first pattern only with RMSE distribution
optimizer.visualize_patterns(pattern_indices=[0])

# Visualize first pattern without RMSE distribution (pattern only)
optimizer.visualize_patterns(
    pattern_indices=[0], 
    show_rmse_distribution=False,
    specific_name='first_pattern_only'
)

# 4. Visualize first 3 patterns without RMSE distribution
optimizer.visualize_patterns(
    pattern_indices=[0, 1, 2], 
    show_rmse_distribution=False,
    specific_name='first_three_patterns'
)

print(f"Visualizations saved to images/MITBIH/ directory")
```

### Multiple Time Series Example (REMC, two series)

```python
import pandas as pd
import numpy as np
from patx import PatternExtractor, get_model, load_remc_data
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

# Load the included REMC dataset with two time series (H3K4me3, H3K4me1)
data = load_remc_data(series=("H3K4me3", "H3K4me1"))
X_list = data['X_list']  # list of np arrays, one per series
y = data['y']
series_names = data['series_names']  # ["H3K4me3", "H3K4me1"]

print(f"Loaded {len(X_list)} series: {series_names}")
print(f"Samples: {len(y)}, time points per series: {X_list[0].shape[1]}")
print(f"Class distribution: {np.bincount(y)}")

# Split indices, then slice each series list (multiple time series)
indices = np.arange(len(y))
train_indices, test_indices = train_test_split(
    indices, test_size=0.3, random_state=42, stratify=y
)

X_train_list = [X[train_indices] for X in X_list]
X_test_list = [X[test_indices] for X in X_list]
y_train, y_test = y[train_indices], y[test_indices]

print(f"Train samples: {len(y_train)}, Test samples: {len(y_test)}")

# Initialize LightGBM model
model = get_model('classification', 'REMC')

# Create PatternExtractor for multiple series (defaults infer multi-series)
print("Starting pattern extraction for multiple time series...")
optimizer = PatternExtractor(
    X_train=X_train_list,
    y_train=y_train,
    dataset='REMC',
    X_test=X_test_list
)

# Extract features and train model
result = optimizer.feature_extraction()

# Get results
trained_model = result['model']
patterns = result['patterns']
test_probabilities = trained_model.predict_proba_positive(result['X_test'])
test_predictions = (test_probabilities > 0.5).astype(int)

# Evaluate performance
auc_score = roc_auc_score(y_test, test_probabilities)
print(f"\nResults:")
print(f"Discovered {len(patterns)} patterns across {len(X_list)} time series")
print(f"Test AUC: {auc_score:.4f}")

# Visualize patterns
optimizer.visualize_patterns()
print("Pattern visualizations saved!")
```

## API Reference

### PatternExtractor

The main class for pattern extraction.

After calling `feature_extraction()`, the extractor stores:

- `patterns`: list of 1D numpy arrays (length = time points), each the discovered pattern, with active region filled and rest zeros
- `starts` / `ends`: start and end indices for each pattern’s active region
- `series_indices` (when multiple series): which series a pattern was optimized on
- `features`: cached training feature matrix built from discovered patterns (and optional initial features)
- `X_test`: feature matrix for the provided test data (aligned to `features` columns)
- `model`: the trained model refit on the final feature set

Return value of `feature_extraction()` is a dict exposing the same keys for convenience.

**Parameters:**
- `X_train`: Training time series data (array or list of arrays for multiple series)
- `y_train`: Training targets
- `dataset`: Dataset name
- `X_test`: Test data for feature extraction (same structure as `X_train`)
- `model`: Optional model instance (defaults to LightGBM based on task)
- `max_n_trials`: Optional max optimization trials (default: 50)
- `n_jobs`: Optional number of parallel jobs (default: -1)
- `show_progress`: Optional progress bar (default: True)
- `dataset`: Dataset name
- `multiple_series`: Optional; inferred when `X_train` is a list
- `metric`: Optional; inferred (binary→auc, multiclass→accuracy, regression→rmse)
- `polynomial_degree`: Optional degree of polynomial patterns (default: 3)
- `val_size`: Optional validation split ratio (default: 0.3)
- `initial_features`: Optional initial features

**Methods:**
- `feature_extraction()`: Extract patterns and return features
- `save_parameters_to_json(dataset_name)`: Save pattern parameters
- `visualize_patterns(pattern_indices=None, dataset_name=None, specific_name='patterns', show_rmse_distribution=True)`: Visualize discovered patterns
  - `pattern_indices`: List of pattern indices to visualize (default: all patterns)
  - `dataset_name`: Dataset name for file organization (default: uses optimizer's dataset)
  - `specific_name`: Name for output file (default: 'patterns')
  - `show_rmse_distribution`: Whether to show RMSE distribution plot (default: True)

### Models

Built-in model support:
- `get_model(task_type, dataset, n_classes)`: Get configured LightGBM model
  - `task_type`: 'classification' or 'regression'
  - `dataset`: Dataset name for parameter optimization
  - `n_classes`: Number of classes (for multiclass classification)
- `LightGBMModel`: LightGBM wrapper with consistent interface
- `evaluate_model_performance(model, X, y, metric)`: Evaluate model

**Examples:**
```python
# Classification with 5 classes
model = get_model('classification', 'MITBIH', n_classes=5)

# Binary classification
model = get_model('classification', 'REMC')

# Regression
model = get_model('regression', 'MyDataset')
```

### Data

- `load_mitbih_data()`: Load the included MIT-BIH Arrhythmia dataset (single time series)
- `load_remc_data()`: Load the included REMC epigenomics dataset (multiple time series)

### Custom Models

You can use any model that implements `fit()` and `predict()` methods. Here are examples:

**XGBoost Example:**
```python
import xgboost as xgb

class XGBoostModel:
    def __init__(self, n_classes=None):
        self.n_classes = n_classes
        self.model = None
    
    def fit(self, X_train, y_train, X_val=None, y_val=None):
        if self.n_classes and self.n_classes > 2:
            self.model = xgb.XGBClassifier(objective='multi:softprob', num_class=self.n_classes)
        else:
            self.model = xgb.XGBClassifier(objective='binary:logistic')
        
        eval_set = [(X_val, y_val)] if X_val is not None else None
        self.model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
        return self
    
    def predict(self, X):
        return self.model.predict(X)
    
    def predict_proba_positive(self, X):
        proba = self.model.predict_proba(X)
        return proba[:, 1] if proba.ndim == 2 else proba

# Use custom model
model = XGBoostModel(n_classes=5)
optimizer = PatternExtractor(X_train, y_train, model=model, ...)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use PatX in your research, please cite:

```bibtex
@software{patx,
  title={PatX: Pattern eXtraction for Time Series Feature Engineering},
  author={Wolber, J.},
  year={2025},
  url={https://github.com/Prgrmmrjns/patX}
}
```