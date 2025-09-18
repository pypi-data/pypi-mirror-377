



import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
from .data_manager import DataObserver,ModelObserver,FeatureObserver,DataManager
from .model_results_widget import ModelResultsWidget
from .model_visualization_widget import ModelVisualizationWidget
from .feature_selection_widget import FeatureSelectionWidget
from .data_info_widget import DataInfoWidget
from .model_trainer import ModelTrainer
from .feature_selector import FeatureSelector
from .configuration_manager import ConfigurationManager
class AdvancedMLApplication(DataObserver, FeatureObserver, ModelObserver):
    """Aplicación principal que coordina todos los componentes"""
    
    def __init__(self, parent, data_loaded_callback: Callable = None):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback or (lambda x: None)
        
        # Managers
        self.data_manager = DataManager()
        self.feature_selector = FeatureSelector()
        self.model_trainer = ModelTrainer()
        
        # Register as observers
        self.data_manager.add_observer(self)
        self.feature_selector.add_observer(self)
        self.model_trainer.add_observer(self)
        
        # Training parameters
        self.n_estimators_var = tk.IntVar(value=100)
        self.test_size_var = tk.DoubleVar(value=0.2)
        self.random_state_var = tk.IntVar(value=42)
        
        # UI components
        self.frame = ttk.Frame(parent)
        self.create_widgets()
    
    def create_widgets(self):
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        self.create_data_tab()
        self.create_feature_tab()
        self.create_training_tab()
        self.create_results_tab()
        self.create_prediction_tab()
    
    def create_data_tab(self):
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Datos")
        
        # Load controls
        load_frame = ttk.LabelFrame(data_frame, text="Cargar Dataset", padding="10")
        load_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(load_frame, text="Cargar CSV/Excel Original", 
                  command=self.load_dataset).pack(side="left", padx=5)
        ttk.Button(load_frame, text="Cargar CSV Filtrado", 
                  command=self.load_filtered_dataset).pack(side="left", padx=5)
        
        # Data info widget
        self.data_info_widget = DataInfoWidget(data_frame)
        self.data_info_widget.frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    def create_feature_tab(self):
        feature_frame = ttk.Frame(self.notebook)
        self.notebook.add(feature_frame, text="🎯 Features")
        
        # Feature selection widget
        self.feature_widget = FeatureSelectionWidget(feature_frame, self.feature_selector)
        
        # Apply button
        apply_frame = ttk.Frame(feature_frame)
        apply_frame.pack(fill="x", padx=10, pady=5)
        
        self.apply_features_btn = ttk.Button(apply_frame, text="Aplicar Selección de Features", 
                                           command=self.apply_feature_selection,
                                           state="disabled")
        self.apply_features_btn.pack(side="left", padx=5)
        
        self.feature_status_label = ttk.Label(apply_frame, text="Carga un dataset primero", foreground="red")
        self.feature_status_label.pack(side="left", padx=(20, 0))
    
    def create_training_tab(self):
        train_frame = ttk.Frame(self.notebook)
        self.notebook.add(train_frame, text="🤖 Entrenamiento")
        
        # Left panel - controls
        left_panel = ttk.Frame(train_frame)
        left_panel.pack(side="left", fill="y", padx=(10, 5))
        
        # Feature status
        features_status_frame = ttk.LabelFrame(left_panel, text="Estado de Features", padding="10")
        features_status_frame.pack(fill='x', pady=(0, 10))
        
        self.features_status_label = ttk.Label(features_status_frame, text="No hay features seleccionadas", foreground="red")
        self.features_status_label.pack(anchor="w")
        
        # Parameters
        params_group = ttk.LabelFrame(left_panel, text="Parámetros Random Forest", padding="10")
        params_group.pack(fill='x', pady=(0, 10))
        
        ttk.Label(params_group, text="N° Estimadores:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Spinbox(params_group, from_=50, to=500, textvariable=self.n_estimators_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Test Size:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.test_size_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Random State:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.random_state_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        # Action buttons
        buttons_group = ttk.LabelFrame(left_panel, text="Acciones", padding="10")
        buttons_group.pack(fill='x', pady=(0, 10))
        
        self.train_btn = ttk.Button(buttons_group, text="Entrenar Modelo", 
                                   command=self.train_model, state="disabled")
        self.train_btn.pack(fill='x', pady=2)
        
        self.save_model_btn = ttk.Button(buttons_group, text="Guardar Modelo", 
                                        command=self.save_model, state="disabled")
        self.save_model_btn.pack(fill='x', pady=2)
        
        ttk.Button(buttons_group, text="Cargar Modelo", 
                  command=self.load_model).pack(fill='x', pady=2)
        
        # Right panel - results
        right_panel = ttk.Frame(train_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10))
        
        self.model_results_widget = ModelResultsWidget(right_panel)
        self.model_results_widget.frame.pack(fill='both', expand=True)
    
    def create_results_tab(self):
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📈 Resultados")
        
        self.visualization_widget = ModelVisualizationWidget(results_frame)
        self.visualization_widget.frame.pack(fill="both", expand=True)
    
    def create_prediction_tab(self):
        pred_frame = ttk.Frame(self.notebook)
        self.notebook.add(pred_frame, text="🔮 Predicción")
        
        # Placeholder for prediction interface
        ttk.Label(pred_frame, text="Interfaz de predicción individual", 
                 font=('Arial', 14)).pack(pady=20)
        
        # This would contain the prediction interface
        # For brevity, not implementing the full prediction interface here
    
    # Observer implementations
    def on_data_changed(self, data: pd.DataFrame):
        """Called when data changes"""
        info = self.data_manager.get_data_info()
        self.data_info_widget.update_info(info)
        self.apply_features_btn.config(state="normal")
        self.feature_status_label.config(text="Dataset cargado. Selecciona features y aplica.", foreground="orange")
        self.data_loaded_callback(data)
    
    def on_features_changed(self, features: List[str], target: str):
        """Called when feature selection changes"""
        # This is automatically handled by the feature widget
        pass
    
    def on_model_changed(self, model: Any, feature_importance: pd.DataFrame = None):
        """Called when model changes"""
        if model is not None:
            self.save_model_btn.config(state="normal")
    
    # Action methods
    def load_dataset(self):
        file_path = filedialog.askopenfilename(
            title="Cargar Dataset",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            if self.data_manager.load_from_file(file_path):
                messagebox.showinfo("Éxito", "Dataset cargado exitosamente")
                self.notebook.select(1)  # Go to features tab
            else:
                messagebox.showerror("Error", "Error cargando dataset")
    
    def load_filtered_dataset(self):
        file_path = filedialog.askopenfilename(
            title="Cargar Dataset Filtrado",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                data = pd.read_csv(file_path, index_col=0)
                
                # For filtered datasets, assume last column is target
                target_column = data.columns[-1]
                feature_columns = list(data.columns[:-1])
                
                self.data_manager.load_from_dataframe(data)
                self.feature_selector.target_column = target_column
                self.feature_selector.selected_features = feature_columns
                
                # Enable training directly
                self.features_status_label.config(
                    text=f"✓ {len(feature_columns)} features cargadas, target: {target_column}",
                    foreground="green"
                )
                self.train_btn.config(state="normal")
                
                messagebox.showinfo("Éxito", "Dataset filtrado cargado. Listo para entrenar.")
                self.notebook.select(2)  # Go to training tab
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando dataset filtrado:\n{str(e)}")
    
    def apply_feature_selection(self):
        """Apply feature selection for training"""
        try:
            if not self.feature_selector.selected_features:
                messagebox.showwarning("Advertencia", "No hay features seleccionadas")
                return
            
            if not self.feature_selector.target_column:
                messagebox.showwarning("Advertencia", "No hay columna target seleccionada")
                return
            
            # Update status
            self.features_status_label.config(
                text=f"✓ {len(self.feature_selector.selected_features)} features seleccionadas, target: {self.feature_selector.target_column}",
                foreground="green"
            )
            
            self.feature_status_label.config(
                text=f"✓ Features aplicadas: {len(self.feature_selector.selected_features)} features para entrenamiento",
                foreground="green"
            )
            
            # Enable training
            self.train_btn.config(state="normal")
            
            # Go to training tab
            self.notebook.select(2)
            
            messagebox.showinfo("Éxito", 
                               f"Selección aplicada correctamente!\n\n"
                               f"Features: {len(self.feature_selector.selected_features)}\n"
                               f"Target: {self.feature_selector.target_column}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error aplicando selección:\n{str(e)}")
    
    def train_model(self):
        """Train the ML model"""
        if not self.feature_selector.selected_features:
            messagebox.showwarning("Advertencia", "Primero selecciona y aplica las features")
            return
        
        try:
            self.train_btn.config(state="disabled")
            
            data = self.data_manager.get_data()
            if data is None:
                raise ValueError("No hay datos cargados")
            
            X = data[self.feature_selector.selected_features]
            y = data[self.feature_selector.target_column]
            
            # Training parameters
            params = {
                'n_estimators': self.n_estimators_var.get(),
                'test_size': self.test_size_var.get(),
                'random_state': self.random_state_var.get()
            }
            
            # Train model
            results = self.model_trainer.train_random_forest(X, y, **params)
            
            # Update results widget
            self.model_results_widget.update_results(results)
            
            # Update visualization
            self.visualization_widget.update_training_results(results)
            
            # Go to results tab
            self.notebook.select(3)
            
            messagebox.showinfo("Entrenamiento Completado", 
                               f"Modelo entrenado exitosamente!\n\n"
                               f"Test R²: {results['test_r2']:.3f}\n"
                               f"Test MAE: {results['test_mae']:.3f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error entrenando modelo:\n{str(e)}")
        finally:
            self.train_btn.config(state="normal")
    
    def save_model(self):
        """Save trained model"""
        if self.model_trainer.model is None:
            messagebox.showwarning("Advertencia", "No hay modelo entrenado")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar Modelo",
            defaultextension=".joblib",
            filetypes=[("Joblib files", "*.joblib")]
        )
        
        if file_path:
            if ConfigurationManager.save_model(self.model_trainer, self.feature_selector, file_path):
                messagebox.showinfo("Éxito", f"Modelo guardado en:\n{file_path}")
            else:
                messagebox.showerror("Error", "Error guardando modelo")
    
    def load_model(self):
        """Load a trained model"""
        file_path = filedialog.askopenfilename(
            title="Cargar Modelo",
            filetypes=[("Joblib files", "*.joblib")]
        )
        
        if file_path:
            try:
                import joblib
                model_data = joblib.load(file_path)
                
                if isinstance(model_data, dict):
                    # Load model
                    self.model_trainer.model = model_data.get('model')
                    self.model_trainer.feature_importance = model_data.get('feature_importance')
                    self.model_trainer.training_results = model_data.get('training_results', {})
                    
                    # Load feature configuration
                    feature_config = model_data.get('feature_config', {})
                    if feature_config and self.data_manager.current_data is not None:
                        available_features = list(self.data_manager.current_data.columns)
                        self.feature_selector.load_config(feature_config, available_features)
                    
                    # Update UI
                    self.features_status_label.config(
                        text=f"✓ Modelo cargado con {len(feature_config.get('selected_features', []))} features",
                        foreground="green"
                    )
                    
                    self.save_model_btn.config(state="normal")
                    self.train_btn.config(state="normal")
                    
                    messagebox.showinfo("Éxito", f"Modelo cargado desde:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando modelo:\n{str(e)}")
    
    def reset(self):
        """Reset the entire application state"""
        self.data_manager.reset()
        self.feature_selector.selected_features = []
        self.feature_selector.target_column = 'vacancies'
        self.feature_selector.feature_stats = {}
        self.model_trainer.model = None
        self.model_trainer.feature_importance = None
        self.model_trainer.training_results = {}
        
        # Reset UI
        self.features_status_label.config(text="No hay features seleccionadas", foreground="red")
        self.feature_status_label.config(text="Carga un dataset primero", foreground="red")
        self.train_btn.config(state="disabled")
        self.save_model_btn.config(state="disabled")
        self.apply_features_btn.config(state="disabled")
        
        # Clear widgets
        self.data_info_widget.clear()
        self.model_results_widget.clear()
        self.visualization_widget.clear_plots()
    
    def get_frame(self):
        """Get the main frame for embedding in other applications"""
        return self.frame
