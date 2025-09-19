"""
Tab avanzado de ML que integra funcionalidades de compute_csv_gui.py
Incluye procesamiento, entrenamiento, predicción y visualización avanzada
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
    """Tab avanzado de ML con funcionalidades integradas"""
    
    def __init__(self, parent, data_loaded_callback: Callable):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        
        self.frame = ttk.Frame(parent)
        
        # Variables de configuración
        self.atm_total_var = tk.IntVar(value=16384)
        self.energy_min_var = tk.DoubleVar(value=-4.0)
        self.energy_max_var = tk.DoubleVar(value=-2.0)
        self.input_dir_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value="./ml_results")
        
        # Variables de entrenamiento
        self.n_estimators_var = tk.IntVar(value=100)
        self.test_size_var = tk.DoubleVar(value=0.2)
        self.random_state_var = tk.IntVar(value=42)
        
        # Variables de predicción
        self.single_file_var = tk.StringVar()
        self.batch_dir_var = tk.StringVar()
        
        # Estado actual
        self.current_data = None
        self.trained_model = None
        self.processing = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del tab"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Crear notebook para sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Sub-tabs
        self.create_config_tab()
        self.create_training_tab()
        self.create_prediction_tab()
        self.create_visualization_tab()
    
    def create_config_tab(self):
        """Tab de configuración y procesamiento"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuración & Datos")
        
        # Frame principal con scroll
        canvas = tk.Canvas(config_frame)
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configuración general
        config_group = ttk.LabelFrame(scrollable_frame, text="Configuración de Procesamiento", padding="10")
        config_group.pack(fill='x', padx=10, pady=5)
        
        # Parámetros en grid
        ttk.Label(config_group, text="Número total de átomos:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(config_group, textvariable=self.atm_total_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(config_group, text="Energía mínima (eV):").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(config_group, textvariable=self.energy_min_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(config_group, text="Energía máxima (eV):").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(config_group, textvariable=self.energy_max_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        
        # Directorios
        dirs_group = ttk.LabelFrame(scrollable_frame, text="Directorios", padding="10")
        dirs_group.pack(fill='x', padx=10, pady=5)
        
        # Directorio de entrada
        ttk.Label(dirs_group, text="Directorio de dumps:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(dirs_group, textvariable=self.input_dir_var, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(dirs_group, text="Explorar...", command=self.select_input_dir).grid(row=0, column=2, padx=5, pady=2)
        
        # Directorio de salida
        ttk.Label(dirs_group, text="Directorio de salida:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(dirs_group, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(dirs_group, text="Explorar...", command=self.select_output_dir).grid(row=1, column=2, padx=5, pady=2)
        
        # Controles de procesamiento
        process_group = ttk.LabelFrame(scrollable_frame, text="Procesamiento de Datos", padding="10")
        process_group.pack(fill='x', padx=10, pady=5)
        
        process_buttons = ttk.Frame(process_group)
        process_buttons.pack(fill='x', pady=5)
        
        self.process_btn = ttk.Button(process_buttons, text="Procesar Dumps → CSV", 
                                     command=self.process_dumps)
        self.process_btn.pack(side='left', padx=5)
        
        ttk.Button(process_buttons, text="Cargar CSV Existente", 
                  command=self.load_csv).pack(side='left', padx=5)
        
        ttk.Button(process_buttons, text="Exportar Dataset", 
                  command=self.export_dataset).pack(side='left', padx=5)
        
        # Área de estado con scroll
        status_group = ttk.LabelFrame(scrollable_frame, text="Estado del Procesamiento", padding="10")
        status_group.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_group, height=12, wrap='word')
        self.status_text.pack(fill='both', expand=True)
        
        # Pack canvas y scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_training_tab(self):
        """Tab de entrenamiento del modelo"""
        train_frame = ttk.Frame(self.notebook)
        self.notebook.add(train_frame, text="Entrenamiento")
        
        # Panel izquierdo - Controles
        left_panel = ttk.Frame(train_frame)
        left_panel.pack(side="left", fill="y", padx=(10, 5))
        
        # Parámetros de entrenamiento
        params_group = ttk.LabelFrame(left_panel, text="Parámetros del Modelo", padding="10")
        params_group.pack(fill='x', pady=(0, 10))
        
        ttk.Label(params_group, text="N° Estimadores:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Spinbox(params_group, from_=50, to=500, textvariable=self.n_estimators_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Tamaño de test:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.test_size_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Random State:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.random_state_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        # Botones de entrenamiento
        train_buttons = ttk.LabelFrame(left_panel, text="Controles de Entrenamiento", padding="10")
        train_buttons.pack(fill='x', pady=(0, 10))
        
        self.train_btn = ttk.Button(train_buttons, text="Entrenar Modelo", 
                                   command=self.train_model)
        self.train_btn.pack(fill='x', pady=2)
        
        self.cv_btn = ttk.Button(train_buttons, text="Validación Cruzada", 
                                command=self.cross_validate, state="disabled")
        self.cv_btn.pack(fill='x', pady=2)
        
        self.save_model_btn = ttk.Button(train_buttons, text="Guardar Modelo", 
                                        command=self.save_model, state="disabled")
        self.save_model_btn.pack(fill='x', pady=2)
        
        ttk.Button(train_buttons, text="Cargar Modelo", 
                  command=self.load_model).pack(fill='x', pady=2)
        
        # Panel derecho - Métricas
        right_panel = ttk.Frame(train_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10))
        
        metrics_group = ttk.LabelFrame(right_panel, text="Métricas y Resultados", padding="10")
        metrics_group.pack(fill='both', expand=True)
        
        self.metrics_text = scrolledtext.ScrolledText(metrics_group, height=20, wrap='word')
        self.metrics_text.pack(fill='both', expand=True)
    
    def create_prediction_tab(self):
        """Tab de predicción"""
        pred_frame = ttk.Frame(self.notebook)
        self.notebook.add(pred_frame, text="Predicción")
        
        # Panel superior - Controles
        top_panel = ttk.Frame(pred_frame)
        top_panel.pack(fill='x', padx=10, pady=5)
        
        # Predicción individual
        single_group = ttk.LabelFrame(top_panel, text="Predicción Individual", padding="10")
        single_group.pack(fill='x', pady=(0, 10))
        
        single_frame = ttk.Frame(single_group)
        single_frame.pack(fill='x')
        
        ttk.Label(single_frame, text="Archivo dump:").pack(side='left')
        ttk.Entry(single_frame, textvariable=self.single_file_var, width=40).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(single_frame, text="Explorar...", command=self.select_single_file).pack(side='right', padx=5)
        ttk.Button(single_frame, text="Predecir", command=self.predict_single).pack(side='right')
        
        # Predicción por lotes
        batch_group = ttk.LabelFrame(top_panel, text="Predicción por Lotes", padding="10")
        batch_group.pack(fill='x')
        
        batch_frame = ttk.Frame(batch_group)
        batch_frame.pack(fill='x')
        
        ttk.Label(batch_frame, text="Directorio:").pack(side='left')
        ttk.Entry(batch_frame, textvariable=self.batch_dir_var, width=40).pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(batch_frame, text="Explorar...", command=self.select_batch_dir).pack(side='right', padx=5)
        ttk.Button(batch_frame, text="Predecir Lote", command=self.predict_batch).pack(side='right')
        
        # Panel inferior - Resultados
        bottom_panel = ttk.Frame(pred_frame)
        bottom_panel.pack(fill='both', expand=True, padx=10, pady=5)
        
        results_group = ttk.LabelFrame(bottom_panel, text="Resultados de Predicción", padding="10")
        results_group.pack(fill='both', expand=True)
        
        self.prediction_text = scrolledtext.ScrolledText(results_group, height=20, wrap='word')
        self.prediction_text.pack(fill='both', expand=True)
    
    def create_visualization_tab(self):
        """Tab de visualización"""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualización")
        
        # Controles superiores
        controls_frame = ttk.Frame(viz_frame)
        controls_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Distribuciones", 
                  command=self.plot_distributions).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Feature Importance", 
                  command=self.plot_feature_importance).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Predicciones vs Real", 
                  command=self.plot_predictions).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Limpiar Gráficos", 
                  command=self.clear_plots).pack(side='right', padx=5)
        
        # Área de gráficos
        self.viz_area = ttk.Frame(viz_frame)
        self.viz_area.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Crear figura matplotlib
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.viz_area)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
    
    # =============================================================================
    # MÉTODOS DE UTILIDAD
    # =============================================================================
    
    def log_message(self, message):
        """Añadir mensaje al área de estado"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.frame.update()
    
    def select_input_dir(self):
        """Seleccionar directorio de entrada"""
        directory = filedialog.askdirectory(title="Seleccionar directorio con archivos .dump")
        if directory:
            self.input_dir_var.set(directory)
    
    def select_output_dir(self):
        """Seleccionar directorio de salida"""
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if directory:
            self.output_dir_var.set(directory)
    
    def select_single_file(self):
        """Seleccionar archivo individual para predicción"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo dump",
            filetypes=[("Dump files", "*.dump"), ("All files", "*.*")]
        )
        if filename:
            self.single_file_var.set(filename)
    
    def select_batch_dir(self):
        """Seleccionar directorio para predicción por lotes"""
        directory = filedialog.askdirectory(title="Seleccionar directorio para predicción por lotes")
        if directory:
            self.batch_dir_var.set(directory)
    
    def load_csv(self):
        """Cargar archivo CSV existente"""
        filename = filedialog.askopenfilename(
            title="Cargar dataset CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.current_data = pd.read_csv(filename)
                self.log_message(f"CSV cargado exitosamente: {Path(filename).name}")
                self.log_message(f"Shape: {self.current_data.shape}")
                self.log_message(f"Columnas: {list(self.current_data.columns)}")
                
                # Notificar callback principal
                self.data_loaded_callback(self.current_data)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar CSV: {str(e)}")
    
    def export_dataset(self):
        """Exportar dataset actual"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "No hay dataset para exportar")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Exportar dataset",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if filename:
            try:
                if filename.endswith('.xlsx'):
                    self.current_data.to_excel(filename, index=False)
                else:
                    self.current_data.to_csv(filename, index=False)
                
                messagebox.showinfo("Éxito", f"Dataset exportado a:\n{filename}")
                self.log_message(f"Dataset exportado: {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    # =============================================================================
    # MÉTODOS DE PROCESAMIENTO
    # =============================================================================
    
    def extract_atoms_from_lammps_file(self, filepath):
        """Extraer número de átomos del encabezado de un archivo LAMMPS"""
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line == "ITEM: NUMBER OF ATOMS":
                        next_line = next(f).strip()
                        return int(next_line)
            return None
        except Exception as e:
            self.log_message(f"Error leyendo {filepath}: {str(e)}")
            return None
    
    def create_histograms(self, dump_data):
        """Crear histogramas de coordinación y energía"""
        features = {}
        
        # Histograma de coordinación (4-12, bins de 2)
        coord_col = 'c_coord' if 'c_coord' in dump_data.columns else None
        if coord_col:
            coord_data = dump_data[coord_col].dropna()
            coord_bins = np.arange(4, 14, 2)  # [4, 6, 8, 10, 12]
            coord_hist, _ = np.histogram(coord_data, bins=coord_bins)
            
            for i, (start, end) in enumerate(zip(coord_bins[:-1], coord_bins[1:])):
                features[f'coord_hist_{int(start)}_{int(end)}'] = coord_hist[i]
        
        # Histograma de energía (rango personalizable, 10 bins)
        energy_col = 'c_peatom' if 'c_peatom' in dump_data.columns else None
        if energy_col:
            energy_data = dump_data[energy_col].dropna()
            energy_bins = np.linspace(self.energy_min_var.get(), self.energy_max_var.get(), 11)
            energy_hist, _ = np.histogram(energy_data, bins=energy_bins)
            
            for i in range(len(energy_hist)):
                features[f'energy_hist_bin_{i+1}'] = energy_hist[i]
        
        return features
    
    def process_dumps(self):
        """Procesar archivos dump y crear CSV con histogramas"""
        if not self.input_dir_var.get():
            messagebox.showwarning("Advertencia", "Selecciona el directorio de entrada")
            return
        
        if self.processing:
            messagebox.showwarning("Advertencia", "Ya hay un procesamiento en curso")
            return
        
        def process_thread():
            self.processing = True
            self.process_btn.config(state="disabled")
            
            try:
                input_path = Path(self.input_dir_var.get())
                output_path = Path(self.output_dir_var.get())
                output_path.mkdir(exist_ok=True)
                
                dump_files = list(input_path.glob("*.dump"))
                
                if not dump_files:
                    self.log_message("No se encontraron archivos .dump")
                    return
                
                self.log_message(f"Procesando {len(dump_files)} archivos dump...")
                
                all_data = []
                
                for i, dump_file in enumerate(dump_files, 1):
                    self.log_message(f"Procesando ({i}/{len(dump_files)}): {dump_file.name}")
                    
                    # Extraer número de átomos del encabezado
                    n_atoms = self.extract_atoms_from_lammps_file(dump_file)
                    if n_atoms is None:
                        self.log_message(f"Error: No se pudo leer {dump_file.name}")
                        continue
                    
                    # Calcular vacancias
                    vacancies = self.atm_total_var.get() - n_atoms
                    
                    try:
                        # Leer datos del dump (asumiendo formato estándar)
                        dump_data = pd.read_csv(dump_file, sep=' ', skiprows=9, 
                                              names=['id', 'type', 'x', 'y', 'z', 'c_peatom', 
                                                    'c_satom1', 'c_satom2', 'c_satom3', 'c_satom4', 
                                                    'c_satom5', 'c_satom6', 'c_coord', 'c_voro1', 'c_keatom'])
                        
                        # Calcular estadísticas básicas
                        stats = {
                            'filename': dump_file.name,
                            'n_atoms': n_atoms,
                            'vacancies': vacancies,
                            'mean_energy': dump_data['c_peatom'].mean(),
                            'std_energy': dump_data['c_peatom'].std(),
                            'mean_coord': dump_data['c_coord'].mean(),
                            'std_coord': dump_data['c_coord'].std(),
                            'min_energy': dump_data['c_peatom'].min(),
                            'max_energy': dump_data['c_peatom'].max(),
                            'min_coord': dump_data['c_coord'].min(),
                            'max_coord': dump_data['c_coord'].max()
                        }
                        
                        # Crear histogramas
                        hist_features = self.create_histograms(dump_data)
                        stats.update(hist_features)
                        
                        all_data.append(stats)
                        
                    except Exception as e:
                        self.log_message(f"Error procesando {dump_file.name}: {str(e)}")
                        continue
                
                # Crear DataFrame y guardar
                if all_data:
                    df = pd.DataFrame(all_data)
                    csv_output = output_path / "advanced_dataset.csv"
                    df.to_csv(csv_output, index=False)
                    
                    self.current_data = df
                    
                    self.log_message(f"Procesamiento completado!")
                    self.log_message(f"Archivo guardado: {csv_output}")
                    self.log_message(f"Total de muestras: {len(df)}")
                    self.log_message(f"Features generadas: {len(df.columns)}")
                    
                    # Notificar callback principal
                    self.data_loaded_callback(df)
                    
                    # Mostrar estadísticas básicas
                    self.log_message(f"\nEstadísticas del dataset:")
                    self.log_message(f"Vacancias - Min: {df['vacancies'].min()}, Max: {df['vacancies'].max()}, Mean: {df['vacancies'].mean():.2f}")
                    
                else:
                    self.log_message("No se pudo procesar ningún archivo")
                    
            except Exception as e:
                self.log_message(f"Error en procesamiento: {str(e)}")
                messagebox.showerror("Error", f"Error en procesamiento: {str(e)}")
            finally:
                self.processing = False
                self.process_btn.config(state="normal")
        
        # Ejecutar en hilo separado
        threading.Thread(target=process_thread, daemon=True).start()
    
    # =============================================================================
    # MÉTODOS DE ENTRENAMIENTO
    # =============================================================================
    
    def train_model(self):
        """Entrenar modelo de ML"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero carga o procesa los datos")
            return
        
        def train_thread():
            try:
                self.train_btn.config(state="disabled")
                self.log_message("Iniciando entrenamiento...")
                
                # Preparar datos
                feature_columns = [col for col in self.current_data.columns 
                                 if col not in ['filename', 'vacancies']]
                
                X = self.current_data[feature_columns]
                y = self.current_data['vacancies']
                
                self.log_message(f"Features utilizadas: {len(feature_columns)}")
                self.log_message(f"Muestras totales: {len(X)}")
                
                # División train/test
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=self.test_size_var.get(), 
                    random_state=self.random_state_var.get()
                )
                
                # Crear pipeline
                preprocessor = ColumnTransformer([
                    ('scaler', StandardScaler(), feature_columns)
                ])
                
                self.trained_model = Pipeline([
                    ('preprocessor', preprocessor),
                    ('regressor', RandomForestRegressor(
                        n_estimators=self.n_estimators_var.get(),
                        random_state=self.random_state_var.get(),
                        n_jobs=-1
                    ))
                ])
                
                # Entrenar
                self.log_message("Entrenando modelo...")
                self.trained_model.fit(X_train, y_train)
                
                # Evaluar
                train_pred = self.trained_model.predict(X_train)
                test_pred = self.trained_model.predict(X_test)
                
                train_mae = mean_absolute_error(y_train, train_pred)
                test_mae = mean_absolute_error(y_test, test_pred)
                train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
                test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
                train_r2 = r2_score(y_train, train_pred)
                test_r2 = r2_score(y_test, test_pred)
                
                # Mostrar resultados
                metrics_text = f"""
=== MÉTRICAS DEL MODELO ===
Algoritmo: Random Forest ({self.n_estimators_var.get()} estimadores)
Features: {len(feature_columns)}
Muestras entrenamiento: {len(X_train)}
Muestras prueba: {len(X_test)}

RENDIMIENTO:
Train MAE: {train_mae:.4f}
Test MAE: {test_mae:.4f}
Train RMSE: {train_rmse:.4f}
Test RMSE: {test_rmse:.4f}
Train R²: {train_r2:.4f}
Test R²: {test_r2:.4f}

INTERPRETACIÓN:
- MAE: Error promedio en número de vacancias
- RMSE: Error cuadrático medio
- R²: Proporción de varianza explicada (0-1, mejor=1)

FEATURES MÁS IMPORTANTES:
"""
                
                # Feature importance
                feature_importance = self.trained_model.named_steps['regressor'].feature_importances_
                importance_df = pd.DataFrame({
                    'feature': feature_columns,
                    'importance': feature_importance
                }).sort_values('importance', ascending=False)
                
                for i, row in importance_df.head(10).iterrows():
                    metrics_text += f"{row['feature'][:30]:30s}: {row['importance']:.4f}\n"
                
                self.metrics_text.delete(1.0, tk.END)
                self.metrics_text.insert(1.0, metrics_text)
                
                self.log_message("Entrenamiento completado exitosamente!")
                
                # Habilitar botones
                self.cv_btn.config(state="normal")
                self.save_model_btn.config(state="normal")
                
            except Exception as e:
                self.log_message(f"Error en entrenamiento: {str(e)}")
                messagebox.showerror("Error", f"Error en entrenamiento: {str(e)}")
            finally:
                self.train_btn.config(state="normal")
        
        threading.Thread(target=train_thread, daemon=True).start()
    
    def cross_validate(self):
        """Realizar validación cruzada"""
        if self.current_data is None or self.trained_model is None:
            messagebox.showwarning("Advertencia", "Primero entrena el modelo")
            return
        
        def cv_thread():
            try:
                self.cv_btn.config(state="disabled")
                self.log_message("Realizando validación cruzada...")
                
                feature_columns = [col for col in self.current_data.columns 
                                 if col not in ['filename', 'vacancies']]
                
                X = self.current_data[feature_columns]
                y = self.current_data['vacancies']
                
                # Validación cruzada con diferentes métricas
                cv_mae = cross_val_score(self.trained_model, X, y, cv=5, 
                                       scoring='neg_mean_absolute_error')
                cv_rmse = cross_val_score(self.trained_model, X, y, cv=5, 
                                        scoring='neg_root_mean_squared_error')
                cv_r2 = cross_val_score(self.trained_model, X, y, cv=5, 
                                      scoring='r2')
                
                cv_text = f"""

=== VALIDACIÓN CRUZADA (5-Fold) ===
MAE Scores: {[-score for score in cv_mae]}
MAE Mean: {-cv_mae.mean():.4f} ± {cv_mae.std():.4f}

RMSE Scores: {[-score for score in cv_rmse]}
RMSE Mean: {-cv_rmse.mean():.4f} ± {cv_rmse.std():.4f}

R² Scores: {cv_r2}
R² Mean: {cv_r2.mean():.4f} ± {cv_r2.std():.4f}

CONSISTENCIA DEL MODELO:
- Desviación estándar baja = modelo consistente
- R² > 0.8 = buen modelo predictivo
- MAE < 5 vacancias = predicciones útiles
"""
                
                self.metrics_text.insert(tk.END, cv_text)
                self.log_message("Validación cruzada completada")
                
            except Exception as e:
                self.log_message(f"Error en validación cruzada: {str(e)}")
            finally:
                self.cv_btn.config(state="normal")
        
        threading.Thread(target=cv_thread, daemon=True).start()
    
    def save_model(self):
        """Guardar modelo entrenado"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "No hay modelo entrenado")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Guardar modelo",
            defaultextension=".joblib",
            filetypes=[("Joblib files", "*.joblib"), ("Pickle files", "*.pkl")]
        )
        
        if filename:
            try:
                # Guardar modelo y metadatos
                model_data = {
                    'model': self.trained_model,
                    'feature_columns': [col for col in self.current_data.columns 
                                      if col not in ['filename', 'vacancies']],
                    'training_params': {
                        'n_estimators': self.n_estimators_var.get(),
                        'test_size': self.test_size_var.get(),
                        'random_state': self.random_state_var.get(),
                        'atm_total': self.atm_total_var.get(),
                        'energy_min': self.energy_min_var.get(),
                        'energy_max': self.energy_max_var.get()
                    }
                }
                
                joblib.dump(model_data, filename)
                self.log_message(f"Modelo guardado: {filename}")
                messagebox.showinfo("Éxito", f"Modelo guardado exitosamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando modelo: {str(e)}")
    
    def load_model(self):
        """Cargar modelo previamente entrenado"""
        filename = filedialog.askopenfilename(
            title="Cargar modelo",
            filetypes=[("Joblib files", "*.joblib"), ("Pickle files", "*.pkl")]
        )
        
        if filename:
            try:
                model_data = joblib.load(filename)
                
                if isinstance(model_data, dict):
                    self.trained_model = model_data['model']
                    
                    # Restaurar parámetros si están disponibles
                    if 'training_params' in model_data:
                        params = model_data['training_params']
                        self.n_estimators_var.set(params.get('n_estimators', 100))
                        self.atm_total_var.set(params.get('atm_total', 16384))
                        self.energy_min_var.set(params.get('energy_min', -4.0))
                        self.energy_max_var.set(params.get('energy_max', -2.0))
                    
                    self.log_message(f"Modelo cargado: {filename}")
                    self.log_message(f"Features requeridas: {len(model_data.get('feature_columns', []))}")
                    
                else:
                    # Modelo legacy
                    self.trained_model = model_data
                    self.log_message(f"Modelo legacy cargado: {filename}")
                
                # Habilitar botones
                self.cv_btn.config(state="normal")
                self.save_model_btn.config(state="normal")
                
                messagebox.showinfo("Éxito", f"Modelo cargado exitosamente")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando modelo: {str(e)}")
    
    # =============================================================================
    # MÉTODOS DE PREDICCIÓN
    # =============================================================================
    
    def predict_single(self):
        """Predecir archivo individual"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "Primero carga un modelo entrenado")
            return
        
        if not self.single_file_var.get():
            messagebox.showwarning("Advertencia", "Selecciona un archivo")
            return
        
        def predict_thread():
            try:
                dump_file = Path(self.single_file_var.get())
                
                self.log_message(f"Prediciendo: {dump_file.name}")
                
                # Procesar archivo
                n_atoms = self.extract_atoms_from_lammps_file(dump_file)
                if n_atoms is None:
                    self.log_message("Error leyendo archivo")
                    return
                
                # Leer datos del dump
                dump_data = pd.read_csv(dump_file, sep=' ', skiprows=9, 
                                      names=['id', 'type', 'x', 'y', 'z', 'c_peatom', 
                                            'c_satom1', 'c_satom2', 'c_satom3', 'c_satom4', 
                                            'c_satom5', 'c_satom6', 'c_coord', 'c_voro1', 'c_keatom'])
                
                # Crear features
                stats = {
                    'n_atoms': n_atoms,
                    'mean_energy': dump_data['c_peatom'].mean(),
                    'std_energy': dump_data['c_peatom'].std(),
                    'mean_coord': dump_data['c_coord'].mean(),
                    'std_coord': dump_data['c_coord'].std(),
                    'min_energy': dump_data['c_peatom'].min(),
                    'max_energy': dump_data['c_peatom'].max(),
                    'min_coord': dump_data['c_coord'].min(),
                    'max_coord': dump_data['c_coord'].max()
                }
                
                hist_features = self.create_histograms(dump_data)
                stats.update(hist_features)
                
                # Crear DataFrame para predicción
                feature_columns = [col for col in self.current_data.columns 
                                 if col not in ['filename', 'vacancies']]
                
                # Asegurar que todas las features están presentes
                for col in feature_columns:
                    if col not in stats:
                        stats[col] = 0.0  # Valor por defecto
                
                X_pred = pd.DataFrame([stats])[feature_columns]
                
                # Predecir
                prediction = self.trained_model.predict(X_pred)[0]
                real_vacancies = self.atm_total_var.get() - n_atoms
                error = abs(prediction - real_vacancies)
                
                result_text = f"""
=== PREDICCIÓN INDIVIDUAL ===
Archivo: {dump_file.name}
Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

DATOS DEL SISTEMA:
- Átomos encontrados: {n_atoms}
- Átomos totales configurados: {self.atm_total_var.get()}

RESULTADOS:
- Vacancias reales: {real_vacancies}
- Vacancias predichas: {prediction:.2f}
- Error absoluto: {error:.2f}
- Error relativo: {(error/real_vacancies*100):.1f}%

CARACTERÍSTICAS DEL SISTEMA:
- Energía promedio: {stats['mean_energy']:.4f} eV
- Coordinación promedio: {stats['mean_coord']:.2f}
- Rango energía: [{stats['min_energy']:.4f}, {stats['max_energy']:.4f}]
- Rango coordinación: [{stats['min_coord']:.0f}, {stats['max_coord']:.0f}]

CALIDAD DE PREDICCIÓN:
{"✓ Excelente" if error < 5 else "⚠ Aceptable" if error < 10 else "✗ Revisar modelo"}
"""
                
                self.prediction_text.delete(1.0, tk.END)
                self.prediction_text.insert(1.0, result_text)
                
            except Exception as e:
                self.log_message(f"Error en predicción: {str(e)}")
                messagebox.showerror("Error", f"Error en predicción: {str(e)}")
        
        threading.Thread(target=predict_thread, daemon=True).start()
    
    def predict_batch(self):
        """Predecir lote de archivos"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "Primero carga un modelo entrenado")
            return
        
        if not self.batch_dir_var.get():
            messagebox.showwarning("Advertencia", "Selecciona un directorio")
            return
        
        def predict_batch_thread():
            try:
                batch_path = Path(self.batch_dir_var.get())
                dump_files = list(batch_path.glob("*.dump"))
                
                if not dump_files:
                    self.log_message("No se encontraron archivos .dump")
                    return
                
                self.log_message(f"Prediciendo {len(dump_files)} archivos...")
                
                results = []
                feature_columns = [col for col in self.current_data.columns 
                                 if col not in ['filename', 'vacancies']]
                
                for i, dump_file in enumerate(dump_files, 1):
                    try:
                        self.log_message(f"Procesando ({i}/{len(dump_files)}): {dump_file.name}")
                        
                        # Similar al proceso individual
                        n_atoms = self.extract_atoms_from_lammps_file(dump_file)
                        if n_atoms is None:
                            continue
                        
                        dump_data = pd.read_csv(dump_file, sep=' ', skiprows=9, 
                                              names=['id', 'type', 'x', 'y', 'z', 'c_peatom', 
                                                    'c_satom1', 'c_satom2', 'c_satom3', 'c_satom4', 
                                                    'c_satom5', 'c_satom6', 'c_coord', 'c_voro1', 'c_keatom'])
                        
                        stats = {
                            'n_atoms': n_atoms,
                            'mean_energy': dump_data['c_peatom'].mean(),
                            'std_energy': dump_data['c_peatom'].std(),
                            'mean_coord': dump_data['c_coord'].mean(),
                            'std_coord': dump_data['c_coord'].std(),
                            'min_energy': dump_data['c_peatom'].min(),
                            'max_energy': dump_data['c_peatom'].max(),
                            'min_coord': dump_data['c_coord'].min(),
                            'max_coord': dump_data['c_coord'].max()
                        }
                        
                        hist_features = self.create_histograms(dump_data)
                        stats.update(hist_features)
                        
                        # Asegurar features completas
                        for col in feature_columns:
                            if col not in stats:
                                stats[col] = 0.0
                        
                        X_pred = pd.DataFrame([stats])[feature_columns]
                        prediction = self.trained_model.predict(X_pred)[0]
                        real_vacancies = self.atm_total_var.get() - n_atoms
                        
                        results.append({
                            'filename': dump_file.name,
                            'n_atoms': n_atoms,
                            'real_vacancies': real_vacancies,
                            'predicted_vacancies': prediction,
                            'error': abs(prediction - real_vacancies),
                            'rel_error_pct': abs(prediction - real_vacancies) / real_vacancies * 100 if real_vacancies > 0 else 0,
                            'mean_energy': stats['mean_energy'],
                            'mean_coord': stats['mean_coord']
                        })
                        
                    except Exception as e:
                        self.log_message(f"Error procesando {dump_file.name}: {str(e)}")
                        continue
                
                if results:
                    # Crear DataFrame con resultados
                    results_df = pd.DataFrame(results)
                    
                    # Guardar resultados
                    output_file = Path(self.output_dir_var.get()) / "batch_predictions.csv"
                    Path(self.output_dir_var.get()).mkdir(exist_ok=True)
                    results_df.to_csv(output_file, index=False)
                    
                    # Calcular estadísticas
                    mean_error = results_df['error'].mean()
                    median_error = results_df['error'].median()
                    max_error = results_df['error'].max()
                    min_error = results_df['error'].min()
                    mean_rel_error = results_df['rel_error_pct'].mean()
                    
                    # Contar predicciones por calidad
                    excellent = len(results_df[results_df['error'] < 5])
                    good = len(results_df[(results_df['error'] >= 5) & (results_df['error'] < 10)])
                    poor = len(results_df[results_df['error'] >= 10])
                    
                    batch_text = f"""
=== PREDICCIÓN POR LOTES ===
Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Archivos procesados: {len(results)}
Archivo de resultados: {output_file}

ESTADÍSTICAS DE ERROR:
- Error promedio: {mean_error:.2f} vacancias
- Error mediano: {median_error:.2f} vacancias
- Error mínimo: {min_error:.2f} vacancias
- Error máximo: {max_error:.2f} vacancias
- Error relativo promedio: {mean_rel_error:.1f}%

CALIDAD DE PREDICCIONES:
- Excelentes (error < 5): {excellent} ({excellent/len(results)*100:.1f}%)
- Buenas (error 5-10): {good} ({good/len(results)*100:.1f}%)
- Revisar (error > 10): {poor} ({poor/len(results)*100:.1f}%)

PRIMEROS 15 RESULTADOS:
{"Archivo":<25} {"Real":<6} {"Pred":<6} {"Error":<6} {"Rel%":<6}
{"-"*55}
"""
                    
                    for i, row in results_df.head(15).iterrows():
                        filename = row['filename'][:22] + "..." if len(row['filename']) > 25 else row['filename']
                        batch_text += f"{filename:<25} {row['real_vacancies']:<6.0f} {row['predicted_vacancies']:<6.1f} {row['error']:<6.1f} {row['rel_error_pct']:<6.1f}\n"
                    
                    if len(results_df) > 15:
                        batch_text += f"\n... y {len(results_df) - 15} archivos más (ver CSV completo)"
                    
                    self.prediction_text.delete(1.0, tk.END)
                    self.prediction_text.insert(1.0, batch_text)
                    
                    self.log_message(f"Predicción por lotes completada: {len(results)} archivos")
                    messagebox.showinfo("Completado", 
                                       f"Predicción completada!\n\n"
                                       f"Archivos procesados: {len(results)}\n"
                                       f"Error promedio: {mean_error:.2f} vacancias\n"
                                       f"Resultados guardados en: {output_file}")
                
            except Exception as e:
                self.log_message(f"Error en predicción por lotes: {str(e)}")
                messagebox.showerror("Error", f"Error en predicción por lotes: {str(e)}")
        
        threading.Thread(target=predict_batch_thread, daemon=True).start()
    
    # =============================================================================
    # MÉTODOS DE VISUALIZACIÓN
    # =============================================================================
    
    def clear_plots(self):
        """Limpiar todos los gráficos"""
        for ax in self.axes.flat:
            ax.clear()
        self.canvas.draw()
    
    def plot_distributions(self):
        """Mostrar distribuciones de los datos"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero carga los datos")
            return
        
        # Limpiar plots anteriores
        self.clear_plots()
        
        try:
            # Plot 1: Distribución de vacancias
            self.axes[0,0].hist(self.current_data['vacancies'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            self.axes[0,0].set_title('Distribución de Vacancias')
            self.axes[0,0].set_xlabel('Número de Vacancias')
            self.axes[0,0].set_ylabel('Frecuencia')
            self.axes[0,0].grid(True, alpha=0.3)
            
            # Plot 2: Distribución de energía promedio
            if 'mean_energy' in self.current_data.columns:
                self.axes[0,1].hist(self.current_data['mean_energy'], bins=20, alpha=0.7, color='lightcoral', edgecolor='black')
                self.axes[0,1].set_title('Distribución de Energía Promedio')
                self.axes[0,1].set_xlabel('Energía Promedio (eV)')
                self.axes[0,1].set_ylabel('Frecuencia')
                self.axes[0,1].grid(True, alpha=0.3)
            
            # Plot 3: Distribución de coordinación promedio
            if 'mean_coord' in self.current_data.columns:
                self.axes[1,0].hist(self.current_data['mean_coord'], bins=20, alpha=0.7, color='lightgreen', edgecolor='black')
                self.axes[1,0].set_title('Distribución de Coordinación Promedio')
                self.axes[1,0].set_xlabel('Coordinación Promedio')
                self.axes[1,0].set_ylabel('Frecuencia')
                self.axes[1,0].grid(True, alpha=0.3)
            
            # Plot 4: Scatter plot energía vs vacancias
            if 'mean_energy' in self.current_data.columns:
                scatter = self.axes[1,1].scatter(self.current_data['mean_energy'], self.current_data['vacancies'], 
                                               alpha=0.6, color='purple', s=30)
                self.axes[1,1].set_title('Energía vs Vacancias')
                self.axes[1,1].set_xlabel('Energía Promedio (eV)')
                self.axes[1,1].set_ylabel('Número de Vacancias')
                self.axes[1,1].grid(True, alpha=0.3)
                
                # Añadir línea de tendencia
                z = np.polyfit(self.current_data['mean_energy'], self.current_data['vacancies'], 1)
                p = np.poly1d(z)
                self.axes[1,1].plot(self.current_data['mean_energy'], p(self.current_data['mean_energy']), 
                                   "r--", alpha=0.8, linewidth=2)
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando distribuciones: {str(e)}")
    
    def plot_feature_importance(self):
        """Mostrar importancia de features"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "Primero entrena el modelo")
            return
        
        self.clear_plots()
        
        try:
            # Obtener importancias
            regressor = self.trained_model.named_steps['regressor']
            feature_names = [col for col in self.current_data.columns 
                           if col not in ['filename', 'vacancies']]
            
            importances = regressor.feature_importances_
            indices = np.argsort(importances)[::-1]
            
            # Top 20 features
            top_n = min(20, len(importances))
            
            # Plot 1: Barras horizontales (top 10)
            top_10_idx = indices[:10]
            top_10_names = [feature_names[i][:20] for i in top_10_idx]  # Truncar nombres largos
            top_10_scores = importances[top_10_idx]
            
            y_pos = np.arange(len(top_10_names))
            self.axes[0,0].barh(y_pos, top_10_scores, color='steelblue', alpha=0.7)
            self.axes[0,0].set_yticks(y_pos)
            self.axes[0,0].set_yticklabels(top_10_names, fontsize=8)
            self.axes[0,0].set_title('Top 10 Features Más Importantes')
            self.axes[0,0].set_xlabel('Importancia')
            self.axes[0,0].grid(True, alpha=0.3)
            
            # Plot 2: Importancia acumulada
            cumsum = np.cumsum(importances[indices])
            self.axes[0,1].plot(range(1, len(cumsum)+1), cumsum, 'b-', linewidth=2, marker='o', markersize=2)
            self.axes[0,1].axhline(y=0.8, color='r', linestyle='--', alpha=0.7, label='80% varianza')
            self.axes[0,1].axhline(y=0.9, color='orange', linestyle='--', alpha=0.7, label='90% varianza')
            self.axes[0,1].set_title('Importancia Acumulada')
            self.axes[0,1].set_xlabel('Número de Features')
            self.axes[0,1].set_ylabel('Importancia Acumulada')
            self.axes[0,1].legend()
            self.axes[0,1].grid(True, alpha=0.3)
            
            # Plot 3: Histograma de importancias
            self.axes[1,0].hist(importances, bins=20, alpha=0.7, color='green', edgecolor='black')
            self.axes[1,0].set_title('Distribución de Importancias')
            self.axes[1,0].set_xlabel('Importancia')
            self.axes[1,0].set_ylabel('Número de Features')
            self.axes[1,0].grid(True, alpha=0.3)
            
            # Plot 4: Features por categoría
            categories = ['coord', 'energy', 'stress', 'voro', 'n_atoms', 'other']
            cat_importance = {cat: 0 for cat in categories}
            
            for i, name in enumerate(feature_names):
                importance = importances[i]
                if 'coord' in name.lower():
                    cat_importance['coord'] += importance
                elif 'energy' in name.lower() or 'peatom' in name.lower():
                    cat_importance['energy'] += importance
                elif 'stress' in name.lower() or 'satom' in name.lower():
                    cat_importance['stress'] += importance
                elif 'voro' in name.lower():
                    cat_importance['voro'] += importance
                elif 'n_atoms' in name.lower():
                    cat_importance['n_atoms'] += importance
                else:
                    cat_importance['other'] += importance
            
            # Filtrar categorías con importancia > 0
            cats_with_data = {k: v for k, v in cat_importance.items() if v > 0}
            
            if cats_with_data:
                wedges, texts, autotexts = self.axes[1,1].pie(cats_with_data.values(), 
                                                            labels=cats_with_data.keys(), 
                                                            autopct='%1.1f%%',
                                                            startangle=90)
                self.axes[1,1].set_title('Importancia por Categoría')
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando feature importance: {str(e)}")
    
    def plot_predictions(self):
        """Mostrar predicciones vs valores reales"""
        if self.trained_model is None or self.current_data is None:
            messagebox.showwarning("Advertencia", "Primero entrena el modelo")
            return
        
        self.clear_plots()
        
        try:
            # Preparar datos
            feature_columns = [col for col in self.current_data.columns 
                             if col not in ['filename', 'vacancies']]
            
            X = self.current_data[feature_columns]
            y = self.current_data['vacancies']
            
            # Hacer predicciones
            predictions = self.trained_model.predict(X)
            residuals = y - predictions
            
            # Plot 1: Predicciones vs reales
            self.axes[0,0].scatter(y, predictions, alpha=0.6, color='blue', s=30)
            
            # Línea diagonal perfecta
            min_val = min(y.min(), predictions.min())
            max_val = max(y.max(), predictions.max())
            self.axes[0,0].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Predicción perfecta')
            
            self.axes[0,0].set_xlabel('Vacancias Reales')
            self.axes[0,0].set_ylabel('Vacancias Predichas')
            self.axes[0,0].set_title('Predicciones vs Valores Reales')
            self.axes[0,0].legend()
            self.axes[0,0].grid(True, alpha=0.3)
            
            # Calcular y mostrar R²
            r2 = r2_score(y, predictions)
            self.axes[0,0].text(0.05, 0.95, f'R² = {r2:.3f}', transform=self.axes[0,0].transAxes, 
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # Plot 2: Histograma de residuos
            self.axes[0,1].hist(residuals, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            self.axes[0,1].axvline(x=0, color='red', linestyle='--', linewidth=2)
            self.axes[0,1].set_xlabel('Residuos (Real - Predicho)')
            self.axes[0,1].set_ylabel('Frecuencia')
            self.axes[0,1].set_title('Distribución de Residuos')
            self.axes[0,1].grid(True, alpha=0.3)
            
            # Plot 3: Residuos vs predicciones
            self.axes[1,0].scatter(predictions, residuals, alpha=0.6, color='green', s=30)
            self.axes[1,0].axhline(y=0, color='red', linestyle='--', linewidth=2)
            self.axes[1,0].set_xlabel('Predicciones')
            self.axes[1,0].set_ylabel('Residuos')
            self.axes[1,0].set_title('Residuos vs Predicciones')
            self.axes[1,0].grid(True, alpha=0.3)
            
            # Plot 4: Errores absolutos
            abs_errors = np.abs(residuals)
            self.axes[1,1].scatter(y, abs_errors, alpha=0.6, color='orange', s=30)
            self.axes[1,1].set_xlabel('Vacancias Reales')
            self.axes[1,1].set_ylabel('Error Absoluto')
            self.axes[1,1].set_title('Error Absoluto vs Valores Reales')
            self.axes[1,1].grid(True, alpha=0.3)
            
            # Añadir estadísticas de error
            mae = mean_absolute_error(y, predictions)
            rmse = np.sqrt(mean_squared_error(y, predictions))
            self.axes[1,1].text(0.05, 0.95, f'MAE = {mae:.2f}\nRMSE = {rmse:.2f}', 
                               transform=self.axes[1,1].transAxes,
                               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrando predicciones: {str(e)}")
    
    def reset(self):
        """Reset completo del tab"""
        # Reset variables
        self.atm_total_var.set(16384)
        self.energy_min_var.set(-4.0)
        self.energy_max_var.set(-2.0)
        self.input_dir_var.set("")
        self.output_dir_var.set("./ml_results")
        self.n_estimators_var.set(100)
        self.test_size_var.set(0.2)
        self.random_state_var.set(42)
        self.single_file_var.set("")
        self.batch_dir_var.set("")
        
        # Reset estado
        self.current_data = None
        self.trained_model = None
        self.processing = False
        
        # Reset displays
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, "Tab reiniciado. Listo para procesar datos.")
        
        self.metrics_text.delete(1.0, tk.END)
        self.prediction_text.delete(1.0, tk.END)
        
        # Reset botones
        self.process_btn.config(state="normal")
        self.train_btn.config(state="normal")
        self.cv_btn.config(state="disabled")
        self.save_model_btn.config(state="disabled")
        
        # Reset gráficos
        self.clear_plots()
        
        self.log_message("Advanced ML Tab reiniciado")
"""
Advanced ML Tab con visualizaciones integradas
Incluye gráficos de predicciones vs reales, residuos, feature importance
"""
"""
Advanced ML Tab con visualizaciones integradas - VERSIÓN COMPLETA
Incluye gráficos de predicciones vs reales, residuos normalizados, feature importance
"""
"""
Advanced ML Tab con visualizaciones integradas - VERSIÓN COMPLETA
Incluye gráficos de predicciones vs reales, residuos normalizados, feature importance
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

class AdvancedMLTabWithPlots:
    """Advanced ML Tab con visualizaciones integradas"""
    
    def __init__(self, parent, data_loaded_callback):
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
        self.create_feature_analysis_tab()
        self.create_prediction_tab()
    
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
        self.notebook.add(results_frame, text="📊 Resultados")
        
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
        self.fig, self.axes = plt.subplots(2, 3, figsize=(18, 12))
        self.fig.tight_layout(pad=3.0)
        
        # Canvas para mostrar los gráficos
        self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_feature_analysis_tab(self):
        """Tab de análisis detallado de features"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="🔍 Análisis Features")
        
        # Botones de control
        control_frame = ttk.Frame(analysis_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="Actualizar Análisis", 
                  command=self.update_feature_analysis).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Exportar Feature Importance", 
                  command=self.export_feature_importance).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Exportar Modelo RF", 
                  command=self.export_rf_model).pack(side="left", padx=5)
        
        # Crear notebook interno para diferentes análisis
        self.analysis_notebook = ttk.Notebook(analysis_frame)
        self.analysis_notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Sub-tab 1: Feature Importance
        self.create_importance_subtab()
        
        # Sub-tab 2: Correlación de Features
        self.create_correlation_subtab()
        
        # Sub-tab 3: Métricas del Modelo
        self.create_model_metrics_subtab()
    
    def create_importance_subtab(self):
        """Sub-tab de importancia de features"""
        importance_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(importance_frame, text="Feature Importance")
        
        # Área de gráfico de importancia
        self.importance_fig, self.importance_ax = plt.subplots(figsize=(12, 8))
        self.importance_canvas = FigureCanvasTkAgg(self.importance_fig, importance_frame)
        self.importance_canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tabla de importancia
        table_frame = ttk.LabelFrame(importance_frame, text="Top Features", padding="5")
        table_frame.pack(fill="x", padx=5, pady=5)
        
        # Crear tabla con scrollbar
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill="both", expand=True)
        
        # Columnas de la tabla
        columns = ('Rank', 'Feature', 'Importance', 'Cumulative %')
        self.importance_tree = ttk.Treeview(table_container, columns=columns, show='headings', height=8)
        
        # Configurar encabezados
        self.importance_tree.heading('Rank', text='#')
        self.importance_tree.heading('Feature', text='Feature')
        self.importance_tree.heading('Importance', text='Importancia')
        self.importance_tree.heading('Cumulative %', text='Acumulado %')
        
        # Configurar anchos
        self.importance_tree.column('Rank', width=50, anchor='center')
        self.importance_tree.column('Feature', width=300, anchor='w')
        self.importance_tree.column('Importance', width=100, anchor='center')
        self.importance_tree.column('Cumulative %', width=100, anchor='center')
        
        # Scrollbar para tabla
        importance_scrollbar = ttk.Scrollbar(table_container, orient="vertical", 
                                           command=self.importance_tree.yview)
        self.importance_tree.configure(yscrollcommand=importance_scrollbar.set)
        
        self.importance_tree.pack(side="left", fill="both", expand=True)
        importance_scrollbar.pack(side="right", fill="y")
    
    def create_correlation_subtab(self):
        """Sub-tab de correlación entre features"""
        correlation_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(correlation_frame, text="Correlaciones")
        
        # Área de texto para correlaciones
        corr_text_frame = ttk.LabelFrame(correlation_frame, text="Correlaciones con Target", padding="10")
        corr_text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.correlation_text = scrolledtext.ScrolledText(corr_text_frame, height=20, wrap='word')
        self.correlation_text.pack(fill="both", expand=True)
    
    def create_model_metrics_subtab(self):
        """Sub-tab de métricas detalladas del modelo"""
        metrics_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(metrics_frame, text="Métricas del Modelo")
        
        # Área de métricas detalladas
        detailed_metrics_frame = ttk.LabelFrame(metrics_frame, text="Métricas Detalladas Random Forest", padding="10")
        detailed_metrics_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.detailed_metrics_text = scrolledtext.ScrolledText(detailed_metrics_frame, height=20, wrap='word')
        self.detailed_metrics_text.pack(fill="both", expand=True)
    
    def create_prediction_tab(self):
        """Tab de predicción"""
        pred_frame = ttk.Frame(self.notebook)
        self.notebook.add(pred_frame, text="🔮 Predicción")
        
        # Predicción individual
        single_group = ttk.LabelFrame(pred_frame, text="Predicción Individual", padding="10")
        single_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(single_group, text="Ingrese valores para las features principales:").pack(anchor='w')
        
        # Frame para inputs de features
        self.features_frame = ttk.Frame(single_group)
        self.features_frame.pack(fill='x', pady=10)
        
        ttk.Button(single_group, text="Predecir", command=self.predict_single).pack()
        
        # Resultados de predicción
        pred_results_group = ttk.LabelFrame(pred_frame, text="Resultados", padding="10")
        pred_results_group.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.prediction_text = scrolledtext.ScrolledText(pred_results_group, height=15, wrap='word')
        self.prediction_text.pack(fill='both', expand=True)
    
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
                    data = pd.read_csv(file_path, index_col=0)
                
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
                raise ValueError(f"No se encontró la columna target '{self.target_column}' en el dataset")
            
            # Definir feature columns (numéricas, excluyendo target)
            self.feature_columns = [col for col in numeric_columns if col != self.target_column]
            
            if not self.feature_columns:
                raise ValueError("No se encontraron columnas numéricas para usar como features")
            
            # Actualizar información
            self.update_dataset_info(text_columns)
            
            # Notificar al callback
            self.data_loaded_callback(data)
            
            # Actualizar interfaz de predicción
            self.update_prediction_interface()
            
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
            from sklearn.model_selection import train_test_split
            X_train, self.X_test, y_train, self.y_test = train_test_split(
                X_clean, y, 
                test_size=self.test_size_var.get(),
                random_state=self.random_state_var.get()
            )
            
            # Crear y entrenar modelo
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            
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
            from sklearn.model_selection import cross_val_score
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
            
            # Actualizar interfaz de predicción con features importantes
            self.update_prediction_interface_with_importance()
            
            messagebox.showinfo("Entrenamiento Completado", 
                               f"Modelo entrenado exitosamente!\n\n"
                               f"Test R²: {test_r2:.3f}\n"
                               f"Test MAE: {test_mae:.3f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error entrenando modelo:\n{str(e)}")
        finally:
            self.train_btn.config(state="normal")
    
    def update_feature_analysis(self):
        """Actualizar análisis de features"""
        if self.trained_model is None or not hasattr(self, 'feature_importance'):
            messagebox.showwarning("Advertencia", "Primero entrena un modelo")
            return
        
        try:
            # Actualizar gráfico de importancia
            self.update_importance_plot()
            
            # Actualizar tabla de importancia
            self.update_importance_table()
            
            # Actualizar correlaciones
            self.update_correlations()
            
            # Actualizar métricas detalladas
            self.update_detailed_metrics()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando análisis:\n{str(e)}")
    
    def update_importance_plot(self):
        """Actualizar gráfico de importancia de features"""
        self.importance_ax.clear()
        
        # Tomar top 20 features
        top_features = self.feature_importance.head(20)
        
        # Crear gráfico de barras horizontales
        bars = self.importance_ax.barh(range(len(top_features)), top_features['importance'], 
                                      color='steelblue', alpha=0.8)
        
        # Configurar ejes
        self.importance_ax.set_yticks(range(len(top_features)))
        self.importance_ax.set_yticklabels(top_features['feature'], fontsize=10)
        self.importance_ax.set_xlabel('Importancia', fontsize=12)
        self.importance_ax.set_title('Top 20 importancias de features (RF)', fontsize=14, fontweight='bold')
        
        # Invertir eje Y para mostrar más importante arriba
        self.importance_ax.invert_yaxis()
        
        # Agregar valores en las barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            self.importance_ax.text(width + 0.001, bar.get_y() + bar.get_height()/2, 
                                  f'{width:.3f}', ha='left', va='center', fontsize=9)
        
        # Mejorar apariencia
        self.importance_ax.grid(axis='x', alpha=0.3)
        self.importance_ax.spines['top'].set_visible(False)
        self.importance_ax.spines['right'].set_visible(False)
        
        self.importance_fig.tight_layout()
        self.importance_canvas.draw()
    
    def update_importance_table(self):
        """Actualizar tabla de importancia"""
        # Limpiar tabla anterior
        for item in self.importance_tree.get_children():
            self.importance_tree.delete(item)
        
        # Calcular porcentaje acumulativo
        cumulative_importance = np.cumsum(self.feature_importance['importance'])
        total_importance = cumulative_importance.iloc[-1]
        cumulative_percent = (cumulative_importance / total_importance) * 100
        
        # Llenar tabla con todas las features
        for i, (_, row) in enumerate(self.feature_importance.iterrows()):
            self.importance_tree.insert('', 'end', values=(
                i + 1,
                row['feature'],
                f"{row['importance']:.4f}",
                f"{cumulative_percent.iloc[i]:.1f}%"
            ))
    
    def update_correlations(self):
        """Actualizar análisis de correlaciones"""
        if self.current_data is None:
            return
        
        # Calcular correlaciones con el target
        correlations = self.current_data[self.feature_columns + [self.target_column]].corr()[self.target_column]
        correlations = correlations.drop(self.target_column).sort_values(key=abs, ascending=False)
        
        # Generar texto de correlaciones
        corr_text = """CORRELACIONES CON TARGET (VACANCIES)
=====================================

Las correlaciones muestran la relación lineal entre cada feature y el target.
Valores cercanos a ±1 indican fuerte correlación, cercanos a 0 indican poca correlación.

TOP 20 CORRELACIONES MÁS ALTAS:
"""
        
        for i, (feature, corr) in enumerate(correlations.head(20).items()):
            direction = "Positiva" if corr > 0 else "Negativa"
            strength = "Muy fuerte" if abs(corr) > 0.8 else "Fuerte" if abs(corr) > 0.6 else "Moderada" if abs(corr) > 0.4 else "Débil"
            corr_text += f"{i+1:2d}. {feature[:40]:40s}: {corr:+.4f} ({direction}, {strength})\n"
        
        corr_text += "\n\nTOP 10 CORRELACIONES MÁS BAJAS (MENOS INFORMATIVAS):\n"
        
        for i, (feature, corr) in enumerate(correlations.tail(10).items()):
            corr_text += f"{i+1:2d}. {feature[:40]:40s}: {corr:+.4f}\n"
        
        # Estadísticas de correlaciones
        corr_text += f"""

ESTADÍSTICAS DE CORRELACIONES:
  Media absoluta: {abs(correlations).mean():.4f}
  Mediana absoluta: {abs(correlations).median():.4f}
  Máxima correlación: {correlations.max():.4f} ({correlations.idxmax()})
  Mínima correlación: {correlations.min():.4f} ({correlations.idxmin()})
  
  Features con correlación > 0.5: {sum(abs(correlations) > 0.5)}
  Features con correlación > 0.7: {sum(abs(correlations) > 0.7)}
  Features con correlación > 0.9: {sum(abs(correlations) > 0.9)}
"""
        
        self.correlation_text.delete(1.0, tk.END)
        self.correlation_text.insert(1.0, corr_text)
    
    def update_detailed_metrics(self):
        """Actualizar métricas detalladas del modelo"""
        if self.trained_model is None:
            return
        
        # Obtener información detallada del Random Forest
        rf_info = f"""INFORMACIÓN DETALLADA DEL RANDOM FOREST
======================================

CONFIGURACIÓN DEL MODELO:
  Número de estimadores: {self.trained_model.n_estimators}
  Criterio de división: {self.trained_model.criterion}
  Profundidad máxima: {self.trained_model.max_depth if self.trained_model.max_depth else 'Sin límite'}
  Min muestras por split: {self.trained_model.min_samples_split}
  Min muestras por hoja: {self.trained_model.min_samples_leaf}
  Max features por split: {self.trained_model.max_features}
  Bootstrap: {'Sí' if self.trained_model.bootstrap else 'No'}
  Random state: {self.trained_model.random_state}

ESTADÍSTICAS DE LOS ÁRBOLES:
"""
        
        if hasattr(self.trained_model, 'estimators_'):
            tree_depths = [tree.tree_.max_depth for tree in self.trained_model.estimators_]
            tree_nodes = [tree.tree_.node_count for tree in self.trained_model.estimators_]
            tree_leaves = [tree.tree_.n_leaves for tree in self.trained_model.estimators_]
            
            rf_info += f"""  Profundidad promedio: {np.mean(tree_depths):.1f} ± {np.std(tree_depths):.1f}
  Profundidad mínima: {min(tree_depths)}
  Profundidad máxima: {max(tree_depths)}
  
  Nodos promedio por árbol: {np.mean(tree_nodes):.1f} ± {np.std(tree_nodes):.1f}
  Hojas promedio por árbol: {np.mean(tree_leaves):.1f} ± {np.std(tree_leaves):.1f}

ANÁLISIS DE FEATURES:
  Total features disponibles: {len(self.feature_columns)}
  Features con importancia > 0.01: {sum(self.feature_importance['importance'] > 0.01)}
  Features con importancia > 0.05: {sum(self.feature_importance['importance'] > 0.05)}
  Features con importancia > 0.10: {sum(self.feature_importance['importance'] > 0.10)}
  
  Top 5 features representan: {self.feature_importance.head(5)['importance'].sum():.1%} de la importancia
  Top 10 features representan: {self.feature_importance.head(10)['importance'].sum():.1%} de la importancia
  Top 20 features representan: {self.feature_importance.head(20)['importance'].sum():.1%} de la importancia
"""
        
        # Información de rendimiento si está disponible
        if self.X_test is not None and self.y_test is not None:
            # Calcular métricas adicionales
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, explained_variance_score
            
            mae = mean_absolute_error(self.y_test, self.test_predictions)
            rmse = np.sqrt(mean_squared_error(self.y_test, self.test_predictions))
            r2 = r2_score(self.y_test, self.test_predictions)
            evs = explained_variance_score(self.y_test, self.test_predictions)
            
            # Error percentual absoluto medio (MAPE)
            mape = np.mean(np.abs((self.y_test - self.test_predictions) / self.y_test)) * 100
            
            # Error mediano absoluto
            median_ae = np.median(np.abs(self.y_test - self.test_predictions))
            
            rf_info += f"""

MÉTRICAS DE RENDIMIENTO DETALLADAS:
  R² Score: {r2:.6f}
  Explained Variance Score: {evs:.6f}
  Mean Absolute Error: {mae:.4f}
  Root Mean Squared Error: {rmse:.4f}
  Mean Absolute Percentage Error: {mape:.2f}%
  Median Absolute Error: {median_ae:.4f}
  
  Error estándar: {np.std(self.y_test - self.test_predictions):.4f}
  Error mínimo: {np.min(np.abs(self.y_test - self.test_predictions)):.4f}
  Error máximo: {np.max(np.abs(self.y_test - self.test_predictions)):.4f}

DISTRIBUCIÓN DE ERRORES:
  25% de predicciones tienen error < {np.percentile(np.abs(self.y_test - self.test_predictions), 25):.2f}
  50% de predicciones tienen error < {np.percentile(np.abs(self.y_test - self.test_predictions), 50):.2f}
  75% de predicciones tienen error < {np.percentile(np.abs(self.y_test - self.test_predictions), 75):.2f}
  90% de predicciones tienen error < {np.percentile(np.abs(self.y_test - self.test_predictions), 90):.2f}
  95% de predicciones tienen error < {np.percentile(np.abs(self.y_test - self.test_predictions), 95):.2f}
"""
        
        self.detailed_metrics_text.delete(1.0, tk.END)
        self.detailed_metrics_text.insert(1.0, rf_info)
    
    def export_feature_importance(self):
        """Exportar tabla de feature importance"""
        if not hasattr(self, 'feature_importance'):
            messagebox.showwarning("Advertencia", "No hay feature importance para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Feature Importance",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                # Añadir porcentaje acumulativo
                cumulative_importance = np.cumsum(self.feature_importance['importance'])
                total_importance = cumulative_importance.iloc[-1]
                cumulative_percent = (cumulative_importance / total_importance) * 100
                
                export_df = self.feature_importance.copy()
                export_df['cumulative_importance'] = cumulative_importance
                export_df['cumulative_percent'] = cumulative_percent
                export_df['rank'] = range(1, len(export_df) + 1)
                
                # Reordenar columnas
                export_df = export_df[['rank', 'feature', 'importance', 'cumulative_importance', 'cumulative_percent']]
                
                if file_path.endswith('.xlsx'):
                    export_df.to_excel(file_path, index=False)
                else:
                    export_df.to_csv(file_path, index=False)
                
                messagebox.showinfo("Éxito", f"Feature importance exportado a:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando feature importance:\n{str(e)}")
    
    def export_rf_model(self):
        """Exportar modelo Random Forest completo con metadatos"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "No hay modelo entrenado para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Modelo Random Forest",
            defaultextension=".joblib",
            filetypes=[("Joblib files", "*.joblib")]
        )
        
        if file_path:
            try:
                import joblib
                from datetime import datetime
                
                # Crear paquete completo del modelo
                model_package = {
                    'model': self.trained_model,
                    'feature_columns': self.feature_columns,
                    'target_column': self.target_column,
                    'feature_importance': self.feature_importance,
                    'training_params': {
                        'n_estimators': self.n_estimators_var.get(),
                        'test_size': self.test_size_var.get(),
                        'random_state': self.random_state_var.get()
                    },
                    'model_info': {
                        'n_features': len(self.feature_columns),
                        'n_samples_train': len(self.current_data) if self.current_data is not None else None,
                        'training_date': datetime.now().isoformat(),
                        'model_type': 'RandomForestRegressor',
                        'sklearn_version': None  # Se puede añadir si se importa sklearn
                    }
                }
                
                # Añadir métricas de rendimiento si están disponibles
                if self.X_test is not None and self.y_test is not None:
                    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
                    
                    mae = mean_absolute_error(self.y_test, self.test_predictions)
                    rmse = np.sqrt(mean_squared_error(self.y_test, self.test_predictions))
                    r2 = r2_score(self.y_test, self.test_predictions)
                    
                    model_package['performance_metrics'] = {
                        'test_mae': mae,
                        'test_rmse': rmse,
                        'test_r2': r2,
                        'n_test_samples': len(self.X_test)
                    }
                
                # Guardar modelo
                joblib.dump(model_package, file_path)
                
                messagebox.showinfo("Éxito", 
                                   f"Modelo Random Forest exportado exitosamente!\n\n"
                                   f"Archivo: {file_path}\n"
                                   f"Incluye: modelo, features, importancia, métricas\n"
                                   f"Features: {len(self.feature_columns)}\n"
                                   f"Estimadores: {self.trained_model.n_estimators}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando modelo:\n{str(e)}")
    
    def update_plots(self):
        """Actualizar todos los gráficos con residuos normalizados"""
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
            
            # Configurar estilo
            plt.style.use('default')
            sns.set_palette("husl")
            
            # CALCULAR RESIDUOS NORMALIZADOS: 1 - pred/real
            # Evitar división por cero
            y_test_safe = self.y_test.copy()
            y_test_safe[y_test_safe == 0] = 1e-10  # Reemplazar ceros con valor muy pequeño
            
            normalized_residuals = 1 - (self.test_predictions / y_test_safe)
            
            # 1. Predicciones vs Valores Reales
            ax1 = self.axes[0, 0]
            ax1.scatter(self.y_test, self.test_predictions, alpha=0.6, color='red', s=50)
            
            # Línea diagonal perfecta
            min_val = min(self.y_test.min(), self.test_predictions.min())
            max_val = max(self.y_test.max(), self.test_predictions.max())
            ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Predicción perfecta')
            
            ax1.set_xlabel('Valores Reales (y_true)')
            ax1.set_ylabel('Predicciones (y_pred)')
            ax1.set_title('Predicciones vs Valores Reales')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Calcular y mostrar métricas
            from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
            r2 = r2_score(self.y_test, self.test_predictions)
            mae = mean_absolute_error(self.y_test, self.test_predictions)
            rmse = np.sqrt(mean_squared_error(self.y_test, self.test_predictions))
            
            ax1.text(0.05, 0.95, f'R² = {r2:.3f}\nMAE = {mae:.3f}\nRMSE = {rmse:.3f}', 
                    transform=ax1.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                    verticalalignment='top')
            
            # 2. Gráfico de Residuos NORMALIZADOS
            ax2 = self.axes[0, 1]
            ax2.scatter(self.test_predictions, normalized_residuals, alpha=0.6, color='red', s=50)
            ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
            ax2.set_xlabel('Valores Predichos (y_pred)')
            ax2.set_ylabel('Residuos Normalizados (1 - pred/real)')
            ax2.set_title('Gráfico de Residuos Normalizados')
            ax2.grid(True, alpha=0.3)
            
            # 3. Distribución de Residuos NORMALIZADOS
            ax3 = self.axes[0, 2]
            ax3.hist(normalized_residuals, bins=20, alpha=0.7, color='red', edgecolor='black')
            ax3.axvline(x=0, color='red', linestyle='--', linewidth=2)
            ax3.set_xlabel('Residuos Normalizados')
            ax3.set_ylabel('Frecuencia')
            ax3.set_title('Distribución de Residuos Normalizados')
            ax3.grid(True, alpha=0.3)
            
            # 4. Serie de Predicciones por Muestra
            ax4 = self.axes[1, 0]
            indices = range(len(self.y_test))
            ax4.plot(indices, self.y_test.values, 'o-', label='Valores Reales', color='orange', alpha=0.7)
            ax4.plot(indices, self.test_predictions, 'o-', label='Predicciones', color='blue', alpha=0.7)
            ax4.set_xlabel('Índice de Muestra')
            ax4.set_ylabel('Valor')
            ax4.set_title('Serie de Predicciones por Muestra')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            # 5. Errores Absolutos NORMALIZADOS por Muestra
            ax5 = self.axes[1, 1]
            abs_normalized_errors = np.abs(normalized_residuals)
            ax5.bar(indices, abs_normalized_errors, alpha=0.7, color='purple')
            ax5.set_xlabel('Índice de Muestra')
            ax5.set_ylabel('Error Absoluto Normalizado')
            ax5.set_title('Errores Absolutos Normalizados por Muestra')
            ax5.grid(True, alpha=0.3)
            
            # 6. Métricas de Evaluación ACTUALIZADAS
            ax6 = self.axes[1, 2]
            ax6.axis('off')  # Sin ejes para este panel
            
            # Calcular métricas adicionales con residuos normalizados
            mean_norm_error = np.mean(np.abs(normalized_residuals))
            std_norm_error = np.std(normalized_residuals)
            max_norm_error = np.max(abs_normalized_errors)
            
            # MAPE usando la fórmula original
            mape = np.mean(np.abs((self.y_test - self.test_predictions) / self.y_test)) * 100 if (self.y_test != 0).all() else 0
            
            metrics_text = f"""Métricas de Evaluación

MAE: {mae:.4f}
RMSE: {rmse:.4f}
R²: {r2:.4f}
MAPE: {mape:.2f}%
Max Error: {np.max(np.abs(self.y_test - self.test_predictions)):.4f}

Residuos Normalizados:
Mean |Error Norm|: {mean_norm_error:.4f}
Std Error Norm: {std_norm_error:.4f}
Max Error Norm: {max_norm_error:.4f}

Muestras: {len(self.y_test)}
Rango real: [{self.y_test.min():.2f}, {self.y_test.max():.2f}]
Rango pred: [{self.test_predictions.min():.2f}, {self.test_predictions.max():.2f}]"""
            
            ax6.text(0.1, 0.9, metrics_text, transform=ax6.transAxes, fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                    verticalalignment='top', fontfamily='monospace')
            
            # Ajustar layout
            self.fig.tight_layout(pad=2.0)
            self.canvas.draw()
            
            # Actualizar análisis de features si está disponible
            if hasattr(self, 'update_feature_analysis'):
                self.update_feature_analysis()
            
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
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")]
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráficos guardados en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando gráficos:\n{str(e)}")
    
    def update_prediction_interface(self):
        """Actualizar interfaz de predicción con features principales"""
        # Limpiar frame anterior
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        # Mostrar las primeras 10 features
        display_features = self.feature_columns[:10]
        self.feature_vars = {}
        
        for i, feature in enumerate(display_features):
            row = i // 2
            col = (i % 2) * 3
            
            ttk.Label(self.features_frame, text=f"{feature}:").grid(row=row, column=col, sticky='w', padx=5, pady=2)
            
            var = tk.DoubleVar(value=0.0)
            self.feature_vars[feature] = var
            
            entry = ttk.Entry(self.features_frame, textvariable=var, width=15)
            entry.grid(row=row, column=col+1, padx=5, pady=2)
    
    def update_prediction_interface_with_importance(self):
        """Actualizar interfaz de predicción con features más importantes"""
        if not hasattr(self, 'feature_importance'):
            return
        
        # Limpiar frame anterior
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        # Mostrar top 10 features más importantes
        top_features = self.feature_importance.head(10)['feature'].tolist()
        self.feature_vars = {}
        
        for i, feature in enumerate(top_features):
            row = i // 2
            col = (i % 2) * 3
            
            # Obtener valor promedio para sugerir
            avg_value = self.current_data[feature].mean()
            
            label_text = f"{feature} (avg: {avg_value:.2f}):"
            ttk.Label(self.features_frame, text=label_text).grid(row=row, column=col, sticky='w', padx=5, pady=2)
            
            var = tk.DoubleVar(value=avg_value)
            self.feature_vars[feature] = var
            
            entry = ttk.Entry(self.features_frame, textvariable=var, width=15)
            entry.grid(row=row, column=col+1, padx=5, pady=2)
    
    def predict_single(self):
        """Realizar predicción individual"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "Primero entrena un modelo")
            return
        
        try:
            # Crear vector de features con valores por defecto
            feature_vector = []
            input_features = []
            
            for feature in self.feature_columns:
                if feature in self.feature_vars:
                    value = self.feature_vars[feature].get()
                    input_features.append(f"{feature}: {value:.3f}")
                else:
                    value = self.current_data[feature].mean()
                
                feature_vector.append(value)
            
            # Realizar predicción
            X_pred = np.array(feature_vector).reshape(1, -1)
            prediction = self.trained_model.predict(X_pred)[0]
            
            # Obtener intervalo de confianza aproximado
            tree_predictions = [tree.predict(X_pred)[0] for tree in self.trained_model.estimators_]
            pred_std = np.std(tree_predictions)
            
            # Mostrar resultado
            result_text = f"""PREDICCIÓN INDIVIDUAL
====================

VALORES DE ENTRADA (top features):
"""
            
            for input_feat in input_features:
                result_text += f"  • {input_feat}\n"
            
            result_text += f"""

RESULTADO:
  Vacancias predichas: {prediction:.2f}
  Rango estimado: {prediction - 1.96*pred_std:.2f} - {prediction + 1.96*pred_std:.2f}
  Incertidumbre: ± {1.96*pred_std:.2f}

INTERPRETACIÓN:
  El modelo predice {prediction:.0f} vacancias con una 
  incertidumbre de ±{1.96*pred_std:.1f} vacancias (95% confianza).
"""
            
            self.prediction_text.delete(1.0, tk.END)
            self.prediction_text.insert(1.0, result_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en predicción:\n{str(e)}")
    
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
                import joblib
                
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
                import joblib
                
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
    
    def export_model(self):
        """Exportar modelo (wrapper para compatibilidad)"""
        self.save_model()
    
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
        self.prediction_text.delete(1.0, tk.END)
        
        # Reset botones
        self.save_btn.config(state="disabled")
        
        # Limpiar interfaz de predicción
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        # Limpiar gráficos
        for ax in self.axes.flat:
            ax.clear()
            ax.text(0.5, 0.5, 'Carga un dataset\ny entrena un modelo', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
        self.canvas.draw()


# Función adicional para crear gráfico de feature importance como en tu imagen
def create_feature_importance_plot():
    """Crear gráfico separado de feature importance (similar a tu imagen)"""
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    def plot_feature_importance_standalone(feature_importance_df, top_n=20):
        """
        Crear gráfico de barras horizontales de feature importance
        Parámetros:
        - feature_importance_df: DataFrame con columnas 'feature' e 'importance'  
        - top_n: número de features a mostrar
        """
        # Configurar estilo
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Tomar top N features
        top_features = feature_importance_df.head(top_n)
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Crear gráfico de barras horizontales
        bars = ax.barh(range(len(top_features)), top_features['importance'], 
                      color='steelblue', alpha=0.8)
        
        # Configurar ejes
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'])
        ax.set_xlabel('Importancia', fontsize=12)
        ax.set_title(f'Top {top_n} importancias de features (RF)', fontsize=14, fontweight='bold')
        
        # Invertir eje Y para mostrar más importante arriba
        ax.invert_yaxis()
        
        # Agregar valores en las barras
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width + 0.001, bar.get_y() + bar.get_height()/2, 
                   f'{width:.3f}', ha='left', va='center', fontsize=9)
        
        # Mejorar apariencia
        ax.grid(axis='x', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        return fig, ax
    
    return plot_feature_importance_standalone


# Ejemplo de uso principal
if __name__ == "__main__":
    """
    Ejemplo de cómo usar la clase AdvancedMLTabWithPlots
    """
    import tkinter as tk
    from tkinter import ttk
    
    def data_callback(data):
        print(f"Dataset cargado: {data.shape}")
    
    # Crear ventana principal
    root = tk.Tk()
    root.title("Advanced ML with Plots - Ejemplo")
    root.geometry("1400x900")
    
    # Crear notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Crear instancia del tab avanzado
    ml_tab = AdvancedMLTabWithPlots(notebook, data_callback)
    notebook.add(ml_tab.frame, text="Advanced ML")
    
    # Iniciar aplicación
    root.mainloop()


# Funciones auxiliares adicionales para análisis
def calculate_feature_stability(model, X_data, y_data, n_bootstraps=100):
    """
    Calcular estabilidad de importancia de features usando bootstrap
    
    Parámetros:
    - model: modelo Random Forest entrenado
    - X_data: datos de features para bootstrap
    - y_data: datos de target correspondientes
    - n_bootstraps: número de iteraciones bootstrap
    
    Retorna:
    - DataFrame con estadísticas de estabilidad por feature
    """
    from sklearn.utils import resample
    
    feature_importances = []
    
    for _ in range(n_bootstraps):
        # Bootstrap sample
        X_bootstrap, y_bootstrap = resample(X_data, y_data, random_state=None)
        
        # Re-entrenar modelo en muestra bootstrap
        bootstrap_model = type(model)(**model.get_params())
        bootstrap_model.fit(X_bootstrap, y_bootstrap)
        
        # Guardar importancias
        feature_importances.append(bootstrap_model.feature_importances_)
    
    # Convertir a DataFrame
    importances_df = pd.DataFrame(feature_importances, columns=X_data.columns)
    
    # Calcular estadísticas
    stability_stats = pd.DataFrame({
        'feature': X_data.columns,
        'mean_importance': importances_df.mean(),
        'std_importance': importances_df.std(),
        'cv_importance': importances_df.std() / importances_df.mean(),  # Coeficiente de variación
        'min_importance': importances_df.min(),
        'max_importance': importances_df.max()
    }).sort_values('mean_importance', ascending=False)
    
    return stability_stats


def generate_model_report(ml_tab_instance, output_path=None):
    """
    Generar reporte completo del modelo en formato texto
    
    Parámetros:
    - ml_tab_instance: instancia de AdvancedMLTabWithPlots
    - output_path: ruta para guardar reporte (opcional)
    
    Retorna:
    - String con reporte completo
    """
    if ml_tab_instance.trained_model is None:
        return "No hay modelo entrenado para generar reporte"
    
    from datetime import datetime
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    
    # Calcular métricas
    mae = mean_absolute_error(ml_tab_instance.y_test, ml_tab_instance.test_predictions)
    rmse = np.sqrt(mean_squared_error(ml_tab_instance.y_test, ml_tab_instance.test_predictions))
    r2 = r2_score(ml_tab_instance.y_test, ml_tab_instance.test_predictions)
    
    # Calcular residuos normalizados
    y_test_safe = ml_tab_instance.y_test.copy()
    y_test_safe[y_test_safe == 0] = 1e-10
    normalized_residuals = 1 - (ml_tab_instance.test_predictions / y_test_safe)
    
    report = f"""
REPORTE DE MODELO RANDOM FOREST
===============================
Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONFIGURACIÓN DEL MODELO:
  Estimadores: {ml_tab_instance.trained_model.n_estimators}
  Criterio: {ml_tab_instance.trained_model.criterion}
  Features utilizadas: {len(ml_tab_instance.feature_columns)}
  Target: {ml_tab_instance.target_column}

DATOS:
  Total muestras: {len(ml_tab_instance.current_data)}
  Muestras entrenamiento: {len(ml_tab_instance.y_test) * (1 / ml_tab_instance.test_size_var.get() - 1):.0f}
  Muestras prueba: {len(ml_tab_instance.y_test)}
  Test size: {ml_tab_instance.test_size_var.get():.1%}

MÉTRICAS DE RENDIMIENTO:
  R² Score: {r2:.4f}
  MAE: {mae:.4f}
  RMSE: {rmse:.4f}
  MAPE: {np.mean(np.abs((ml_tab_instance.y_test - ml_tab_instance.test_predictions) / ml_tab_instance.y_test)) * 100:.2f}%

RESIDUOS NORMALIZADOS (1 - pred/real):
  Error normalizado medio: {np.mean(np.abs(normalized_residuals)):.4f}
  Desviación estándar: {np.std(normalized_residuals):.4f}
  Error máximo normalizado: {np.max(np.abs(normalized_residuals)):.4f}

TOP 10 FEATURES MÁS IMPORTANTES:
"""
    
    for i, (_, row) in enumerate(ml_tab_instance.feature_importance.head(10).iterrows()):
        report += f"  {i+1:2d}. {row['feature'][:50]:50s}: {row['importance']:.4f}\n"
    
    report += f"""

DISTRIBUCIÓN DE ERRORES:
  P25: {np.percentile(np.abs(ml_tab_instance.y_test - ml_tab_instance.test_predictions), 25):.2f}
  P50: {np.percentile(np.abs(ml_tab_instance.y_test - ml_tab_instance.test_predictions), 50):.2f}
  P75: {np.percentile(np.abs(ml_tab_instance.y_test - ml_tab_instance.test_predictions), 75):.2f}
  P90: {np.percentile(np.abs(ml_tab_instance.y_test - ml_tab_instance.test_predictions), 90):.2f}
  P95: {np.percentile(np.abs(ml_tab_instance.y_test - ml_tab_instance.test_predictions), 95):.2f}

INTERPRETACIÓN:
  Calidad del modelo: {'Excelente' if r2 > 0.9 else 'Bueno' if r2 > 0.7 else 'Moderado' if r2 > 0.5 else 'Pobre'}
  Precisión: {'Alta' if mae < 5 else 'Media' if mae < 10 else 'Baja'}
  
RECOMENDACIONES:
"""
    
    if r2 < 0.7:
        report += "  - Considerar más features o ingeniería de features\n"
        report += "  - Probar hiperparámetros diferentes\n"
    if mae > 10:
        report += "  - Revisar outliers en los datos\n"
        report += "  - Considerar transformaciones de datos\n"
    if np.std(normalized_residuals) > 0.3:
        report += "  - Alta variabilidad en errores normalizados\n"
        report += "  - Considerar estratificación por rangos de target\n"
    
    # Guardar reporte si se especifica ruta
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Reporte guardado en: {output_path}")
    
    return report