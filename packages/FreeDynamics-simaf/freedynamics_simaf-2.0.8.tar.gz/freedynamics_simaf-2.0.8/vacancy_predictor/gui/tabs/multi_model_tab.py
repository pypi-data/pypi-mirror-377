"""
Multi-Model ML Tab - Complete implementation
Archivo: vacancy_predictor/tabs/multi_model_tab.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import pandas as pd
import numpy as np
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.model_selection import train_test_split
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class MultiModelTab:
    """Multi-Model ML tab for model comparison and training"""
    
    def __init__(self, parent, data_loaded_callback, processor=None):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        self.processor = processor
        
        self.frame = ttk.Frame(parent)
        
        # Data
        self.current_data = None
        self.feature_columns = []
        self.target_column = 'vacancies'
        
        # Training state
        self.training_in_progress = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create main interface"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Create notebook for sections
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        self.create_data_tab()
        self.create_training_tab()
        self.create_results_tab()
    
    def create_data_tab(self):
        """Data configuration tab"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Datos")
        
        # Data info
        info_frame = ttk.LabelFrame(data_frame, text="Información del Dataset", padding="10")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.data_info_text = scrolledtext.ScrolledText(info_frame, height=8, wrap='word')
        self.data_info_text.pack(fill="both", expand=True)
        
        # Feature selection
        features_frame = ttk.LabelFrame(data_frame, text="Selección de Features", padding="10")
        features_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Target selection
        target_frame = ttk.Frame(features_frame)
        target_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(target_frame, text="Columna Target:").pack(side="left")
        self.target_combo = ttk.Combobox(target_frame, state="readonly", width=20)
        self.target_combo.pack(side="left", padx=(10, 0))
        self.target_combo.bind('<<ComboboxSelected>>', self.on_target_change)
        
        # Features listbox
        listbox_frame = ttk.Frame(features_frame)
        listbox_frame.pack(fill="both", expand=True)
        
        self.features_listbox = tk.Listbox(listbox_frame, selectmode=tk.EXTENDED)
        features_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", 
                                         command=self.features_listbox.yview)
        self.features_listbox.configure(yscrollcommand=features_scrollbar.set)
        
        self.features_listbox.pack(side="left", fill="both", expand=True)
        features_scrollbar.pack(side="right", fill="y")
        
        # Selection buttons
        buttons_frame = ttk.Frame(features_frame)
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Seleccionar Todo", 
                  command=self.select_all_features).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Auto-Seleccionar (Top 30)", 
                  command=self.auto_select_features).pack(side="left", padx=5)
    
    def create_training_tab(self):
        """Training configuration and execution"""
        training_frame = ttk.Frame(self.notebook)
        self.notebook.add(training_frame, text="🚀 Entrenamiento")
        
        # Model selection
        models_frame = ttk.LabelFrame(training_frame, text="Modelos Disponibles", padding="10")
        models_frame.pack(fill="x", padx=10, pady=5)
        
        self.model_vars = {}
        if self.processor:
            available_models = self.processor.get_available_models()
            for model_key, model_name in available_models.items():
                var = tk.BooleanVar(value=True)
                self.model_vars[model_key] = var
                ttk.Checkbutton(models_frame, text=model_name, 
                              variable=var).pack(anchor="w")
        else:
            # Fallback si no hay processor
            ttk.Label(models_frame, text="Procesador multi-modelo no disponible").pack()
        
        # Training options
        options_frame = ttk.LabelFrame(training_frame, text="Opciones de Entrenamiento", padding="10")
        options_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid search option
        self.use_grid_search_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Usar Grid Search (recomendado)", 
                       variable=self.use_grid_search_var).pack(anchor="w")
        
        # Test size
        test_frame = ttk.Frame(options_frame)
        test_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(test_frame, text="Tamaño de prueba:").pack(side="left")
        self.test_size_var = tk.DoubleVar(value=0.2)
        test_scale = ttk.Scale(test_frame, from_=0.1, to=0.4, orient=tk.HORIZONTAL, 
                              variable=self.test_size_var, length=200)
        test_scale.pack(side="left", padx=(10, 5))
        
        self.test_size_label = ttk.Label(test_frame, text="20%")
        self.test_size_label.pack(side="left")
        test_scale.configure(command=self.update_test_size_label)
        
        # Training controls
        controls_frame = ttk.LabelFrame(training_frame, text="Control", padding="10")
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill="x")
        
        self.train_button = ttk.Button(button_frame, text="🚀 Entrenar Modelos", 
                                      command=self.start_training)
        self.train_button.pack(side="left", padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Detener", 
                                     command=self.stop_training, state="disabled")
        self.stop_button.pack(side="left", padx=5)
        
        # Progress
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
        self.training_log = scrolledtext.ScrolledText(progress_frame, height=10, wrap='word')
        self.training_log.pack(fill="both", expand=True, pady=(10, 0))
    
    def create_results_tab(self):
        """Results and visualization"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📈 Resultados")
        
        # Results table
        table_frame = ttk.LabelFrame(results_frame, text="Comparación de Modelos", padding="10")
        table_frame.pack(fill="x", padx=10, pady=5)
        
        columns = ('Modelo', 'MAE', 'RMSE', 'R²', 'MAPE (%)')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100, anchor='center')
        
        results_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", 
                                        command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side="left", fill="x", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Best model info
        best_frame = ttk.LabelFrame(results_frame, text="Mejor Modelo", padding="10")
        best_frame.pack(fill="x", padx=10, pady=5)
        
        self.best_model_text = tk.Text(best_frame, height=4, wrap='word', state='disabled')
        self.best_model_text.pack(fill="x")
        
        # Visualization
        viz_frame = ttk.LabelFrame(results_frame, text="Visualización", padding="10")
        viz_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Viz controls
        viz_controls = ttk.Frame(viz_frame)
        viz_controls.pack(fill="x", pady=(0, 10))
        
        ttk.Button(viz_controls, text="📊 Comparar Modelos", 
                  command=self.plot_comparison).pack(side="left", padx=5)
        ttk.Button(viz_controls, text="🎯 Predicciones", 
                  command=self.plot_predictions).pack(side="left", padx=5)
        ttk.Button(viz_controls, text="💾 Exportar Modelos", 
                  command=self.export_models).pack(side="right", padx=5)
        
        # Plot canvas
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    # Data methods
    def load_dataset_from_dataframe(self, data):
        """Load dataset from DataFrame"""
        self.current_data = data.copy()
        self.update_data_info()
        self.update_feature_list()
        self.update_target_combo()
        
        # Switch to data tab
        self.notebook.select(0)
    
    def update_data_info(self):
        """Update data info display"""
        if self.current_data is None:
            return
        
        info_text = f"""Dataset cargado exitosamente:

• Filas: {len(self.current_data):,}
• Columnas: {len(self.current_data.columns)}
• Memoria: {self.current_data.memory_usage(deep=True).sum() / 1024**2:.1f} MB
• Valores faltantes: {self.current_data.isnull().sum().sum():,}

Tipos de datos:
• Numéricos: {len(self.current_data.select_dtypes(include=[np.number]).columns)}
• Categóricos: {len(self.current_data.select_dtypes(include=['object']).columns)}

Estado: ✅ Listo para seleccionar features y entrenar modelos
"""
        
        self.data_info_text.delete(1.0, tk.END)
        self.data_info_text.insert(1.0, info_text)
    
    def update_feature_list(self):
        """Update features listbox"""
        self.features_listbox.delete(0, tk.END)
        
        if self.current_data is None:
            return
        
        # Exclude non-feature columns
        exclude_cols = ['file_path', 'filename', 'vacancies', 'file']
        feature_candidates = [col for col in self.current_data.columns if col not in exclude_cols]
        
        for feature in sorted(feature_candidates):
            self.features_listbox.insert(tk.END, feature)
    
    def update_target_combo(self):
        """Update target combobox"""
        if self.current_data is None:
            return
        
        target_candidates = [col for col in self.current_data.columns if 'vacan' in col.lower()]
        if not target_candidates:
            target_candidates = ['vacancies'] if 'vacancies' in self.current_data.columns else []
        
        self.target_combo['values'] = target_candidates
        if target_candidates:
            self.target_combo.set(target_candidates[0])
            self.target_column = target_candidates[0]
    
    def on_target_change(self, event):
        """Handle target change"""
        self.target_column = self.target_combo.get()
    
    def select_all_features(self):
        """Select all features"""
        self.features_listbox.select_set(0, tk.END)
    
    def auto_select_features(self):
        """Auto-select top correlated features"""
        if self.current_data is None or self.target_column not in self.current_data.columns:
            messagebox.showwarning("Advertencia", "Configure target primero")
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
            
            # Select top 30
            sorted_features = sorted(correlations.items(), key=lambda x: x[1], reverse=True)[:30]
            top_features = [feat for feat, _ in sorted_features]
            
            # Update selection
            self.features_listbox.selection_clear(0, tk.END)
            for i in range(self.features_listbox.size()):
                if self.features_listbox.get(i) in top_features:
                    self.features_listbox.select_set(i)
            
            messagebox.showinfo("Éxito", f"Seleccionadas {len(top_features)} features por correlación")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en selección: {str(e)}")
    
    def update_test_size_label(self, value):
        """Update test size label"""
        percentage = int(float(value) * 100)
        self.test_size_label.config(text=f"{percentage}%")
    
    # Training methods
    def start_training(self):
        """Start training"""
        if self.training_in_progress:
            return
        
        if self.current_data is None:
            messagebox.showerror("Error", "No hay datos cargados")
            return
        
        if not self.processor:
            messagebox.showerror("Error", "Procesador multi-modelo no disponible")
            return
        
        selected_indices = self.features_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Seleccione features")
            return
        
        selected_models = [name for name, var in self.model_vars.items() if var.get()]
        if not selected_models:
            messagebox.showerror("Error", "Seleccione modelos")
            return
        
        self.feature_columns = [self.features_listbox.get(i) for i in selected_indices]
        
        # Start training thread
        self.training_in_progress = True
        self.train_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        thread = threading.Thread(target=self._training_worker, args=(selected_models,), daemon=True)
        thread.start()
    
    def _training_worker(self, selected_models):
        """Training worker thread"""
        try:
            self._log_message("=== INICIANDO ENTRENAMIENTO MULTI-MODELO ===")
            
            # Prepare data
            X = self.current_data[self.feature_columns]
            y = self.current_data[self.target_column]
            
            self._log_message(f"Features: {len(self.feature_columns)}")
            self._log_message(f"Muestras: {len(X)}")
            
            # Split data
            test_size = self.test_size_var.get()
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
            
            use_grid_search = self.use_grid_search_var.get()
            total_models = len(selected_models)
            
            for i, model_name in enumerate(selected_models):
                if not self.training_in_progress:
                    break
                
                progress = (i / total_models) * 90
                self._update_progress(progress, f"Entrenando {model_name}...")
                
                self._log_message(f"\n--- {model_name.upper()} ---")
                
                try:
                    if model_name == 'random_forest':
                        self.processor.train_random_forest(X_train, y_train, use_grid_search=use_grid_search)
                    elif model_name == 'xgboost':
                        self.processor.train_xgboost(X_train, y_train, use_grid_search=use_grid_search)
                    elif model_name == 'neural_network':
                        X_train_nn, X_val, y_train_nn, y_val = train_test_split(
                            X_train, y_train, test_size=0.2, random_state=42
                        )
                        self.processor.train_neural_network(X_train_nn, y_train_nn, X_val, y_val)
                    
                    self._log_message(f"✓ {model_name} entrenado exitosamente")
                    
                except Exception as e:
                    self._log_message(f"✗ Error en {model_name}: {str(e)}")
                    logger.error(f"Training error for {model_name}: {str(e)}")
            
            # Evaluate models
            if self.training_in_progress:
                self._update_progress(90, "Evaluando modelos...")
                self._log_message("\n--- EVALUACIÓN ---")
                
                for model_name in self.processor.models.keys():
                    try:
                        results = self.processor.evaluate_model(model_name, X_test, y_test)
                        self._log_message(f"{model_name}: MAE={results['mae']:.4f}, R²={results['r2']:.4f}")
                    except Exception as e:
                        self._log_message(f"Error evaluando {model_name}: {str(e)}")
                
                # Update UI
                self.frame.after(0, self._update_results_display)
            
            self._update_progress(100, "Entrenamiento completado")
            self._log_message("\n=== COMPLETADO ===")
            
        except Exception as e:
            self._log_message(f"ERROR: {str(e)}")
            logger.error(f"Training error: {str(e)}")
            
        finally:
            self.frame.after(0, self._reset_training_state)
    
    def stop_training(self):
        """Stop training"""
        self.training_in_progress = False
        self._log_message("Deteniendo...")
    
    def _reset_training_state(self):
        """Reset training state"""
        self.training_in_progress = False
        self.train_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Listo")
    
    def _update_progress(self, value, message):
        """Update progress"""
        self.progress_var.set(value)
        self.status_var.set(message)
    
    def _log_message(self, message):
        """Log message"""
        self.training_log.insert(tk.END, f"{message}\n")
        self.training_log.see(tk.END)
    
    def _update_results_display(self):
        """Update results display"""
        if not self.processor or not self.processor.model_results:
            return
        
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Add results
        for model_name, results in self.processor.model_results.items():
            if 'error' not in results:
                model_display = self.processor.available_models.get(model_name, model_name)
                self.results_tree.insert('', 'end', values=(
                    model_display,
                    f"{results['mae']:.4f}",
                    f"{results['rmse']:.4f}",
                    f"{results['r2']:.4f}",
                    f"{results['mape']:.2f}"
                ))
        
        # Update best model
        try:
            best_model_name, best_results = self.processor.get_best_model('r2')
            best_display = self.processor.available_models.get(best_model_name, best_model_name)
            
            best_text = f"""Mejor Modelo: {best_display}
R² Score: {best_results['r2']:.4f}
MAE: {best_results['mae']:.4f}
RMSE: {best_results['rmse']:.4f}
MAPE: {best_results['mape']:.2f}%"""
            
            self.best_model_text.config(state='normal')
            self.best_model_text.delete(1.0, tk.END)
            self.best_model_text.insert(1.0, best_text)
            self.best_model_text.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Error updating best model: {str(e)}")
        
        # Switch to results tab
        self.notebook.select(2)
    
    # Visualization methods
    def plot_comparison(self):
        """Plot model comparison"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados")
            return
        
        try:
            self.ax.clear()
            
            models = []
            r2_scores = []
            mae_scores = []
            
            for model_name, results in self.processor.model_results.items():
                if 'error' not in results:
                    models.append(self.processor.available_models.get(model_name, model_name))
                    r2_scores.append(results['r2'])
                    mae_scores.append(results['mae'])
            
            if not models:
                self.ax.text(0.5, 0.5, 'No hay resultados', ha='center', va='center')
                self.canvas.draw()
                return
            
            # Create bar plot
            x = np.arange(len(models))
            width = 0.35
            
            bars1 = self.ax.bar(x - width/2, r2_scores, width, label='R² Score', alpha=0.8)
            
            # Normalize MAE for display (invert so higher is better)
            if mae_scores:
                max_mae = max(mae_scores)
                mae_norm = [(max_mae - mae) / max_mae for mae in mae_scores]
                bars2 = self.ax.bar(x + width/2, mae_norm, width, label='MAE (norm.)', alpha=0.8)
            
            self.ax.set_xlabel('Modelos')
            self.ax.set_ylabel('Puntuación')
            self.ax.set_title('Comparación de Modelos')
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(models, rotation=45, ha='right')
            self.ax.legend()
            self.ax.grid(True, alpha=0.3)
            
            # Add value labels
            for bar, value in zip(bars1, r2_scores):
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{value:.3f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en gráfico: {str(e)}")
    
    def plot_predictions(self):
        """Plot predictions vs actual"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados")
            return
        
        try:
            self.ax.clear()
            
            best_model_name, best_results = self.processor.get_best_model('r2')
            
            y_true = best_results['actual']
            y_pred = best_results['predictions']
            
            # Scatter plot
            self.ax.scatter(y_true, y_pred, alpha=0.6, s=50)
            
            # Perfect line
            min_val = min(y_true.min(), y_pred.min())
            max_val = max(y_true.max(), y_pred.max())
            self.ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2)
            
            self.ax.set_xlabel('Valores Reales')
            self.ax.set_ylabel('Predicciones')
            self.ax.set_title(f'Predicciones vs Reales - {self.processor.available_models.get(best_model_name, best_model_name)}')
            self.ax.grid(True, alpha=0.3)
            
            # Add metrics
            r2 = best_results['r2']
            mae = best_results['mae']
            self.ax.text(0.05, 0.95, f'R² = {r2:.3f}\nMAE = {mae:.3f}', 
                        transform=self.ax.transAxes, 
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                        verticalalignment='top')
            
            plt.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en gráfico: {str(e)}")
    
    def export_models(self):
        """Export trained models"""
        if not self.processor or not self.processor.models:
            messagebox.showwarning("Advertencia", "No hay modelos entrenados")
            return
        
        try:
            directory = filedialog.askdirectory(title="Seleccionar directorio para exportar")
            
            if directory:
                self.processor.save_models(directory)
                messagebox.showinfo("Éxito", f"Modelos exportados a: {directory}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando: {str(e)}")
    
    def reset(self):
        """Reset tab"""
        self.current_data = None
        self.feature_columns = []
        self.target_column = 'vacancies'
        
        if hasattr(self, 'data_info_text'):
            self.data_info_text.delete(1.0, tk.END)
        if hasattr(self, 'features_listbox'):
            self.features_listbox.delete(0, tk.END)
        if hasattr(self, 'target_combo'):
            self.target_combo.set('')
        
        self._reset_training_state()