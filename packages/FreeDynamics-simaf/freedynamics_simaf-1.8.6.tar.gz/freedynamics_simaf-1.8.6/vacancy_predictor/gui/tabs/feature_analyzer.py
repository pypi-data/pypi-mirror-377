
import pandas as pd
import numpy as np
from typing import Dict

class FeatureAnalyzer:
    """Analiza y categoriza features"""
    
    @staticmethod
    def categorize_feature(feature_name: str) -> str:
        """Categorizar feature basándose en su nombre"""
        feature_lower = feature_name.lower()
        
        if 'coord' in feature_lower:
            return 'Coordinación'
        elif any(word in feature_lower for word in ['energy', 'pe_', 'peatom']):
            return 'Energía'
        elif any(word in feature_lower for word in ['stress', 'vm', 'satom']):
            return 'Stress'
        elif any(word in feature_lower for word in ['hist', 'bin']):
            return 'Histogramas'
        elif 'voro' in feature_lower:
            return 'Voronoi'
        elif any(word in feature_lower for word in ['mean', 'std', 'min', 'max', 'p10', 'p25', 'p75', 'p90']):
            return 'Estadísticas'
        else:
            return 'Otras'
    
    @staticmethod
    def calculate_feature_stats(data: pd.DataFrame, target_column: str) -> Dict[str, Dict]:
        """Calcular estadísticas para todas las features"""
        feature_stats = {}
        target_data = data[target_column] if target_column in data.columns else None
        
        for col in data.columns:
            if col == target_column:
                continue
                
            col_data = data[col]
            category = FeatureAnalyzer.categorize_feature(col)
            
            stats = {
                'category': category,
                'dtype': str(col_data.dtype),
                'sample_values': col_data.dropna().head(3).astype(str).tolist(),
                'missing_count': col_data.isnull().sum(),
                'unique_count': col_data.nunique()
            }
            
            if pd.api.types.is_numeric_dtype(col_data):
                stats.update({
                    'mean': col_data.mean(),
                    'std': col_data.std(),
                    'min': col_data.min(),
                    'max': col_data.max()
                })
                
                if target_data is not None:
                    try:
                        correlation = col_data.corr(target_data)
                        stats['correlation'] = correlation if not pd.isna(correlation) else 0.0
                    except:
                        stats['correlation'] = 0.0
                else:
                    stats['correlation'] = 0.0
            
            feature_stats[col] = stats
        
        return feature_stats
