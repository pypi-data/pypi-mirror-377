


import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
from .data_manager import ModelObserver
class ModelTrainer:
    """Entrena y gestiona modelos de ML"""
    
    def __init__(self):
        self.model = None
        self.feature_importance = None
        self.training_results = {}
        self.observers: List[ModelObserver] = []
    
    def add_observer(self, observer: ModelObserver):
        self.observers.append(observer)
    
    def notify_observers(self):
        for observer in self.observers:
            observer.on_model_changed(self.model, self.feature_importance)
    
    def train_random_forest(self, X: pd.DataFrame, y: pd.Series, **params) -> Dict:
        """Entrenar Random Forest y retornar métricas"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split, cross_val_score
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            from sklearn.impute import SimpleImputer
            
            # Imputar valores faltantes
            if X.isnull().any().any():
                imputer = SimpleImputer(strategy='median')
                X_clean = pd.DataFrame(imputer.fit_transform(X), columns=X.columns, index=X.index)
            else:
                X_clean = X
            
            # División train/test
            test_size = params.get('test_size', 0.2)
            random_state = params.get('random_state', 42)
            
            X_train, X_test, y_train, y_test = train_test_split(
                X_clean, y, test_size=test_size, random_state=random_state
            )
            
            # Crear y entrenar modelo
            self.model = RandomForestRegressor(
                n_estimators=params.get('n_estimators', 100),
                random_state=random_state,
                n_jobs=-1
            )
            
            self.model.fit(X_train, y_train)
            
            # Predicciones
            train_pred = self.model.predict(X_train)
            test_pred = self.model.predict(X_test)
            
            # Métricas
            results = {
                'train_mae': mean_absolute_error(y_train, train_pred),
                'test_mae': mean_absolute_error(y_test, test_pred),
                'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
                'train_r2': r2_score(y_train, train_pred),
                'test_r2': r2_score(y_test, test_pred),
                'X_test': X_test,
                'y_test': y_test,
                'test_predictions': test_pred,
                'train_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            # Validación cruzada
            cv_mae = -cross_val_score(self.model, X_clean, y, cv=5, scoring='neg_mean_absolute_error')
            cv_r2 = cross_val_score(self.model, X_clean, y, cv=5, scoring='r2')
            
            results.update({
                'cv_mae_mean': cv_mae.mean(),
                'cv_mae_std': cv_mae.std(),
                'cv_r2_mean': cv_r2.mean(),
                'cv_r2_std': cv_r2.std()
            })
            
            # Feature importance
            self.feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            self.training_results = results
            self.notify_observers()
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Error en entrenamiento: {e}")
            raise e
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None:
            raise ValueError("No hay modelo entrenado")
        return self.model.predict(X)
    
    def get_model_summary(self) -> str:
        if not self.training_results:
            return "No hay modelo entrenado"
        
        results = self.training_results
        
        summary = f"""RESULTADOS DEL ENTRENAMIENTO
===========================

MÉTRICAS DE RENDIMIENTO:
  Train MAE:  {results['train_mae']:.3f}
  Test MAE:   {results['test_mae']:.3f}
  Train RMSE: {results['train_rmse']:.3f}
  Test RMSE:  {results['test_rmse']:.3f}
  Train R²:   {results['train_r2']:.3f}
  Test R²:    {results['test_r2']:.3f}

VALIDACIÓN CRUZADA (5-fold):
  CV MAE:  {results['cv_mae_mean']:.3f} ± {results['cv_mae_std']:.3f}
  CV R²:   {results['cv_r2_mean']:.3f} ± {results['cv_r2_std']:.3f}

MUESTRAS:
  Entrenamiento: {results['train_samples']}
  Prueba: {results['test_samples']}
"""
        
        if self.feature_importance is not None:
            summary += "\nTOP 10 FEATURES MÁS IMPORTANTES:\n"
            for i, row in self.feature_importance.head(10).iterrows():
                summary += f"  {row['feature'][:30]:30s}: {row['importance']:.4f}\n"
        
        return summary