"""
Tab avanzado de ML simplificado y estable
Sin selección de features - versión robusta
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
from pathlib import Path
import threading
import logging
from typing import Callable, Optional, Dict, Any

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

logger = logging.getLogger(__name__)

class AdvancedMLTab:
    """Tab avanzado de ML con funcionalidades integradas - Versión Estable"""
    
    def __init__(self, parent, data_loaded_callback: Callable):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        
        self.frame = ttk.Frame(parent)
        
        # Variables de entrenamiento
        self.n_estimators_var = tk.IntVar(value=100)
        self.test_size_var = tk.DoubleVar(value=0.2)
        self.random_state_var = tk.IntVar(value=42)
        
        # Estado actual
        self.current_data = None
        self.trained_model = None
        self.feature_columns = []
        self.target_column = 'vacancies'
        self.X_test = None
        self.y_test = None
        self.test_predictions = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del tab"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Crear notebook para sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        self.create_data_tab()
        self.create_training_tab()
        self.create_results_tab()
    
    def create_data_tab(self):
        """Tab de carga y exploración de datos"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Datos")
        
        # Sección de carga
        load_frame = ttk.LabelFrame(data_frame, text="Cargar Dataset", padding="10")
        load_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(load_frame, text="Cargar CSV/Excel", 
                  command=self.load_dataset).pack(side="left", padx=5)
        
        # Información del dataset
        info_frame = ttk.LabelFrame(data_frame, text="Información del Dataset", padding="10")
        info_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=20, wrap='word')
        self.info_text.pack(fill="both", expand=True)
    
    def create_training_tab(self):
        """Tab de entrenamiento"""
        train_frame = ttk.Frame(self.notebook)
        self.notebook.add(train_frame, text="🤖 Entrenamiento")
        
        # Panel izquierdo - Controles
        left_panel = ttk.Frame(train_frame)
        left_panel.pack(side="left", fill="y", padx=(10, 5))
        
        # Parámetros
        params_group = ttk.LabelFrame(left_panel, text="Parámetros Random Forest", padding="10")
        params_group.pack(fill='x', pady=(0, 10))
        
        ttk.Label(params_group, text="N° Estimadores:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Spinbox(params_group, from_=50, to=500, textvariable=self.n_estimators_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Test Size:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.test_size_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Random State:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.random_state_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        # Botones
        buttons_group = ttk.LabelFrame(left_panel, text="Acciones", padding="10")
        buttons_group.pack(fill='x', pady=(0, 10))
        
        self.train_btn = ttk.Button(buttons_group, text="Entrenar Modelo", 
                                   command=self.train_model)
        self.train_btn.pack(fill='x', pady=2)
        
        self.save_btn = ttk.Button(buttons_group, text="Guardar Modelo", 
                                  command=self.save_model, state="disabled")
        self.save_btn.pack(fill='x', pady=2)
        
        ttk.Button(buttons_group, text="Cargar Modelo", 
                  command=self.load_model).pack(fill='x', pady=2)
        
        # Panel derecho - Resultados de texto
        right_panel = ttk.Frame(train_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10))
        
        results_group = ttk.LabelFrame(right_panel, text="Métricas del Entrenamiento", padding="10")
        results_group.pack(fill='both', expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_group, height=20, wrap='word')
        self.results_text.pack(fill='both', expand=True)
    
    def create_results_tab(self):
        """Tab de resultados con visualizaciones"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📈 Resultados")
        
        # Botones de control de gráficos
        control_frame = ttk.Frame(results_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="Actualizar Gráficos", 
                  command=self.update_plots).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Guardar Gráficos", 
                  command=self.save_plots).pack(side="left", padx=5)
        
        # Frame para los gráficos
        self.plots_frame = ttk.Frame(results_frame)
        self.plots_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Crear figura de matplotlib
        self.fig, self.axes = plt.subplots(2, 3, figsize=(15, 10))
        self.fig.tight_layout(pad=3.0)
        
        # Canvas para mostrar los gráficos
        self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def load_dataset(self):
        """Cargar dataset desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Cargar Dataset",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    data = pd.read_excel(file_path)
                else:
                    data = pd.read_csv(file_path)
                
                self.load_dataset_from_dataframe(data)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando dataset:\n{str(e)}")
    
    def load_dataset_from_dataframe(self, data):
        """Cargar dataset desde un DataFrame"""
        try:
            self.current_data = data.copy()
            
            # Identificar columnas de texto y numéricas
            text_columns = []
            numeric_columns = []
            
            for col in data.columns:
                if data[col].dtype == 'object' or data[col].dtype.name == 'string':
                    text_columns.append(col)
                else:
                    numeric_columns.append(col)
            
            # Verificar que existe la columna target
            if self.target_column not in data.columns:
                # Buscar columnas similares
                potential_targets = [col for col in data.columns if 'vacanc' in col.lower()]
                if potential_targets:
                    self.target_column = potential_targets[0]
                    messagebox.showinfo("Info", f"Usando '{self.target_column}' como columna target")
                else:
                    raise ValueError(f"No se encontró la columna target '{self.target_column}' en el dataset")
            
            # Definir feature columns (numéricas, excluyendo target)
            self.feature_columns = [col for col in numeric_columns if col != self.target_column]
            
            if not self.feature_columns:
                raise ValueError("No se encontraron columnas numéricas para usar como features")
            
            # Actualizar información
            self.update_dataset_info(text_columns)
            
            # Notificar al callback
            self.data_loaded_callback(data)
            
            messagebox.showinfo("Éxito", 
                               f"Dataset cargado exitosamente!\n\n"
                               f"Filas: {len(data)}\n"
                               f"Features numéricas: {len(self.feature_columns)}\n"
                               f"Columnas de texto excluidas: {len(text_columns)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando dataset:\n{str(e)}")
    
    def update_dataset_info(self, text_columns):
        """Actualizar información del dataset"""
        if self.current_data is None:
            return
        
        info_lines = [
            "INFORMACIÓN DEL DATASET",
            "=" * 40,
            f"Filas: {len(self.current_data)}",
            f"Columnas totales: {len(self.current_data.columns)}",
            "",
            f"TARGET COLUMN: {self.target_column}",
            f"Valores únicos de target: {self.current_data[self.target_column].nunique()}",
            f"Rango de target: {self.current_data[self.target_column].min()} - {self.current_data[self.target_column].max()}",
            "",
            f"FEATURE COLUMNS ({len(self.feature_columns)}):",
            "-" * 20
        ]
        
        # Mostrar primeras 20 features
        for i, col in enumerate(self.feature_columns[:20]):
            info_lines.append(f"  {i+1:2d}. {col}")
        
        if len(self.feature_columns) > 20:
            info_lines.append(f"  ... y {len(self.feature_columns) - 20} más")
        
        if text_columns:
            info_lines.extend([
                "",
                f"COLUMNAS DE TEXTO EXCLUIDAS ({len(text_columns)}):",
                "-" * 25
            ])
            for col in text_columns:
                info_lines.append(f"  • {col}")
        
        # Estadísticas básicas del target
        target_stats = self.current_data[self.target_column].describe()
        info_lines.extend([
            "",
            "ESTADÍSTICAS DEL TARGET:",
            "-" * 25,
            f"  Media: {target_stats['mean']:.2f}",
            f"  Mediana: {target_stats['50%']:.2f}",
            f"  Desv. estándar: {target_stats['std']:.2f}",
            f"  Min: {target_stats['min']:.0f}",
            f"  Max: {target_stats['max']:.0f}"
        ])
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "\n".join(info_lines))
    
    def train_model(self):
        """Entrenar modelo Random Forest"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero carga un dataset")
            return
        
        try:
            self.train_btn.config(state="disabled")
            
            # Preparar datos
            X = self.current_data[self.feature_columns]
            y = self.current_data[self.target_column]
            
            # Verificar que no hay valores NaN
            if X.isnull().any().any():
                from sklearn.impute import SimpleImputer
                imputer = SimpleImputer(strategy='median')
                X_clean = pd.DataFrame(imputer.fit_transform(X), columns=X.columns, index=X.index)
            else:
                X_clean = X
            
            # División train/test
            X_train, self.X_test, y_train, self.y_test = train_test_split(
                X_clean, y, 
                test_size=self.test_size_var.get(),
                random_state=self.random_state_var.get()
            )
            
            # Crear y entrenar modelo
            self.trained_model = RandomForestRegressor(
                n_estimators=self.n_estimators_var.get(),
                random_state=self.random_state_var.get(),
                n_jobs=-1
            )
            
            self.trained_model.fit(X_train, y_train)
            
            # Evaluar modelo
            train_pred = self.trained_model.predict(X_train)
            self.test_predictions = self.trained_model.predict(self.X_test)
            
            train_mae = mean_absolute_error(y_train, train_pred)
            test_mae = mean_absolute_error(self.y_test, self.test_predictions)
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            test_rmse = np.sqrt(mean_squared_error(self.y_test, self.test_predictions))
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(self.y_test, self.test_predictions)
            
            # Validación cruzada
            cv_mae = -cross_val_score(self.trained_model, X_clean, y, cv=5, scoring='neg_mean_absolute_error')
            cv_r2 = cross_val_score(self.trained_model, X_clean, y, cv=5, scoring='r2')
            
            # Feature importance
            self.feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.trained_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Mostrar resultados de texto
            results_text = f"""RESULTADOS DEL ENTRENAMIENTO
===========================

CONFIGURACIÓN:
  Random Forest con {self.n_estimators_var.get()} estimadores
  Test size: {self.test_size_var.get():.1%}
  Features utilizadas: {len(self.feature_columns)}
  Muestras de entrenamiento: {len(X_train)}
  Muestras de prueba: {len(self.X_test)}

MÉTRICAS DE RENDIMIENTO:
  Train MAE:  {train_mae:.3f}
  Test MAE:   {test_mae:.3f}
  Train RMSE: {train_rmse:.3f}
  Test RMSE:  {test_rmse:.3f}
  Train R²:   {train_r2:.3f}
  Test R²:    {test_r2:.3f}

VALIDACIÓN CRUZADA (5-fold):
  CV MAE:  {cv_mae.mean():.3f} ± {cv_mae.std():.3f}
  CV R²:   {cv_r2.mean():.3f} ± {cv_r2.std():.3f}

TOP 15 FEATURES MÁS IMPORTANTES:
"""
            
            for i, row in self.feature_importance.head(15).iterrows():
                results_text += f"  {row['feature'][:40]:40s}: {row['importance']:.4f}\n"
            
            results_text += f"""

INTERPRETACIÓN:
  {'🟢 Excelente' if test_r2 > 0.9 else '🟡 Bueno' if test_r2 > 0.7 else '🔴 Mejorable'} (R² = {test_r2:.3f})
  {'🟢 Bajo error' if test_mae < 5 else '🟡 Error moderado' if test_mae < 10 else '🔴 Error alto'} (MAE = {test_mae:.1f})
"""
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results_text)
            
            # Habilitar botón de guardado
            self.save_btn.config(state="normal")
            
            # Actualizar gráficos
            self.update_plots()
            
            # Cambiar al tab de resultados para mostrar gráficos
            self.notebook.select(2)  # Tab de Resultados
            
            messagebox.showinfo("Entrenamiento Completado", 
                               f"Modelo entrenado exitosamente!\n\n"
                               f"Test R²: {test_r2:.3f}\n"
                               f"Test MAE: {test_mae:.3f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error entrenando modelo:\n{str(e)}")
        finally:
            self.train_btn.config(state="normal")
    
    def update_plots(self):
        """Actualizar todos los gráficos"""
        if self.trained_model is None or self.X_test is None:
            # Limpiar gráficos si no hay modelo
            for ax in self.axes.flat:
                ax.clear()
                ax.text(0.5, 0.5, 'Entrena un modelo\npara ver gráficos', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
            self.canvas.draw()
            return
        
        try:
            # Limpiar gráficos anteriores
            for ax in self.axes.flat:
                ax.clear()
            
            # 1. Predicciones vs Valores Reales
            ax1 = self.axes[0, 0]
            ax1.scatter(self.y_test, self.test_predictions, alpha=0.6, color='blue', s=50)
            
            # Línea diagonal perfecta
            min_val = min(self.y_test.min(), self.test_predictions.min())
            max_val = max(self.y_test.max(), self.test_predictions.max())
            ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Predicción perfecta')
            
            ax1.set_xlabel('Valores Reales')
            ax1.set_ylabel('Predicciones')
            ax1.set_title('Predicciones vs Valores Reales')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Mostrar R²
            r2 = r2_score(self.y_test, self.test_predictions)
            ax1.text(0.05, 0.95, f'R² = {r2:.3f}', transform=ax1.transAxes, 
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # 2. Residuos
            residuals = self.y_test - self.test_predictions
            ax2 = self.axes[0, 1]
            ax2.scatter(self.test_predictions, residuals, alpha=0.6, color='green', s=50)
            ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
            ax2.set_xlabel('Predicciones')
            ax2.set_ylabel('Residuos')
            ax2.set_title('Gráfico de Residuos')
            ax2.grid(True, alpha=0.3)
            
            # 3. Distribución de Residuos
            ax3 = self.axes[0, 2]
            ax3.hist(residuals, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax3.axvline(x=0, color='red', linestyle='--', linewidth=2)
            ax3.set_xlabel('Residuos')
            ax3.set_ylabel('Frecuencia')
            ax3.set_title('Distribución de Residuos')
            ax3.grid(True, alpha=0.3)
            
            # 4. Feature Importance
            ax4 = self.axes[1, 0]
            top_features = self.feature_importance.head(10)
            y_pos = np.arange(len(top_features))
            ax4.barh(y_pos, top_features['importance'], color='steelblue', alpha=0.8)
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels([feat[:20] + '...' if len(feat) > 20 else feat for feat in top_features['feature']], fontsize=8)
            ax4.set_xlabel('Importancia')
            ax4.set_title('Top 10 Features Más Importantes')
            ax4.invert_yaxis()
            ax4.grid(True, alpha=0.3)
            
            # 5. Errores Absolutos
            abs_errors = np.abs(residuals)
            ax5 = self.axes[1, 1]
            ax5.scatter(self.y_test, abs_errors, alpha=0.6, color='orange', s=50)
            ax5.set_xlabel('Valores Reales')
            ax5.set_ylabel('Error Absoluto')
            ax5.set_title('Error Absoluto vs Valores Reales')
            ax5.grid(True, alpha=0.3)
            
            # 6. Métricas de Evaluación
            ax6 = self.axes[1, 2]
            ax6.axis('off')
            
            mae = mean_absolute_error(self.y_test, self.test_predictions)
            rmse = np.sqrt(mean_squared_error(self.y_test, self.test_predictions))
            mape = np.mean(np.abs((self.y_test - self.test_predictions) / self.y_test)) * 100 if (self.y_test != 0).all() else 0
            
            metrics_text = f"""Métricas de Evaluación

R²: {r2:.4f}
MAE: {mae:.4f}
RMSE: {rmse:.4f}
MAPE: {mape:.2f}%

Muestras Test: {len(self.y_test)}
Error Std: {np.std(residuals):.4f}
Error Max: {np.max(abs_errors):.4f}

Rango Real:
[{self.y_test.min():.1f}, {self.y_test.max():.1f}]

Rango Pred:
[{self.test_predictions.min():.1f}, {self.test_predictions.max():.1f}]"""
            
            ax6.text(0.1, 0.9, metrics_text, transform=ax6.transAxes, fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                    verticalalignment='top', fontfamily='monospace')
            
            # Ajustar layout
            self.fig.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error actualizando gráficos: {e}")
    
    def save_plots(self):
        """Guardar gráficos como imagen"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "No hay gráficos para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar Gráficos",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")]
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráficos guardados en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando gráficos:\n{str(e)}")
    
    def save_model(self):
        """Guardar modelo entrenado"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "No hay modelo entrenado")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar Modelo",
            defaultextension=".joblib",
            filetypes=[("Joblib files", "*.joblib")]
        )
        
        if file_path:
            try:
                # Guardar modelo con metadatos
                model_data = {
                    'model': self.trained_model,
                    'feature_columns': self.feature_columns,
                    'target_column': self.target_column,
                    'training_params': {
                        'n_estimators': self.n_estimators_var.get(),
                        'test_size': self.test_size_var.get(),
                        'random_state': self.random_state_var.get()
                    },
                    'feature_importance': self.feature_importance if hasattr(self, 'feature_importance') else None
                }
                
                joblib.dump(model_data, file_path)
                messagebox.showinfo("Éxito", f"Modelo guardado en:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando modelo:\n{str(e)}")
    
    def load_model(self):
        """Cargar modelo previamente entrenado"""
        file_path = filedialog.askopenfilename(
            title="Cargar Modelo",
            filetypes=[("Joblib files", "*.joblib")]
        )
        
        if file_path:
            try:
                model_data = joblib.load(file_path)
                
                if isinstance(model_data, dict):
                    self.trained_model = model_data['model']
                    
                    # Verificar compatibilidad de features
                    saved_features = model_data.get('feature_columns', [])
                    if self.current_data is not None:
                        missing_features = set(saved_features) - set(self.current_data.columns)
                        if missing_features:
                            messagebox.showwarning("Advertencia", 
                                                 f"El dataset actual no tiene las features:\n{missing_features}")
                        else:
                            self.feature_columns = saved_features
                    else:
                        self.feature_columns = saved_features
                    
                    # Restaurar parámetros
                    params = model_data.get('training_params', {})
                    self.n_estimators_var.set(params.get('n_estimators', 100))
                    self.test_size_var.set(params.get('test_size', 0.2))
                    self.random_state_var.set(params.get('random_state', 42))
                    
                    # Restaurar feature importance si está disponible
                    if 'feature_importance' in model_data:
                        self.feature_importance = model_data['feature_importance']
                    
                    self.save_btn.config(state="normal")
                    messagebox.showinfo("Éxito", f"Modelo cargado desde:\n{file_path}")
                    
                else:
                    # Modelo legacy sin metadatos
                    self.trained_model = model_data
                    messagebox.showinfo("Éxito", "Modelo legacy cargado")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando modelo:\n{str(e)}")
    
    def reset(self):
        """Reset del tab"""
        self.current_data = None
        self.trained_model = None
        self.feature_columns = []
        self.X_test = None
        self.y_test = None
        self.test_predictions = None
        
        # Reset displays
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Carga un dataset para comenzar")
        
        self.results_text.delete(1.0, tk.END)
        
        # Reset botones
        self.save_btn.config(state="disabled")
        
        # Limpiar gráficos
        for ax in self.axes.flat:
            ax.clear()
            ax.text(0.5, 0.5, 'Carga un dataset\ny entrena un modelo', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
        self.canvas.draw()


# Alias para compatibilidad con código existente
AdvancedMLTabWithFeatureSelection = AdvancedMLTab