"""
Multi-Model ML Tab para Vacancy Predictor - VERSIÓN MEJORADA
Archivo: vacancy_predictor/gui/tabs/multi_model_tab.py

Incluye gráficos comparativos completamente funcionales
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import pandas as pd
import numpy as np
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
from sklearn.model_selection import train_test_split
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MultiModelTab:
    """Multi-Model ML tab con gráficos comparativos completos"""
    
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
        
        # Plot variables
        self.plot_figure = None
        self.plot_canvas = None
        
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
        self.create_visualization_tab()  # Nueva pestaña de visualización
    
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
        
        # Features list
        ttk.Label(features_frame, text="Features disponibles:").pack(anchor="w", pady=(10, 5))
        
        features_container = ttk.Frame(features_frame)
        features_container.pack(fill="both", expand=True)
        
        self.features_listbox = tk.Listbox(features_container, selectmode="extended", height=10)
        scrollbar = ttk.Scrollbar(features_container, orient="vertical", command=self.features_listbox.yview)
        self.features_listbox.config(yscrollcommand=scrollbar.set)
        
        self.features_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        buttons_frame = ttk.Frame(data_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Cargar Datos", 
                  command=self.load_data).pack(side="left", padx=(0, 10))
        ttk.Button(buttons_frame, text="Actualizar Features", 
                  command=self.update_features).pack(side="left")
    
    def create_training_tab(self):
        """Training configuration tab"""
        training_frame = ttk.Frame(self.notebook)
        self.notebook.add(training_frame, text="🔧 Entrenamiento")
        
        # Training configuration
        config_frame = ttk.LabelFrame(training_frame, text="Configuración de Entrenamiento", padding="10")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # Model selection
        model_frame = ttk.Frame(config_frame)
        model_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(model_frame, text="Modelos a entrenar:").pack(anchor="w")
        
        self.model_vars = {}
        if self.processor:
            # Solo mostrar modelos realmente disponibles
            for model_name, display_name in self.processor.available_models.items():
                var = tk.BooleanVar(value=True)
                self.model_vars[model_name] = var
                ttk.Checkbutton(model_frame, text=display_name, variable=var).pack(anchor="w")
            
            # Mostrar información de dependencias
            if hasattr(self.processor, 'get_available_models_info'):
                info = self.processor.get_available_models_info()
                if info['total_available'] < 3:  # Si no están todos disponibles
                    info_text = "Modelos disponibles actualmente. Para más opciones:\n"
                    for model, dep_info in info['dependencies'].items():
                        if "✗" in dep_info:
                            if "xgboost" in dep_info:
                                info_text += "• pip install xgboost\n"
                            elif "tensorflow" in dep_info:
                                info_text += "• pip install tensorflow\n"
                    
                    if "pip install" in info_text:
                        info_label = ttk.Label(model_frame, text=info_text, 
                                             font=('Arial', 9), foreground='gray')
                        info_label.pack(anchor="w", pady=(5, 0))
        else:
            ttk.Label(model_frame, text="MultiModelProcessor no disponible", 
                     foreground='red').pack(anchor="w")
        
        # Training parameters
        params_frame = ttk.Frame(config_frame)
        params_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(params_frame, text="Test Size:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.test_size_var = tk.DoubleVar(value=0.2)
        ttk.Scale(params_frame, from_=0.1, to=0.4, variable=self.test_size_var, 
                 orient="horizontal", length=200).grid(row=0, column=1, sticky="ew")
        self.test_size_label = ttk.Label(params_frame, text="0.20")
        self.test_size_label.grid(row=0, column=2, padx=(10, 0))
        
        self.test_size_var.trace('w', self.update_test_size_label)
        
        ttk.Label(params_frame, text="Grid Search:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.grid_search_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(params_frame, variable=self.grid_search_var).grid(row=1, column=1, sticky="w", pady=(10, 0))
        
        params_frame.columnconfigure(1, weight=1)
        
        # Training controls
        controls_frame = ttk.Frame(training_frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        self.train_button = ttk.Button(controls_frame, text="Entrenar Modelos", 
                                      command=self.start_training, state="disabled")
        self.train_button.pack(side="left", padx=(0, 10))
        
        self.progress_var = tk.StringVar(value="Listo")
        self.progress_label = ttk.Label(controls_frame, textvariable=self.progress_var)
        self.progress_label.pack(side="left")
        
        # Training log
        log_frame = ttk.LabelFrame(training_frame, text="Log de Entrenamiento", padding="10")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.training_log = scrolledtext.ScrolledText(log_frame, height=12, wrap='word')
        self.training_log.pack(fill="both", expand=True)
    
    def create_results_tab(self):
        """Results display tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📈 Resultados")
        
        # Results table
        table_frame = ttk.LabelFrame(results_frame, text="Comparación de Modelos", padding="10")
        table_frame.pack(fill="x", padx=10, pady=5)
        
        # Treeview for results
        columns = ('Modelo', 'MAE', 'RMSE', 'R²', 'MAPE')
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100, anchor="center")
        
        results_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.config(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Best model info
        best_frame = ttk.LabelFrame(results_frame, text="Mejor Modelo", padding="10")
        best_frame.pack(fill="x", padx=10, pady=5)
        
        self.best_model_text = scrolledtext.ScrolledText(best_frame, height=6, wrap='word')
        self.best_model_text.pack(fill="both", expand=True)
        
        # Export buttons
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(export_frame, text="Exportar Resultados", 
                  command=self.export_results).pack(side="left", padx=(0, 10))
        ttk.Button(export_frame, text="Guardar Mejor Modelo", 
                  command=self.save_best_model).pack(side="left")
    
    def create_visualization_tab(self):
        """Nueva pestaña de visualización mejorada"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="📊 Visualizaciones")
        
        # Control panel
        control_frame = ttk.Frame(viz_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="Comparación de Métricas", 
                  command=self.plot_metrics_comparison).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Predicciones vs Reales", 
                  command=self.plot_predictions_comparison).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Distribución de Errores", 
                  command=self.plot_error_distribution).pack(side="left", padx=(0, 10))
        ttk.Button(control_frame, text="Análisis de Residuos", 
                  command=self.plot_residuals_analysis).pack(side="left")
        
        # Plot area
        plot_frame = ttk.Frame(viz_frame)
        plot_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create matplotlib figure
        self.plot_figure = Figure(figsize=(12, 8), dpi=100)
        self.plot_canvas = FigureCanvasTkAgg(self.plot_figure, plot_frame)
        self.plot_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Navigation toolbar
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(self.plot_canvas, plot_frame)
        toolbar.update()
    
    def update_test_size_label(self, *args):
        """Update test size label"""
        self.test_size_label.config(text=f"{self.test_size_var.get():.2f}")
        
    def load_data(self):
        """Abrir cuadro de diálogo para cargar datos CSV"""
        try:
            filename = filedialog.askopenfilename(
                title="Seleccionar archivo CSV",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
            )
            if not filename:
                return  # Usuario canceló

            self.current_data = pd.read_csv(filename)

            if self.current_data is not None:
                self.update_data_info()
                self.populate_feature_lists()
                self.train_button.config(state="normal")
                messagebox.showinfo("Éxito", f"Datos cargados desde:\n{filename}")
            else:
                messagebox.showwarning("Advertencia", "No se pudieron cargar los datos")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")
        
    def update_data_info(self):
        """Update data information display"""
        if self.current_data is None:
            return
        
        info = f"""Dataset cargado exitosamente:
• Filas: {len(self.current_data):,}
• Columnas: {len(self.current_data.columns)}
• Memoria: {self.current_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB

Columnas disponibles:
{', '.join(self.current_data.columns.tolist())}

Tipos de datos:
{self.current_data.dtypes.value_counts().to_string()}

Valores faltantes por columna:
{self.current_data.isnull().sum().sort_values(ascending=False).head(10).to_string()}
"""
        
        self.data_info_text.delete(1.0, tk.END)
        self.data_info_text.insert(1.0, info)
    
    def populate_feature_lists(self):
        """Populate feature selection lists"""
        if self.current_data is None:
            return
        
        # Target combo
        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
        self.target_combo['values'] = numeric_columns
        
        if 'vacancies' in numeric_columns:
            self.target_combo.set('vacancies')
        elif numeric_columns:
            self.target_combo.set(numeric_columns[0])
        
        # Features listbox
        self.features_listbox.delete(0, tk.END)
        for col in self.current_data.columns:
            if col != self.target_combo.get():
                self.features_listbox.insert(tk.END, col)
        
        # Select all by default
        self.features_listbox.select_set(0, tk.END)
    
    def update_features(self):
        """Update feature selection"""
        target = self.target_combo.get()
        if not target:
            messagebox.showwarning("Advertencia", "Seleccione una columna target")
            return
        
        self.target_column = target
        selected_indices = self.features_listbox.curselection()
        self.feature_columns = [self.features_listbox.get(i) for i in selected_indices]
        
        if not self.feature_columns:
            messagebox.showwarning("Advertencia", "Seleccione al menos una feature")
            return
        
        self.log_training(f"Target: {self.target_column}")
        self.log_training(f"Features seleccionadas: {len(self.feature_columns)}")
    
    def start_training(self):
        """Start model training in background thread"""
        if self.training_in_progress:
            return
        
        if not self.feature_columns:
            self.update_features()
        
        if not self.feature_columns or not self.target_column:
            messagebox.showwarning("Advertencia", "Configure las features y target")
            return
        
        # Get selected models
        selected_models = [name for name, var in self.model_vars.items() if var.get()]
        if not selected_models:
            messagebox.showwarning("Advertencia", "Seleccione al menos un modelo")
            return
        
        self.training_in_progress = True
        self.train_button.config(state="disabled")
        self.progress_var.set("Entrenando...")
        
        # Start training thread
        thread = threading.Thread(target=self.train_models, args=(selected_models,))
        thread.daemon = True
        thread.start()
    
    def train_models(self, selected_models):
        """Train selected models"""
        try:
            if not self.processor:
                raise Exception("MultiModelProcessor no disponible")
            
            self.log_training("Iniciando entrenamiento de modelos...")
            
            # Prepare data
            X = self.current_data[self.feature_columns].copy()
            y = self.current_data[self.target_column].copy()
            
            self.log_training(f"Datos preparados: {X.shape[0]} muestras, {X.shape[1]} features")
            
            # Train models
            results = self.processor.train_all_models(
                X, y,
                test_size=self.test_size_var.get(),
                models_to_train=selected_models,
                use_grid_search=self.grid_search_var.get()
            )
            
            # Update UI in main thread
            self.parent.after(0, self.training_completed, results)
            
        except Exception as e:
            self.parent.after(0, self.training_failed, str(e))
    
    def training_completed(self, results):
        """Handle training completion"""
        self.training_in_progress = False
        self.train_button.config(state="normal")
        self.progress_var.set("Entrenamiento completado")
        
        self.log_training("Entrenamiento completado exitosamente")
        self.update_results_display()
        
        # Switch to results tab
        self.notebook.select(2)
    
    def training_failed(self, error_message):
        """Handle training failure"""
        self.training_in_progress = False
        self.train_button.config(state="normal")
        self.progress_var.set("Error en entrenamiento")
        
        self.log_training(f"Error: {error_message}")
        messagebox.showerror("Error", f"Error durante el entrenamiento:\n{error_message}")
    
    def log_training(self, message):
        """Add message to training log"""
        self.training_log.insert(tk.END, f"{message}\n")
        self.training_log.see(tk.END)
    
    def update_results_display(self):
        """Update results table and best model info"""
        if not self.processor or not self.processor.model_results:
            return
        
        try:
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
                        f"{results['mape']:.2f}%"
                    ))
            
            # Update best model
            try:
                best_model_name, best_results = self.processor.get_best_model('r2')
                best_display = self.processor.available_models.get(best_model_name, best_model_name)
                
                best_text = f"""Mejor Modelo: {best_display}
R² Score: {best_results['r2']:.4f}
MAE: {best_results['mae']:.4f}
RMSE: {best_results['rmse']:.4f}
MAPE: {best_results['mape']:.2f}%

Interpretación:
• Calidad: {'Excelente' if best_results['r2'] > 0.9 else 'Buena' if best_results['r2'] > 0.7 else 'Moderada' if best_results['r2'] > 0.5 else 'Pobre'}
• Precisión: {'Alta' if best_results['mae'] < 5 else 'Media' if best_results['mae'] < 10 else 'Baja'}
"""
                
                self.best_model_text.config(state='normal')
                self.best_model_text.delete(1.0, tk.END)
                self.best_model_text.insert(1.0, best_text)
                self.best_model_text.config(state='disabled')
                
            except Exception as e:
                logger.error(f"Error updating best model: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error updating results display: {e}")
    
    # =============== MÉTODOS DE VISUALIZACIÓN MEJORADOS ===============
    
    def plot_metrics_comparison(self):
        """Gráfico de comparación de métricas entre modelos"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados para visualizar")
            return
        
        try:
            self.plot_figure.clear()
            
            # Preparar datos
            models = []
            r2_scores = []
            mae_scores = []
            rmse_scores = []
            mape_scores = []
            
            for model_name, results in self.processor.model_results.items():
                if 'error' not in results:
                    models.append(self.processor.available_models.get(model_name, model_name))
                    r2_scores.append(results['r2'])
                    mae_scores.append(results['mae'])
                    rmse_scores.append(results['rmse'])
                    mape_scores.append(results['mape'])
            
            if not models:
                self.show_no_data_message()
                return
            
            # Crear subplots
            gs = self.plot_figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # R² Score
            ax1 = self.plot_figure.add_subplot(gs[0, 0])
            bars1 = ax1.bar(models, r2_scores, color='skyblue', alpha=0.8)
            ax1.set_title('R² Score (Mayor es Mejor)')
            ax1.set_ylabel('R²')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, alpha=0.3)
            
            # Agregar valores en las barras
            for bar, value in zip(bars1, r2_scores):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontsize=9)
            
            # MAE
            ax2 = self.plot_figure.add_subplot(gs[0, 1])
            bars2 = ax2.bar(models, mae_scores, color='lightcoral', alpha=0.8)
            ax2.set_title('Mean Absolute Error (Menor es Mejor)')
            ax2.set_ylabel('MAE')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
            
            for bar, value in zip(bars2, mae_scores):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + max(mae_scores)*0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontsize=9)
            
            # RMSE
            ax3 = self.plot_figure.add_subplot(gs[1, 0])
            bars3 = ax3.bar(models, rmse_scores, color='lightgreen', alpha=0.8)
            ax3.set_title('Root Mean Squared Error (Menor es Mejor)')
            ax3.set_ylabel('RMSE')
            ax3.tick_params(axis='x', rotation=45)
            ax3.grid(True, alpha=0.3)
            
            for bar, value in zip(bars3, rmse_scores):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + max(rmse_scores)*0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontsize=9)
            
            # MAPE
            ax4 = self.plot_figure.add_subplot(gs[1, 1])
            bars4 = ax4.bar(models, mape_scores, color='gold', alpha=0.8)
            ax4.set_title('Mean Absolute Percentage Error (Menor es Mejor)')
            ax4.set_ylabel('MAPE (%)')
            ax4.tick_params(axis='x', rotation=45)
            ax4.grid(True, alpha=0.3)
            
            for bar, value in zip(bars4, mape_scores):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + max(mape_scores)*0.01,
                        f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
            
            self.plot_figure.suptitle('Comparación de Métricas entre Modelos', fontsize=14, fontweight='bold')
            
            self.plot_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando gráfico de métricas: {str(e)}")
    
    def plot_predictions_comparison(self):
        """Gráfico de predicciones vs valores reales para todos los modelos"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados para visualizar")
            return
        
        try:
            self.plot_figure.clear()
            
            # Filtrar modelos válidos
            valid_models = {name: results for name, results in self.processor.model_results.items() 
                           if 'error' not in results and 'predictions' in results}
            
            if not valid_models:
                self.show_no_data_message()
                return
            
            n_models = len(valid_models)
            
            if n_models == 1:
                # Un solo subplot para un modelo
                ax = self.plot_figure.add_subplot(1, 1, 1)
                self.plot_single_prediction(ax, list(valid_models.items())[0])
            else:
                # Múltiples subplots
                cols = min(2, n_models)
                rows = (n_models + 1) // 2
                
                for i, (model_name, results) in enumerate(valid_models.items()):
                    ax = self.plot_figure.add_subplot(rows, cols, i + 1)
                    self.plot_single_prediction(ax, (model_name, results))
            
            self.plot_figure.suptitle('Predicciones vs Valores Reales por Modelo', 
                                    fontsize=14, fontweight='bold')
            self.plot_figure.tight_layout()
            
            self.plot_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando gráfico de predicciones: {str(e)}")
    
    def plot_single_prediction(self, ax, model_data):
        """Crear gráfico de predicciones vs reales para un modelo"""
        model_name, results = model_data
        model_display = self.processor.available_models.get(model_name, model_name)
        
        y_true = results['actual']
        y_pred = results['predictions']
        
        # Scatter plot
        ax.scatter(y_true, y_pred, alpha=0.6, s=30, color='blue')
        
        # Línea de predicción perfecta
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, 
               label='Predicción perfecta')
        
        # Estadísticas
        r2 = results['r2']
        mae = results['mae']
        
        ax.set_xlabel('Valores Reales')
        ax.set_ylabel('Predicciones')
        ax.set_title(f'{model_display}\nR²={r2:.3f}, MAE={mae:.3f}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Añadir línea de tendencia
        z = np.polyfit(y_true, y_pred, 1)
        p = np.poly1d(z)
        ax.plot(y_true, p(y_true), "g--", alpha=0.8, linewidth=1, label=f'Tendencia (y={z[0]:.2f}x+{z[1]:.2f})')
        ax.legend()
    
    def plot_error_distribution(self):
        """Gráfico de distribución de errores"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados para visualizar")
            return
        
        try:
            self.plot_figure.clear()
            
            # Filtrar modelos válidos
            valid_models = {name: results for name, results in self.processor.model_results.items() 
                           if 'error' not in results and 'predictions' in results}
            
            if not valid_models:
                self.show_no_data_message()
                return
            
            n_models = len(valid_models)
            
            if n_models == 1:
                # Un solo modelo
                ax = self.plot_figure.add_subplot(1, 1, 1)
                model_name, results = list(valid_models.items())[0]
                self.plot_single_error_distribution(ax, model_name, results)
            else:
                # Múltiples modelos - comparación en un solo gráfico
                ax = self.plot_figure.add_subplot(1, 1, 1)
                
                colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
                
                for i, (model_name, results) in enumerate(valid_models.items()):
                    model_display = self.processor.available_models.get(model_name, model_name)
                    errors = results['actual'] - results['predictions']
                    
                    # Histograma con transparencia
                    ax.hist(errors, bins=30, alpha=0.6, label=model_display, 
                           color=colors[i % len(colors)], density=True)
                
                ax.set_xlabel('Error (Real - Predicción)')
                ax.set_ylabel('Densidad')
                ax.set_title('Distribución de Errores por Modelo')
                ax.legend()
                ax.grid(True, alpha=0.3)
                ax.axvline(x=0, color='black', linestyle='--', alpha=0.7, label='Error = 0')
            
            self.plot_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando distribución de errores: {str(e)}")
    
    def plot_single_error_distribution(self, ax, model_name, results):
        """Crear distribución de errores para un modelo"""
        model_display = self.processor.available_models.get(model_name, model_name)
        errors = results['actual'] - results['predictions']
        
        # Histograma
        n, bins, patches = ax.hist(errors, bins=30, alpha=0.7, color='skyblue', density=True)
        
        # Estadísticas
        mean_error = np.mean(errors)
        std_error = np.std(errors)
        
        # Líneas de referencia
        ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Error = 0')
        ax.axvline(x=mean_error, color='green', linestyle='-', linewidth=2, 
                  label=f'Error medio = {mean_error:.3f}')
        ax.axvline(x=mean_error + std_error, color='orange', linestyle=':', alpha=0.7, 
                  label=f'±1σ = ±{std_error:.3f}')
        ax.axvline(x=mean_error - std_error, color='orange', linestyle=':', alpha=0.7)
        
        ax.set_xlabel('Error (Real - Predicción)')
        ax.set_ylabel('Densidad')
        ax.set_title(f'Distribución de Errores - {model_display}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Añadir texto con estadísticas
        stats_text = f'Media: {mean_error:.3f}\nStd: {std_error:.3f}\nMAE: {results["mae"]:.3f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def plot_residuals_analysis(self):
        """Análisis de residuos completo"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados para visualizar")
            return
        
        try:
            # Obtener el mejor modelo
            best_model_name, best_results = self.processor.get_best_model('r2')
            model_display = self.processor.available_models.get(best_model_name, best_model_name)
            
            y_true = best_results['actual']
            y_pred = best_results['predictions']
            residuals = y_true - y_pred
            
            self.plot_figure.clear()
            
            # Crear grid de subplots
            gs = self.plot_figure.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # 1. Residuos vs Predicciones
            ax1 = self.plot_figure.add_subplot(gs[0, 0])
            ax1.scatter(y_pred, residuals, alpha=0.6, s=30)
            ax1.axhline(y=0, color='red', linestyle='--')
            ax1.set_xlabel('Predicciones')
            ax1.set_ylabel('Residuos')
            ax1.set_title('Residuos vs Predicciones')
            ax1.grid(True, alpha=0.3)
            
            # Añadir línea de tendencia de residuos
            z = np.polyfit(y_pred, residuals, 1)
            p = np.poly1d(z)
            ax1.plot(y_pred, p(y_pred), "r-", alpha=0.8, linewidth=1)
            
            # 2. Q-Q plot (normalidad de residuos)
            ax2 = self.plot_figure.add_subplot(gs[0, 1])
            from scipy import stats
            stats.probplot(residuals, dist="norm", plot=ax2)
            ax2.set_title('Q-Q Plot (Normalidad)')
            ax2.grid(True, alpha=0.3)
            
            # 3. Residuos vs Valores Reales
            ax3 = self.plot_figure.add_subplot(gs[1, 0])
            ax3.scatter(y_true, residuals, alpha=0.6, s=30, color='green')
            ax3.axhline(y=0, color='red', linestyle='--')
            ax3.set_xlabel('Valores Reales')
            ax3.set_ylabel('Residuos')
            ax3.set_title('Residuos vs Valores Reales')
            ax3.grid(True, alpha=0.3)
            
            # 4. Histograma de residuos estandarizados
            ax4 = self.plot_figure.add_subplot(gs[1, 1])
            standardized_residuals = residuals / np.std(residuals)
            ax4.hist(standardized_residuals, bins=20, alpha=0.7, color='orange', density=True)
            
            # Superponer distribución normal
            x = np.linspace(-3, 3, 100)
            ax4.plot(x, stats.norm.pdf(x, 0, 1), 'r-', linewidth=2, label='Normal(0,1)')
            ax4.set_xlabel('Residuos Estandarizados')
            ax4.set_ylabel('Densidad')
            ax4.set_title('Distribución de Residuos Estandarizados')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            self.plot_figure.suptitle(f'Análisis de Residuos - {model_display}', 
                                    fontsize=14, fontweight='bold')
            
            self.plot_canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en análisis de residuos: {str(e)}")
    
    def show_no_data_message(self):
        """Mostrar mensaje cuando no hay datos"""
        self.plot_figure.clear()
        ax = self.plot_figure.add_subplot(1, 1, 1)
        ax.text(0.5, 0.5, 'No hay resultados para visualizar\n\nEntrene algunos modelos primero', 
               ha='center', va='center', transform=ax.transAxes, 
               fontsize=14, bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        ax.set_xticks([])
        ax.set_yticks([])
        self.plot_canvas.draw()
    
    # =============== MÉTODOS DE EXPORTACIÓN ===============
    
    def export_results(self):
        """Exportar resultados a archivo"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("CSV files", "*.csv"),
                    ("JSON files", "*.json")
                ]
            )
            
            if not filename:
                return
            
            # Preparar datos para exportar
            results_data = []
            for model_name, results in self.processor.model_results.items():
                if 'error' not in results:
                    model_display = self.processor.available_models.get(model_name, model_name)
                    results_data.append({
                        'Modelo': model_display,
                        'Modelo_ID': model_name,
                        'R²': results['r2'],
                        'MAE': results['mae'],
                        'RMSE': results['rmse'],
                        'MSE': results['mse'],
                        'MAPE': results['mape']
                    })
            
            results_df = pd.DataFrame(results_data)
            
            if filename.endswith('.xlsx'):
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    results_df.to_excel(writer, sheet_name='Resumen_Modelos', index=False)
                    
                    # Añadir predicciones del mejor modelo
                    try:
                        best_model_name, best_results = self.processor.get_best_model('r2')
                        pred_df = pd.DataFrame({
                            'Valores_Reales': best_results['actual'],
                            'Predicciones': best_results['predictions'],
                            'Error': best_results['actual'] - best_results['predictions'],
                            'Error_Absoluto': np.abs(best_results['actual'] - best_results['predictions'])
                        })
                        pred_df.to_excel(writer, sheet_name=f'Predicciones_{best_model_name}', index=False)
                    except:
                        pass
                        
            elif filename.endswith('.csv'):
                results_df.to_csv(filename, index=False)
            elif filename.endswith('.json'):
                # Exportar todo como JSON
                export_data = {
                    'metadata': {
                        'timestamp': pd.Timestamp.now().isoformat(),
                        'target_column': self.target_column,
                        'feature_columns': self.feature_columns,
                        'test_size': self.test_size_var.get()
                    },
                    'results': {}
                }
                
                for model_name, results in self.processor.model_results.items():
                    if 'error' not in results:
                        # Convertir arrays numpy a listas para JSON
                        export_results = results.copy()
                        if 'predictions' in export_results:
                            export_results['predictions'] = export_results['predictions'].tolist()
                        if 'actual' in export_results:
                            export_results['actual'] = export_results['actual'].tolist()
                        export_data['results'][model_name] = export_results
                
                import json
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
            
            messagebox.showinfo("Éxito", f"Resultados exportados a:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando resultados:\n{str(e)}")
    
    def save_best_model(self):
        """Guardar el mejor modelo entrenado"""
        if not self.processor or not self.processor.model_results:
            messagebox.showwarning("Advertencia", "No hay modelos entrenados")
            return
        
        try:
            best_model_name, best_results = self.processor.get_best_model('r2')
            
            if best_model_name not in self.processor.trained_models:
                messagebox.showwarning("Advertencia", "Modelo no encontrado en memoria")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".joblib",
                filetypes=[
                    ("Joblib files", "*.joblib"),
                    ("Pickle files", "*.pkl")
                ],
                initialvalue=f"best_model_{best_model_name}.joblib"
            )
            
            if not filename:
                return
            
            # Preparar datos del modelo para guardar
            model_data = {
                'model': self.processor.trained_models[best_model_name],
                'model_name': best_model_name,
                'model_display': self.processor.available_models.get(best_model_name, best_model_name),
                'feature_columns': self.feature_columns,
                'target_column': self.target_column,
                'results': best_results,
                'training_params': {
                    'test_size': self.test_size_var.get(),
                    'grid_search': self.grid_search_var.get()
                },
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            import joblib
            joblib.dump(model_data, filename)
            
            messagebox.showinfo("Éxito", f"Mejor modelo ({self.processor.available_models.get(best_model_name, best_model_name)}) guardado en:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando modelo:\n{str(e)}")
    
    # =============== MÉTODOS DE UTILIDAD ===============
    
    def reset(self):
        """Resetear el tab"""
        self.current_data = None
        self.feature_columns = []
        self.training_in_progress = False
        
        # Limpiar interfaz
        self.data_info_text.delete(1.0, tk.END)
        self.training_log.delete(1.0, tk.END)
        self.best_model_text.config(state='normal')
        self.best_model_text.delete(1.0, tk.END)
        self.best_model_text.config(state='disabled')
        
        # Limpiar tabla de resultados
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Limpiar gráficos
        if self.plot_figure:
            self.plot_figure.clear()
            self.plot_canvas.draw()
        
        # Resetear controles
        self.train_button.config(state="disabled")
        self.progress_var.set("Listo")
        
        # Limpiar listas
        self.target_combo.set('')
        self.features_listbox.delete(0, tk.END)
        
        self.log_training("Tab reiniciado")
    
    def set_data(self, data):
        """Establecer datos desde fuente externa"""
        self.current_data = data
        if data is not None:
            self.update_data_info()
            self.populate_feature_lists()
            self.train_button.config(state="normal")
            self.log_training("Datos cargados desde fuente externa")
    
    def get_training_status(self):
        """Obtener estado del entrenamiento"""
        return {
            'training_in_progress': self.training_in_progress,
            'has_data': self.current_data is not None,
            'has_results': self.processor and bool(self.processor.model_results),
            'feature_count': len(self.feature_columns),
            'target_column': self.target_column
        }