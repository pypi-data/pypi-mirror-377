"""
Models module for Vacancy Predictor
"""

from .base_model import BaseModel
from .random_forest_model import RandomForestModel

__all__ = [
    'BaseModel',
    'RandomForestModel'
]

# Model registry for easy access
MODEL_REGISTRY = {
    'random_forest': RandomForestModel,
    'rf': RandomForestModel,  # Alias
}

def get_model(model_name: str, **kwargs):
    """
    Factory function to get model by name
    
    Args:
        model_name: Name of the model ('random_forest', 'rf')
        **kwargs: Parameters to pass to the model constructor
        
    Returns:
        Model instance
    """
    if model_name not in MODEL_REGISTRY:
        available_models = list(MODEL_REGISTRY.keys())
        raise ValueError(f"Unknown model: {model_name}. Available models: {available_models}")
    
    model_class = MODEL_REGISTRY[model_name]
    return model_class(**kwargs)