"""
Prediction module for making predictions with trained models
"""

import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any, Optional
import logging
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)

class Predictor:
    """
    Handles predictions with trained models
    """
    
    def __init__(self):
        self.model = None
        self.model_metadata = None
        self.feature_names = None
        self.label_encoder = None
        
    def load_model(self, model_path: Union[str, Path]) -> None:
        """
        Load a trained model from file
        
        Args:
            model_path: Path to the saved model
        """
        model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            model_data = joblib.load(model_path)
            
            if isinstance(model_data, dict):
                self.model = model_data.get('model')
                self.model_metadata = model_data.get('model_type')
                self.feature_names = model_data.get('feature_names', [])
                self.label_encoder = model_data.get('label_encoder')
            else:
                # Assume it's just the model
                self.model = model_data
                self.feature_names = []
            
            logger.info(f"Model loaded from: {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def predict(self, X: Union[pd.DataFrame, np.ndarray, List]) -> np.ndarray:
        """
        Make predictions on input data
        
        Args:
            X: Input features for prediction
            
        Returns:
            Array of predictions
        """
        if self.model is None:
            raise ValueError("No model loaded. Use load_model() first.")
        
        # Convert input to DataFrame if needed
        if isinstance(X, list):
            if self.feature_names:
                X = pd.DataFrame([X], columns=self.feature_names)
            else:
                X = pd.DataFrame([X])
        elif isinstance(X, np.ndarray):
            if self.feature_names and X.shape[1] == len(self.feature_names):
                X = pd.DataFrame(X, columns=self.feature_names)
            else:
                X = pd.DataFrame(X)
        
        # Validate features
        if self.feature_names and list(X.columns) != self.feature_names:
            logger.warning("Feature names don't match trained model")
        
        try:
            predictions = self.model.predict(X)
            
            # Decode predictions if using label encoder
            if self.label_encoder and hasattr(self.label_encoder, 'inverse_transform'):
                predictions = self.label_encoder.inverse_transform(predictions)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Predict class probabilities (for classification models)
        
        Args:
            X: Input features
            
        Returns:
            Array of class probabilities
        """
        if self.model is None:
            raise ValueError("No model loaded. Use load_model() first.")
        
        if not hasattr(self.model, 'predict_proba'):
            raise ValueError("Model does not support probability predictions")
        
        if isinstance(X, np.ndarray):
            if self.feature_names:
                X = pd.DataFrame(X, columns=self.feature_names)
            else:
                X = pd.DataFrame(X)
        
        try:
            probabilities = self.model.predict_proba(X)
            return probabilities
            
        except Exception as e:
            logger.error(f"Probability prediction failed: {str(e)}")
            raise
    
    def get_feature_names(self) -> List[str]:
        """
        Get the feature names expected by the model
        
        Returns:
            List of feature names
        """
        return self.feature_names or []
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        if self.model is None:
            return {"status": "No model loaded"}
        
        info = {
            "model_type": str(type(self.model).__name__),
            "feature_count": len(self.feature_names) if self.feature_names else "Unknown",
            "feature_names": self.feature_names,
            "has_probability_prediction": hasattr(self.model, 'predict_proba'),
            "metadata": self.model_metadata
        }
        
        return info