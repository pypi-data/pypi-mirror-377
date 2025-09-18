"""
Vacancy Predictor GUI Package
===========================

Módulo GUI para la aplicación de predicción de vacantes con machine learning.
Contiene todos los componentes de interfaz gráfica modularizados.

Estructura:
- Core: Componentes base (managers, observers)
- Widgets: Componentes de UI reutilizables  
- Tabs: Pestañas principales de la aplicación
- App: Aplicación principal

Versión: 3.0 - Arquitectura Modularizada
"""

# Core components (base classes and managers)
from .data_manager import DataManager, DataObserver, FeatureObserver, ModelObserver
from .feature_analyzer import FeatureAnalyzer  
from .model_trainer import ModelTrainer
from .feature_selector import FeatureSelector
from .configuration_manager import ConfigurationManager

# Widgets (UI components)
from .data_info_widget import DataInfoWidget
from .model_results_widget import ModelResultsWidget
from .model_visualization_widget import ModelVisualizationWidget
from .feature_selection_widget import FeatureSelectionWidget

# Tabs (main application tabs)
from .advanced_ml_tab import AdvancedMLTabWithFeatureSelection
from .batch_processor_tab import BatchProcessingTab
from .feature_selection_tab import FeatureSelectionTab

# Advanced ML application (modular version)
from .advanced_ml_application import AdvancedMLApplication

# Version info
__version__ = "3.0.0"
__author__ = "Vacancy Predictor Team"
__description__ = "Machine Learning GUI for Vacancy Prediction"

# Public API - componentes principales para uso externo
__all__ = [
    # Core managers
    'DataManager',
    'ModelTrainer', 
    'FeatureSelector',
    'FeatureAnalyzer',
    'ConfigurationManager',
    
    # Observer interfaces
    'DataObserver',
    'FeatureObserver', 
    'ModelObserver',
    
    # Main widgets
    'DataInfoWidget',
    'ModelResultsWidget',
    'ModelVisualizationWidget',
    'FeatureSelectionWidget',
    
    # Application tabs
    'AdvancedMLTabWithFeatureSelection',
    'BatchProcessingTab',
    'FeatureSelectionTab',
    
    # Applications
    'VacancyPredictorApp',
    'AdvancedMLApplication',
    
    # Main function
    'main',
    
    # Version
    '__version__'
]

# Configuración de logging para el paquete
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

def get_version():
    """Obtener versión del paquete"""
    return __version__

def get_components():
    """Obtener lista de componentes disponibles"""
    return {
        'core': ['DataManager', 'ModelTrainer', 'FeatureSelector', 'FeatureAnalyzer'],
        'widgets': ['DataInfoWidget', 'ModelResultsWidget', 'ModelVisualizationWidget'],
        'tabs': ['AdvancedMLTabWithFeatureSelection', 'BatchProcessingTab'],
        'apps': ['VacancyPredictorApp', 'AdvancedMLApplication']
    }

# Verificación de dependencias críticas
def check_dependencies():
    """Verificar que las dependencias críticas estén disponibles"""
    missing = []
    
    try:
        import tkinter
    except ImportError:
        missing.append('tkinter')
    
    try:
        import pandas
    except ImportError:
        missing.append('pandas')
        
    try:
        import numpy
    except ImportError:
        missing.append('numpy')
        
    try:
        import matplotlib
    except ImportError:
        missing.append('matplotlib')
        
    try:
        import sklearn
    except ImportError:
        missing.append('scikit-learn')
    
    if missing:
        raise ImportError(f"Missing required dependencies: {', '.join(missing)}")
    
    return True

# Auto-verificación al importar (opcional)
try:
    check_dependencies()
except ImportError as e:
    logging.getLogger(__name__).warning(f"Dependency check failed: {e}")