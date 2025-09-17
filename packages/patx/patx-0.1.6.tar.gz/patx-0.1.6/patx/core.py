"""
Core PatternOptimizer class for extracting polynomial patterns from time series data.
"""

import numpy as np
from sklearn.model_selection import train_test_split
import optuna
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from .models import evaluate_model_performance, clone_model, get_model

optuna.logging.set_verbosity(optuna.logging.WARNING)


class PatternExtractor:
    """
    Extract polynomial patterns from time series data for feature engineering.
    
    This class uses Optuna optimization to find polynomial patterns in time series
    that are most predictive for the target variable.
    """
    
    def __init__(self, X_train, y_train, dataset, X_test=None, model=None,
                 max_n_trials=50, n_jobs=-1, show_progress=True,
                 multiple_series=None, metric=None, polynomial_degree=3,
                 val_size=0.3, initial_features=None):
        """
        Initialize PatternExtractor.
        
        Parameters
        ----------
        X_train : array-like or list of arrays
            Training data
        y_train : array-like
            Training targets
        dataset : str
            Dataset name
        X_test : array-like or list of arrays, optional
            Test data for feature extraction (same structure as X_train)
        model : object, optional
            Model with fit() and predict() methods. Defaults to LightGBM.
        max_n_trials : int, optional
            Maximum number of optimization trials (default: 50)
        n_jobs : int, optional
            Number of parallel jobs for optimization (default: -1)
        show_progress : bool, optional
            Whether to show progress bar (default: True)
        multiple_series : bool, optional
            Whether data contains multiple time series. If None, inferred from X_train (default: None)
        metric : str, optional
            Evaluation metric ('rmse', 'accuracy', 'auc'). If None, inferred (default: None)
        polynomial_degree : int, optional
            Degree of polynomial patterns (default: 3)
        val_size : float, optional
            Validation size (default: 0.3)
        initial_features : array-like, optional
            Initial features to include
        """
        # Infer multiple series if not provided
        inferred_multiple = isinstance(X_train, list)
        self.multiple_series = inferred_multiple if multiple_series is None else multiple_series

        # Normalize X_train into expected internal shape
        if self.multiple_series and isinstance(X_train, list):
            self.X_series_list = [np.asarray(x, dtype=np.float32) for x in X_train]
            self.X_train = np.stack(self.X_series_list, axis=1)
        else:
            self.X_series_list = None
            self.X_train = np.asarray(X_train, dtype=np.float32)

        self.y_train = np.asarray(y_train, dtype=np.float32)

        # Store X_test with new name
        self.X_test = X_test

        # Defaults for control params
        self.max_n_trials = max_n_trials
        self.pattern_list = []
        self.pattern_starts = []
        self.pattern_ends = []
        self.pattern_series_indices = []
        self.n_jobs = n_jobs
        self.show_progress = show_progress
        self.dataset = dataset
        # Determine task type and defaults
        unique_targets = np.unique(self.y_train)
        is_classification = unique_targets.size <= 20 and np.allclose(unique_targets, unique_targets.astype(int))
        if model is None:
            task_type = 'classification' if is_classification else 'regression'
            n_classes = int(unique_targets.size) if task_type == 'classification' else None
            self.model = get_model(task_type, dataset, n_classes=n_classes)
        else:
            self.model = model
        if metric is None:
            if is_classification:
                # Prefer AUC for binary problems, else accuracy
                self.metric = 'auc' if unique_targets.size == 2 else 'accuracy'
            else:
                self.metric = 'rmse'
        else:
            self.metric = metric
        self.features_list = []
        self.best_score = float('inf') if self.metric == 'rmse' else -float('inf')
        self.val_size = val_size
        self.polynomial_degree = polynomial_degree
        self.initial_features = initial_features
    
    def polynomial_pattern(self, coeffs, n_points):
        """Generate polynomial pattern from coefficients."""
        x = np.linspace(-1, 1, n_points, dtype=np.float16)
        coeffs = np.array(coeffs, dtype=np.float16)
        powers = np.arange(len(coeffs), dtype=np.float16)
        return np.sum(coeffs * (x[:, None] ** powers), axis=1)

    def calculate_pattern_rmse(self, X_region, pattern_values):
        """Calculate RMSE between data region and pattern."""
        return np.sqrt(np.mean((X_region - pattern_values) ** 2, axis=1))

    def objective(self, trial, dim):
        """Optuna objective function for pattern optimization."""
        series_index = trial.suggest_int('series_index', 0, self.X_train.shape[1] - 1) if self.multiple_series else None
        pattern_start = trial.suggest_int('pattern_start', 0, dim - 2)
        pattern_width = trial.suggest_int('pattern_width', 1, dim - pattern_start)
        coeffs = [trial.suggest_float(f'c{i}', -1, 1) for i in range(self.polynomial_degree + 1)]
        X_data = self.X_train[:, series_index, :] if self.multiple_series and series_index is not None and self.X_train.ndim == 3 else self.X_train
        X_region = X_data[:, pattern_start:pattern_start + pattern_width]
        new_feature = self.calculate_pattern_rmse(X_region, self.polynomial_pattern(coeffs, pattern_width))
        X_combined = np.column_stack(self.features_list + [new_feature]) if self.features_list else new_feature.reshape(-1, 1)
        X_train, X_val, y_train, y_val = train_test_split(X_combined, self.y_train, test_size=self.val_size, random_state=42)
        
        # Create a fresh model instance for this trial to avoid threading issues
        model = clone_model(self.model)
        
        model.fit(X_train, y_train, X_val, y_val)
        return evaluate_model_performance(model, X_val, y_val, self.metric)
    
    def feature_extraction(self, X_series_list=None):
        """
        Extract features using optimized polynomial patterns.
        
        Parameters
        ----------
        X_series_list : list, optional
            List of time series data
            
        Returns
        -------
        dict
            Dictionary containing patterns, features, and model results
        """
        first_pattern = True
        if X_series_list is not None and self.multiple_series:
            self.X_series_list = [np.asarray(x, dtype=np.float32) for x in X_series_list]
            self.X_train = np.stack(self.X_series_list, axis=1)
        dim = self.X_train.shape[2] if self.multiple_series and self.X_train.ndim == 3 else self.X_train.shape[1]
        train_initial_features, test_initial_features = (None, None) if self.initial_features is None else ((np.asarray(self.initial_features[0], dtype=np.float32), np.asarray(self.initial_features[1], dtype=np.float32)) if isinstance(self.initial_features, tuple) and len(self.initial_features) == 2 else (np.asarray(self.initial_features, dtype=np.float32), None))
        if train_initial_features is not None: 
            self.features_list = [train_initial_features]
        
        while True:
            study = optuna.create_study(direction="minimize" if self.metric == 'rmse' else "maximize", pruner=optuna.pruners.MedianPruner())
            study.optimize(lambda trial: self.objective(trial, dim), n_trials=self.max_n_trials, n_jobs=self.n_jobs, show_progress_bar=self.show_progress)
            if first_pattern or (self.metric == 'rmse' and study.best_value < self.best_score) or (self.metric != 'rmse' and study.best_value > self.best_score):
                self.best_score = study.best_value
                best_params = study.best_trial.params
                pattern_start = best_params['pattern_start']
                pattern_width = best_params['pattern_width']
                coeffs = [best_params[f'c{i}'] for i in range(self.polynomial_degree + 1)]
                series_index = best_params.get('series_index')
                pattern_values = self.polynomial_pattern(coeffs, pattern_width)
                pattern_end = pattern_start + pattern_width
                new_pattern = np.zeros(dim, dtype=np.float32)
                new_pattern[pattern_start:pattern_end] = pattern_values
                self.pattern_list.append(new_pattern)
                self.pattern_starts.append(pattern_start)
                self.pattern_ends.append(pattern_end)
                if self.multiple_series:
                    self.pattern_series_indices.append(series_index)
                X_data = self.X_train
                if self.multiple_series and series_index is not None and X_data.ndim == 3:
                    X_data = X_data[:, series_index, :]
                X_region = X_data[:, pattern_start:pattern_end]
                new_feature_full = self.calculate_pattern_rmse(X_region, pattern_values)
                self.features_list.append(new_feature_full)
                first_pattern = False
            else:
                break
        
        cached_features = np.column_stack(self.features_list) if self.features_list else np.empty((self.X_train.shape[0], 0))
        X_train, X_val, y_train, y_val = train_test_split(cached_features, self.y_train, test_size=self.val_size, random_state=42)
        self.model.fit(X_train, y_train, X_val, y_val)
        n_test_samples = self.X_test[0].shape[0] if isinstance(self.X_test, list) else self.X_test.shape[0]
        n_pattern_features = len(self.pattern_list)
        n_initial_features = train_initial_features.shape[1] if train_initial_features is not None else 0
        X_test = np.empty((n_test_samples, n_initial_features + n_pattern_features), dtype=np.float32)
        X_test[:, :n_initial_features] = test_initial_features if test_initial_features is not None else 0.0
        for i, pattern in enumerate(self.pattern_list):
            series_idx = self.pattern_series_indices[i] if self.multiple_series and self.pattern_series_indices else None
            X_for_pattern = self.X_test[series_idx] if self.multiple_series and isinstance(self.X_test, list) and series_idx is not None else self.X_test
            X_data = np.asarray(X_for_pattern, dtype=np.float32) if not isinstance(X_for_pattern, np.ndarray) else X_for_pattern
            if self.multiple_series and series_idx is not None and X_data.ndim == 3:
                X_data = X_data[:, series_idx, :]
            start, end = self.pattern_starts[i], self.pattern_ends[i]
            X_region = X_data[:, start:end]
            pattern_feature = self.calculate_pattern_rmse(X_region, pattern[start:end]).reshape(-1, 1)
            X_test[:, n_initial_features + i:n_initial_features + i+1] = pattern_feature
        result = {'patterns': self.pattern_list,'starts': self.pattern_starts,'ends': self.pattern_ends,'features': cached_features,'X_train': X_train,'X_val': X_val,'y_train': y_train,'y_val': y_val,'X_test': X_test}
        if self.multiple_series and self.pattern_series_indices: 
            result['series_indices'] = self.pattern_series_indices
        X_combined = np.vstack((X_train, X_val))
        y_combined = np.hstack((y_train, y_val))
        X_train, X_val, y_train, y_val = train_test_split(X_combined, y_combined, test_size=self.val_size, random_state=42)
        self.model.fit(X_train, y_train, X_val, y_val)
        result['model'] = self.model
        return result

    def save_parameters_to_json(self, dataset_name):
        """
        Save all optimized pattern parameters to a JSON file.
        
        Parameters
        ----------
        dataset_name : str
            Name of the dataset for file organization
        """
        params_dict = {
            'dataset': self.dataset,
            'metric': self.metric,
            'polynomial_degree': self.polynomial_degree,
            'n_patterns': len(self.pattern_list),
            'patterns': []
        }
        for i, pattern in enumerate(self.pattern_list):
            pattern_info = {
                'pattern_id': i,
                'pattern_start': int(self.pattern_starts[i]),
                'pattern_width': int(self.pattern_ends[i] - self.pattern_starts[i]),
                'pattern_values': pattern[self.pattern_starts[i]:self.pattern_ends[i]].tolist(),
            }
            if self.multiple_series and self.pattern_series_indices:
                pattern_info['series_index'] = int(self.pattern_series_indices[i])
            params_dict['patterns'].append(pattern_info)
        
        os.makedirs(f'json_files/{dataset_name}', exist_ok=True)
        with open(f'json_files/{dataset_name}/pattern_parameters.json', 'w') as f:
            json.dump(params_dict, f, indent=2)

    def visualize_patterns(self, pattern_indices=None, dataset_name=None, specific_name='patterns', show_rmse_distribution=True):
        """
        Visualize selected patterns and save as PNG file.
        
        Parameters
        ----------
        pattern_indices : list, optional
            List of pattern indices to visualize. If None, visualizes all patterns.
        dataset_name : str, optional
            Dataset name for file organization. If None, uses self.dataset.
        specific_name : str, optional
            Specific name for the output file (default: 'patterns')
        show_rmse_distribution : bool, optional
            Whether to show RMSE distribution plot (default: True)
        """
        if not self.pattern_list:
            print("No patterns found. Run feature_extraction() first.")
            return
            
        if pattern_indices is None:
            pattern_indices = list(range(len(self.pattern_list)))
        if dataset_name is None:
            dataset_name = self.dataset
            
        valid_indices = [i for i in pattern_indices if 0 <= i < len(self.pattern_list)]
        n_patterns = len(valid_indices)
        if n_patterns == 0:
            print("No valid pattern indices provided.")
            return
        
        n_cols = 2 if show_rmse_distribution else 1
        fig, axes = plt.subplots(n_patterns, n_cols, figsize=(16 if show_rmse_distribution else 8, 4*n_patterns))
        if n_patterns == 1:
            if show_rmse_distribution:
                axes = axes.reshape(1, -1)
            else:
                axes = [axes]
        
        for idx, pattern_idx in enumerate(valid_indices):
            pattern = self.pattern_list[pattern_idx]
            start = self.pattern_starts[pattern_idx]
            end = self.pattern_ends[pattern_idx]
            
            # Pattern visualization
            ax_left = axes[idx, 0] if show_rmse_distribution else axes[idx]
            ax_left.plot(range(len(pattern)), pattern, 'b-', alpha=0.3, label='Full Pattern')
            active_pattern = pattern[start:end]
            active_x = range(start, end)
            ax_left.plot(active_x, active_pattern, 'r-', linewidth=3, label='Active Region')
            ax_left.scatter(active_x, active_pattern, c='red', s=50, zorder=5)
            
            title = f'Pattern {pattern_idx} (positions {start}-{end})'
            if self.multiple_series and self.pattern_series_indices:
                title += f', Series {self.pattern_series_indices[pattern_idx]}'
            ax_left.set_title(title)
            ax_left.set_xlabel('Position')
            ax_left.set_ylabel('Pattern Value')
            ax_left.legend()
            ax_left.grid(True, alpha=0.3)
            y_min, y_max = ax_left.get_ylim()
            ax_left.set_ylim(y_min - 0.1, y_max + 0.1)
            
            # RMSE distribution plot (optional)
            if show_rmse_distribution:
                ax_right = axes[idx, 1]
                series_idx = self.pattern_series_indices[pattern_idx] if self.multiple_series and self.pattern_series_indices else None
                X_for_pattern = self.X_train
                if self.multiple_series and series_idx is not None and self.X_train.ndim == 3:
                    X_for_pattern = self.X_train[:, series_idx, :]
                X_data = np.asarray(X_for_pattern, dtype=np.float32)
                pattern_region = pattern[start:end]
                X_region = X_data[:, start:end]
                rmse_values = self.calculate_pattern_rmse(X_region, pattern_region.astype(np.float32)).flatten()
                df = pd.DataFrame({'RMSE': rmse_values,'Target': self.y_train})
                
                unique_targets = len(np.unique(self.y_train))
                if unique_targets <= 10:
                    sns.histplot(data=df, x='RMSE', hue='Target', bins=100, alpha=0.7, ax=ax_right)
                    ax_right.set_title('RMSE Distribution (by Target)')
                else:
                    sns.histplot(data=df, x='RMSE', bins=100, alpha=0.7, ax=ax_right)
                    ax_right.set_title('RMSE Distribution')
                ax_right.set_xlabel('RMSE')
                ax_right.set_ylabel('Count')
                ax_right.grid(True, alpha=0.3)
        
        plt.tight_layout()
        os.makedirs(f'images/{dataset_name}', exist_ok=True)
        filename = f'images/{dataset_name}/{specific_name}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Patterns visualized and saved to: {filename}")
