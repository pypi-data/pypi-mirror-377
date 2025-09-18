"""
GUI tabs module for Vacancy Predictor
"""

from .data_tabs import DataTab
from .training_tab import TrainingTab
from .prediction_tab import PredictionTab
from .visualization_tab import VisualizationTab
from .lammps_tab import AtomVisualizer3D,LAMMPSTab
from .feature_selector_gui import FeatureSelectorGUI
from .batch_processor_tab import BatchProcessingTab
from vacancy_predictor.gui.tabs.feature_tabs import FeatureSelectionTab
__all__ = [
    'DataTab',
    'TrainingTab', 
    'PredictionTab',
    'VisualizationTab'
]