"""
Enhanced Data Processor with Multiple ML Models
Supports Random Forest, XGBoost, and optionally Neural Networks
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Tuple
import logging
import joblib
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost no disponible. Instale con: pip install xgboost")

# Optional neural network imports
try:
    import tensorflow as tf
    from tensorflow import keras
    from keras import layers
    NEURAL_NETWORKS_AVAILABLE = True
except ImportError:
    NEURAL_NETWORKS_AVAILABLE = False
    print("TensorFlow no disponible. Redes neuronales deshabilitadas.")

logger = logging.getLogger(__name__)

class MultiModelProcessor:
    """
    Enhanced processor with multiple ML models for vacancy prediction
    """
    
    def __init__(self):
        self.data = None
        self.features = None
        self.target = None
        self.target_column = None
        
        # Model storage
        self.models = {}
        self.model_results = {}
        self.scaler = None
        
        # Supported models
        self.available_models = {
            'random_forest': 'Random Forest'
        }
        
        if XGBOOST_AVAILABLE:
            self.available_models['xgboost'] = 'XGBoost'
        
        if NEURAL_NETWORKS_AVAILABLE:
            self.available_models['neural_network'] = 'Neural Network'
        
        # Default model configurations
        self.model_configs = {
            'random_forest': {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'random_state': [42]
            }
        }
        
        if XGBOOST_AVAILABLE:
            self.model_configs['xgboost'] = {
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 6, 10],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 0.9, 1.0],
                'random_state': [42]
            }
        
        if NEURAL_NETWORKS_AVAILABLE:
            self.model_configs['neural_network'] = {
                'hidden_layers': [[64, 32], [128, 64, 32], [256, 128, 64]],
                'dropout_rate': [0.1, 0.2, 0.3],
                'learning_rate': [0.001, 0.01, 0.1],
                'batch_size': [32, 64, 128],
                'epochs': [50, 100, 200]
            }
    
    def get_available_models(self) -> Dict[str, str]:
        """Get list of available models"""
        return self.available_models.copy()
    
    def set_model_config(self, model_name: str, config: Dict[str, Any]) -> None:
        """Set custom configuration for a model"""
        if model_name not in self.available_models:
            raise ValueError(f"Model {model_name} not available")
        
        self.model_configs[model_name] = config
        logger.info(f"Updated configuration for {model_name}")
    
    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get current configuration for a model"""
        return self.model_configs.get(model_name, {})
    
    def prepare_data(self, X: pd.DataFrame, y: pd.Series, 
                    test_size: float = 0.2, scale_features: bool = True) -> Tuple:
        """
        Prepare data for training with optional scaling
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Scale features if requested
        if scale_features:
            self.scaler = StandardScaler()
            X_train_scaled = pd.DataFrame(
                self.scaler.fit_transform(X_train),
                columns=X_train.columns,
                index=X_train.index
            )
            X_test_scaled = pd.DataFrame(
                self.scaler.transform(X_test),
                columns=X_test.columns,
                index=X_test.index
            )
            return X_train_scaled, X_test_scaled, y_train, y_test
        
        return X_train, X_test, y_train, y_test
    
    def train_random_forest(self, X_train: pd.DataFrame, y_train: pd.Series,
                           custom_params: Dict = None, use_grid_search: bool = True) -> Dict:
        """Train Random Forest model"""
        logger.info("Training Random Forest model...")
        
        if custom_params:
            params = custom_params
        elif use_grid_search:
            # Grid search for best parameters
            rf = RandomForestRegressor(random_state=42, n_jobs=-1)
            grid_search = GridSearchCV(
                rf, self.model_configs['random_forest'],
                cv=5, scoring='neg_mean_absolute_error',
                n_jobs=-1, verbose=1
            )
            grid_search.fit(X_train, y_train)
            params = grid_search.best_params_
            logger.info(f"Best RF parameters: {params}")
        else:
            # Use default parameters
            params = {
                'n_estimators': 200,
                'max_depth': 20,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42,
                'n_jobs': -1
            }
        
        # Train final model
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        
        # Store model and parameters
        self.models['random_forest'] = {
            'model': model,
            'params': params,
            'feature_importance': pd.DataFrame({
                'feature': X_train.columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
        }
        
        return self.models['random_forest']
    
    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                     custom_params: Dict = None, use_grid_search: bool = True) -> Dict:
        """Train XGBoost model"""
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost not available. Install with: pip install xgboost")
            
        logger.info("Training XGBoost model...")
        
        if custom_params:
            params = custom_params
        elif use_grid_search:
            # Grid search for best parameters
            xgb_model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
            grid_search = GridSearchCV(
                xgb_model, self.model_configs['xgboost'],
                cv=5, scoring='neg_mean_absolute_error',
                n_jobs=-1, verbose=1
            )
            grid_search.fit(X_train, y_train)
            params = grid_search.best_params_
            logger.info(f"Best XGBoost parameters: {params}")
        else:
            # Use default parameters
            params = {
                'n_estimators': 200,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.9,
                'random_state': 42,
                'n_jobs': -1
            }
        
        # Train final model
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train)
        
        # Store model and parameters
        self.models['xgboost'] = {
            'model': model,
            'params': params,
            'feature_importance': pd.DataFrame({
                'feature': X_train.columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
        }
        
        return self.models['xgboost']
    
    def train_neural_network(self, X_train: pd.DataFrame, y_train: pd.Series,
                           X_val: pd.DataFrame, y_val: pd.Series,
                           custom_params: Dict = None) -> Dict:
        """Train Neural Network model (if TensorFlow available)"""
        if not NEURAL_NETWORKS_AVAILABLE:
            raise ImportError("TensorFlow not available for neural networks")
        
        logger.info("Training Neural Network model...")
        
        if custom_params:
            params = custom_params
        else:
            # Use default parameters
            params = {
                'hidden_layers': [128, 64, 32],
                'dropout_rate': 0.2,
                'learning_rate': 0.001,
                'batch_size': 64,
                'epochs': 100
            }
        
        # Build model architecture
        model = keras.Sequential()
        
        # Input layer
        model.add(layers.Dense(params['hidden_layers'][0], 
                              activation='relu', 
                              input_shape=(X_train.shape[1],)))
        model.add(layers.Dropout(params['dropout_rate']))
        
        # Hidden layers
        for units in params['hidden_layers'][1:]:
            model.add(layers.Dense(units, activation='relu'))
            model.add(layers.Dropout(params['dropout_rate']))
        
        # Output layer
        model.add(layers.Dense(1, activation='linear'))
        
        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=params['learning_rate'])
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
        
        # Callbacks
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss', patience=20, restore_best_weights=True
        )
        
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=10, min_lr=1e-7
        )
        
        # Train model
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=params['epochs'],
            batch_size=params['batch_size'],
            callbacks=[early_stopping, reduce_lr],
            verbose=1
        )
        
        # Store model and parameters
        self.models['neural_network'] = {
            'model': model,
            'params': params,
            'history': history.history,
            'feature_importance': None  # Could implement permutation importance
        }
        
        return self.models['neural_network']
    
    def evaluate_model(self, model_name: str, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """Evaluate a trained model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        model = self.models[model_name]['model']
        
        # Make predictions
        if model_name == 'neural_network':
            # Neural networks might return 2D array, flatten it
            y_pred = model.predict(X_test)
            if len(y_pred.shape) > 1:
                y_pred = y_pred.flatten()
        else:
            y_pred = model.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        # Calculate additional metrics
        # Avoid division by zero in MAPE calculation
        mape = np.mean(np.abs((y_test - y_pred) / np.where(y_test != 0, y_test, 1e-8))) * 100
        
        results = {
            'model_name': model_name,
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'mape': mape,
            'predictions': y_pred,
            'actual': y_test.values
        }
        
        self.model_results[model_name] = results
        
        logger.info(f"{model_name} evaluation - MAE: {mae:.4f}, R²: {r2:.4f}")
        
        return results
    
    def train_all_models(self, X: pd.DataFrame, y: pd.Series,
                        test_size: float = 0.2,
                        models_to_train: List[str] = None,
                        use_grid_search: bool = True) -> Dict:
        """Train multiple models and compare performance"""
        
        if models_to_train is None:
            models_to_train = list(self.available_models.keys())
        
        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(
            X, y, test_size, scale_features='neural_network' in models_to_train
        )
        
        # For neural networks, create validation set
        if 'neural_network' in models_to_train:
            X_train_nn, X_val, y_train_nn, y_val = train_test_split(
                X_train, y_train, test_size=0.2, random_state=42
            )
        
        results_summary = {}
        
        # Train each model
        for model_name in models_to_train:
            try:
                if model_name == 'random_forest':
                    self.train_random_forest(X_train, y_train, use_grid_search=use_grid_search)
                elif model_name == 'xgboost' and XGBOOST_AVAILABLE:
                    self.train_xgboost(X_train, y_train, use_grid_search=use_grid_search)
                elif model_name == 'neural_network' and NEURAL_NETWORKS_AVAILABLE:
                    self.train_neural_network(X_train_nn, y_train_nn, X_val, y_val)
                else:
                    logger.warning(f"Model {model_name} not available, skipping...")
                    continue
                
                # Evaluate model
                results = self.evaluate_model(model_name, X_test, y_test)
                results_summary[model_name] = results
                
            except Exception as e:
                logger.error(f"Error training {model_name}: {str(e)}")
                results_summary[model_name] = {'error': str(e)}
        
        return results_summary
    
    def get_best_model(self, metric: str = 'r2') -> Tuple[str, Dict]:
        """Get the best performing model based on specified metric"""
        if not self.model_results:
            raise ValueError("No models have been trained and evaluated yet")
        
        valid_metrics = ['mae', 'mse', 'rmse', 'r2', 'mape']
        if metric not in valid_metrics:
            raise ValueError(f"Metric must be one of: {valid_metrics}")
        
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
            else:  # Lower is better for mae, mse, rmse, mape
                if score < best_score:
                    best_score = score
                    best_model = model_name
        
        if best_model is None:
            raise ValueError("No valid model results found")
        
        return best_model, self.model_results[best_model]
    
    def compare_models(self) -> pd.DataFrame:
        """Create comparison table of all trained models"""
        if not self.model_results:
            raise ValueError("No models have been trained yet")
        
        comparison_data = []
        
        for model_name, results in self.model_results.items():
            if 'error' not in results:
                comparison_data.append({
                    'Model': self.available_models[model_name],
                    'MAE': results['mae'],
                    'RMSE': results['rmse'],
                    'R²': results['r2'],
                    'MAPE (%)': results['mape']
                })
        
        df = pd.DataFrame(comparison_data)
        
        # Sort by R² (descending)
        if not df.empty:
            df = df.sort_values('R²', ascending=False)
        
        return df
    
    def save_models(self, output_dir: Union[str, Path]) -> None:
        """Save all trained models"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for model_name, model_data in self.models.items():
            model_file = output_path / f"{model_name}_model.joblib"
            
            if model_name == 'neural_network':
                # Save Keras model separately
                keras_file = output_path / f"{model_name}_model.h5"
                model_data['model'].save(keras_file)
                
                # Save other data
                other_data = {k: v for k, v in model_data.items() if k != 'model'}
                joblib.dump(other_data, model_file)
            else:
                joblib.dump(model_data, model_file)
        
        # Save scaler if used
        if self.scaler is not None:
            scaler_file = output_path / "scaler.joblib"
            joblib.dump(self.scaler, scaler_file)
        
        # Save results
        results_file = output_path / "model_results.joblib"
        joblib.dump(self.model_results, results_file)
        
        logger.info(f"Models saved to {output_path}")
    
    def load_models(self, input_dir: Union[str, Path]) -> None:
        """Load previously saved models"""
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Directory not found: {input_path}")
        
        # Load models
        for model_name in self.available_models.keys():
            model_file = input_path / f"{model_name}_model.joblib"
            
            if model_file.exists():
                if model_name == 'neural_network':
                    # Load Keras model
                    keras_file = input_path / f"{model_name}_model.h5"
                    if keras_file.exists():
                        model = keras.models.load_model(keras_file)
                        other_data = joblib.load(model_file)
                        other_data['model'] = model
                        self.models[model_name] = other_data
                else:
                    self.models[model_name] = joblib.load(model_file)
        
        # Load scaler
        scaler_file = input_path / "scaler.joblib"
        if scaler_file.exists():
            self.scaler = joblib.load(scaler_file)
        
        # Load results
        results_file = input_path / "model_results.joblib"
        if results_file.exists():
            self.model_results = joblib.load(results_file)
        
        logger.info(f"Models loaded from {input_path}")
    
    def predict_with_model(self, model_name: str, X: pd.DataFrame) -> np.ndarray:
        """Make predictions with a specific model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not available")
        
        model = self.models[model_name]['model']
        
        # Apply scaling if necessary
        if self.scaler is not None and model_name == 'neural_network':
            X_scaled = pd.DataFrame(
                self.scaler.transform(X),
                columns=X.columns,
                index=X.index
            )
            return model.predict(X_scaled).flatten()
        
        return model.predict(X)
    
    def get_feature_importance(self, model_name: str) -> pd.DataFrame:
        """Get feature importance for tree-based models"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not available")
        
        if model_name in ['random_forest', 'xgboost']:
            return self.models[model_name]['feature_importance']
        else:
            raise ValueError(f"Feature importance not available for {model_name}")