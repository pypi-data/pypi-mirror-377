"""
Model training module with support for multiple algorithms and evaluation metrics
"""

import pandas as pd
import numpy as np
import pickle
import joblib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import logging
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.preprocessing import LabelEncoder

# Regression models
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.svm import SVR

# Classification models
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB

logger = logging.getLogger(__name__)

class ModelTrainer:
    """
    Handles training of multiple ML models with automatic evaluation
    """
    
    def __init__(self):
        self.model = None
        self.model_type = None
        self.features = None
        self.target = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.training_history = []
        self.label_encoder = None
        
        # Available algorithms
        self.regression_algorithms = {
            'linear_regression': LinearRegression,
            'ridge': Ridge,
            'lasso': Lasso,
            'random_forest': RandomForestRegressor,
            'decision_tree': DecisionTreeRegressor,
            'gradient_boosting': GradientBoostingRegressor,
            'svr': SVR
        }
        
        self.classification_algorithms = {
            'logistic_regression': LogisticRegression,
            'random_forest': RandomForestClassifier,
            'decision_tree': DecisionTreeClassifier,
            'gradient_boosting': GradientBoostingClassifier,
            'svc': SVC,
            'naive_bayes': GaussianNB
        }
    
    def train(self, 
              data: Tuple[pd.DataFrame, pd.Series],
              algorithm: str = 'random_forest',
              test_size: float = 0.2,
              random_state: int = 42,
              cv_folds: int = 5,
              hyperparameter_tuning: bool = False,
              **kwargs) -> Dict[str, Any]:
        """
        Train a model with the specified algorithm
        
        Args:
            data: Tuple of (features, target)
            algorithm: Algorithm to use
            test_size: Proportion of data for testing
            random_state: Random state for reproducibility
            cv_folds: Number of cross-validation folds
            hyperparameter_tuning: Whether to perform hyperparameter tuning
            **kwargs: Additional parameters for the algorithm
            
        Returns:
            Dict with training results and metrics
        """
        self.features, self.target = data
        
        # Determine if this is a classification or regression problem
        self.model_type = self._determine_problem_type(self.target)
        
        # Validate algorithm
        if self.model_type == 'classification':
            if algorithm not in self.classification_algorithms:
                raise ValueError(f"Algorithm '{algorithm}' not available for classification. "
                               f"Available: {list(self.classification_algorithms.keys())}")
            model_class = self.classification_algorithms[algorithm]
        else:
            if algorithm not in self.regression_algorithms:
                raise ValueError(f"Algorithm '{algorithm}' not available for regression. "
                               f"Available: {list(self.regression_algorithms.keys())}")
            model_class = self.regression_algorithms[algorithm]
        
        # Prepare data
        self._prepare_data(test_size, random_state)
        
        # Initialize model
        if hyperparameter_tuning:
            self.model = self._tune_hyperparameters(model_class, algorithm, cv_folds, **kwargs)
        else:
            self.model = model_class(**kwargs)
        
        # Train model
        logger.info(f"Training {algorithm} model...")
        self.model.fit(self.X_train, self.y_train)
        
        # Evaluate model
        results = self._evaluate_model(algorithm, cv_folds)
        
        # Store training history
        self.training_history.append({
            'algorithm': algorithm,
            'results': results,
            'parameters': kwargs,
            'timestamp': pd.Timestamp.now()
        })
        
        logger.info(f"Model training completed. Score: {results['test_score']:.4f}")
        
        return results
    
    def _determine_problem_type(self, target: pd.Series) -> str:
        """
        Determine if this is a classification or regression problem
        """
        if target.dtype == 'object' or target.nunique() <= 10:
            return 'classification'
        else:
            return 'regression'
    
    def _prepare_data(self, test_size: float, random_state: int) -> None:
        """
        Prepare training and testing data
        """
        # Handle categorical target for classification
        if self.model_type == 'classification' and self.target.dtype == 'object':
            self.label_encoder = LabelEncoder()
            target_encoded = self.label_encoder.fit_transform(self.target)
        else:
            target_encoded = self.target
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.features, target_encoded, 
            test_size=test_size, 
            random_state=random_state,
            stratify=target_encoded if self.model_type == 'classification' else None
        )
        
        logger.info(f"Data split: Train {self.X_train.shape[0]}, Test {self.X_test.shape[0]}")
    
    def _tune_hyperparameters(self, model_class, algorithm: str, cv_folds: int, **kwargs) -> Any:
        """
        Perform hyperparameter tuning using GridSearchCV
        """
        param_grids = self._get_param_grids(algorithm)
        
        if algorithm not in param_grids:
            logger.warning(f"No hyperparameter grid defined for {algorithm}. Using default parameters.")
            return model_class(**kwargs)
        
        logger.info(f"Performing hyperparameter tuning for {algorithm}...")
        
        grid_search = GridSearchCV(
            model_class(), 
            param_grids[algorithm],
            cv=cv_folds,
            scoring='neg_mean_squared_error' if self.model_type == 'regression' else 'accuracy',
            n_jobs=-1
        )
        
        grid_search.fit(self.X_train, self.y_train)
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        
        return grid_search.best_estimator_
    
    def _get_param_grids(self, algorithm: str) -> Dict[str, Dict]:
        """
        Get hyperparameter grids for different algorithms
        """
        return {
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10]
            },
            'gradient_boosting': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            'ridge': {
                'alpha': [0.1, 1.0, 10.0, 100.0]
            },
            'lasso': {
                'alpha': [0.1, 1.0, 10.0, 100.0]
            },
            'svc': {
                'C': [0.1, 1, 10],
                'kernel': ['linear', 'rbf'],
                'gamma': ['scale', 'auto']
            },
            'svr': {
                'C': [0.1, 1, 10],
                'kernel': ['linear', 'rbf'],
                'gamma': ['scale', 'auto']
            }
        }
    
    def _evaluate_model(self, algorithm: str, cv_folds: int) -> Dict[str, Any]:
        """
        Evaluate the trained model
        """
        # Predictions
        y_pred_train = self.model.predict(self.X_train)
        y_pred_test = self.model.predict(self.X_test)
        
        results = {
            'algorithm': algorithm,
            'model_type': self.model_type,
            'feature_count': self.X_train.shape[1],
            'train_samples': self.X_train.shape[0],
            'test_samples': self.X_test.shape[0]
        }
        
        if self.model_type == 'regression':
            # Regression metrics
            results.update({
                'train_score': r2_score(self.y_train, y_pred_train),
                'test_score': r2_score(self.y_test, y_pred_test),
                'train_rmse': np.sqrt(mean_squared_error(self.y_train, y_pred_train)),
                'test_rmse': np.sqrt(mean_squared_error(self.y_test, y_pred_test)),
                'train_mae': mean_absolute_error(self.y_train, y_pred_train),
                'test_mae': mean_absolute_error(self.y_test, y_pred_test)
            })
        else:
            # Classification metrics
            results.update({
                'train_score': accuracy_score(self.y_train, y_pred_train),
                'test_score': accuracy_score(self.y_test, y_pred_test),
                'precision': precision_score(self.y_test, y_pred_test, average='weighted'),
                'recall': recall_score(self.y_test, y_pred_test, average='weighted'),
                'f1_score': f1_score(self.y_test, y_pred_test, average='weighted')
            })
        
        # Cross-validation score
        if self.model_type == 'regression':
            cv_scores = cross_val_score(self.model, self.features, self.target, cv=cv_folds, scoring='r2')
        else:
            target_for_cv = self.label_encoder.transform(self.target) if self.label_encoder else self.target
            cv_scores = cross_val_score(self.model, self.features, target_for_cv, cv=cv_folds, scoring='accuracy')
        
        results['cv_score_mean'] = cv_scores.mean()
        results['cv_score_std'] = cv_scores.std()
        
        # Feature importance (if available)
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.features.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            results['feature_importance'] = feature_importance.to_dict('records')
        
        return results
    
    def compare_algorithms(self, 
                          data: Tuple[pd.DataFrame, pd.Series],
                          algorithms: Optional[List[str]] = None,
                          **kwargs) -> pd.DataFrame:
        """
        Compare multiple algorithms and return results
        """
        if algorithms is None:
            if self._determine_problem_type(data[1]) == 'classification':
                algorithms = list(self.classification_algorithms.keys())
            else:
                algorithms = list(self.regression_algorithms.keys())
        
        results = []
        
        for algorithm in algorithms:
            try:
                logger.info(f"Training {algorithm}...")
                result = self.train(data, algorithm=algorithm, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error training {algorithm}: {str(e)}")
        
        # Convert to DataFrame for easy comparison
        comparison_df = pd.DataFrame(results)
        
        # Sort by test score (descending)
        comparison_df = comparison_df.sort_values('test_score', ascending=False)
        
        return comparison_df
    
    def save_model(self, filepath: str) -> None:
        """
        Save the trained model
        """
        if self.model is None:
            raise ValueError("No model trained yet")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save model and metadata
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': list(self.features.columns),
            'label_encoder': self.label_encoder,
            'training_history': self.training_history
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to: {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load a trained model
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.model_type = model_data['model_type']
        self.label_encoder = model_data.get('label_encoder')
        self.training_history = model_data.get('training_history', [])
        
        logger.info(f"Model loaded from: {filepath}")
    
    def get_training_summary(self) -> pd.DataFrame:
        """
        Get summary of all training sessions
        """
        if not self.training_history:
            return pd.DataFrame()
        
        summaries = []
        for entry in self.training_history:
            summary = {
                'algorithm': entry['algorithm'],
                'timestamp': entry['timestamp'],
                'test_score': entry['results']['test_score'],
                'cv_score_mean': entry['results']['cv_score_mean'],
                'feature_count': entry['results']['feature_count']
            }
            summaries.append(summary)
        
        return pd.DataFrame(summaries)
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions with the trained model
        """
        if self.model is None:
            raise ValueError("No model trained yet")
        
        predictions = self.model.predict(X)
        
        # Decode predictions if using label encoder
        if self.label_encoder and self.model_type == 'classification':
            predictions = self.label_encoder.inverse_transform(predictions)
        
        return predictions