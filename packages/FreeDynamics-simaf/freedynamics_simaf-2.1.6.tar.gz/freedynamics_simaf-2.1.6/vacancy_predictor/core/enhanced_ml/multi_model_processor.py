"""
Multi-Model Processor Mejorado para Vacancy Predictor
Archivo: vacancy_predictor/core/enhanced_ml/multi_model_processor.py

Incluye métodos adicionales para mejor comparación y análisis
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)

# Verificar disponibilidad de librerías opcionales
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logger.warning("XGBoost no disponible")

try:
    import tensorflow as tf
    # Intentar importación moderna primero
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, Dropout
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.callbacks import EarlyStopping
    except ImportError:
        # Fallback para versiones más antiguas
        from keras.models import Sequential
        from keras.layers import Dense, Dropout
        from keras.optimizers import Adam
        from keras.callbacks import EarlyStopping
    NEURAL_NETWORKS_AVAILABLE = True
    logger.info("TensorFlow/Keras disponible")
except ImportError:
    NEURAL_NETWORKS_AVAILABLE = False
    logger.warning("TensorFlow/Keras no disponible")

class MultiModelProcessor:
    """Procesador multi-modelo mejorado con análisis comparativo"""
    
    def __init__(self):
        self.available_models = {}
        self._initialize_available_models()
        
        self.trained_models = {}
        self.model_results = {}
        self.scalers = {}
        self.feature_columns = []
        self.target_column = None
        
        # Configuraciones por defecto
        self.default_configs = {
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            },
            'xgboost': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 6, 10],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0]
            },
            'neural_network': {
                'hidden_layers': [(64, 32), (128, 64, 32), (256, 128, 64)],
                'dropout_rate': [0.2, 0.3, 0.5],
                'learning_rate': [0.001, 0.01, 0.1],
                'batch_size': [32, 64, 128]
            }
        }
    
    def _initialize_available_models(self):
        """Inicializar modelos disponibles basado en dependencias"""
        # Random Forest siempre disponible (viene con scikit-learn)
        self.available_models['random_forest'] = 'Random Forest'
        
        # XGBoost
        if XGBOOST_AVAILABLE:
            self.available_models['xgboost'] = 'XGBoost'
        else:
            logger.info("XGBoost no disponible - instalar con: pip install xgboost")
        
        # Neural Networks
        if NEURAL_NETWORKS_AVAILABLE:
            self.available_models['neural_network'] = 'Red Neuronal'
        else:
            logger.info("TensorFlow/Keras no disponible - instalar con: pip install tensorflow")
    
    def get_available_models_info(self):
        """Obtener información sobre modelos disponibles"""
        info = {
            'available': list(self.available_models.keys()),
            'total_available': len(self.available_models),
            'dependencies': {
                'random_forest': 'scikit-learn (✓ Siempre disponible)',
                'xgboost': f'xgboost ({"✓ Disponible" if XGBOOST_AVAILABLE else "✗ No instalado"})',
                'neural_network': f'tensorflow/keras ({"✓ Disponible" if NEURAL_NETWORKS_AVAILABLE else "✗ No instalado"})'
            }
        }
        return info
    
    def prepare_data(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, 
                    scale_features: bool = False, random_state: int = 42) -> Tuple:
        """Preparar datos para entrenamiento con opción de escalado"""
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Escalar si es necesario (para redes neuronales)
        if scale_features:
            scaler = StandardScaler()
            X_train_scaled = pd.DataFrame(
                scaler.fit_transform(X_train),
                columns=X_train.columns,
                index=X_train.index
            )
            X_test_scaled = pd.DataFrame(
                scaler.transform(X_test),
                columns=X_test.columns,
                index=X_test.index
            )
            
            self.scalers['features'] = scaler
            return X_train_scaled, X_test_scaled, y_train, y_test
        
        return X_train, X_test, y_train, y_test
    
    def train_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series, 
                           use_grid_search: bool = True) -> RandomForestRegressor:
        """Entrenar Random Forest con Grid Search opcional"""
        
        if use_grid_search:
            rf = RandomForestRegressor(random_state=42)
            grid_search = GridSearchCV(
                rf, 
                self.default_configs['random_forest'],
                cv=3,
                scoring='r2',
                n_jobs=-1,
                verbose=1
            )
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            
            logger.info(f"Random Forest mejores parámetros: {grid_search.best_params_}")
        else:
            best_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                random_state=42
            )
            best_model.fit(X_train, y_train)
        
        self.trained_models['random_forest'] = best_model
        return best_model
    
    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                     use_grid_search: bool = True):
        """Entrenar XGBoost con Grid Search opcional"""
        
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost no está instalado")
        
        if use_grid_search:
            xgb_model = xgb.XGBRegressor(random_state=42, eval_metric='rmse')
            grid_search = GridSearchCV(
                xgb_model,
                self.default_configs['xgboost'],
                cv=3,
                scoring='r2',
                n_jobs=-1,
                verbose=1
            )
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            
            logger.info(f"XGBoost mejores parámetros: {grid_search.best_params_}")
        else:
            best_model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                eval_metric='rmse'
            )
            best_model.fit(X_train, y_train)
        
        self.trained_models['xgboost'] = best_model
        return best_model
    
    def train_neural_network(self, X_train: pd.DataFrame, y_train: pd.Series,
                           X_val: pd.DataFrame, y_val: pd.Series,
                           epochs: int = 100):
        """Entrenar Red Neuronal con Keras"""
        
        if not NEURAL_NETWORKS_AVAILABLE:
            raise ImportError("TensorFlow no está instalado")
        
        # Crear modelo
        model = Sequential([
            Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(1)
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        # Entrenar
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=64,
            callbacks=[early_stopping],
            verbose=0
        )
        
        self.trained_models['neural_network'] = model
        return model
    
    def evaluate_model(self, model_name: str, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """Evaluar modelo entrenado"""
        
        if model_name not in self.trained_models:
            raise ValueError(f"Modelo {model_name} no ha sido entrenado")
        
        model = self.trained_models[model_name]
        
        # Hacer predicciones
        if model_name == 'neural_network':
            # Para redes neuronales, las predicciones pueden ser 2D
            y_pred = model.predict(X_test)
            if len(y_pred.shape) > 1:
                y_pred = y_pred.flatten()
        else:
            y_pred = model.predict(X_test)
        
        # Calcular métricas
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # Calcular MAPE evitando división por cero
        mape = np.mean(np.abs((y_test - y_pred) / np.where(y_test != 0, y_test, 1e-8))) * 100
        
        # Métricas adicionales
        results = {
            'model_name': model_name,
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'mape': mape,
            'predictions': y_pred,
            'actual': y_test.values,
            'residuals': y_test.values - y_pred,
            'n_samples': len(y_test)
        }
        
        # Métricas adicionales de calidad
        results.update(self._calculate_additional_metrics(y_test.values, y_pred))
        
        self.model_results[model_name] = results
        
        logger.info(f"{model_name} evaluación - MAE: {mae:.4f}, R²: {r2:.4f}")
        
        return results
    
    def _calculate_additional_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calcular métricas adicionales de evaluación"""
        
        residuals = y_true - y_pred
        
        return {
            # Métricas de residuos
            'mean_residual': np.mean(residuals),
            'std_residual': np.std(residuals),
            'median_residual': np.median(residuals),
            'max_residual': np.max(np.abs(residuals)),
            
            # Percentiles de errores absolutos
            'mae_p25': np.percentile(np.abs(residuals), 25),
            'mae_p50': np.percentile(np.abs(residuals), 50),
            'mae_p75': np.percentile(np.abs(residuals), 75),
            'mae_p90': np.percentile(np.abs(residuals), 90),
            'mae_p95': np.percentile(np.abs(residuals), 95),
            
            # Métricas de sesgo
            'mean_percentage_error': np.mean((y_true - y_pred) / np.where(y_true != 0, y_true, 1e-8)) * 100,
            
            # Correlación entre predicciones y valores reales
            'prediction_correlation': np.corrcoef(y_true, y_pred)[0, 1]
        }
    
    def train_all_models(self, X: pd.DataFrame, y: pd.Series,
                        test_size: float = 0.2,
                        models_to_train: List[str] = None,
                        use_grid_search: bool = True,
                        random_state: int = 42) -> Dict:
        """Entrenar múltiples modelos y comparar rendimiento"""
        
        if models_to_train is None:
            models_to_train = [name for name in self.available_models.keys() 
                             if 'No disponible' not in self.available_models[name]]
        
        self.feature_columns = X.columns.tolist()
        self.target_column = y.name
        
        # Preparar datos
        X_train, X_test, y_train, y_test = self.prepare_data(
            X, y, test_size, scale_features='neural_network' in models_to_train,
            random_state=random_state
        )
        
        # Para redes neuronales, crear conjunto de validación
        if 'neural_network' in models_to_train:
            X_train_nn, X_val, y_train_nn, y_val = train_test_split(
                X_train, y_train, test_size=0.2, random_state=random_state
            )
        
        results_summary = {}
        
        # Entrenar cada modelo
        for model_name in models_to_train:
            try:
                logger.info(f"Entrenando {model_name}...")
                
                if model_name == 'random_forest':
                    self.train_random_forest(X_train, y_train, use_grid_search=use_grid_search)
                elif model_name == 'xgboost' and XGBOOST_AVAILABLE:
                    self.train_xgboost(X_train, y_train, use_grid_search=use_grid_search)
                elif model_name == 'neural_network' and NEURAL_NETWORKS_AVAILABLE:
                    self.train_neural_network(X_train_nn, y_train_nn, X_val, y_val)
                else:
                    logger.warning(f"Modelo {model_name} no disponible, saltando...")
                    continue
                
                # Evaluar modelo
                results = self.evaluate_model(model_name, X_test, y_test)
                results_summary[model_name] = results
                
            except Exception as e:
                logger.error(f"Error entrenando {model_name}: {str(e)}")
                results_summary[model_name] = {'error': str(e)}
        
        return results_summary
    
    def get_best_model(self, metric: str = 'r2') -> Tuple[str, Dict]:
        """Obtener el mejor modelo basado en la métrica especificada"""
        if not self.model_results:
            raise ValueError("No hay modelos entrenados y evaluados")
        
        valid_metrics = ['mae', 'mse', 'rmse', 'r2', 'mape']
        if metric not in valid_metrics:
            raise ValueError(f"Métrica debe ser una de: {valid_metrics}")
        
        best_model = None
        best_score = float('-inf') if metric == 'r2' else float('inf')
        
        for model_name, results in self.model_results.items():
            if 'error' in results:
                continue
                
            score = results[metric]
            
            if metric == 'r2':
                if score > best_score:
                    best_score = score
                    best_model = model_name
            else:  # Menor es mejor para mae, mse, rmse, mape
                if score < best_score:
                    best_score = score
                    best_model = model_name
        
        if best_model is None:
            raise ValueError("No se encontraron resultados válidos de modelos")
        
        return best_model, self.model_results[best_model]
    
    def compare_models(self) -> pd.DataFrame:
        """Crear tabla de comparación de todos los modelos entrenados"""
        if not self.model_results:
            raise ValueError("No hay modelos entrenados para comparar")
        
        comparison_data = []
        for model_name, results in self.model_results.items():
            if 'error' not in results:
                comparison_data.append({
                    'Modelo': self.available_models.get(model_name, model_name),
                    'Modelo_ID': model_name,
                    'R²': results['r2'],
                    'MAE': results['mae'],
                    'RMSE': results['rmse'],
                    'MSE': results['mse'],
                    'MAPE': results['mape'],
                    'Muestras': results['n_samples'],
                    'Correlación': results.get('prediction_correlation', 0),
                    'Error_Max': results.get('max_residual', 0),
                    'MAE_P90': results.get('mae_p90', 0)
                })
        
        df = pd.DataFrame(comparison_data)
        return df.sort_values('R²', ascending=False)
    
    def get_model_rankings(self) -> Dict[str, pd.DataFrame]:
        """Obtener rankings de modelos por diferentes métricas"""
        if not self.model_results:
            raise ValueError("No hay modelos entrenados para rankear")
        
        comparison_df = self.compare_models()
        
        rankings = {}
        
        # Ranking por R² (mayor es mejor)
        rankings['r2'] = comparison_df.sort_values('R²', ascending=False).reset_index(drop=True)
        rankings['r2']['Ranking_R²'] = range(1, len(rankings['r2']) + 1)
        
        # Ranking por MAE (menor es mejor)
        rankings['mae'] = comparison_df.sort_values('MAE', ascending=True).reset_index(drop=True)
        rankings['mae']['Ranking_MAE'] = range(1, len(rankings['mae']) + 1)
        
        # Ranking por RMSE (menor es mejor)
        rankings['rmse'] = comparison_df.sort_values('RMSE', ascending=True).reset_index(drop=True)
        rankings['rmse']['Ranking_RMSE'] = range(1, len(rankings['rmse']) + 1)
        
        # Ranking por MAPE (menor es mejor)
        rankings['mape'] = comparison_df.sort_values('MAPE', ascending=True).reset_index(drop=True)
        rankings['mape']['Ranking_MAPE'] = range(1, len(rankings['mape']) + 1)
        
        return rankings
    
    def get_feature_importance(self, model_name: str = None) -> pd.DataFrame:
        """Obtener importancia de features para modelos que la soporten"""
        if model_name is None:
            # Usar el mejor modelo
            model_name, _ = self.get_best_model('r2')
        
        if model_name not in self.trained_models:
            raise ValueError(f"Modelo {model_name} no ha sido entrenado")
        
        model = self.trained_models[model_name]
        
        if model_name == 'random_forest':
            importances = model.feature_importances_
        elif model_name == 'xgboost' and hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            # Para modelos sin feature importance (como redes neuronales)
            logger.warning(f"Modelo {model_name} no soporta feature importance")
            return pd.DataFrame()
        
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        # Añadir importancia relativa
        feature_importance_df['importance_relative'] = (
            feature_importance_df['importance'] / feature_importance_df['importance'].sum() * 100
        )
        
        return feature_importance_df
    
    def generate_detailed_report(self, output_path: str = None) -> str:
        """Generar reporte detallado de todos los modelos"""
        if not self.model_results:
            return "No hay modelos entrenados para generar reporte"
        
        from datetime import datetime
        
        report = f"""
REPORTE DETALLADO DE MODELOS - VACANCY PREDICTOR
===============================================
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONFIGURACIÓN:
  Target: {self.target_column}
  Features: {len(self.feature_columns)}
  Modelos entrenados: {len([r for r in self.model_results.values() if 'error' not in r])}

"""
        
        # Resumen de modelos
        try:
            comparison_df = self.compare_models()
            report += "RESUMEN DE RENDIMIENTO:\n"
            report += comparison_df[['Modelo', 'R²', 'MAE', 'RMSE', 'MAPE']].to_string(index=False)
            report += "\n\n"
        except:
            pass
        
        # Detalles por modelo
        for model_name, results in self.model_results.items():
            if 'error' in results:
                report += f"MODELO: {self.available_models.get(model_name, model_name)} - ERROR\n"
                report += f"  Error: {results['error']}\n\n"
                continue
            
            model_display = self.available_models.get(model_name, model_name)
            report += f"MODELO: {model_display}\n"
            report += "=" * (len(model_display) + 8) + "\n"
            
            # Métricas principales
            report += f"  R² Score: {results['r2']:.6f}\n"
            report += f"  MAE: {results['mae']:.4f}\n"
            report += f"  RMSE: {results['rmse']:.4f}\n"
            report += f"  MAPE: {results['mape']:.2f}%\n"
            
            # Métricas adicionales
            if 'mean_residual' in results:
                report += f"  Error medio: {results['mean_residual']:.4f}\n"
                report += f"  Desv. std. residuos: {results['std_residual']:.4f}\n"
                report += f"  Error máximo: {results['max_residual']:.4f}\n"
                report += f"  Correlación pred-real: {results.get('prediction_correlation', 0):.4f}\n"
            
            # Distribución de errores
            if 'mae_p25' in results:
                report += f"\n  DISTRIBUCIÓN DE ERRORES ABSOLUTOS:\n"
                report += f"    P25: {results['mae_p25']:.4f}\n"
                report += f"    P50: {results['mae_p50']:.4f}\n"
                report += f"    P75: {results['mae_p75']:.4f}\n"
                report += f"    P90: {results['mae_p90']:.4f}\n"
                report += f"    P95: {results['mae_p95']:.4f}\n"
            
            # Interpretación
            r2 = results['r2']
            mae = results['mae']
            
            report += f"\n  INTERPRETACIÓN:\n"
            if r2 > 0.9:
                report += f"    Calidad: Excelente (R²={r2:.3f})\n"
            elif r2 > 0.7:
                report += f"    Calidad: Buena (R²={r2:.3f})\n"
            elif r2 > 0.5:
                report += f"    Calidad: Moderada (R²={r2:.3f})\n"
            else:
                report += f"    Calidad: Pobre (R²={r2:.3f})\n"
            
            if mae < 5:
                report += f"    Precisión: Alta (MAE={mae:.3f})\n"
            elif mae < 10:
                report += f"    Precisión: Media (MAE={mae:.3f})\n"
            else:
                report += f"    Precisión: Baja (MAE={mae:.3f})\n"
            
            report += "\n"
        
        # Mejor modelo
        try:
            best_model_name, best_results = self.get_best_model('r2')
            best_display = self.available_models.get(best_model_name, best_model_name)
            
            report += f"MEJOR MODELO: {best_display}\n"
            report += "=" * (len(best_display) + 14) + "\n"
            report += f"  Basado en R² Score: {best_results['r2']:.6f}\n"
            report += f"  MAE: {best_results['mae']:.4f}\n"
            report += f"  Explicación: El modelo explica {best_results['r2']*100:.1f}% de la varianza\n"
            
        except Exception as e:
            report += f"Error determinando mejor modelo: {str(e)}\n"
        
        # Feature importance del mejor modelo
        try:
            feature_importance = self.get_feature_importance()
            if not feature_importance.empty:
                report += f"\nTOP 10 FEATURES MÁS IMPORTANTES ({best_display}):\n"
                for i, (_, row) in enumerate(feature_importance.head(10).iterrows()):
                    report += f"  {i+1:2d}. {row['feature'][:50]:50s}: {row['importance']:.4f} ({row['importance_relative']:.1f}%)\n"
        except:
            pass
        
        # Recomendaciones
        report += "\nRECOMENDACIONES:\n"
        
        try:
            best_r2 = self.get_best_model('r2')[1]['r2']
            best_mae = self.get_best_model('mae')[1]['mae']
            
            if best_r2 < 0.7:
                report += "  • Considerar más features o ingeniería de features\n"
                report += "  • Probar hiperparámetros diferentes\n"
                report += "  • Evaluar calidad de los datos\n"
            
            if best_mae > 10:
                report += "  • Revisar outliers en los datos\n"
                report += "  • Considerar transformaciones de datos\n"
                report += "  • Evaluar si el target es adecuado\n"
            
            if len(self.model_results) < 3:
                report += "  • Probar más tipos de modelos\n"
                report += "  • Considerar ensemble methods\n"
            
        except:
            pass
        
        # Guardar si se especifica ruta
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Reporte guardado en: {output_path}")
        
        return report
    
    def save_all_models(self, directory_path: str):
        """Guardar todos los modelos entrenados"""
        from pathlib import Path
        
        save_dir = Path(directory_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        saved_models = []
        
        for model_name, model in self.trained_models.items():
            try:
                # Preparar datos del modelo
                model_data = {
                    'model': model,
                    'model_name': model_name,
                    'model_display': self.available_models.get(model_name, model_name),
                    'feature_columns': self.feature_columns,
                    'target_column': self.target_column,
                    'results': self.model_results.get(model_name, {}),
                    'timestamp': pd.Timestamp.now().isoformat()
                }
                
                # Incluir scaler si existe
                if model_name in self.scalers:
                    model_data['scaler'] = self.scalers[model_name]
                elif 'features' in self.scalers:
                    model_data['scaler'] = self.scalers['features']
                
                # Guardar
                filename = save_dir / f"model_{model_name}.joblib"
                joblib.dump(model_data, filename)
                saved_models.append(str(filename))
                
                logger.info(f"Modelo {model_name} guardado en {filename}")
                
            except Exception as e:
                logger.error(f"Error guardando modelo {model_name}: {str(e)}")
        
        return saved_models
    
    def load_model(self, model_path: str) -> Dict:
        """Cargar modelo desde archivo"""
        try:
            model_data = joblib.load(model_path)
            
            model_name = model_data['model_name']
            self.trained_models[model_name] = model_data['model']
            
            if 'results' in model_data:
                self.model_results[model_name] = model_data['results']
            
            if 'scaler' in model_data:
                self.scalers[model_name] = model_data['scaler']
            
            if 'feature_columns' in model_data:
                self.feature_columns = model_data['feature_columns']
            
            if 'target_column' in model_data:
                self.target_column = model_data['target_column']
            
            logger.info(f"Modelo {model_name} cargado exitosamente")
            return model_data
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {str(e)}")
            raise
    
    def predict_with_best_model(self, X_new: pd.DataFrame) -> np.ndarray:
        """Hacer predicciones con el mejor modelo"""
        best_model_name, _ = self.get_best_model('r2')
        
        if best_model_name not in self.trained_models:
            raise ValueError("Mejor modelo no disponible")
        
        model = self.trained_models[best_model_name]
        
        # Aplicar escalado si es necesario
        if best_model_name == 'neural_network' and 'features' in self.scalers:
            X_scaled = pd.DataFrame(
                self.scalers['features'].transform(X_new),
                columns=X_new.columns,
                index=X_new.index
            )
            predictions = model.predict(X_scaled)
            if len(predictions.shape) > 1:
                predictions = predictions.flatten()
        else:
            predictions = model.predict(X_new)
        
        return predictions
    
    def get_model_summary(self) -> Dict:
        """Obtener resumen general de todos los modelos"""
        if not self.model_results:
            return {"error": "No hay modelos entrenados"}
        
        valid_results = {name: results for name, results in self.model_results.items() 
                        if 'error' not in results}
        
        if not valid_results:
            return {"error": "No hay resultados válidos"}
        
        # Estadísticas generales
        r2_scores = [results['r2'] for results in valid_results.values()]
        mae_scores = [results['mae'] for results in valid_results.values()]
        
        try:
            best_model_name, best_results = self.get_best_model('r2')
            best_display = self.available_models.get(best_model_name, best_model_name)
        except:
            best_model_name = list(valid_results.keys())[0]
            best_results = valid_results[best_model_name]
            best_display = self.available_models.get(best_model_name, best_model_name)
        
        return {
            'total_models_trained': len(valid_results),
            'best_model': {
                'name': best_model_name,
                'display_name': best_display,
                'r2': best_results['r2'],
                'mae': best_results['mae']
            },
            'r2_stats': {
                'max': max(r2_scores),
                'min': min(r2_scores),
                'mean': np.mean(r2_scores),
                'std': np.std(r2_scores)
            },
            'mae_stats': {
                'max': max(mae_scores),
                'min': min(mae_scores),
                'mean': np.mean(mae_scores),
                'std': np.std(mae_scores)
            },
            'feature_count': len(self.feature_columns),
            'target_column': self.target_column
        }