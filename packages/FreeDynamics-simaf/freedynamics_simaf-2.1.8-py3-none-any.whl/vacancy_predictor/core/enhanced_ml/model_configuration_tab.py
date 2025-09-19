"""
GUI Component for Model Configuration and Training
Integrates with the Enhanced DataProcessor
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import pandas as pd
import numpy as np
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from sklearn.model_selection import train_test_split
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class ModelConfigurationTab:
    """Tab for configuring and training multiple ML models"""
    
    def __init__(self, parent, data_loaded_callback, processor=None):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        self.processor = processor  # MultiModelProcessor instance
        
        self.frame = ttk.Frame(parent)
        
        # Data
        self.current_data = None
        self.feature_columns = []
        self.target_column = 'vacancies'
        
        # Model configuration storage
        self.model_configs = {}
        self.training_results = {}
        
        # Training state
        self.training_in_progress = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the main interface"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self.create_data_setup_tab()
        self.create_model_config_tab()
        self.create_training_tab()
        self.create_results_tab()
    
    def create_data_setup_tab(self):
        """Tab for data setup and feature selection"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Configuración de Datos")
        
        # Data info section
        info_frame = ttk.LabelFrame(data_frame, text="Información del Dataset", padding="10")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.data_info_text = scrolledtext.ScrolledText(info_frame, height=8, wrap='word')
        self.data_info_text.pack(fill="both", expand=True)
        
        # Feature selection section
        features_frame = ttk.LabelFrame(data_frame, text="Selección de Features", padding="10")
        features_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Target selection
        target_frame = ttk.Frame(features_frame)
        target_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(target_frame, text="Columna Target:").pack(side="left")
        self.target_combo = ttk.Combobox(target_frame, state="readonly", width=20)
        self.target_combo.pack(side="left", padx=(10, 0))
        self.target_combo.bind('<<ComboboxSelected>>', self.on_target_change)
        
        # Features listbox with scrollbar
        listbox_frame = ttk.Frame(features_frame)
        listbox_frame.pack(fill="both", expand=True)
        
        self.features_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED)
        features_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", 
                                         command=self.features_listbox.yview)
        self.features_listbox.configure(yscrollcommand=features_scrollbar.set)
        
        self.features_listbox.pack(side="left", fill="both", expand=True)
        features_scrollbar.pack(side="right", fill="y")
        
        # Feature selection buttons
        buttons_frame = ttk.Frame(features_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Seleccionar Todo", 
                  command=self.select_all_features).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Deseleccionar Todo", 
                  command=self.deselect_all_features).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Auto-Seleccionar (Top 50)", 
                  command=self.auto_select_features).pack(side="left", padx=5)
        
        # Data validation button
        ttk.Button(features_frame, text="🔍 Validar Datos", 
                  command=self.validate_data).pack(pady=(10, 0))
    
    def create_model_config_tab(self):
        """Tab for model configuration"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ Configuración de Modelos")
        
        # Model selection
        selection_frame = ttk.LabelFrame(config_frame, text="Selección de Modelos", padding="10")
        selection_frame.pack(fill="x", padx=10, pady=5)
        
        self.model_vars = {}
        if self.processor:
            available_models = self.processor.get_available_models()
            for model_key, model_name in available_models.items():
                var = tk.BooleanVar(value=True)
                self.model_vars[model_key] = var
                ttk.Checkbutton(selection_frame, text=model_name, 
                              variable=var).pack(anchor="w")
        
        # Configuration notebook for each model
        self.config_notebook = ttk.Notebook(config_frame)
        self.config_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.create_rf_config_tab()
        self.create_xgb_config_tab()
        
        # Add neural network tab if available
        try:
            from enhanced_ml.multi_model_processor import NEURAL_NETWORKS_AVAILABLE
            if self.processor and 'neural_network' in self.processor.get_available_models():
                self.create_nn_config_tab()
        except ImportError:
            pass  # Neural networks not available
    
    def create_rf_config_tab(self):
        """Random Forest configuration tab"""
        rf_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(rf_frame, text="Random Forest")
        
        # Parameter configuration
        params_frame = ttk.LabelFrame(rf_frame, text="Parámetros", padding="10")
        params_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid layout for parameters
        row = 0
        
        # N Estimators
        ttk.Label(params_frame, text="N° Estimadores:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.rf_n_estimators = tk.StringVar(value="100,200,300")
        ttk.Entry(params_frame, textvariable=self.rf_n_estimators, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        row += 1
        ttk.Label(params_frame, text="Profundidad Máxima:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.rf_max_depth = tk.StringVar(value="10,20,None")
        ttk.Entry(params_frame, textvariable=self.rf_max_depth, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        row += 1
        ttk.Label(params_frame, text="Min Samples Split:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.rf_min_samples_split = tk.StringVar(value="2,5,10")
        ttk.Entry(params_frame, textvariable=self.rf_min_samples_split, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        row += 1
        ttk.Label(params_frame, text="Min Samples Leaf:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.rf_min_samples_leaf = tk.StringVar(value="1,2,4")
        ttk.Entry(params_frame, textvariable=self.rf_min_samples_leaf, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        # Grid search option
        options_frame = ttk.LabelFrame(rf_frame, text="Opciones", padding="10")
        options_frame.pack(fill="x", padx=10, pady=5)
        
        self.rf_use_grid_search = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Usar Grid Search (recomendado)", 
                       variable=self.rf_use_grid_search).pack(anchor="w")
        
        # Help text
        help_frame = ttk.Frame(rf_frame)
        help_frame.pack(fill="x", padx=10, pady=5)
        
        help_text = """Ayuda: Ingrese valores separados por comas. Use 'None' para sin límite.
Ejemplo: '10,20,None' para probar profundidades 10, 20 y sin límite."""
        ttk.Label(help_frame, text=help_text, font=("Arial", 8), 
                 foreground="gray", wraplength=400).pack(anchor="w")
    
    def create_xgb_config_tab(self):
        """XGBoost configuration tab"""
        xgb_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(xgb_frame, text="XGBoost")
        
        # Parameter configuration
        params_frame = ttk.LabelFrame(xgb_frame, text="Parámetros", padding="10")
        params_frame.pack(fill="x", padx=10, pady=5)
        
        row = 0
        
        # N Estimators
        ttk.Label(params_frame, text="N° Estimadores:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.xgb_n_estimators = tk.StringVar(value="100,200,300")
        ttk.Entry(params_frame, textvariable=self.xgb_n_estimators, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        row += 1
        ttk.Label(params_frame, text="Profundidad Máxima:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.xgb_max_depth = tk.StringVar(value="3,6,10")
        ttk.Entry(params_frame, textvariable=self.xgb_max_depth, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        row += 1
        ttk.Label(params_frame, text="Learning Rate:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.xgb_learning_rate = tk.StringVar(value="0.01,0.1,0.2")
        ttk.Entry(params_frame, textvariable=self.xgb_learning_rate, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        row += 1
        ttk.Label(params_frame, text="Subsample:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.xgb_subsample = tk.StringVar(value="0.8,0.9,1.0")
        ttk.Entry(params_frame, textvariable=self.xgb_subsample, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        # Options
        options_frame = ttk.LabelFrame(xgb_frame, text="Opciones", padding="10")
        options_frame.pack(fill="x", padx=10, pady=5)
        
        self.xgb_use_grid_search = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Usar Grid Search (recomendado)", 
                       variable=self.xgb_use_grid_search).pack(anchor="w")
    
    def create_nn_config_tab(self):
        """Neural Network configuration tab"""
        nn_frame = ttk.Frame(self.config_notebook)
        self.config_notebook.add(nn_frame, text="Red Neuronal")
        
        # Architecture section
        arch_frame = ttk.LabelFrame(nn_frame, text="Arquitectura", padding="10")
        arch_frame.pack(fill="x", padx=10, pady=5)
        
        row = 0
        
        # Hidden layers
        ttk.Label(arch_frame, text="Capas Ocultas:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.nn_hidden_layers = tk.StringVar(value="128,64,32")
        ttk.Entry(arch_frame, textvariable=self.nn_hidden_layers, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        row += 1
        ttk.Label(arch_frame, text="Dropout Rate:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.nn_dropout = tk.DoubleVar(value=0.2)
        ttk.Scale(arch_frame, from_=0.0, to=0.5, orient=tk.HORIZONTAL, 
                 variable=self.nn_dropout, length=150).grid(row=row, column=1, padx=5, pady=2)
        
        # Training parameters
        train_frame = ttk.LabelFrame(nn_frame, text="Entrenamiento", padding="10")
        train_frame.pack(fill="x", padx=10, pady=5)
        
        row = 0
        
        ttk.Label(train_frame, text="Learning Rate:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.nn_learning_rate = tk.DoubleVar(value=0.001)
        ttk.Entry(train_frame, textvariable=self.nn_learning_rate, width=20).grid(row=row, column=1, padx=5, pady=2)
        
        row += 1
        ttk.Label(train_frame, text="Batch Size:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.nn_batch_size = tk.IntVar(value=64)
        ttk.Spinbox(train_frame, from_=16, to=256, textvariable=self.nn_batch_size, width=18).grid(row=row, column=1, padx=5, pady=2)
        
        row += 1
        ttk.Label(train_frame, text="Épocas:").grid(row=row, column=0, sticky="w", padx=5, pady=2)
        self.nn_epochs = tk.IntVar(value=100)
        ttk.Spinbox(train_frame, from_=50, to=500, textvariable=self.nn_epochs, width=18).grid(row=row, column=1, padx=5, pady=2)
        
        # Help text for neural networks
        help_frame = ttk.Frame(nn_frame)
        help_frame.pack(fill="x", padx=10, pady=5)
        
        nn_help_text = """Ayuda Red Neuronal:
• Capas Ocultas: Neuronas por capa separadas por comas (ej: 128,64,32)
• Dropout: Previene overfitting (0.1-0.3 recomendado)
• Learning Rate: Velocidad de aprendizaje (0.001-0.01 típico)"""
        ttk.Label(help_frame, text=nn_help_text, font=("Arial", 8), 
                 foreground="gray", wraplength=400).pack(anchor="w")
    
    def create_training_tab(self):
        """Tab for model training"""
        training_frame = ttk.Frame(self.notebook)
        self.notebook.add(training_frame, text="🚀 Entrenamiento")
        
        # Training configuration
        config_frame = ttk.LabelFrame(training_frame, text="Configuración de Entrenamiento", padding="10")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # Test size
        ttk.Label(config_frame, text="Tamaño del conjunto de prueba:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.test_size_var = tk.DoubleVar(value=0.2)
        test_scale = ttk.Scale(config_frame, from_=0.1, to=0.4, orient=tk.HORIZONTAL, 
                              variable=self.test_size_var, length=200)
        test_scale.grid(row=0, column=1, padx=5, pady=2)
        
        self.test_size_label = ttk.Label(config_frame, text="20%")
        self.test_size_label.grid(row=0, column=2, padx=5, pady=2)
        test_scale.configure(command=self.update_test_size_label)
        
        # Cross-validation folds
        ttk.Label(config_frame, text="Folds para validación cruzada:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.cv_folds_var = tk.IntVar(value=5)
        ttk.Spinbox(config_frame, from_=3, to=10, textvariable=self.cv_folds_var, width=10).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Training controls
        controls_frame = ttk.LabelFrame(training_frame, text="Control de Entrenamiento", padding="10")
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill="x")
        
        self.train_button = ttk.Button(button_frame, text="🚀 Entrenar Modelos Seleccionados", 
                                      command=self.start_training)
        self.train_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Detener", 
                                     command=self.stop_training, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="💾 Guardar Configuración", 
                  command=self.save_config).pack(side="right", padx=5)
        ttk.Button(button_frame, text="📁 Cargar Configuración", 
                  command=self.load_config).pack(side="right", padx=5)
        
        # Progress section
        progress_frame = ttk.LabelFrame(training_frame, text="Progreso", padding="10")
        progress_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Listo para entrenar")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack(anchor="w")
        
        # Training log
        self.training_log = scrolledtext.ScrolledText(progress_frame, height=12, wrap='word')
        self.training_log.pack(fill="both", expand=True, pady=(10, 0))
    
    def create_results_tab(self):
        """Tab for training results and model comparison"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📊 Resultados")
        
        # Results summary
        summary_frame = ttk.LabelFrame(results_frame, text="Resumen de Resultados", padding="10")
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        # Create treeview for model comparison
        columns = ('Modelo', 'MAE', 'RMSE', 'R²', 'MAPE (%)')
        self.results_tree = ttk.Treeview(summary_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100, anchor='center')
        
        results_scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", 
                                        command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side="left", fill="x", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Best model info
        best_model_frame = ttk.LabelFrame(results_frame, text="Mejor Modelo", padding="10")
        best_model_frame.pack(fill="x", padx=10, pady=5)
        
        self.best_model_text = tk.Text(best_model_frame, height=4, wrap='word', state='disabled')
        self.best_model_text.pack(fill="x")
        
        # Visualization section
        viz_frame = ttk.LabelFrame(results_frame, text="Visualizaciones", padding="10")
        viz_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Visualization controls
        viz_controls = ttk.Frame(viz_frame)
        viz_controls.pack(fill="x", pady=(0, 10))
        
        ttk.Button(viz_controls, text="📈 Comparar Modelos", 
                  command=self.plot_model_comparison).pack(side="left", padx=5)
        ttk.Button(viz_controls, text="🎯 Predicciones vs Real", 
                  command=self.plot_predictions).pack(side="left", padx=5)
        ttk.Button(viz_controls, text="📊 Feature Importance", 
                  command=self.plot_feature_importance).pack(side="left", padx=5)
        
        # Matplotlib canvas
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Export section
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(export_frame, text="💾 Exportar Modelos", 
                  command=self.export_models).pack(side="left", padx=5)
        ttk.Button(export_frame, text="📋 Exportar Resultados", 
                  command=self.export_results).pack(side="left", padx=5)
    
    # Data handling methods
    def load_dataset_from_dataframe(self, data):
        """Load dataset from DataFrame"""
        self.current_data = data.copy()
        self.update_data_info()
        self.update_feature_list()
        self.update_target_combo()
    
    def update_data_info(self):
        """Update data information display"""
        if self.current_data is None:
            return
        
        info_text = f"""Dataset Information:
• Filas: {len(self.current_data)}
• Columnas: {len(self.current_data.columns)}
• Valores faltantes: {self.current_data.isnull().sum().sum()}
• Memoria: {self.current_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB

Tipos de datos:
• Numéricos: {len(self.current_data.select_dtypes(include=[np.number]).columns)}
• Categóricos: {len(self.current_data.select_dtypes(include=['object']).columns)}
"""
        
        self.data_info_text.delete(1.0, tk.END)
        self.data_info_text.insert(1.0, info_text)
    
    def update_feature_list(self):
        """Update features listbox"""
        self.features_listbox.delete(0, tk.END)
        
        if self.current_data is None:
            return
        
        # Exclude common non-feature columns
        exclude_cols = ['file_path', 'filename', 'vacancies']
        feature_candidates = [col for col in self.current_data.columns if col not in exclude_cols]
        
        for feature in sorted(feature_candidates):
            self.features_listbox.insert(tk.END, feature)
    
    def update_target_combo(self):
        """Update target combobox"""
        if self.current_data is None:
            return
        
        target_candidates = [col for col in self.current_data.columns if 'vacan' in col.lower()]
        if not target_candidates:
            target_candidates = ['vacancies']
        
        self.target_combo['values'] = target_candidates
        if target_candidates:
            self.target_combo.set(target_candidates[0])
            self.target_column = target_candidates[0]
    
    def on_target_change(self, event):
        """Handle target column change"""
        self.target_column = self.target_combo.get()
    
    def select_all_features(self):
        """Select all features"""
        self.features_listbox.select_set(0, tk.END)
    
    def deselect_all_features(self):
        """Deselect all features"""
        self.features_listbox.selection_clear(0, tk.END)
    
    def auto_select_features(self):
        """Auto-select top features based on correlation with target"""
        if self.current_data is None or self.target_column not in self.current_data.columns:
            messagebox.showwarning("Advertencia", "Primero configure los datos y target")
            return
        
        try:
            # Calculate correlations
            numeric_cols = self.current_data.select_dtypes(include=[np.number]).columns
            target_data = self.current_data[self.target_column]
            
            correlations = {}
            for col in numeric_cols:
                if col != self.target_column:
                    corr = self.current_data[col].corr(target_data)
                    if not np.isnan(corr):
                        correlations[col] = abs(corr)
            
            # Sort by correlation and select top 50
            sorted_features = sorted(correlations.items(), key=lambda x: x[1], reverse=True)[:50]
            top_features = [feat for feat, _ in sorted_features]
            
            # Select in listbox
            self.deselect_all_features()
            for i in range(self.features_listbox.size()):
                if self.features_listbox.get(i) in top_features:
                    self.features_listbox.select_set(i)
            
            messagebox.showinfo("Información", f"Seleccionadas {len(top_features)} features por correlación")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en selección automática: {str(e)}")
    
    def validate_data(self):
        """Validate data for training"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "No hay datos cargados")
            return
        
        # Check target column
        if self.target_column not in self.current_data.columns:
            messagebox.showerror("Error", "Columna target no encontrada")
            return
        
        # Check selected features
        selected_indices = self.features_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Advertencia", "Seleccione al menos una feature")
            return
        
        selected_features = [self.features_listbox.get(i) for i in selected_indices]
        
        # Check for missing values
        missing_features = []
        for feature in selected_features:
            if self.current_data[feature].isnull().sum() > 0:
                missing_features.append(feature)
        
        # Check for constant features
        constant_features = []
        for feature in selected_features:
            if self.current_data[feature].nunique() <= 1:
                constant_features.append(feature)
        
        # Show validation results
        validation_text = "Validación de Datos:\n\n"
        validation_text += f"✓ Dataset: {len(self.current_data)} filas\n"
        validation_text += f"✓ Target: {self.target_column}\n"
        validation_text += f"✓ Features seleccionadas: {len(selected_features)}\n\n"
        
        if missing_features:
            validation_text += f"⚠️ Features con valores faltantes: {len(missing_features)}\n"
            validation_text += f"   {missing_features[:5]}{'...' if len(missing_features) > 5 else ''}\n\n"
        
        if constant_features:
            validation_text += f"⚠️ Features constantes (sin varianza): {len(constant_features)}\n"
            validation_text += f"   {constant_features[:5]}{'...' if len(constant_features) > 5 else ''}\n\n"
        
        if not missing_features and not constant_features:
            validation_text += "✅ Datos listos para entrenamiento\n"
        
        messagebox.showinfo("Validación de Datos", validation_text)
    
    # Training methods
    def update_test_size_label(self, value):
        """Update test size label"""
        percentage = int(float(value) * 100)
        self.test_size_label.config(text=f"{percentage}%")
    
    def parse_parameter_string(self, param_str):
        """Parse parameter string into list"""
        try:
            values = []
            for item in param_str.split(','):
                item = item.strip()
                if item.lower() == 'none':
                    values.append(None)
                elif '.' in item:
                    values.append(float(item))
                else:
                    values.append(int(item))
            return values
        except ValueError:
            raise ValueError(f"Error parsing parameter string: {param_str}")
    
    def get_model_configurations(self):
        """Get current model configurations"""
        configs = {}
        
        try:
            # Random Forest
            if self.model_vars.get('random_forest', tk.BooleanVar()).get():
                configs['random_forest'] = {
                    'n_estimators': self.parse_parameter_string(self.rf_n_estimators.get()),
                    'max_depth': self.parse_parameter_string(self.rf_max_depth.get()),
                    'min_samples_split': self.parse_parameter_string(self.rf_min_samples_split.get()),
                    'min_samples_leaf': self.parse_parameter_string(self.rf_min_samples_leaf.get()),
                    'random_state': [42],
                    'use_grid_search': self.rf_use_grid_search.get()
                }
            
            # XGBoost
            if (self.model_vars.get('xgboost', tk.BooleanVar()).get() and 
                hasattr(self, 'xgb_n_estimators')):
                configs['xgboost'] = {
                    'n_estimators': self.parse_parameter_string(self.xgb_n_estimators.get()),
                    'max_depth': self.parse_parameter_string(self.xgb_max_depth.get()),
                    'learning_rate': self.parse_parameter_string(self.xgb_learning_rate.get()),
                    'subsample': self.parse_parameter_string(self.xgb_subsample.get()),
                    'random_state': [42],
                    'use_grid_search': self.xgb_use_grid_search.get()
                }
            
            # Neural Network
            if (self.model_vars.get('neural_network', tk.BooleanVar()).get() and 
                hasattr(self, 'nn_hidden_layers')):
                
                hidden_layers = [int(x.strip()) for x in self.nn_hidden_layers.get().split(',')]
                
                configs['neural_network'] = {
                    'hidden_layers': hidden_layers,
                    'dropout_rate': self.nn_dropout.get(),
                    'learning_rate': self.nn_learning_rate.get(),
                    'batch_size': self.nn_batch_size.get(),
                    'epochs': self.nn_epochs.get()
                }
            
            return configs
            
        except Exception as e:
            raise ValueError(f"Error en configuración de modelos: {str(e)}")
    
    def start_training(self):
        """Start model training in separate thread"""
        if self.training_in_progress:
            messagebox.showwarning("Advertencia", "Entrenamiento en progreso")
            return
        
        try:
            # Validate inputs
            if self.current_data is None:
                messagebox.showerror("Error", "No hay datos cargados")
                return
            
            selected_indices = self.features_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("Error", "Seleccione features para entrenar")
                return
            
            # Get configurations
            model_configs = self.get_model_configurations()
            if not model_configs:
                messagebox.showerror("Error", "Seleccione al menos un modelo")
                return
            
            # Prepare data
            self.feature_columns = [self.features_listbox.get(i) for i in selected_indices]
            
            # Start training thread
            self.training_in_progress = True
            self.train_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            training_thread = threading.Thread(target=self._training_worker, 
                                             args=(model_configs,), daemon=True)
            training_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error iniciando entrenamiento: {str(e)}")
            self._reset_training_state()
    
    def _training_worker(self, model_configs):
        """Worker thread for model training"""
        try:
            self._log_message("=== INICIANDO ENTRENAMIENTO ===")
            
            # Prepare data
            X = self.current_data[self.feature_columns]
            y = self.current_data[self.target_column]
            
            self._log_message(f"Features: {len(self.feature_columns)}")
            self._log_message(f"Muestras: {len(X)}")
            self._log_message(f"Target: {self.target_column}")
            
            # Configure processor
            if self.processor:
                for model_name, config in model_configs.items():
                    if model_name != 'neural_network':
                        # Remove our custom keys from config
                        clean_config = {k: v for k, v in config.items() 
                                      if k not in ['use_grid_search']}
                        self.processor.set_model_config(model_name, clean_config)
            
            # Train models
            models_to_train = list(model_configs.keys())
            total_models = len(models_to_train)
            
            for i, model_name in enumerate(models_to_train):
                if not self.training_in_progress:  # Check for stop signal
                    break
                
                progress = (i / total_models) * 100
                self._update_progress(progress, f"Entrenando {model_name}...")
                
                self._log_message(f"\n--- ENTRENANDO {model_name.upper()} ---")
                
                try:
                    if self.processor:
                        # Use grid search setting
                        use_grid_search = model_configs[model_name].get('use_grid_search', True)
                        
                        if model_name == 'random_forest':
                            self.processor.train_random_forest(X, y, use_grid_search=use_grid_search)
                        elif model_name == 'xgboost':
                            # Check if XGBoost is available in the processor
                            try:
                                self.processor.train_xgboost(X, y, use_grid_search=use_grid_search)
                            except ImportError as e:
                                self._log_message(f"XGBoost no disponible: {str(e)}")
                                continue
                        elif model_name == 'neural_network':
                            # For NN, we need train/val split
                            X_train_split, X_val, y_train_split, y_val = train_test_split(
                                X, y, test_size=0.2, random_state=42
                            )
                            custom_params = {k: v for k, v in model_configs[model_name].items() 
                                           if k != 'use_grid_search'}
                            try:
                                self.processor.train_neural_network(X_train_split, y_train_split, X_val, y_val, 
                                                                   custom_params=custom_params)
                            except ImportError as e:
                                self._log_message(f"TensorFlow no disponible: {str(e)}")
                                continue
                        
                        self._log_message(f"✓ {model_name} entrenado exitosamente")
                    
                except Exception as e:
                    self._log_message(f"✗ Error entrenando {model_name}: {str(e)}")
                    logger.error(f"Training error for {model_name}: {str(e)}")
            
            # Final evaluation
            if self.training_in_progress and self.processor:
                self._update_progress(90, "Evaluando modelos...")
                self._log_message("\n--- EVALUACIÓN FINAL ---")
                
                # Evaluate all trained models
                X_test = X.sample(frac=self.test_size_var.get(), random_state=42)
                y_test = y.loc[X_test.index]
                
                for model_name in self.processor.models.keys():
                    try:
                        results = self.processor.evaluate_model(model_name, X_test, y_test)
                        self._log_message(f"{model_name}: MAE={results['mae']:.4f}, R²={results['r2']:.4f}")
                    except Exception as e:
                        self._log_message(f"Error evaluando {model_name}: {str(e)}")
                
                # Update results display
                self.frame.after(0, self._update_results_display)
            
            self._update_progress(100, "Entrenamiento completado")
            self._log_message("\n=== ENTRENAMIENTO COMPLETADO ===")
            
        except Exception as e:
            error_msg = f"Error durante entrenamiento: {str(e)}"
            self._log_message(f"ERROR: {error_msg}")
            logger.error(error_msg)
            
        finally:
            # Reset training state
            self.frame.after(0, self._reset_training_state)
    
    def stop_training(self):
        """Stop training process"""
        self.training_in_progress = False
        self._log_message("Deteniendo entrenamiento...")
        self._reset_training_state()
    
    def _reset_training_state(self):
        """Reset training UI state"""
        self.training_in_progress = False
        self.train_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Listo para entrenar")
    
    def _update_progress(self, value, message):
        """Update progress bar and status"""
        self.progress_var.set(value)
        self.status_var.set(message)
        self.frame.update_idletasks()
    
    def _log_message(self, message):
        """Add message to training log"""
        self.training_log.insert(tk.END, f"{message}\n")
        self.training_log.see(tk.END)
        self.frame.update_idletasks()
    
    def _update_results_display(self):
        """Update results display with latest training results"""
        if not self.processor or not self.processor.model_results:
            return
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add model results to tree
        for model_name, results in self.processor.model_results.items():
            if 'error' not in results:
                model_display_name = self.processor.available_models.get(model_name, model_name)
                self.results_tree.insert('', 'end', values=(
                    model_display_name,
                    f"{results['mae']:.4f}",
                    f"{results['rmse']:.4f}",
                    f"{results['r2']:.4f}",
                    f"{results['mape']:.2f}"
                ))
        
        # Update best model info
        try:
            best_model_name, best_results = self.processor.get_best_model('r2')
            best_model_display = self.processor.available_models.get(best_model_name, best_model_name)
            
            best_text = f"""Mejor Modelo: {best_model_display}
R² Score: {best_results['r2']:.4f}
MAE: {best_results['mae']:.4f}
RMSE: {best_results['rmse']:.4f}
MAPE: {best_results['mape']:.2f}%"""
            
            self.best_model_text.config(state='normal')
            self.best_model_text.delete(1.0, tk.END)
            self.best_model_text.insert(1.0, best_text)
            self.best_model_text.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Error updating best model info: {str(e)}")
    
    # Visualization methods
    def plot_model_comparison(self):
        """Plot model comparison chart"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados para mostrar")
            return
        
        try:
            self.ax.clear()
            
            # Prepare data
            models = []
            mae_scores = []
            r2_scores = []
            
            for model_name, results in self.processor.model_results.items():
                if 'error' not in results:
                    models.append(self.processor.available_models.get(model_name, model_name))
                    mae_scores.append(results['mae'])
                    r2_scores.append(results['r2'])
            
            if not models:
                self.ax.text(0.5, 0.5, 'No hay resultados válidos', 
                           ha='center', va='center', transform=self.ax.transAxes)
                self.canvas.draw()
                return
            
            # Create comparison plot
            x = np.arange(len(models))
            width = 0.35
            
            # Normalize scores for better visualization
            mae_normalized = [(max(mae_scores) - mae) / max(mae_scores) for mae in mae_scores]
            
            bars1 = self.ax.bar(x - width/2, r2_scores, width, label='R² Score', alpha=0.8)
            bars2 = self.ax.bar(x + width/2, mae_normalized, width, label='MAE (normalizado)', alpha=0.8)
            
            self.ax.set_xlabel('Modelos')
            self.ax.set_ylabel('Puntuación')
            self.ax.set_title('Comparación de Modelos')
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(models, rotation=45, ha='right')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, value in zip(bars1, r2_scores):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{value:.3f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando gráfico: {str(e)}")
    
    def plot_predictions(self):
        """Plot predictions vs actual values"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados para mostrar")
            return
        
        try:
            self.ax.clear()
            
            # Get best model results
            best_model_name, best_results = self.processor.get_best_model('r2')
            
            y_true = best_results['actual']
            y_pred = best_results['predictions']
            
            # Scatter plot
            self.ax.scatter(y_true, y_pred, alpha=0.6, s=50)
            
            # Perfect prediction line
            min_val = min(y_true.min(), y_pred.min())
            max_val = max(y_true.max(), y_pred.max())
            self.ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, 
                        label='Predicción perfecta')
            
            self.ax.set_xlabel('Valores Reales')
            self.ax.set_ylabel('Predicciones')
            self.ax.set_title(f'Predicciones vs Reales - {self.processor.available_models.get(best_model_name, best_model_name)}')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # Add metrics text
            r2 = best_results['r2']
            mae = best_results['mae']
            self.ax.text(0.05, 0.95, f'R² = {r2:.3f}\nMAE = {mae:.3f}', 
                        transform=self.ax.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                        verticalalignment='top')
            
            plt.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando gráfico: {str(e)}")
    
    def plot_feature_importance(self):
        """Plot feature importance for tree-based models"""
        if not self.processor or not self.processor.models:
            messagebox.showwarning("Advertencia", "No hay modelos entrenados")
            return
        
        try:
            # Find a tree-based model with feature importance
            importance_data = None
            model_name = None
            
            for name in ['random_forest', 'xgboost']:
                if name in self.processor.models:
                    importance_data = self.processor.get_feature_importance(name)
                    model_name = name
                    break
            
            if importance_data is None:
                messagebox.showinfo("Información", "No hay modelos con feature importance disponible")
                return
            
            self.ax.clear()
            
            # Get top 20 features
            top_features = importance_data.head(20)
            
            # Horizontal bar plot
            y_pos = np.arange(len(top_features))
            bars = self.ax.barh(y_pos, top_features['importance'], alpha=0.8)
            
            self.ax.set_yticks(y_pos)
            self.ax.set_yticklabels(top_features['feature'])
            self.ax.set_xlabel('Importancia')
            self.ax.set_title(f'Top 20 Feature Importance - {self.processor.available_models.get(model_name, model_name)}')
            self.ax.invert_yaxis()
            self.ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                self.ax.text(width + 0.001, bar.get_y() + bar.get_height()/2, 
                           f'{width:.3f}', ha='left', va='center', fontsize=8)
            
            plt.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando gráfico: {str(e)}")
    
    # Export methods
    def save_config(self):
        """Save current configuration"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            
            if filename:
                config = {
                    'target_column': self.target_column,
                    'selected_features': [self.features_listbox.get(i) for i in self.features_listbox.curselection()],
                    'test_size': self.test_size_var.get(),
                    'cv_folds': self.cv_folds_var.get(),
                    'model_configs': self.get_model_configurations()
                }
                
                import json
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=4)
                
                messagebox.showinfo("Éxito", f"Configuración guardada en: {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuración: {str(e)}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            from tkinter import filedialog
            import json
            
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Apply configuration
                if 'target_column' in config:
                    self.target_column = config['target_column']
                    self.target_combo.set(self.target_column)
                
                if 'test_size' in config:
                    self.test_size_var.set(config['test_size'])
                
                if 'cv_folds' in config:
                    self.cv_folds_var.set(config['cv_folds'])
                
                # Apply model configurations
                if 'model_configs' in config:
                    model_configs = config['model_configs']
                    
                    # Random Forest
                    if 'random_forest' in model_configs:
                        rf_config = model_configs['random_forest']
                        self.rf_n_estimators.set(','.join(map(str, rf_config.get('n_estimators', [100]))))
                        self.rf_max_depth.set(','.join(map(str, rf_config.get('max_depth', [10]))))
                        self.rf_min_samples_split.set(','.join(map(str, rf_config.get('min_samples_split', [2]))))
                        self.rf_min_samples_leaf.set(','.join(map(str, rf_config.get('min_samples_leaf', [1]))))
                        self.rf_use_grid_search.set(rf_config.get('use_grid_search', True))
                    
                    # XGBoost
                    if 'xgboost' in model_configs:
                        xgb_config = model_configs['xgboost']
                        self.xgb_n_estimators.set(','.join(map(str, xgb_config.get('n_estimators', [100]))))
                        self.xgb_max_depth.set(','.join(map(str, xgb_config.get('max_depth', [6]))))
                        self.xgb_learning_rate.set(','.join(map(str, xgb_config.get('learning_rate', [0.1]))))
                        self.xgb_subsample.set(','.join(map(str, xgb_config.get('subsample', [1.0]))))
                        self.xgb_use_grid_search.set(xgb_config.get('use_grid_search', True))
                    
                    # Neural Network
                    if 'neural_network' in model_configs and hasattr(self, 'nn_hidden_layers'):
                        nn_config = model_configs['neural_network']
                        self.nn_hidden_layers.set(','.join(map(str, nn_config.get('hidden_layers', [128, 64, 32]))))
                        self.nn_dropout.set(nn_config.get('dropout_rate', 0.2))
                        self.nn_learning_rate.set(nn_config.get('learning_rate', 0.001))
                        self.nn_batch_size.set(nn_config.get('batch_size', 64))
                        self.nn_epochs.set(nn_config.get('epochs', 100))
                
                # Select features
                if 'selected_features' in config:
                    self.deselect_all_features()
                    selected_features = config['selected_features']
                    for i in range(self.features_listbox.size()):
                        if self.features_listbox.get(i) in selected_features:
                            self.features_listbox.select_set(i)
                
                messagebox.showinfo("Éxito", f"Configuración cargada desde: {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando configuración: {str(e)}")
    
    def export_models(self):
        """Export trained models"""
        if not self.processor or not self.processor.models:
            messagebox.showwarning("Advertencia", "No hay modelos entrenados")
            return
        
        try:
            from tkinter import filedialog
            
            directory = filedialog.askdirectory(title="Seleccionar directorio para exportar modelos")
            
            if directory:
                self.processor.save_models(directory)
                messagebox.showinfo("Éxito", f"Modelos exportados a: {directory}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando modelos: {str(e)}")
    
    def export_results(self):
        """Export training results"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
            )
            
            if filename:
                # Create results DataFrame
                comparison_df = self.processor.compare_models()
                
                if filename.endswith('.xlsx'):
                    comparison_df.to_excel(filename, index=False)
                else:
                    comparison_df.to_csv(filename, index=False)
                
                messagebox.showinfo("Éxito", f"Resultados exportados a: {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando resultados: {str(e)}")
    
    def reset(self):
        """Reset the tab"""
        self.current_data = None
        self.feature_columns = []
        self.target_column = 'vacancies'
        self.training_results = {}
        
        # Reset UI
        self.data_info_text.delete(1.0, tk.END)
        self.features_listbox.delete(0, tk.END)
        self.target_combo.set('')
        
        # Clear results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.best_model_text.config(state='normal')
        self.best_model_text.delete(1.0, tk.END)
        self.best_model_text.config(state='disabled')
        
        # Clear plots
        self.ax.clear()
        self.ax.text(0.5, 0.5, 'Entrene modelos para ver visualizaciones', 
                   ha='center', va='center', transform=self.ax.transAxes)
        self.canvas.draw()
        
        # Reset training state
        self._reset_training_state()
        
        # Clear log
        self.training_log.delete(1.0, tk.END)