"""
Tab de entrenamiento de modelos ML
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from typing import Callable, Optional, Dict, Any
import logging
import threading
import time
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

class TrainingTab:
    """Tab para entrenamiento de modelos de machine learning"""
    
    def __init__(self, parent, model_trainer, data_processor, model_trained_callback: Callable = None):
        """
        Inicializar tab de entrenamiento
        
        Args:
            parent: Widget padre (notebook)
            model_trainer: Instancia del entrenador de modelos
            data_processor: Instancia del procesador de datos
            model_trained_callback: Callback cuando se entrena un modelo
        """
        self.parent = parent
        self.model_trainer = model_trainer
        self.data_processor = data_processor
        self.model_trained_callback = model_trained_callback
        
        # Variables de estado
        self.current_data = None
        self.trained_models = {}
        self.training_in_progress = False
        
        # Crear la interfaz
        self.create_interface()
        logger.info("TrainingTab initialized")
    
    def create_interface(self):
        """Crear la interfaz del tab"""
        # Frame principal
        self.frame = ttk.Frame(self.parent)
        
        # Configurar grid
        self.frame.grid_rowconfigure(0, weight=0)  # Header
        self.frame.grid_rowconfigure(1, weight=1)  # Main content
        self.frame.grid_rowconfigure(2, weight=0)  # Progress
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header()
        
        # Contenido principal
        self.create_main_content()
        
        # Barra de progreso
        self.create_progress_section()
    
    def create_header(self):
        """Crear sección de header"""
        header_frame = ttk.LabelFrame(self.frame, text="Training Configuration", padding=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Configurar grid del header
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Información del dataset
        ttk.Label(header_frame, text="Dataset Status:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.dataset_status_label = ttk.Label(header_frame, text="No data loaded", foreground="red")
        self.dataset_status_label.grid(row=0, column=1, sticky="w")
        
        # Selección de target
        ttk.Label(header_frame, text="Target Column:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(5, 0))
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(header_frame, textvariable=self.target_var, state="readonly")
        self.target_combo.grid(row=1, column=1, sticky="ew", pady=(5, 0))
        self.target_combo.bind("<<ComboboxSelected>>", self.on_target_selected)
        
        # Botones de acción
        button_frame = ttk.Frame(header_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        self.refresh_btn = ttk.Button(button_frame, text="Refresh Data", command=self.refresh_data)
        self.refresh_btn.pack(side="left", padx=(0, 5))
        
        self.train_all_btn = ttk.Button(button_frame, text="Train All Models", command=self.train_all_models)
        self.train_all_btn.pack(side="left", padx=5)
        
        self.save_models_btn = ttk.Button(button_frame, text="Save Best Model", command=self.save_best_model)
        self.save_models_btn.pack(side="left", padx=5)
    
    def create_main_content(self):
        """Crear contenido principal"""
        main_frame = ttk.Frame(self.frame)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Configurar grid
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Panel izquierdo - Configuración de modelos
        self.create_model_config_panel(main_frame)
        
        # Panel derecho - Resultados
        self.create_results_panel(main_frame)
    
    def create_model_config_panel(self, parent):
        """Crear panel de configuración de modelos"""
        config_frame = ttk.LabelFrame(parent, text="Model Configuration", padding=10)
        config_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Configurar grid
        config_frame.grid_rowconfigure(1, weight=1)
        config_frame.grid_columnconfigure(0, weight=1)
        
        # Información del dataset
        info_frame = ttk.Frame(config_frame)
        info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Estadísticas del dataset
        ttk.Label(info_frame, text="Samples:").grid(row=0, column=0, sticky="w")
        self.samples_label = ttk.Label(info_frame, text="0")
        self.samples_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(info_frame, text="Features:").grid(row=1, column=0, sticky="w")
        self.features_label = ttk.Label(info_frame, text="0")
        self.features_label.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        # Lista de modelos disponibles
        models_frame = ttk.LabelFrame(config_frame, text="Available Models", padding=5)
        models_frame.grid(row=1, column=0, sticky="nsew")
        models_frame.grid_rowconfigure(0, weight=1)
        models_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview para modelos
        self.models_tree = ttk.Treeview(models_frame, columns=("status", "score"), show="tree headings", height=8)
        self.models_tree.grid(row=0, column=0, sticky="nsew")
        
        # Configurar columnas
        self.models_tree.heading("#0", text="Model", anchor="w")
        self.models_tree.heading("status", text="Status", anchor="center")
        self.models_tree.heading("score", text="Score", anchor="center")
        
        self.models_tree.column("#0", width=150, minwidth=100)
        self.models_tree.column("status", width=80, minwidth=60)
        self.models_tree.column("score", width=80, minwidth=60)
        
        # Scrollbar para modelos
        models_scroll = ttk.Scrollbar(models_frame, orient="vertical", command=self.models_tree.yview)
        models_scroll.grid(row=0, column=1, sticky="ns")
        self.models_tree.configure(yscrollcommand=models_scroll.set)
        
        # Poblar lista de modelos
        self.populate_models_list()
        
        # Botones de entrenamiento individual
        model_buttons_frame = ttk.Frame(config_frame)
        model_buttons_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        self.train_selected_btn = ttk.Button(model_buttons_frame, text="Train Selected", 
                                           command=self.train_selected_model)
        self.train_selected_btn.pack(side="left", padx=(0, 5))
        
        self.clear_results_btn = ttk.Button(model_buttons_frame, text="Clear Results", 
                                          command=self.clear_results)
        self.clear_results_btn.pack(side="left")
    
    def create_results_panel(self, parent):
        """Crear panel de resultados"""
        results_frame = ttk.LabelFrame(parent, text="Training Results", padding=10)
        results_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Configurar grid
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Métricas generales
        metrics_frame = ttk.Frame(results_frame)
        metrics_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        metrics_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(metrics_frame, text="Best Model:").grid(row=0, column=0, sticky="w")
        self.best_model_label = ttk.Label(metrics_frame, text="None", font=("TkDefaultFont", 9, "bold"))
        self.best_model_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Label(metrics_frame, text="Best Score:").grid(row=1, column=0, sticky="w")
        self.best_score_label = ttk.Label(metrics_frame, text="0.000", font=("TkDefaultFont", 9, "bold"))
        self.best_score_label.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        # Detalles de entrenamiento
        details_frame = ttk.LabelFrame(results_frame, text="Training Details", padding=5)
        details_frame.grid(row=1, column=0, sticky="nsew")
        details_frame.grid_rowconfigure(0, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        
        # Text widget para detalles
        self.details_text = tk.Text(details_frame, wrap="word", font=("Consolas", 9))
        self.details_text.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar para detalles
        details_scroll = ttk.Scrollbar(details_frame, orient="vertical", command=self.details_text.yview)
        details_scroll.grid(row=0, column=1, sticky="ns")
        self.details_text.configure(yscrollcommand=details_scroll.set)
        
        # Botones de análisis
        analysis_frame = ttk.Frame(results_frame)
        analysis_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        self.show_metrics_btn = ttk.Button(analysis_frame, text="Show Metrics", 
                                         command=self.show_detailed_metrics)
        self.show_metrics_btn.pack(side="left", padx=(0, 5))
        
        self.compare_models_btn = ttk.Button(analysis_frame, text="Compare Models", 
                                           command=self.compare_models)
        self.compare_models_btn.pack(side="left")
    
    def create_progress_section(self):
        """Crear sección de progreso"""
        progress_frame = ttk.Frame(self.frame)
        progress_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        # Configurar grid
        progress_frame.grid_columnconfigure(1, weight=1)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress_bar.grid(row=0, column=1, sticky="ew")
        
        # Botón de cancelar (inicialmente oculto)
        self.cancel_btn = ttk.Button(progress_frame, text="Cancel", command=self.cancel_training)
        self.cancel_btn.grid(row=0, column=2, sticky="e", padx=(10, 0))
        self.cancel_btn.grid_remove()
    
    def populate_models_list(self):
        """Poblar lista de modelos disponibles"""
        # Limpiar lista
        for item in self.models_tree.get_children():
            self.models_tree.delete(item)
        
        # Modelos disponibles
        models = [
            "Random Forest",
            "Gradient Boosting", 
            "SVM",
            "Logistic Regression",
            "K-Neighbors",
            "Decision Tree"
        ]
        
        # Agregar modelos al tree
        for model in models:
            self.models_tree.insert("", "end", text=model, values=("Not trained", "---"))
    
    def refresh_data(self):
        """Refrescar información del dataset"""
        try:
            if self.data_processor and hasattr(self.data_processor, 'current_data'):
                self.current_data = self.data_processor.current_data
                
                if self.current_data is not None:
                    # Actualizar información del dataset
                    self.dataset_status_label.config(text=f"Loaded ({len(self.current_data)} samples)", 
                                                    foreground="green")
                    self.samples_label.config(text=str(len(self.current_data)))
                    self.features_label.config(text=str(len(self.current_data.columns)))
                    
                    # Actualizar combobox de target
                    columns = list(self.current_data.columns)
                    self.target_combo['values'] = columns
                    
                    if columns:
                        # Seleccionar última columna por defecto
                        self.target_var.set(columns[-1])
                        self.on_target_selected()
                    
                    self.enable_training_controls()
                    self.add_details("Dataset refreshed successfully")
                    
                else:
                    self.dataset_status_label.config(text="No data loaded", foreground="red")
                    self.disable_training_controls()
            else:
                self.dataset_status_label.config(text="Data processor not available", foreground="red")
                self.disable_training_controls()
                
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            messagebox.showerror("Error", f"Error refreshing data: {str(e)}")
    
    def on_target_selected(self, event=None):
        """Callback cuando se selecciona target column"""
        if self.current_data is not None and self.target_var.get():
            target_col = self.target_var.get()
            feature_count = len(self.current_data.columns) - 1  # Excluyendo target
            self.add_details(f"Target column set to: {target_col}")
            self.add_details(f"Features available: {feature_count}")
    
    def enable_training_controls(self):
        """Habilitar controles de entrenamiento"""
        self.train_all_btn.config(state="normal")
        self.train_selected_btn.config(state="normal")
    
    def disable_training_controls(self):
        """Deshabilitar controles de entrenamiento"""
        self.train_all_btn.config(state="disabled")
        self.train_selected_btn.config(state="disabled")
        self.save_models_btn.config(state="disabled")
    
    def train_all_models(self):
        """Entrenar todos los modelos"""
        if not self.validate_training_conditions():
            return
        
        # Iniciar entrenamiento en hilo separado
        self.training_in_progress = True
        self.show_progress()
        
        training_thread = threading.Thread(target=self._train_all_models_worker)
        training_thread.daemon = True
        training_thread.start()
    
    def train_selected_model(self):
        """Entrenar modelo seleccionado"""
        selection = self.models_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model to train")
            return
        
        if not self.validate_training_conditions():
            return
        
        # Obtener modelo seleccionado
        item = selection[0]
        model_name = self.models_tree.item(item, "text")
        
        # Iniciar entrenamiento en hilo separado
        self.training_in_progress = True
        self.show_progress()
        
        training_thread = threading.Thread(target=self._train_single_model_worker, args=(model_name,))
        training_thread.daemon = True
        training_thread.start()
    
    def validate_training_conditions(self):
        """Validar condiciones para entrenamiento"""
        if self.current_data is None:
            messagebox.showerror("Error", "No data available. Please load data first.")
            return False
        
        if not self.target_var.get():
            messagebox.showerror("Error", "Please select a target column.")
            return False
        
        if self.training_in_progress:
            messagebox.showwarning("Warning", "Training already in progress.")
            return False
        
        return True
    
    def _train_all_models_worker(self):
        """Worker para entrenar todos los modelos"""
        try:
            # Preparar datos
            X, y = self.prepare_training_data()
            
            models = [
                "Random Forest",
                "Gradient Boosting", 
                "SVM",
                "Logistic Regression",
                "K-Neighbors",
                "Decision Tree"
            ]
            
            total_models = len(models)
            
            for i, model_name in enumerate(models):
                if not self.training_in_progress:  # Verificar cancelación
                    break
                
                # Actualizar progreso
                progress = (i / total_models) * 100
                self.update_progress(f"Training {model_name}...", progress)
                
                # Entrenar modelo
                result = self.train_single_model(model_name, X, y)
                
                # Actualizar interfaz en hilo principal
                self.frame.after(0, self.update_model_result, model_name, result)
            
            # Finalizar entrenamiento
            self.frame.after(0, self.training_completed)
            
        except Exception as e:
            logger.error(f"Error in training worker: {e}")
            self.frame.after(0, self.training_error, str(e))
    
    def _train_single_model_worker(self, model_name):
        """Worker para entrenar un modelo específico"""
        try:
            # Preparar datos
            X, y = self.prepare_training_data()
            
            # Actualizar progreso
            self.update_progress(f"Training {model_name}...", 50)
            
            # Entrenar modelo
            result = self.train_single_model(model_name, X, y)
            
            # Actualizar interfaz
            self.frame.after(0, self.update_model_result, model_name, result)
            self.frame.after(0, self.training_completed)
            
        except Exception as e:
            logger.error(f"Error training {model_name}: {e}")
            self.frame.after(0, self.training_error, str(e))
    
    def prepare_training_data(self):
        """Preparar datos para entrenamiento"""
        target_col = self.target_var.get()
        
        # Separar features y target
        X = self.current_data.drop(columns=[target_col])
        y = self.current_data[target_col]
        
        # Convertir a numérico si es necesario
        X = X.select_dtypes(include=[np.number])
        
        if len(X.columns) == 0:
            raise ValueError("No numeric features available for training")
        
        return X, y
    
    def train_single_model(self, model_name, X, y):
        """Entrenar un modelo específico"""
        try:
            if self.model_trainer:
                # Mapear nombres de modelos
                model_mapping = {
                    "Random Forest": "RandomForest",
                    "Gradient Boosting": "GradientBoosting",
                    "SVM": "SVM",
                    "Logistic Regression": "LogisticRegression", 
                    "K-Neighbors": "KNeighbors",
                    "Decision Tree": "DecisionTree"
                }
                
                sklearn_name = model_mapping.get(model_name, model_name)
                score = self.model_trainer.train_model(X, y, sklearn_name)
                
                # Guardar modelo entrenado
                self.trained_models[model_name] = {
                    'model': self.model_trainer.model,
                    'score': score,
                    'features': list(X.columns)
                }
                
                return {'success': True, 'score': score}
            else:
                return {'success': False, 'error': 'Model trainer not available'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_model_result(self, model_name, result):
        """Actualizar resultado de modelo en la interfaz"""
        # Encontrar item en el tree
        for item in self.models_tree.get_children():
            if self.models_tree.item(item, "text") == model_name:
                if result['success']:
                    score = f"{result['score']:.3f}"
                    self.models_tree.item(item, values=("Trained", score))
                    self.add_details(f"{model_name}: Score = {score}")
                else:
                    self.models_tree.item(item, values=("Error", "---"))
                    self.add_details(f"{model_name}: Error - {result['error']}")
                break
        
        # Actualizar mejor modelo
        self.update_best_model()
    
    def update_best_model(self):
        """Actualizar información del mejor modelo"""
        if not self.trained_models:
            return
        
        # Encontrar mejor modelo
        best_model = max(self.trained_models.items(), key=lambda x: x[1]['score'])
        best_name, best_info = best_model
        
        self.best_model_label.config(text=best_name)
        self.best_score_label.config(text=f"{best_info['score']:.3f}")
        
        # Habilitar botón de guardar
        self.save_models_btn.config(state="normal")
    
    def show_progress(self):
        """Mostrar controles de progreso"""
        self.cancel_btn.grid()
        self.disable_training_controls()
    
    def hide_progress(self):
        """Ocultar controles de progreso"""
        self.cancel_btn.grid_remove()
        self.progress_bar['value'] = 0
        self.status_label.config(text="Ready")
        self.enable_training_controls()
    
    def update_progress(self, status, progress):
        """Actualizar progreso"""
        self.frame.after(0, lambda: self.status_label.config(text=status))
        self.frame.after(0, lambda: self.progress_bar.config(value=progress))
    
    def training_completed(self):
        """Callback cuando se completa el entrenamiento"""
        self.training_in_progress = False
        self.hide_progress()
        self.add_details("Training completed successfully")
        
        # Notificar callback si existe
        if self.model_trained_callback and self.trained_models:
            best_model = max(self.trained_models.items(), key=lambda x: x[1]['score'])
            self.model_trained_callback(best_model[1]['model'])
    
    def training_error(self, error_msg):
        """Callback cuando hay error en entrenamiento"""
        self.training_in_progress = False
        self.hide_progress()
        self.add_details(f"Training error: {error_msg}")
        messagebox.showerror("Training Error", f"An error occurred during training:\n{error_msg}")
    
    def cancel_training(self):
        """Cancelar entrenamiento"""
        self.training_in_progress = False
        self.hide_progress()
        self.add_details("Training cancelled by user")
    
    def clear_results(self):
        """Limpiar resultados de entrenamiento"""
        # Limpiar modelos entrenados
        self.trained_models.clear()
        
        # Resetear tree
        self.populate_models_list()
        
        # Resetear labels
        self.best_model_label.config(text="None")
        self.best_score_label.config(text="0.000")
        
        # Limpiar detalles
        self.details_text.delete(1.0, tk.END)
        
        # Deshabilitar botón de guardar
        self.save_models_btn.config(state="disabled")
        
        self.add_details("Results cleared")
    
    def save_best_model(self):
        """Guardar el mejor modelo"""
        if not self.trained_models:
            messagebox.showwarning("Warning", "No trained models available")
            return
        
        # Obtener mejor modelo
        best_model = max(self.trained_models.items(), key=lambda x: x[1]['score'])
        best_name, best_info = best_model
        
        # Diálogo para guardar
        file_path = filedialog.asksaveasfilename(
            title="Save Best Model",
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
            initialvalue=f"best_model_{best_name.replace(' ', '_').lower()}.pkl"
        )
        
        if file_path:
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(best_info['model'], f)
                
                self.add_details(f"Best model ({best_name}) saved to: {file_path}")
                messagebox.showinfo("Success", f"Model saved successfully!\n\nModel: {best_name}\nScore: {best_info['score']:.3f}")
                
            except Exception as e:
                logger.error(f"Error saving model: {e}")
                messagebox.showerror("Error", f"Error saving model: {str(e)}")
    
    def show_detailed_metrics(self):
        """Mostrar métricas detalladas"""
        if not self.trained_models:
            messagebox.showwarning("Warning", "No trained models available")
            return
        
        # Crear ventana de métricas
        metrics_window = tk.Toplevel(self.frame)
        metrics_window.title("Model Metrics")
        metrics_window.geometry("600x400")
        
        # Text widget para métricas
        text_widget = tk.Text(metrics_window, wrap="word", font=("Consolas", 10))
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(metrics_window, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Generar contenido de métricas
        content = "MODEL TRAINING METRICS\n"
        content += "=" * 50 + "\n\n"
        
        for model_name, model_info in self.trained_models.items():
            content += f"Model: {model_name}\n"
            content += f"Score: {model_info['score']:.4f}\n"
            content += f"Features: {len(model_info['features'])}\n"
            content += f"Feature List: {', '.join(model_info['features'][:5])}{'...' if len(model_info['features']) > 5 else ''}\n"
            content += "-" * 30 + "\n"
        
        # Mejor modelo
        if self.trained_models:
            best_model = max(self.trained_models.items(), key=lambda x: x[1]['score'])
            content += f"\nBEST MODEL\n"
            content += "=" * 20 + "\n"
            content += f"Model: {best_model[0]}\n"
            content += f"Score: {best_model[1]['score']:.4f}\n"
        
        text_widget.insert(1.0, content)
        text_widget.config(state="disabled")
    
    def compare_models(self):
        """Comparar modelos entrenados"""
        if len(self.trained_models) < 2:
            messagebox.showwarning("Warning", "Need at least 2 trained models for comparison")
            return
        
        # Crear ventana de comparación
        comparison_window = tk.Toplevel(self.frame)
        comparison_window.title("Model Comparison")
        comparison_window.geometry("800x600")
        
        # Crear notebook para diferentes vistas
        notebook = ttk.Notebook(comparison_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab de tabla de comparación
        table_frame = ttk.Frame(notebook)
        notebook.add(table_frame, text="Comparison Table")
        
        # Treeview para comparación
        tree = ttk.Treeview(table_frame, columns=("score", "features"), show="tree headings")
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        tree.heading("#0", text="Model", anchor="w")
        tree.heading("score", text="Score", anchor="center")
        tree.heading("features", text="Features", anchor="center")
        
        tree.column("#0", width=200)
        tree.column("score", width=100)
        tree.column("features", width=100)
        
        # Poblar tabla ordenada por score
        sorted_models = sorted(self.trained_models.items(), key=lambda x: x[1]['score'], reverse=True)
        for i, (name, info) in enumerate(sorted_models):
            rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            tree.insert("", "end", text=f"{rank} {name}", 
                       values=(f"{info['score']:.4f}", len(info['features'])))
        
        # Tab de gráfico (placeholder)
        chart_frame = ttk.Frame(notebook)
        notebook.add(chart_frame, text="Performance Chart")
        
        chart_label = ttk.Label(chart_frame, text="Performance visualization would go here", 
                               anchor="center")
        chart_label.pack(expand=True)
    
    def add_details(self, message):
        """Agregar mensaje a los detalles"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.details_text.insert(tk.END, formatted_message)
        self.details_text.see(tk.END)
    
    def get_frame(self):
        """Obtener el frame principal del tab"""
        return self.frame
    
    def reset(self):
        """Resetear el tab"""
        self.current_data = None
        self.trained_models.clear()
        self.training_in_progress = False
        
        # Resetear interfaz
        self.dataset_status_label.config(text="No data loaded", foreground="red")
        self.samples_label.config(text="0")
        self.features_label.config(text="0")
        self.target_combo['values'] = []
        self.target_var.set("")
        
        self.populate_models_list()
        self.best_model_label.config(text="None")
        self.best_score_label.config(text="0.000")
        self.details_text.delete(1.0, tk.END)
        
        self.disable_training_controls()
        self.hide_progress()
        
        logger.info("TrainingTab reset")
    
    def on_data_updated(self, data):
        """Callback cuando se actualizan los datos"""
        self.current_data = data
        self.refresh_data()
    
    def get_training_status(self):
        """Obtener estado del entrenamiento"""
        return {
            'has_data': self.current_data is not None,
            'models_trained': len(self.trained_models),
            'training_in_progress': self.training_in_progress,
            'best_model': max(self.trained_models.items(), key=lambda x: x[1]['score'])[0] if self.trained_models else None,
            'best_score': max(self.trained_models.values(), key=lambda x: x['score'])['score'] if self.trained_models else 0
        }


# Función de utilidad para crear el tab
def create_training_tab(parent, model_trainer, data_processor, callback=None):
    """
    Factory function para crear TrainingTab
    
    Args:
        parent: Widget padre
        model_trainer: Instancia del entrenador
        data_processor: Instancia del procesador de datos
        callback: Callback opcional cuando se entrena un modelo
        
    Returns:
        Instancia de TrainingTab
    """
    return TrainingTab(parent, model_trainer, data_processor, callback)