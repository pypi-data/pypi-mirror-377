"""
Base model class for all ML models in Vacancy Predictor
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, Union
import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseModel(ABC):
    """
    Abstract base class for all ML models
    """
    
    def __init__(self, **kwargs):
        self.model = None
        self.is_trained = False
        self.feature_names = None
        self.target_name = None
        self.model_params = kwargs
        self.training_history = []
        self.feature_importance_ = None
        
    @abstractmethod
    def build_model(self, **kwargs):
        """Build the underlying ML model"""
        pass
    
    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs):
        """Train the model"""
        pass
    
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        pass
    
    @abstractmethod
    def get_model_type(self) -> str:
        """Return model type (regression/classification)"""
        pass
    
    def get_params(self) -> Dict[str, Any]:
        """Get model parameters"""
        if self.model is None:
            return self.model_params
        return self.model.get_params()
    
    def set_params(self, **params):
        """Set model parameters"""
        self.model_params.update(params)
        if self.model is not None:
            self.model.set_params(**params)
    
    def save_model(self, filepath: Union[str, Path]) -> None:
        """Save the trained model"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'model_class': self.__class__.__name__,
            'model_params': self.model_params,
            'feature_names': self.feature_names,
            'target_name': self.target_name,
            'training_history': self.training_history,
            'feature_importance': self.feature_importance_,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to: {filepath}")
    
    @classmethod
    def load_model(cls, filepath: Union[str, Path]):
        """Load a trained model"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = joblib.load(filepath)
        
        # Create instance
        instance = cls(**model_data['model_params'])
        instance.model = model_data['model']
        instance.feature_names = model_data['feature_names']
        instance.target_name = model_data['target_name']
        instance.training_history = model_data.get('training_history', [])
        instance.feature_importance_ = model_data.get('feature_importance')
        instance.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from: {filepath}")
        return instance
    
    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """Get feature importance if available"""
        if self.feature_importance_ is None:
            return None
        
        if self.feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(self.feature_importance_))]
        else:
            feature_names = self.feature_names
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.feature_importance_
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def validate_input(self, X: pd.DataFrame) -> None:
        """Validate input data"""
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        
        if self.feature_names is not None:
            missing_features = set(self.feature_names) - set(X.columns)
            if missing_features:
                raise ValueError(f"Missing features: {missing_features}")
            
            # Reorder columns to match training
            X = X[self.feature_names]
        
        # Check for missing values
        if X.isnull().any().any():
            logger.warning("Input data contains missing values")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information"""
        return {
            'model_class': self.__class__.__name__,
            'model_type': self.get_model_type(),
            'is_trained': self.is_trained,
            'parameters': self.get_params(),
            'feature_count': len(self.feature_names) if self.feature_names else None,
            'feature_names': self.feature_names,
            'target_name': self.target_name,
            'has_feature_importance': self.feature_importance_ is not None,
            'training_sessions': len(self.training_history)
        }
    
    def __repr__(self) -> str:
        status = "trained" if self.is_trained else "untrained"
        return f"{self.__class__.__name__}({status})"