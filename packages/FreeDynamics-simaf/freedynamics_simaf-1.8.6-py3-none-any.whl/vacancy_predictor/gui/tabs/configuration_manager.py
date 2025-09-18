import json
import pandas as pd
from typing import Dict, Optional, Any

class ConfigurationManager:
    """Gestiona la carga y guardado de configuraciones"""
    
    @staticmethod
    def save_feature_config(config: Dict, file_path: str) -> bool:
        try:
            config_data = {
                **config,
                'metadata': {
                    'timestamp': pd.Timestamp.now().isoformat(),
                    'version': '1.0',
                    'type': 'feature_selection'
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"[ERROR] Error guardando configuración: {e}")
            return False
    
    @staticmethod
    def load_feature_config(file_path: str) -> Optional[Dict]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'selected_features' not in config:
                raise ValueError("Configuración inválida")
            
            return config
        except Exception as e:
            print(f"[ERROR] Error cargando configuración: {e}")
            return None
    
    @staticmethod
    def save_model(model_trainer: Any, feature_selector: Any, file_path: str) -> bool:
        try:
            import joblib
            
            model_data = {
                'model': model_trainer.model,
                'feature_importance': getattr(model_trainer, 'feature_importance', None),
                'training_results': getattr(model_trainer, 'training_results', {}),
                'feature_config': feature_selector.get_config(),
                'metadata': {
                    'timestamp': pd.Timestamp.now().isoformat(),
                    'version': '1.0'
                }
            }
            
            joblib.dump(model_data, file_path)
            return True
        except Exception as e:
            print(f"[ERROR] Error guardando modelo: {e}")
            return False
