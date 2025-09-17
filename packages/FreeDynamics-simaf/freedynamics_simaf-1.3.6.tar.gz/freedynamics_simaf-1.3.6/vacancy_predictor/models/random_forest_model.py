"""
Random Forest model implementation for Vacancy Predictor
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Union
import logging
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
import time

from .base_model import BaseModel

logger = logging.getLogger(__name__)

class RandomForestModel(BaseModel):
    """
    Random Forest implementation for both regression and classification
    """
    
    def __init__(self, 
                 task_type: str = 'auto',
                 n_estimators: int = 100,
                 max_depth: Optional[int] = None,
                 min_samples_split: int = 2,
                 min_samples_leaf: int = 1,
                 max_features: str = 'sqrt',
                 random_state: int = 42,
                 n_jobs: int = -1,
                 **kwargs):
        """
        Initialize Random Forest model
        
        Args:
            task_type: 'regression', 'classification', or 'auto'
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of trees
            min_samples_split: Minimum samples required to split a node
            min_samples_leaf: Minimum samples required at a leaf node
            max_features: Number of features to consider for best split
            random_state: Random state for reproducibility
            n_jobs: Number of jobs to run in parallel
        """
        
        self.task_type = task_type
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.random_state = random_state
        self.n_jobs = n_jobs
        
        # Store all parameters
        params = {
            'task_type': task_type,
            'n_estimators': n_estimators,
            'max_depth': max_depth,
            'min_samples_split': min_samples_split,
            'min_samples_leaf': min_samples_leaf,
            'max_features': max_features,
            'random_state': random_state,
            'n_jobs': n_jobs,
            **kwargs
        }
        
        super().__init__(**params)
    
    def _determine_task_type(self, y: pd.Series) -> str:
        """Automatically determine if this is regression or classification"""
        if self.task_type != 'auto':
            return self.task_type
        
        # Check if target is numeric and has many unique values
        if y.dtype in ['int64', 'float64'] and y.nunique() > 10:
            return 'regression'
        else:
            return 'classification'
    
    def build_model(self, task_type: str = None, **kwargs):
        """Build the Random Forest model"""
        if task_type is None:
            task_type = self.task_type
        
        # Common parameters for both regression and classification
        common_params = {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split,
            'min_samples_leaf': self.min_samples_leaf,
            'max_features': self.max_features,
            'random_state': self.random_state,
            'n_jobs': self.n_jobs
        }
        
        # Update with any additional parameters
        common_params.update(kwargs)
        
        if task_type == 'regression':
            self.model = RandomForestRegressor(**common_params)
        elif task_type == 'classification':
            self.model = RandomForestClassifier(**common_params)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
        
        logger.info(f"Built Random Forest {task_type} model with {self.n_estimators} estimators")
    
    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs):
        """Train the Random Forest model"""
        
        # Store feature and target names
        self.feature_names = list(X.columns)
        self.target_name = y.name or 'target'
        
        # Determine task type
        actual_task_type = self._determine_task_type(y)
        
        # Build model if not already built or task type changed
        if self.model is None or actual_task_type != self.task_type:
            self.task_type = actual_task_type
            self.build_model(actual_task_type)
        
        # Validate input
        self.validate_input(X)
        
        # Record training start time
        start_time = time.time()
        
        logger.info(f"Training Random Forest {self.task_type} model...")
        logger.info(f"Training data shape: {X.shape}")
        logger.info(f"Target unique values: {y.nunique()}")
        
        # Train the model
        self.model.fit(X, y)
        
        # Mark as trained
        self.is_trained = True
        
        # Store feature importance
        self.feature_importance_ = self.model.feature_importances_
        
        # Calculate training time
        training_time = time.time() - start_time
        
        # Record training session
        training_info = {
            'timestamp': pd.Timestamp.now(),
            'task_type': self.task_type,
            'n_samples': len(X),
            'n_features': len(X.columns),
            'training_time_seconds': training_time,
            'model_params': self.get_params()
        }
        
        self.training_history.append(training_info)
        
        logger.info(f"Training completed in {training_time:.2f} seconds")
        
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions with the trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Validate input
        self.validate_input(X)
        
        # Ensure columns are in the same order as training
        if self.feature_names:
            X = X[self.feature_names]
        
        predictions = self.model.predict(X)
        
        logger.info(f"Made predictions for {len(X)} samples")
        
        return predictions
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities (classification only)"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        if self.task_type != 'classification':
            raise ValueError("predict_proba is only available for classification tasks")
        
        # Validate input
        self.validate_input(X)
        
        # Ensure columns are in the same order as training
        if self.feature_names:
            X = X[self.feature_names]
        
        probabilities = self.model.predict_proba(X)
        
        logger.info(f"Predicted probabilities for {len(X)} samples")
        
        return probabilities
    
    def get_model_type(self) -> str:
        """Return model type"""
        return self.task_type
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series, cv_folds: int = 5) -> Dict[str, Any]:
        """Evaluate model performance"""
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        # Make predictions
        y_pred = self.predict(X)
        
        results = {
            'task_type': self.task_type,
            'n_samples': len(X),
            'n_features': len(X.columns)
        }
        
        if self.task_type == 'regression':
            # Regression metrics
            results.update({
                'r2_score': r2_score(y, y_pred),
                'rmse': np.sqrt(mean_squared_error(y, y_pred)),
                'mae': np.mean(np.abs(y - y_pred))
            })
            
            # Cross-validation score
            cv_scores = cross_val_score(self.model, X, y, cv=cv_folds, scoring='r2')
            
        else:
            # Classification metrics
            accuracy = accuracy_score(y, y_pred)
            results.update({
                'accuracy': accuracy,
                'classification_report': classification_report(y, y_pred, output_dict=True)
            })
            
            # Cross-validation score
            cv_scores = cross_val_score(self.model, X, y, cv=cv_folds, scoring='accuracy')
        
        # Add cross-validation results
        results.update({
            'cv_score_mean': cv_scores.mean(),
            'cv_score_std': cv_scores.std(),
            'cv_scores': cv_scores.tolist()
        })
        
        return results
    
    def get_feature_importance_detailed(self, top_n: int = None) -> pd.DataFrame:
        """Get detailed feature importance analysis"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        importance_df = self.get_feature_importance()
        
        if importance_df is None:
            return None
        
        # Add additional statistics
        importance_df['importance_percentage'] = (
            importance_df['importance'] / importance_df['importance'].sum() * 100
        )
        
        importance_df['cumulative_importance'] = (
            importance_df['importance_percentage'].cumsum()
        )
        
        if top_n:
            importance_df = importance_df.head(top_n)
        
        return importance_df
    
    def get_oob_score(self) -> Optional[float]:
        """Get out-of-bag score if available"""
        if not self.is_trained:
            return None
        
        # Enable OOB scoring and retrain if needed
        if not hasattr(self.model, 'oob_score_'):
            logger.warning("OOB score not available. Retrain with oob_score=True")
            return None
        
        return self.model.oob_score_
    
    def get_tree_info(self) -> Dict[str, Any]:
        """Get information about individual trees"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        trees = self.model.estimators_
        
        tree_info = {
            'n_trees': len(trees),
            'tree_depths': [tree.get_depth() for tree in trees],
            'tree_n_leaves': [tree.get_n_leaves() for tree in trees],
            'tree_n_nodes': [tree.tree_.node_count for tree in trees]
        }
        
        # Add summary statistics
        tree_info['avg_depth'] = np.mean(tree_info['tree_depths'])
        tree_info['avg_leaves'] = np.mean(tree_info['tree_n_leaves'])
        tree_info['avg_nodes'] = np.mean(tree_info['tree_n_nodes'])
        
        return tree_info
    
    def optimize_hyperparameters(self, X: pd.DataFrame, y: pd.Series, 
                                param_grid: Dict = None, cv_folds: int = 5) -> Dict[str, Any]:
        """Optimize hyperparameters using GridSearchCV"""
        from sklearn.model_selection import GridSearchCV
        
        if param_grid is None:
            # Default parameter grid
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
        
        # Determine task type
        task_type = self._determine_task_type(y)
        
        # Build base model for grid search
        self.build_model(task_type)
        
        # Set up scoring
        scoring = 'r2' if task_type == 'regression' else 'accuracy'
        
        logger.info(f"Starting hyperparameter optimization with {cv_folds}-fold CV...")
        
        # Perform grid search
        grid_search = GridSearchCV(
            self.model,
            param_grid,
            cv=cv_folds,
            scoring=scoring,
            n_jobs=self.n_jobs,
            verbose=1
        )
        
        grid_search.fit(X, y)
        
        # Update model with best parameters
        self.model = grid_search.best_estimator_
        self.is_trained = True
        self.feature_names = list(X.columns)
        self.target_name = y.name or 'target'
        self.feature_importance_ = self.model.feature_importances_
        
        results = {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': grid_search.cv_results_
        }
        
        logger.info(f"Optimization completed. Best score: {grid_search.best_score_:.4f}")
        logger.info(f"Best parameters: {grid_search.best_params_}")
        
        return results