
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class DataObserver(ABC):
    """Interface para observadores de cambios en datos"""
    @abstractmethod
    def on_data_changed(self, data: pd.DataFrame):
        pass

class FeatureObserver(ABC):
    """Interface para observadores de cambios en features"""
    @abstractmethod
    def on_features_changed(self, features: List[str], target: str):
        pass

class ModelObserver(ABC):
    """Interface para observadores de cambios en modelo"""
    @abstractmethod
    def on_model_changed(self, model: Any, feature_importance: pd.DataFrame = None):
        pass

class DataManager:
    """Gestiona la carga y almacenamiento de datos"""
    
    def __init__(self):
        self.current_data: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None
        self.observers: List[DataObserver] = []
    
    def add_observer(self, observer: DataObserver):
        self.observers.append(observer)
    
    def notify_observers(self):
        if self.current_data is not None:
            for observer in self.observers:
                observer.on_data_changed(self.current_data)
    
    def load_from_file(self, file_path: str) -> bool:
        """Cargar datos desde archivo"""
        try:
            if file_path.endswith('.xlsx'):
                data = pd.read_excel(file_path)
            else:
                data = pd.read_csv(file_path, index_col=0)
            
            self.current_data = data
            self.file_path = file_path
            self.notify_observers()
            return True
            
        except Exception as e:
            print(f"[ERROR] Error cargando archivo: {e}")
            return False
    
    def get_data(self) -> Optional[pd.DataFrame]:
        return self.current_data.copy() if self.current_data is not None else None
    
    def get_data_info(self) -> Dict[str, Any]:
        if self.current_data is None:
            return {}
        
        return {
            'shape': self.current_data.shape,
            'numeric_columns': len(self.current_data.select_dtypes(include=[np.number]).columns),
            'text_columns': len(self.current_data.select_dtypes(include=['object']).columns),
            'memory_usage': self.current_data.memory_usage(deep=True).sum(),
            'file_path': self.file_path
        }
