"""
GUI tabs module for Vacancy Predictor
"""

from .data_tabs import DataTab
from .training_tab import TrainingTab
from .prediction_tab import PredictionTab
from .visualization_tab import VisualizationTab

__all__ = [
    'DataTab',
    'TrainingTab', 
    'PredictionTab',
    'VisualizationTab'
]