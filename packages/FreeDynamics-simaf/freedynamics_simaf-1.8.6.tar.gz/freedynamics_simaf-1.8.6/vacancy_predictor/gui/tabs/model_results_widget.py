
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
class ModelResultsWidget:
    """Widget para mostrar resultados del modelo"""
    
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Métricas del Entrenamiento", padding="10")
        self.results_text = scrolledtext.ScrolledText(self.frame, height=20, wrap='word')
        self.results_text.pack(fill='both', expand=True)
    
    def on_model_changed(self, model: Any, feature_importance: pd.DataFrame = None):
        if model is not None:
            # Mostrar resumen del modelo
            summary = self.get_model_summary(model, feature_importance)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, summary)
    
    def update_results(self, results: Dict):
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

INTERPRETACIÓN:
  {'Excelente' if results['test_r2'] > 0.9 else 'Bueno' if results['test_r2'] > 0.7 else 'Mejorable'} (R² = {results['test_r2']:.3f})
  {'Bajo error' if results['test_mae'] < 5 else 'Error moderado' if results['test_mae'] < 10 else 'Error alto'} (MAE = {results['test_mae']:.1f})
"""
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, summary)
    
    def clear(self):
        self.results_text.delete(1.0, tk.END)
