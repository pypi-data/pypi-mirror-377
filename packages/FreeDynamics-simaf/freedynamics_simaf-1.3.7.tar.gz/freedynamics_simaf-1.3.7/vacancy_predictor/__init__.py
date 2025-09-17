"""
Vacancy Predictor - A comprehensive ML tool for vacancy prediction with GUI
"""

from .core.data_processor import DataProcessor
from .core.model_trainer import ModelTrainer
from .core.predictor import Predictor
from .core.visualizer import Visualizer

__version__ = "1.0.0"
__author__ = "Tu Nombre"
__email__ = "tu.email@example.com"

# Main API exports
__all__ = [
    'DataProcessor',
    'ModelTrainer', 
    'Predictor',
    'Visualizer',
    'VacancyPredictor'
]

class VacancyPredictor:
    """
    Main API class that combines all functionality
    """
    def __init__(self):
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        self.predictor = Predictor()
        self.visualizer = Visualizer()
        
    def load_data(self, file_path):
        """Load data from various formats"""
        return self.data_processor.load_data(file_path)
        
    def select_features(self, features):
        """Select features for training"""
        return self.data_processor.select_features(features)
        
    def set_target(self, target_column):
        """Set target column for prediction"""
        return self.data_processor.set_target(target_column)
        
    def train(self, algorithm='random_forest', **kwargs):
        """Train a model with specified algorithm"""
        return self.model_trainer.train(
            self.data_processor.get_training_data(),
            algorithm=algorithm,
            **kwargs
        )
        
    def predict(self, data):
        """Make predictions on new data"""
        return self.predictor.predict(data)
        
    def save_model(self, filepath):
        """Save trained model"""
        return self.model_trainer.save_model(filepath)
        
    def load_model(self, filepath):
        """Load a trained model"""
        return self.model_trainer.load_model(filepath)