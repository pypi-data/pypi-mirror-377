import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any

# Importar solo las interfaces, no las clases concretas
from .data_manager import FeatureObserver

class FeatureSelector:
    """Gestiona la selección de features"""
    
    def __init__(self):
        self.selected_features: List[str] = []
        self.target_column: str = 'vacancies'
        self.feature_stats: Dict[str, Dict] = {}
        self.observers: List[FeatureObserver] = []
    
    def add_observer(self, observer: FeatureObserver):
        self.observers.append(observer)
    
    def notify_observers(self):
        for observer in self.observers:
            observer.on_features_changed(self.selected_features, self.target_column)
    
    def update_data(self, data: pd.DataFrame):
        """Actualizar con nuevos datos"""
        # Calcular stats directamente aquí en lugar de usar FeatureAnalyzer
        self.feature_stats = self._calculate_stats(data, self.target_column)
        
        # Auto-seleccionar features numéricas por defecto
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        self.selected_features = [col for col in numeric_cols if col != self.target_column]
    
    def _calculate_stats(self, data: pd.DataFrame, target_column: str) -> Dict[str, Dict]:
        """Calcular estadísticas básicas para features"""
        feature_stats = {}
        target_data = data[target_column] if target_column in data.columns else None
        
        for col in data.columns:
            if col == target_column:
                continue
                
            col_data = data[col]
            category = self._categorize_feature(col)
            
            stats = {
                'category': category,
                'dtype': str(col_data.dtype),
                'sample_values': col_data.dropna().head(3).astype(str).tolist()
            }
            
            if pd.api.types.is_numeric_dtype(col_data) and target_data is not None:
                try:
                    correlation = col_data.corr(target_data)
                    stats['correlation'] = correlation if not pd.isna(correlation) else 0.0
                except:
                    stats['correlation'] = 0.0
            else:
                stats['correlation'] = 0.0
            
            feature_stats[col] = stats
        
        return feature_stats
    
    def _categorize_feature(self, feature_name: str) -> str:
        """Categorizar feature (simplificado)"""
        feature_lower = feature_name.lower()
        
        if 'coord' in feature_lower:
            return 'Coordinación'
        elif 'energy' in feature_lower:
            return 'Energía'
        elif 'stress' in feature_lower:
            return 'Stress'
        elif 'hist' in feature_lower:
            return 'Histogramas'
        else:
            return 'Otras'
    
    def set_target(self, target: str):
        if target != self.target_column:
            if self.target_column in self.selected_features:
                self.selected_features.remove(self.target_column)
            if target in self.selected_features:
                self.selected_features.remove(target)
            
            self.target_column = target
            self.notify_observers()
    
    def toggle_feature(self, feature: str):
        if feature == self.target_column:
            return
        
        if feature in self.selected_features:
            self.selected_features.remove(feature)
        else:
            self.selected_features.append(feature)
        
        self.notify_observers()
    
    def get_config(self) -> Dict:
        return {
            'selected_features': self.selected_features.copy(),
            'target_column': self.target_column,
            'feature_stats': self.feature_stats.copy()
        }
