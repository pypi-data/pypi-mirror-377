"""
Tab para procesamiento batch de archivos LAMMPS dump con selección de features
VERSIÓN COMPLETA con botón de entrenamiento integrado
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
import numpy as np
import logging
import threading
import json
from typing import Callable, Optional, Dict, List, Set

# Importar el procesador batch
from vacancy_predictor.core.batch_processor import BatchDumpProcessor

logger = logging.getLogger(__name__)

class BatchProcessingTab:
    """Tab para procesamiento batch con selección de features y entrenamiento integrado"""
    
    def __init__(self, parent, data_loaded_callback: Callable):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        
        # Procesador batch
        self.processor = BatchDumpProcessor()
        self.processor.set_progress_callback(self.update_progress)
        
        self.frame = ttk.Frame(parent)
        
        # Variables de procesamiento
        self.directory_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value="ml_dataset_output")
        
        # Variables de configuración
        self.atm_total_var = tk.IntVar(value=16384)
        self.energy_min_var = tk.DoubleVar(value=-4.0)
        self.energy_max_var = tk.DoubleVar(value=-3.0)
        self.energy_bins_var = tk.IntVar(value=10)
        
        # Variables de entrenamiento ML
        self.test_size_var = tk.DoubleVar(value=0.2)
        self.n_estimators_var = tk.IntVar(value=100)
        self.random_state_var = tk.IntVar(value=42)
        
        # Dataset y estado
        self.current_dataset = None
        self.selected_features = set()
        self.trained_model = None
        self.is_processing = False
        self.is_training = False
        
        # Crear interfaz
        self.create_widgets()
    
    def create_widgets(self):
        """Crear todos los widgets del tab"""
        # Crear notebook para secciones
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 1. Pestaña de configuración y procesamiento
        self.create_processing_tab()
        
        # 2. Pestaña de selección de features
        self.create_features_tab()
        
        # 3. Pestaña de entrenamiento ML
        self.create_training_tab()
        
        # 4. Pestaña de resultados
        self.create_results_tab()
    
    def create_processing_tab(self):
        """Crear pestaña de configuración y procesamiento"""
        process_frame = ttk.Frame(self.notebook)
        self.notebook.add(process_frame, text="🔧 Configuración & Procesamiento")
        
        # Configuración LAMMPS
        config_frame = ttk.LabelFrame(process_frame, text="Configuración LAMMPS", padding="10")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # Parámetros en grid
        ttk.Label(config_frame, text="Número total de átomos:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.atm_total_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Energía mínima (eV):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.energy_min_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Energía máxima (eV):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.energy_max_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Bins de energía:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.energy_bins_var, width=15).grid(row=3, column=1, padx=5, pady=2)
        
        # Directorios
        dirs_frame = ttk.LabelFrame(process_frame, text="Directorios", padding="10")
        dirs_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(dirs_frame, text="Directorio con dumps:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(dirs_frame, textvariable=self.directory_var, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(dirs_frame, text="Explorar...", command=self.browse_directory).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(dirs_frame, text="Directorio de salida:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(dirs_frame, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(dirs_frame, text="Explorar...", command=self.browse_output_directory).grid(row=1, column=2, padx=5, pady=2)
        
        # Botón de procesamiento
        process_btn_frame = ttk.Frame(process_frame)
        process_btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.process_button = ttk.Button(process_btn_frame, text="🚀 Procesar Archivos Dump", 
                                        command=self.start_processing, style="Action.TButton")
        self.process_button.pack(side="left", padx=5)
        
        ttk.Button(process_btn_frame, text="Cargar Dataset Existente", 
                  command=self.load_existing_dataset).pack(side="left", padx=5)
        
        # Progreso
        progress_frame = ttk.LabelFrame(process_frame, text="Progreso", padding="10")
        progress_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Listo para procesar")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack(anchor="w")
        
        # Log de procesamiento
        self.process_log = tk.Text(progress_frame, height=10, wrap="word", font=("Courier", 9))
        self.process_log.pack(fill="both", expand=True, pady=(10, 0))
    
    def create_features_tab(self):
        """Crear pestaña de selección de features"""
        features_frame = ttk.Frame(self.notebook)
        self.notebook.add(features_frame, text="🎯 Selección de Features")
        
        # Info del dataset
        info_frame = ttk.LabelFrame(features_frame, text="Información del Dataset", padding="10")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.dataset_info_label = ttk.Label(info_frame, text="No hay dataset cargado", 
                                           font=("Arial", 10))
        self.dataset_info_label.pack(anchor="w")
        
        # Tabla de features
        table_frame = ttk.LabelFrame(features_frame, text="Features Disponibles", padding="10")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Botones de control
        control_frame = ttk.Frame(table_frame)
        control_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(control_frame, text="Seleccionar Todo", 
                  command=self.select_all_features).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Deseleccionar Todo", 
                  command=self.deselect_all_features).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Auto-Seleccionar (Top 30)", 
                  command=self.auto_select_features).pack(side="left", padx=5)
        
        # Treeview para features
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill="both", expand=True)
        
        columns = ("Feature", "Tipo", "Correlación", "Importancia", "Seleccionado")
        self.features_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.features_tree.heading(col, text=col)
            self.features_tree.column(col, width=150, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.features_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.features_tree.xview)
        self.features_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.features_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind eventos
        self.features_tree.bind("<Double-1>", self.toggle_feature_selection)
        
        # Resumen de selección
        summary_frame = ttk.LabelFrame(features_frame, text="Resumen de Selección", padding="10")
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.selection_summary_label = ttk.Label(summary_frame, text="0 features seleccionadas", 
                                                font=("Arial", 10, "bold"))
        self.selection_summary_label.pack(anchor="w")
    
    def create_training_tab(self):
        """Crear pestaña de entrenamiento ML"""
        training_frame = ttk.Frame(self.notebook)
        self.notebook.add(training_frame, text="🤖 Entrenamiento ML")
        
        # Configuración del modelo
        model_config_frame = ttk.LabelFrame(training_frame, text="Configuración del Modelo", padding="10")
        model_config_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(model_config_frame, text="Tamaño de prueba:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(model_config_frame, textvariable=self.test_size_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(model_config_frame, text="Nº Estimadores:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(model_config_frame, textvariable=self.n_estimators_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(model_config_frame, text="Random State:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(model_config_frame, textvariable=self.random_state_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        
        # Botones de entrenamiento
        training_controls_frame = ttk.LabelFrame(training_frame, text="Control de Entrenamiento", padding="10")
        training_controls_frame.pack(fill="x", padx=10, pady=5)
        
        buttons_frame = ttk.Frame(training_controls_frame)
        buttons_frame.pack(fill="x")
        
        self.train_button = ttk.Button(buttons_frame, text="🚀 Entrenar Modelo", 
                                      command=self.start_training, style="Action.TButton")
        self.train_button.pack(side="left", padx=5)
        
        self.stop_train_button = ttk.Button(buttons_frame, text="⏹️ Detener", 
                                           command=self.stop_training, state="disabled")
        self.stop_train_button.pack(side="left", padx=5)
        
        ttk.Button(buttons_frame, text="💾 Guardar Modelo", 
                  command=self.save_model).pack(side="right", padx=5)
        ttk.Button(buttons_frame, text="📁 Cargar Modelo", 
                  command=self.load_model).pack(side="right", padx=5)
        
        # Progreso de entrenamiento
        train_progress_frame = ttk.LabelFrame(training_frame, text="Progreso de Entrenamiento", padding="10")
        train_progress_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.train_progress_var = tk.DoubleVar()
        self.train_progress_bar = ttk.Progressbar(train_progress_frame, variable=self.train_progress_var, 
                                                 maximum=100, length=400)
        self.train_progress_bar.pack(fill="x", pady=(0, 10))
        
        self.train_status_var = tk.StringVar(value="Listo para entrenar")
        self.train_status_label = ttk.Label(train_progress_frame, textvariable=self.train_status_var)
        self.train_status_label.pack(anchor="w")
        
        # Log de entrenamiento
        self.training_log = tk.Text(train_progress_frame, height=12, wrap="word", font=("Courier", 9))
        self.training_log.pack(fill="both", expand=True, pady=(10, 0))
    
    def create_results_tab(self):
        """Crear pestaña de resultados"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📊 Resultados")
        
        # Métricas del modelo
        metrics_frame = ttk.LabelFrame(results_frame, text="Métricas del Modelo", padding="10")
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        self.metrics_text = tk.Text(metrics_frame, height=8, wrap="word", 
                                   state="disabled", font=("Courier", 9))
        self.metrics_text.pack(fill="both", expand=True)
        
        # Botones de acción
        actions_frame = ttk.LabelFrame(results_frame, text="Acciones", padding="10")
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        action_buttons = ttk.Frame(actions_frame)
        action_buttons.pack(fill="x")
        
        ttk.Button(action_buttons, text="📈 Ver Gráficos", 
                  command=self.show_plots).pack(side="left", padx=5)
        ttk.Button(action_buttons, text="📋 Feature Importance", 
                  command=self.show_feature_importance).pack(side="left", padx=5)
        ttk.Button(action_buttons, text="🔮 Hacer Predicción", 
                  command=self.make_prediction).pack(side="left", padx=5)
        
        # Resultados detallados
        detailed_frame = ttk.LabelFrame(results_frame, text="Resultados Detallados", padding="10")
        detailed_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.results_text = tk.Text(detailed_frame, height=12, wrap="word", 
                                   state="disabled", font=("Courier", 9))
        
        results_scrollbar = ttk.Scrollbar(detailed_frame, orient="vertical", 
                                        command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
    
    # Métodos de procesamiento
    def browse_directory(self):
        """Seleccionar directorio con archivos .dump"""
        directory = filedialog.askdirectory(title="Seleccionar directorio con archivos .dump")
        if directory:
            self.directory_var.set(directory)
            try:
                dump_files = self.processor.find_dump_files(directory)
                message = f"Directorio seleccionado: {len(dump_files)} archivos .dump encontrados"
                self.update_status(message)
            except Exception as e:
                logger.error(f"Error explorando directorio: {e}")
    
    def browse_output_directory(self):
        """Seleccionar directorio de salida"""
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if directory:
            self.output_dir_var.set(directory)
    
    def start_processing(self):
        """Iniciar procesamiento de archivos dump"""
        if self.is_processing:
            return
        
        if not self.directory_var.get():
            messagebox.showwarning("Advertencia", "Seleccione un directorio con archivos .dump")
            return
        
        # Configurar procesador
        self.processor.set_parameters(
            atm_total=self.atm_total_var.get(),
            energy_min=self.energy_min_var.get(),
            energy_max=self.energy_max_var.get(),
            energy_bins=self.energy_bins_var.get()
        )
        
        # Iniciar procesamiento en hilo separado
        self.is_processing = True
        self.process_button.config(state="disabled")
        
        thread = threading.Thread(target=self._processing_worker, daemon=True)
        thread.start()
    
    def _processing_worker(self):
        """Worker para procesamiento de archivos"""
        try:
            self.log_process("Iniciando procesamiento de archivos dump...")
            
            # Procesar directorio
            dataset = self.processor.process_directory(self.directory_var.get())
            
            # Guardar dataset
            output_dir = Path(self.output_dir_var.get())
            output_dir.mkdir(exist_ok=True)
            
            csv_path = output_dir / "batch_dataset.csv"
            dataset.to_csv(csv_path)
            
            # Actualizar UI
            self.current_dataset = dataset
            self.frame.after(0, self._update_after_processing, dataset, csv_path)
            
        except Exception as e:
            self.frame.after(0, self._handle_processing_error, str(e))
        finally:
            self.frame.after(0, self._reset_processing_state)
    
    def _update_after_processing(self, dataset, csv_path):
        """Actualizar UI después del procesamiento"""
        self.log_process(f"Procesamiento completado: {csv_path}")
        self.update_dataset_info(dataset)
        self.update_features_table(dataset)
        
        # Cambiar a tab de features
        self.notebook.select(1)
        
        # Notificar callback
        self.data_loaded_callback(dataset)
    
    def _handle_processing_error(self, error_msg):
        """Manejar errores de procesamiento"""
        self.log_process(f"ERROR: {error_msg}")
        messagebox.showerror("Error", f"Error en procesamiento: {error_msg}")
    
    def _reset_processing_state(self):
        """Resetear estado de procesamiento"""
        self.is_processing = False
        self.process_button.config(state="normal")
        self.progress_var.set(0)
        self.status_var.set("Listo para procesar")
    
    def load_existing_dataset(self):
        """Cargar dataset existente"""
        file_path = filedialog.askopenfilename(
            title="Cargar Dataset",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    dataset = pd.read_excel(file_path, index_col=0)
                else:
                    dataset = pd.read_csv(file_path, index_col=0)
                
                self.current_dataset = dataset
                self.update_dataset_info(dataset)
                self.update_features_table(dataset)
                
                # Cambiar a tab de features
                self.notebook.select(1)
                
                # Notificar callback
                self.data_loaded_callback(dataset)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando dataset: {str(e)}")
    
    # Métodos de selección de features
    def update_dataset_info(self, dataset):
        """Actualizar información del dataset"""
        if dataset is not None:
            info = f"Dataset: {len(dataset)} muestras, {len(dataset.columns)} columnas"
            if 'vacancies' in dataset.columns:
                vac_stats = dataset['vacancies'].describe()
                info += f" | Vacancies: {vac_stats['min']:.0f}-{vac_stats['max']:.0f} (mean: {vac_stats['mean']:.1f})"
            self.dataset_info_label.config(text=info)
    
    def update_features_table(self, dataset):
        """Actualizar tabla de features"""
        # Limpiar tabla
        for item in self.features_tree.get_children():
            self.features_tree.delete(item)
        
        if dataset is None:
            return
        
        # Excluir columnas metadata
        exclude_cols = ['file_path', 'vacancies']
        feature_cols = [col for col in dataset.columns if col not in exclude_cols]
        
        # Calcular correlaciones con target si existe
        correlations = {}
        if 'vacancies' in dataset.columns:
            for col in feature_cols:
                try:
                    corr = dataset[col].corr(dataset['vacancies'])
                    correlations[col] = corr if not pd.isna(corr) else 0.0
                except:
                    correlations[col] = 0.0
        
        # Llenar tabla
        for col in feature_cols:
            corr = correlations.get(col, 0.0)
            dtype = str(dataset[col].dtype)
            
            # Determinar tipo simplificado
            if 'float' in dtype or 'int' in dtype:
                type_simple = "Numérico"
            else:
                type_simple = "Categórico"
            
            # Insertar en tabla
            self.features_tree.insert('', 'end', values=(
                col,
                type_simple,
                f"{abs(corr):.3f}",
                "TBD",  # Importancia se calculará después del entrenamiento
                "No"
            ))
        
        self.update_selection_summary()
    
    def toggle_feature_selection(self, event):
        """Alternar selección de feature con doble click"""
        item = self.features_tree.selection()[0]
        feature_name = self.features_tree.item(item, 'values')[0]
        
        if feature_name in self.selected_features:
            self.selected_features.remove(feature_name)
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], "No"
            ))
        else:
            self.selected_features.add(feature_name)
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], "Sí"
            ))
        
        self.update_selection_summary()
    
    def select_all_features(self):
        """Seleccionar todas las features"""
        self.selected_features.clear()
        for item in self.features_tree.get_children():
            feature_name = self.features_tree.item(item, 'values')[0]
            self.selected_features.add(feature_name)
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], "Sí"
            ))
        self.update_selection_summary()
    
    def deselect_all_features(self):
        """Deseleccionar todas las features"""
        self.selected_features.clear()
        for item in self.features_tree.get_children():
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], "No"
            ))
        self.update_selection_summary()
    
    def auto_select_features(self):
        """Auto-seleccionar top features por correlación"""
        if self.current_dataset is None or 'vacancies' not in self.current_dataset.columns:
            messagebox.showwarning("Advertencia", "No hay dataset con target para auto-selección")
            return
        
        # Calcular correlaciones
        exclude_cols = ['file_path', 'vacancies']
        feature_cols = [col for col in self.current_dataset.columns if col not in exclude_cols]
        
        correlations = []
        for col in feature_cols:
            try:
                corr = abs(self.current_dataset[col].corr(self.current_dataset['vacancies']))
                if not pd.isna(corr):
                    correlations.append((col, corr))
            except:
                pass
        
        # Seleccionar top 30
        correlations.sort(key=lambda x: x[1], reverse=True)
        top_features = [feat for feat, _ in correlations[:30]]
        
        # Actualizar selección
        self.selected_features.clear()
        self.selected_features.update(top_features)
        
        # Actualizar tabla
        for item in self.features_tree.get_children():
            feature_name = self.features_tree.item(item, 'values')[0]
            selected = "Sí" if feature_name in self.selected_features else "No"
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], selected
            ))
        
        self.update_selection_summary()
        messagebox.showinfo("Auto-selección", f"Seleccionadas {len(top_features)} features por correlación")
    
    def update_selection_summary(self):
        """Actualizar resumen de selección"""
        count = len(self.selected_features)
        self.selection_summary_label.config(text=f"{count} features seleccionadas")
    
    # Métodos de entrenamiento
    def start_training(self):
        """Iniciar entrenamiento del modelo"""
        if self.is_training:
            return
        
        if self.current_dataset is None:
            messagebox.showwarning("Advertencia", "No hay dataset cargado")
            return
        
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "Seleccione features para entrenar")
            return
        
        if 'vacancies' not in self.current_dataset.columns:
            messagebox.showerror("Error", "No se encontró columna 'vacancies' como target")
            return
        
        # Iniciar entrenamiento en hilo separado
        self.is_training = True
        self.train_button.config(state="disabled")
        self.stop_train_button.config(state="normal")
        
        thread = threading.Thread(target=self._training_worker, daemon=True)
        thread.start()
        
        # Cambiar a tab de entrenamiento
        self.notebook.select(2)
    
    def _training_worker(self):
        """Worker para entrenamiento del modelo"""
        try:
            self.log_training("Iniciando entrenamiento...")
            
            # Preparar datos
            X = self.current_dataset[list(self.selected_features)]
            y = self.current_dataset['vacancies']
            
            self.log_training(f"Features: {len(self.selected_features)}, Muestras: {len(X)}")
            
            # Dividir datos
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size_var.get(), 
                random_state=self.random_state_var.get()
            )
            
            self.frame.after(0, self._update_train_progress, 20, "Dividiendo datos...")
            
            # Entrenar modelo
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            
            self.frame.after(0, self._update_train_progress, 40, "Entrenando Random Forest...")
            
            model = RandomForestRegressor(
                n_estimators=self.n_estimators_var.get(),
                random_state=self.random_state_var.get(),
                n_jobs=-1
            )
            
            model.fit(X_train, y_train)
            
            self.frame.after(0, self._update_train_progress, 70, "Evaluando modelo...")
            
            # Hacer predicciones
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)
            
            # Calcular métricas
            train_mae = mean_absolute_error(y_train, train_pred)
            test_mae = mean_absolute_error(y_test, test_pred)
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(y_test, test_pred)
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': list(self.selected_features),
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Almacenar resultados
            results = {
                'model': model,
                'feature_importance': feature_importance,
                'metrics': {
                    'train_mae': train_mae,
                    'test_mae': test_mae,
                    'train_rmse': train_rmse,
                    'test_rmse': test_rmse,
                    'train_r2': train_r2,
                    'test_r2': test_r2,
                    'n_features': len(self.selected_features),
                    'n_train': len(X_train),
                    'n_test': len(X_test)
                },
                'test_data': {
                    'X_test': X_test,
                    'y_test': y_test,
                    'predictions': test_pred
                }
            }
            
            self.frame.after(0, self._update_after_training, results)
            
        except Exception as e:
            self.frame.after(0, self._handle_training_error, str(e))
        finally:
            self.frame.after(0, self._reset_training_state)
    
    def _update_train_progress(self, value, message):
        """Actualizar progreso de entrenamiento"""
        self.train_progress_var.set(value)
        self.train_status_var.set(message)
    
    def _update_after_training(self, results):
        """Actualizar UI después del entrenamiento"""
        self.trained_model = results
        
        # Actualizar métricas
        metrics = results['metrics']
        metrics_text = f"""RESULTADOS DEL ENTRENAMIENTO
==============================

CONFIGURACIÓN:
  Algoritmo: Random Forest
  N° Estimadores: {self.n_estimators_var.get()}
  Features utilizadas: {metrics['n_features']}
  Muestras entrenamiento: {metrics['n_train']}
  Muestras prueba: {metrics['n_test']}

MÉTRICAS DE RENDIMIENTO:
  Train MAE:  {metrics['train_mae']:.3f}
  Test MAE:   {metrics['test_mae']:.3f}
  Train RMSE: {metrics['train_rmse']:.3f}
  Test RMSE:  {metrics['test_rmse']:.3f}
  Train R²:   {metrics['train_r2']:.3f}
  Test R²:    {metrics['test_r2']:.3f}

TOP 10 FEATURES MÁS IMPORTANTES:
"""
        
        for i, row in results['feature_importance'].head(10).iterrows():
            metrics_text += f"  {row['feature'][:40]:40s}: {row['importance']:.4f}\n"
        
        # Actualizar feature importance en tabla
        self._update_feature_importance_in_table(results['feature_importance'])
        
        # Mostrar métricas
        self.metrics_text.config(state='normal')
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, metrics_text)
        self.metrics_text.config(state='disabled')
        
        # Log de entrenamiento
        self.log_training("Entrenamiento completado exitosamente!")
        self.log_training(f"Test R²: {metrics['test_r2']:.3f}, Test MAE: {metrics['test_mae']:.3f}")
        
        # Cambiar a tab de resultados
        self.notebook.select(3)
    
    def _update_feature_importance_in_table(self, feature_importance):
        """Actualizar importancia en tabla de features"""
        importance_dict = dict(zip(feature_importance['feature'], feature_importance['importance']))
        
        for item in self.features_tree.get_children():
            values = list(self.features_tree.item(item, 'values'))
            feature_name = values[0]
            
            if feature_name in importance_dict:
                values[3] = f"{importance_dict[feature_name]:.4f}"
            else:
                values[3] = "0.0000"
            
            self.features_tree.item(item, values=values)
    
    def _handle_training_error(self, error_msg):
        """Manejar errores de entrenamiento"""
        self.log_training(f"ERROR: {error_msg}")
        messagebox.showerror("Error", f"Error en entrenamiento: {error_msg}")
    
    def _reset_training_state(self):
        """Resetear estado de entrenamiento"""
        self.is_training = False
        self.train_button.config(state="normal")
        self.stop_train_button.config(state="disabled")
        self.train_progress_var.set(0)
        self.train_status_var.set("Listo para entrenar")
    
    def stop_training(self):
        """Detener entrenamiento"""
        self.is_training = False
        self.log_training("Deteniendo entrenamiento...")
    
    # Métodos de persistencia
    def save_model(self):
        """Guardar modelo entrenado"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "No hay modelo entrenado para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar Modelo",
            defaultextension=".joblib",
            filetypes=[("Joblib files", "*.joblib"), ("Pickle files", "*.pkl")]
        )
        
        if file_path:
            try:
                import joblib
                
                # Crear paquete completo del modelo
                model_package = {
                    'model': self.trained_model['model'],
                    'selected_features': list(self.selected_features),
                    'feature_importance': self.trained_model['feature_importance'],
                    'metrics': self.trained_model['metrics'],
                    'training_config': {
                        'atm_total': self.atm_total_var.get(),
                        'energy_min': self.energy_min_var.get(),
                        'energy_max': self.energy_max_var.get(),
                        'energy_bins': self.energy_bins_var.get(),
                        'test_size': self.test_size_var.get(),
                        'n_estimators': self.n_estimators_var.get(),
                        'random_state': self.random_state_var.get()
                    }
                }
                
                joblib.dump(model_package, file_path)
                messagebox.showinfo("Éxito", f"Modelo guardado en: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando modelo: {str(e)}")
    
    def load_model(self):
        """Cargar modelo previamente entrenado"""
        file_path = filedialog.askopenfilename(
            title="Cargar Modelo",
            filetypes=[("Joblib files", "*.joblib"), ("Pickle files", "*.pkl")]
        )
        
        if file_path:
            try:
                import joblib
                
                model_package = joblib.load(file_path)
                
                if isinstance(model_package, dict) and 'model' in model_package:
                    # Restaurar configuración
                    if 'training_config' in model_package:
                        config = model_package['training_config']
                        self.atm_total_var.set(config.get('atm_total', 16384))
                        self.energy_min_var.set(config.get('energy_min', -4.0))
                        self.energy_max_var.set(config.get('energy_max', -3.0))
                        self.energy_bins_var.set(config.get('energy_bins', 10))
                        self.test_size_var.set(config.get('test_size', 0.2))
                        self.n_estimators_var.set(config.get('n_estimators', 100))
                        self.random_state_var.set(config.get('random_state', 42))
                    
                    # Restaurar selección de features
                    if 'selected_features' in model_package:
                        self.selected_features = set(model_package['selected_features'])
                        self.update_selection_summary()
                    
                    # Restaurar modelo
                    self.trained_model = {
                        'model': model_package['model'],
                        'feature_importance': model_package.get('feature_importance'),
                        'metrics': model_package.get('metrics', {}),
                        'test_data': None  # No restauramos datos de test
                    }
                    
                    messagebox.showinfo("Éxito", f"Modelo cargado desde: {file_path}")
                    
                    # Actualizar métricas si están disponibles
                    if 'metrics' in model_package:
                        self._show_loaded_model_info(model_package['metrics'])
                
                else:
                    messagebox.showwarning("Advertencia", "Formato de modelo no reconocido")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando modelo: {str(e)}")
    
    def _show_loaded_model_info(self, metrics):
        """Mostrar información del modelo cargado"""
        info_text = f"""MODELO CARGADO
===============

CONFIGURACIÓN:
  Features: {metrics.get('n_features', 'N/A')}
  Muestras entrenamiento: {metrics.get('n_train', 'N/A')}
  Muestras prueba: {metrics.get('n_test', 'N/A')}

MÉTRICAS GUARDADAS:
  Test R²: {metrics.get('test_r2', 'N/A'):.3f}
  Test MAE: {metrics.get('test_mae', 'N/A'):.3f}
  Test RMSE: {metrics.get('test_rmse', 'N/A'):.3f}

El modelo está listo para hacer predicciones.
"""
        
        self.metrics_text.config(state='normal')
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, info_text)
        self.metrics_text.config(state='disabled')
    
    # Métodos de visualización y análisis
    def show_plots(self):
        """Mostrar gráficos de resultados"""
        if self.trained_model is None or 'test_data' not in self.trained_model:
            messagebox.showwarning("Advertencia", "No hay datos de test para graficar")
            return
        
        try:
            import matplotlib.pyplot as plt
            
            test_data = self.trained_model['test_data']
            y_true = test_data['y_test']
            y_pred = test_data['predictions']
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            fig.suptitle('Resultados del Modelo Random Forest', fontsize=16)
            
            # 1. Predicciones vs Reales
            axes[0, 0].scatter(y_true, y_pred, alpha=0.6)
            axes[0, 0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
            axes[0, 0].set_xlabel('Valores Reales')
            axes[0, 0].set_ylabel('Predicciones')
            axes[0, 0].set_title('Predicciones vs Reales')
            
            # 2. Residuos
            residuals = y_true - y_pred
            axes[0, 1].scatter(y_pred, residuals, alpha=0.6)
            axes[0, 1].axhline(y=0, color='r', linestyle='--')
            axes[0, 1].set_xlabel('Predicciones')
            axes[0, 1].set_ylabel('Residuos')
            axes[0, 1].set_title('Gráfico de Residuos')
            
            # 3. Distribución de residuos
            axes[1, 0].hist(residuals, bins=20, alpha=0.7, edgecolor='black')
            axes[1, 0].axvline(x=0, color='r', linestyle='--')
            axes[1, 0].set_xlabel('Residuos')
            axes[1, 0].set_ylabel('Frecuencia')
            axes[1, 0].set_title('Distribución de Residuos')
            
            # 4. Feature Importance Top 10
            if 'feature_importance' in self.trained_model:
                top_features = self.trained_model['feature_importance'].head(10)
                y_pos = np.arange(len(top_features))
                axes[1, 1].barh(y_pos, top_features['importance'])
                axes[1, 1].set_yticks(y_pos)
                axes[1, 1].set_yticklabels(top_features['feature'])
                axes[1, 1].set_xlabel('Importancia')
                axes[1, 1].set_title('Top 10 Feature Importance')
                axes[1, 1].invert_yaxis()
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando gráficos: {str(e)}")
    
    def show_feature_importance(self):
        """Mostrar feature importance detallada"""
        if self.trained_model is None or 'feature_importance' not in self.trained_model:
            messagebox.showwarning("Advertencia", "No hay feature importance disponible")
            return
        
        try:
            # Crear ventana de feature importance
            importance_window = tk.Toplevel(self.frame)
            importance_window.title("Feature Importance Detallada")
            importance_window.geometry("800x600")
            
            # Crear treeview
            tree_frame = ttk.Frame(importance_window)
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            columns = ("Rank", "Feature", "Importancia", "% Acumulado")
            tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor="center")
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Llenar datos
            feature_importance = self.trained_model['feature_importance']
            cumulative = 0
            total_importance = feature_importance['importance'].sum()
            
            for i, (_, row) in enumerate(feature_importance.iterrows()):
                cumulative += row['importance']
                percentage = (cumulative / total_importance) * 100
                
                tree.insert('', 'end', values=(
                    i + 1,
                    row['feature'],
                    f"{row['importance']:.6f}",
                    f"{percentage:.1f}%"
                ))
            
            # Botón de exportar
            export_btn = ttk.Button(importance_window, text="Exportar CSV",
                                   command=lambda: self._export_feature_importance())
            export_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando feature importance: {str(e)}")
    
    def _export_feature_importance(self):
        """Exportar feature importance a CSV"""
        if self.trained_model is None or 'feature_importance' not in self.trained_model:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Feature Importance",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                self.trained_model['feature_importance'].to_csv(file_path, index=False)
                messagebox.showinfo("Éxito", f"Feature importance exportada a: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando: {str(e)}")
    
    def make_prediction(self):
        """Hacer predicción interactiva"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "No hay modelo entrenado")
            return
        
        # Crear ventana de predicción
        pred_window = tk.Toplevel(self.frame)
        pred_window.title("Hacer Predicción")
        pred_window.geometry("600x400")
        
        # Instrucciones
        ttk.Label(pred_window, text="Ingrese valores para las features seleccionadas:",
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        # Frame para inputs
        inputs_frame = ttk.Frame(pred_window)
        inputs_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Variables para inputs
        input_vars = {}
        
        # Crear inputs para cada feature seleccionada (máximo 20)
        features_to_show = list(self.selected_features)[:20]
        
        for i, feature in enumerate(features_to_show):
            row = i // 2
            col = (i % 2) * 3
            
            # Obtener valor promedio como sugerencia
            if self.current_dataset is not None and feature in self.current_dataset.columns:
                avg_value = self.current_dataset[feature].mean()
                suggestion = f" (avg: {avg_value:.3f})"
            else:
                avg_value = 0.0
                suggestion = ""
            
            ttk.Label(inputs_frame, text=f"{feature}{suggestion}:").grid(
                row=row, column=col, sticky="w", padx=5, pady=2)
            
            var = tk.DoubleVar(value=avg_value)
            input_vars[feature] = var
            
            ttk.Entry(inputs_frame, textvariable=var, width=15).grid(
                row=row, column=col+1, padx=5, pady=2)
        
        if len(self.selected_features) > 20:
            ttk.Label(inputs_frame, text=f"... y {len(self.selected_features) - 20} features más",
                     font=("Arial", 9, "italic")).grid(row=row+1, column=0, columnspan=6, pady=5)
        
        # Botón de predicción
        def predict():
            try:
                # Crear vector de features
                feature_vector = []
                for feature in self.selected_features:
                    if feature in input_vars:
                        value = input_vars[feature].get()
                    else:
                        # Usar valor promedio para features no mostradas
                        value = self.current_dataset[feature].mean() if self.current_dataset is not None else 0.0
                    feature_vector.append(value)
                
                # Hacer predicción
                X_pred = np.array(feature_vector).reshape(1, -1)
                prediction = self.trained_model['model'].predict(X_pred)[0]
                
                messagebox.showinfo("Predicción", 
                                   f"Vacancies predichas: {prediction:.2f}\n\n"
                                   f"(Redondeado: {round(prediction)} vacancies)")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error en predicción: {str(e)}")
        
        ttk.Button(pred_window, text="🔮 Predecir", command=predict,
                  style="Action.TButton").pack(pady=20)
    
    # Métodos auxiliares
    def update_progress(self, current, total, message=""):
        """Callback para actualizar progreso del procesador"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
        
        if message:
            self.status_var.set(message)
        
        self.frame.update_idletasks()
    
    def update_status(self, message):
        """Actualizar mensaje de estado"""
        self.status_var.set(message)
    
    def log_process(self, message):
        """Agregar mensaje al log de procesamiento"""
        self.process_log.insert(tk.END, f"{message}\n")
        self.process_log.see(tk.END)
        self.frame.update_idletasks()
    
    def log_training(self, message):
        """Agregar mensaje al log de entrenamiento"""
        self.training_log.insert(tk.END, f"{message}\n")
        self.training_log.see(tk.END)
        self.frame.update_idletasks()
    
    def reset(self):
        """Resetear el tab completo"""
        # Resetear variables
        self.directory_var.set("")
        self.output_dir_var.set("ml_dataset_output")
        self.atm_total_var.set(16384)
        self.energy_min_var.set(-4.0)
        self.energy_max_var.set(-3.0)
        self.energy_bins_var.set(10)
        self.test_size_var.set(0.2)
        self.n_estimators_var.set(100)
        self.random_state_var.set(42)
        
        # Resetear datos
        self.current_dataset = None
        self.selected_features.clear()
        self.trained_model = None
        
        # Resetear UI
        self.progress_var.set(0)
        self.train_progress_var.set(0)
        self.status_var.set("Listo para procesar")
        self.train_status_var.set("Listo para entrenar")
        
        self.process_log.delete(1.0, tk.END)
        self.training_log.delete(1.0, tk.END)
        
        self.metrics_text.config(state='normal')
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.config(state='disabled')
        
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        
        # Limpiar tablas
        for item in self.features_tree.get_children():
            self.features_tree.delete(item)
        
        self.update_dataset_info(None)
        self.update_selection_summary()
        
        # Resetear estados
        self.is_processing = False
        self.is_training = False
        self.process_button.config(state="normal")
        self.train_button.config(state="normal")
        self.stop_train_button.config(state="disabled")
        
        # Volver al primer tab
        self.notebook.select(0)