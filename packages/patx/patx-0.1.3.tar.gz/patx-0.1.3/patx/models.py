"""
Model definitions and evaluation utilities for PatX.
"""

import lightgbm as lgb
import xgboost as xgb
from sklearn.metrics import accuracy_score, roc_auc_score, mean_squared_error
import numpy as np


def get_lgb_params(task_type, dataset, n_classes=None):
    """
    Get LightGBM parameters for different tasks and datasets.
    
    Parameters
    ----------
    task_type : str
        Type of task ('classification' or 'regression')
    dataset : str
        Dataset name
    n_classes : int, optional
        Number of classes for multiclass classification
        
    Returns
    -------
    dict
        LightGBM parameters
    """
    params = {
        'learning_rate': 0.1,
        'max_depth': 3,
        'num_iterations': 100,
        'random_state': 42,
        'num_threads': 1,   
        'force_col_wise': True,
        'verbosity': -1,
        'data_sample_strategy': 'goss',
    }
    
    if task_type == 'classification':
        if dataset == 'REMC':
            params['objective'] = 'binary'
            params['metric'] = 'auc'
        else:
            params['objective'] = 'multiclass'
            params['metric'] = 'multi_logloss'
            if n_classes is not None:
                params['num_class'] = n_classes
    else:
        params['objective'] = 'regression'
        params['metric'] = 'rmse'
    
    return params


def get_xgb_params(task_type, dataset, n_classes=None):
    """
    Get XGBoost parameters for different tasks and datasets.
    
    Parameters
    ----------
    task_type : str
        Type of task ('classification' or 'regression')
    dataset : str
        Dataset name
    n_classes : int, optional
        Number of classes for multiclass classification
        
    Returns
    -------
    dict
        XGBoost parameters
    """
    params = {
        'learning_rate': 0.1,
        'max_depth': 3,
        'n_estimators': 100,
        'random_state': 42,
        'n_jobs': 1,
        'verbosity': 0,
    }
    
    if task_type == 'classification':
        if dataset == 'REMC':
            params['objective'] = 'binary:logistic'
            params['eval_metric'] = 'auc'
        else:
            if n_classes is not None and n_classes > 2:
                params['objective'] = 'multi:softprob'
                params['eval_metric'] = 'mlogloss'
                params['num_class'] = n_classes
            else:
                params['objective'] = 'binary:logistic'
                params['eval_metric'] = 'auc'
    else:
        params['objective'] = 'reg:squarederror'
        params['eval_metric'] = 'rmse'
    
    return params


class XGBoostModel:
    """
    Wrapper class for XGBoost models with consistent interface.
    """
    
    def __init__(self, params):
        """
        Initialize XGBoost model.
        
        Parameters
        ----------
        params : dict
            XGBoost parameters
        """
        self.params = params
        self.model = None
        self.task_type = 'classification' if 'binary' in str(params.get('objective', '')) or 'multi' in str(params.get('objective', '')) else 'regression'
    
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """
        Train the XGBoost model.
        
        Parameters
        ----------
        X_train : array-like
            Training features
        y_train : array-like
            Training targets
        X_val : array-like, optional
            Validation features
        y_val : array-like, optional
            Validation targets
            
        Returns
        -------
        self
            Trained model instance
        """
        if self.task_type == 'classification':
            self.model = xgb.XGBClassifier(**self.params)
        else:
            self.model = xgb.XGBRegressor(**self.params)
        
        eval_set = [(X_val, y_val)] if X_val is not None and y_val is not None else None
        
        fit_params = {'verbose': False}
        if eval_set is not None:
            fit_params['eval_set'] = eval_set
            # Use callbacks for early stopping in newer XGBoost versions
            try:
                from xgboost.callback import EarlyStopping
                fit_params['callbacks'] = [EarlyStopping(rounds=10, save_best=True)]
            except ImportError:
                # Fallback for older versions
                fit_params['early_stopping_rounds'] = 10
        
        self.model.fit(X_train, y_train, **fit_params)
        return self
    
    def predict(self, X):
        """
        Make predictions.
        
        Parameters
        ----------
        X : array-like
            Features to predict on
            
        Returns
        -------
        array-like
            Predictions
        """
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """
        Get prediction probabilities.
        
        Parameters
        ----------
        X : array-like
            Features to predict on
            
        Returns
        -------
        array-like
            Prediction probabilities
        """
        if self.task_type == 'classification':
            return self.model.predict_proba(X)
        else:
            raise ValueError("predict_proba not available for regression tasks")
    
    def predict_proba_positive(self, X):
        """
        Get probability of positive class for binary classification.
        
        Parameters
        ----------
        X : array-like
            Features to predict on
            
        Returns
        -------
        array-like
            Probability of positive class
        """
        preds = self.predict_proba(X)
        if preds.ndim == 2:
            return preds[:, 1]
        return preds


class LightGBMModel:
    """
    Wrapper class for LightGBM models with consistent interface.
    """
    
    def __init__(self, params):
        """
        Initialize LightGBM model.
        
        Parameters
        ----------
        params : dict
            LightGBM parameters
        """
        self.params = params
        self.booster = None
    
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """
        Train the LightGBM model.
        
        Parameters
        ----------
        X_train : array-like
            Training features
        y_train : array-like
            Training targets
        X_val : array-like, optional
            Validation features
        y_val : array-like, optional
            Validation targets
            
        Returns
        -------
        self
            Trained model instance
        """
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_sets = []
        if X_val is not None and y_val is not None:
            valid_sets = [lgb.Dataset(X_val, label=y_val, reference=train_data)]
        
        self.booster = lgb.train(
            self.params, 
            train_data, 
            valid_sets=valid_sets, 
            callbacks=[lgb.early_stopping(10, verbose=False)] if valid_sets else None
        )
        return self
    
    def predict(self, X):
        """
        Make predictions.
        
        Parameters
        ----------
        X : array-like
            Features to predict on
            
        Returns
        -------
        array-like
            Predictions
        """
        preds = self.booster.predict(X)
        if self.params.get('objective') == 'multiclass':
            return np.argmax(preds, axis=1)
        elif self.params.get('objective') == 'binary':
            return (preds > 0.5).astype(int)
        return preds
    
    def predict_proba(self, X):
        """
        Get prediction probabilities.
        
        Parameters
        ----------
        X : array-like
            Features to predict on
            
        Returns
        -------
        array-like
            Prediction probabilities
        """
        preds = self.booster.predict(X)
        if self.params.get('objective') == 'binary':
            return np.column_stack([1 - preds, preds])
        else:
            return preds
    
    def predict_proba_positive(self, X):
        """
        Get probability of positive class for binary classification.
        
        Parameters
        ----------
        X : array-like
            Features to predict on
            
        Returns
        -------
        array-like
            Probability of positive class
        """
        preds = self.predict_proba(X)
        if preds.ndim == 2:
            return preds[:, 1]
        return preds


def get_model(model_type='lightgbm', task_type='classification', dataset='', n_classes=None):
    """
    Get a model instance for the specified task and dataset.
    
    Parameters
    ----------
    model_type : str, optional
        Type of model ('lightgbm' or 'xgboost'), default 'lightgbm'
    task_type : str
        Type of task ('classification' or 'regression')
    dataset : str
        Dataset name
    n_classes : int, optional
        Number of classes for multiclass classification
        
    Returns
    -------
    Model instance
        Configured model instance (LightGBMModel or XGBoostModel)
    """
    if model_type.lower() == 'xgboost' or model_type.lower() == 'xgb':
        params = get_xgb_params(task_type, dataset, n_classes)
        return XGBoostModel(params)
    else:  # default to lightgbm
        params = get_lgb_params(task_type, dataset, n_classes)
        return LightGBMModel(params)


def evaluate_model_performance(model, X, y, metric):
    """
    Evaluate model performance using the specified metric.
    
    Parameters
    ----------
    model : object
        Trained model with predict methods
    X : array-like
        Features
    y : array-like
        True targets
    metric : str
        Evaluation metric ('auc', 'accuracy', 'rmse')
        
    Returns
    -------
    float
        Performance score
    """
    if metric == 'auc':
        if len(np.unique(y)) > 2:
            y_pred = model.predict_proba(X)
            score = roc_auc_score(y, y_pred, multi_class='ovr', average='macro')
        else:
            y_pred = model.predict_proba_positive(X)
            score = roc_auc_score(y, y_pred)
    elif metric == 'accuracy':
        y_pred = model.predict(X)
        score = accuracy_score(y, y_pred)
    elif metric == 'rmse':
        y_pred = model.predict(X)
        score = np.sqrt(mean_squared_error(y, y_pred))
    return score
