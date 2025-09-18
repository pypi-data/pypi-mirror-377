#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación simplificada - Vacancy Predictor con Batch Processing y Advanced ML
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
import sys

# Importar tabs necesarios
from vacancy_predictor.gui.tabs.batch_processor_tab import BatchProcessingTab
from vacancy_predictor.gui.tabs.advanced_ml_tab import AdvancedMLTab

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vacancy_predictor.log')
    ]
)
logger = logging.getLogger(__name__)

class VacancyPredictorGUI:
    """Aplicación simplificada con Batch Processing y Advanced ML"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacancy Predictor - ML Suite")
        self.root.geometry("1400x900")
        
        # Maximizar ventana según SO
        try:
            if sys.platform == 'win32':
                self.root.state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except:
            pass
        
        # Referencias a datos actuales
        self.current_data = None
        self.current_batch_dataset = None
        self.current_advanced_data = None
        
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        logger.info("Vacancy Predictor ML Suite initialized")
    
    def setup_styles(self):
        """Configurar estilos"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Estilos personalizados
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TButton', foreground='green')
        style.configure('Action.TButton', foreground='blue')
        style.configure('Processing.TButton', foreground='orange')
        style.configure('Advanced.TButton', foreground='purple')
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='navy')
    
    def create_menu(self):
        """Crear menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.reset_application)
        file_menu.add_separator()
        file_menu.add_command(label="Import Dataset", command=self.import_dataset)
        file_menu.add_command(label="Export All Data", command=self.export_all_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Menú Batch Processing
        batch_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Batch", menu=batch_menu)
        batch_menu.add_command(label="Process Directory", command=self.focus_batch_tab)
        batch_menu.add_command(label="Load Dataset", command=self.load_batch_dataset)
        batch_menu.add_separator()
        batch_menu.add_command(label="Export Results", command=self.export_batch_results)
        
        # Menú Advanced ML
        ml_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Advanced ML", menu=ml_menu)
        ml_menu.add_command(label="Load Dataset & Train", command=self.focus_advanced_ml_tab)
        ml_menu.add_separator()
        ml_menu.add_command(label="Export Model", command=self.export_models)
        
        # Menú Tools
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Data Statistics", command=self.show_data_statistics)
        tools_menu.add_command(label="Memory Usage", command=self.show_memory_usage)
        
        # Menú Help
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Crear interfaz principal con tabs"""
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # 1. PROCESAMIENTO BATCH
        self.batch_tab = BatchProcessingTab(self.notebook, self.on_batch_data_loaded)
        self.notebook.add(self.batch_tab.frame, text="🔄 Batch Processing")
        
        # 2. ADVANCED ML CORREGIDO
        self.advanced_ml_tab = AdvancedMLTabCorrected(self.notebook, self.on_advanced_data_loaded)
        self.notebook.add(self.advanced_ml_tab.frame, text="🧠 Advanced ML")
        
        # Vincular eventos
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_status_bar(self):
        """Crear barra de estado"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x")
        
        # Mensaje principal
        self.status_var = tk.StringVar(value="Vacancy Predictor Ready - Load dataset or process batch files")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                               relief="sunken", anchor="w")
        status_label.pack(side="left", fill="x", expand=True)
        
        # Indicadores
        self.memory_var = tk.StringVar(value="Memory: 0 MB")
        memory_label = ttk.Label(self.status_frame, textvariable=self.memory_var, 
                               relief="sunken", anchor="e", width=15)
        memory_label.pack(side="right")
        
        self.datasets_var = tk.StringVar(value="Datasets: 0")
        datasets_label = ttk.Label(self.status_frame, textvariable=self.datasets_var,
                                 relief="sunken", anchor="e", width=12)
        datasets_label.pack(side="right")

    def update_status(self, message):
        """Actualizar mensaje de estado"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def update_indicators(self):
        """Actualizar indicadores de la barra de estado"""
        datasets = 0
        total_memory = 0
        
        # Contar datasets y memoria
        for data in [self.current_data, self.current_batch_dataset, self.current_advanced_data]:
            if data is not None:
                datasets += 1
                try:
                    total_memory += data.memory_usage(deep=True).sum() / (1024 * 1024)
                except:
                    total_memory += sys.getsizeof(data) / (1024 * 1024)
        
        # Actualizar
        self.datasets_var.set(f"Datasets: {datasets}")
        self.memory_var.set(f"Memory: {total_memory:.1f} MB")

    # =============================================================================
    # CALLBACKS
    # =============================================================================
    
    def on_batch_data_loaded(self, data):
        """Callback cuando se cargan datos del procesamiento batch"""
        self.current_batch_dataset = data
        self.current_data = data
        
        self.update_status(f"Batch dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()
        
        # Cargar automáticamente en Advanced ML si está disponible
        try:
            if hasattr(self.advanced_ml_tab, 'load_dataset_from_dataframe'):
                self.advanced_ml_tab.load_dataset_from_dataframe(data)
        except Exception as e:
            logger.warning(f"Could not sync batch data to Advanced ML: {e}")
    
    def on_advanced_data_loaded(self, data):
        """Callback para datos del Advanced ML tab"""
        self.current_advanced_data = data
        self.current_data = data
        
        self.update_status(f"Advanced ML dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()
        
    def on_tab_changed(self, event):
        """Callback cuando cambia el tab activo"""
        try:
            selected_tab = event.widget.tab('current')['text']
            self.update_status(f"Active tab: {selected_tab}")
        except:
            pass

    # =============================================================================
    # MÉTODOS DE NAVEGACIÓN
    # =============================================================================
    
    def focus_batch_tab(self):
        """Enfocar el tab de procesamiento batch"""
        self.notebook.select(0)
    
    def focus_advanced_ml_tab(self):
        """Enfocar el tab de Advanced ML"""
        self.notebook.select(1)

    # =============================================================================
    # MÉTODOS DE DATOS
    # =============================================================================
    
    def import_dataset(self):
        """Importar dataset desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Importar Dataset",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    data = pd.read_excel(file_path)
                else:
                    data = pd.read_csv(file_path, index_col=0)  # Usar primera columna como índice
                
                # Cargar directamente en Advanced ML
                self.on_advanced_data_loaded(data)
                
                # Cambiar al tab Advanced ML
                self.focus_advanced_ml_tab()
                
                messagebox.showinfo("Éxito", f"Dataset importado exitosamente:\n{file_path}\n\n"
                                           f"Filas: {len(data)}\nColumnas: {len(data.columns)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error importando dataset:\n{str(e)}")
    
    def load_batch_dataset(self):
        """Cargar dataset batch específico"""
        self.import_dataset()
    
    def export_batch_results(self):
        """Exportar resultados batch"""
        if self.current_batch_dataset is not None:
            if hasattr(self.batch_tab, 'export_dataset'):
                self.batch_tab.export_dataset()
            else:
                self.export_dataset_generic(self.current_batch_dataset, "batch_dataset")
        else:
            messagebox.showwarning("Advertencia", "No hay datos batch para exportar")
    
    def export_dataset_generic(self, data, default_name):
        """Exportar dataset genérico"""
        if data is None:
            messagebox.showwarning("Advertencia", "No hay datos para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Dataset",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    data.to_excel(file_path)
                else:
                    data.to_csv(file_path)
                messagebox.showinfo("Éxito", f"Dataset exportado a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando:\n{str(e)}")
    
    def export_models(self):
        """Exportar modelos entrenados"""
        if hasattr(self.advanced_ml_tab, 'export_model'):
            self.advanced_ml_tab.export_model()
        else:
            messagebox.showwarning("Advertencia", "No hay modelo para exportar")

    # =============================================================================
    # MÉTODOS DE INFORMACIÓN
    # =============================================================================
    
    def show_data_statistics(self):
        """Mostrar estadísticas de todos los datasets"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estadísticas de Datos")
        stats_window.geometry("700x500")
        stats_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(stats_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        stats_text = "ESTADÍSTICAS DE DATASETS\n" + "="*50 + "\n\n"
        
        datasets = [
            ("Batch Processing", self.current_batch_dataset),
            ("Advanced ML", self.current_advanced_data)
        ]
        
        for name, data in datasets:
            if data is not None:
                try:
                    memory_mb = data.memory_usage(deep=True).sum() / (1024*1024)
                    dtype_counts = dict(data.dtypes.value_counts())
                except:
                    memory_mb = sys.getsizeof(data) / (1024*1024)
                    dtype_counts = "N/A"
                
                stats_text += f"{name}:\n"
                stats_text += f"  Filas: {len(data)}\n"
                stats_text += f"  Columnas: {len(data.columns)}\n"
                stats_text += f"  Memoria: {memory_mb:.2f} MB\n"
                stats_text += f"  Tipos: {dtype_counts}\n"
                stats_text += "-"*30 + "\n\n"
            else:
                stats_text += f"{name}: No cargado\n\n"
        
        text_widget.insert(1.0, stats_text)
        text_widget.config(state="disabled")
        
        ttk.Button(stats_window, text="Cerrar", 
                  command=stats_window.destroy).pack(pady=10)
    
    def show_memory_usage(self):
        """Mostrar uso de memoria detallado"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            memory_text = f"""USO DE MEMORIA DETALLADO
========================

Proceso actual:
  RSS: {memory_info.rss / (1024*1024):.2f} MB
  VMS: {memory_info.vms / (1024*1024):.2f} MB

"""
        except ImportError:
            memory_text = "USO DE MEMORIA\n==============\n\n(psutil no disponible)\n\n"
        
        memory_text += "Datasets en memoria:\n"
        
        datasets = [
            ("Batch Processing", self.current_batch_dataset), 
            ("Advanced ML", self.current_advanced_data)
        ]
        
        for name, data in datasets:
            if data is not None:
                try:
                    size_mb = data.memory_usage(deep=True).sum() / (1024*1024)
                except:
                    size_mb = sys.getsizeof(data) / (1024*1024)
                memory_text += f"  {name}: {size_mb:.2f} MB\n"
            else:
                memory_text += f"  {name}: 0 MB\n"
        
        messagebox.showinfo("Uso de Memoria", memory_text)

    # =============================================================================
    # EXPORT METHODS
    # =============================================================================
    
    def export_all_data(self):
        """Exportar todos los datos y análisis"""
        directory = filedialog.askdirectory(title="Select directory to export all data")
        if directory:
            try:
                export_dir = Path(directory) / "vacancy_predictor_export"
                export_dir.mkdir(exist_ok=True)
                
                exported_files = []
                
                # Exportar datasets disponibles
                datasets = [
                    ("batch_dataset.csv", self.current_batch_dataset),
                    ("advanced_ml_data.csv", self.current_advanced_data)
                ]
                
                for filename, data in datasets:
                    if data is not None:
                        try:
                            data.to_csv(export_dir / filename)
                            exported_files.append(filename)
                        except Exception as e:
                            logger.warning(f"Could not export {filename}: {e}")
                
                # Exportar modelo si existe
                models_dir = export_dir / "models"
                models_dir.mkdir(exist_ok=True)
                
                if hasattr(self.advanced_ml_tab, 'trained_model') and self.advanced_ml_tab.trained_model is not None:
                    try:
                        import joblib
                        joblib.dump(self.advanced_ml_tab.trained_model, models_dir / "vacancy_model.joblib")
                        exported_files.append("models/vacancy_model.joblib")
                    except Exception as e:
                        logger.warning(f"Could not save model: {e}")
                
                # Crear reporte de exportación
                report_lines = [
                    "VACANCY PREDICTOR - EXPORT REPORT",
                    "=" * 40,
                    f"Export Date: {pd.Timestamp.now()}",
                    f"Export Directory: {export_dir}",
                    "",
                    "EXPORTED FILES:",
                    "-" * 20
                ]
                
                for file in exported_files:
                    report_lines.append(f"✓ {file}")
                
                # Guardar reporte
                with open(export_dir / "export_report.txt", 'w') as f:
                    f.write("\n".join(report_lines))
                
                messagebox.showinfo("Export Complete", 
                                   f"Export finished!\n\n"
                                   f"Files exported: {len(exported_files)}\n"
                                   f"Location: {export_dir}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

    # =============================================================================
    # OTROS MÉTODOS
    # =============================================================================
    
    def show_user_guide(self):
        """Mostrar guía del usuario"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Guía del Usuario")
        guide_window.geometry("800x600")
        guide_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(guide_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        guide_text = """GUÍA DEL USUARIO - VACANCY PREDICTOR ML SUITE
=============================================

WORKFLOW RECOMENDADO:

OPCIÓN 1 - PROCESAMIENTO DESDE ARCHIVOS .DUMP:
1. Use "Batch Processing" para procesar directorios con archivos .dump
2. Los datos se cargarán automáticamente en "Advanced ML"
3. Configure parámetros de entrenamiento
4. Entrene el modelo Random Forest
5. Realice predicciones

OPCIÓN 2 - CARGAR DATASET EXISTENTE:
1. Use "File → Import Dataset" para cargar un CSV existente
2. Vaya al tab "Advanced ML"
3. Configure parámetros de entrenamiento
4. Entrene el modelo Random Forest
5. Realice predicciones

CARACTERÍSTICAS DEL ADVANCED ML:
• Limpieza automática de columnas de texto
• Separación automática de features y target ('vacancies')
• Random Forest con parámetros configurables
• Validación cruzada automática
• Visualizaciones de importancia de features
• Predicciones individuales y por lotes

FORMATO DEL DATASET:
• Debe contener una columna 'vacancies' como target
• Las columnas de texto se excluyen automáticamente
• Se usan todas las columnas numéricas como features

TIPS:
• Los datasets de Batch Processing son compatibles con Advanced ML
• Use nombres descriptivos al exportar
• Revise feature importance para optimizar el modelo
• Guarde modelos entrenados para reutilizar
"""
        
        text_widget.insert(1.0, guide_text)
        text_widget.config(state="disabled")
        
        ttk.Button(guide_window, text="Cerrar", 
                  command=guide_window.destroy).pack(pady=10)
    
    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """Vacancy Predictor ML Suite v3.1
==============================

Suite especializada para predicción de vacancias usando machine learning.

CARACTERÍSTICAS:
• Batch Processing: Procesamiento masivo de archivos .dump
• Advanced ML: Entrenamiento y predicción con Random Forest
• Prevención de data leakage
• Interfaz simplificada y optimizada

CAPACIDADES:
• Extracción automática de 160+ features
• Random Forest con validación cruzada
• Predicciones individuales y por lotes
• Visualizaciones de feature importance
• Export completo de modelos y datos

FORMATOS SOPORTADOS:
• Input: archivos .dump, CSV, Excel
• Output: CSV, XLSX, JOBLIB (modelos)

Version: 3.1.0 - ML Suite
"""
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About Vacancy Predictor")
        about_window.geometry("500x400")
        about_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(about_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert(1.0, about_text)
        text_widget.config(state="disabled")
        
        ttk.Button(about_window, text="Close", 
                  command=about_window.destroy).pack(pady=10)
    
    def reset_application(self):
        """Resetear aplicación completa"""
        if messagebox.askyesno("New Project", 
                              "This will clear all current data and models. Continue?"):
            # Reset datos
            self.current_data = None
            self.current_batch_dataset = None
            self.current_advanced_data = None
            
            # Reset tabs
            if hasattr(self.batch_tab, 'reset'):
                self.batch_tab.reset()
            if hasattr(self.advanced_ml_tab, 'reset'):
                self.advanced_ml_tab.reset()
            
            self.update_status("New project created - Ready for data processing")
            self.update_indicators()
    
    def on_closing(self):
        """Callback al cerrar aplicación"""
        if messagebox.askokcancel("Quit", "Do you want to quit Vacancy Predictor?"):
            try:
                logger.info("Application closing gracefully")
                self.root.destroy()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
                self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            # Configurar atajos de teclado
            self.root.bind('<Control-n>', lambda e: self.reset_application())
            self.root.bind('<Control-i>', lambda e: self.import_dataset())
            self.root.bind('<Control-e>', lambda e: self.export_all_data())
            self.root.bind('<Control-q>', lambda e: self.on_closing())
            self.root.bind('<F1>', lambda e: self.show_user_guide())
            self.root.bind('<F2>', lambda e: self.show_data_statistics())
            self.root.bind('<F3>', lambda e: self.show_memory_usage())
            
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            messagebox.showerror("Critical Error", f"Application encountered a critical error: {e}")


# =============================================================================
# ADVANCED ML TAB CORREGIDO
# =============================================================================

class AdvancedMLTabCorrected:
    """Advanced ML Tab corregido para manejar datasets CSV correctamente"""
    
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
        self.create_prediction_tab()
    
    def create_data_tab(self):
        """Tab de carga y exploración de datos"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📁 Datos")
        
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
        
        # Panel derecho - Resultados
        right_panel = ttk.Frame(train_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10))
        
        results_group = ttk.LabelFrame(right_panel, text="Resultados del Entrenamiento", padding="10")
        results_group.pack(fill='both', expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_group, height=20, wrap='word')
        self.results_text.pack(fill='both', expand=True)
    
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
    
    def update_prediction_interface(self):
        """Actualizar interfaz de predicción con features principales"""
        # Limpiar frame anterior
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        # Mostrar solo las 10 features más importantes si hay modelo entrenado
        # Si no, mostrar las primeras 10
        display_features = self.feature_columns[:10]
        
        self.feature_vars = {}
        
        # Crear inputs para features principales
        for i, feature in enumerate(display_features):
            row = i // 2
            col = (i % 2) * 3
            
            ttk.Label(self.features_frame, text=f"{feature}:").grid(row=row, column=col, sticky='w', padx=5, pady=2)
            
            var = tk.DoubleVar(value=0.0)
            self.feature_vars[feature] = var
            
            entry = ttk.Entry(self.features_frame, textvariable=var, width=15)
            entry.grid(row=row, column=col+1, padx=5, pady=2)
    
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
                # Imputar valores faltantes con la mediana
                from sklearn.impute import SimpleImputer
                imputer = SimpleImputer(strategy='median')
                X_clean = pd.DataFrame(imputer.fit_transform(X), columns=X.columns, index=X.index)
            else:
                X_clean = X
            
            # División train/test
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X_clean, y, 
                test_size=self.test_size_var.get(),
                random_state=self.random_state_var.get()
            )
            
            # Crear y entrenar modelo
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            import numpy as np
            
            self.trained_model = RandomForestRegressor(
                n_estimators=self.n_estimators_var.get(),
                random_state=self.random_state_var.get(),
                n_jobs=-1
            )
            
            self.trained_model.fit(X_train, y_train)
            
            # Evaluar modelo
            train_pred = self.trained_model.predict(X_train)
            test_pred = self.trained_model.predict(X_test)
            
            train_mae = mean_absolute_error(y_train, train_pred)
            test_mae = mean_absolute_error(y_test, test_pred)
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(y_test, test_pred)
            
            # Validación cruzada
            from sklearn.model_selection import cross_val_score
            cv_mae = -cross_val_score(self.trained_model, X_clean, y, cv=5, scoring='neg_mean_absolute_error')
            cv_r2 = cross_val_score(self.trained_model, X_clean, y, cv=5, scoring='r2')
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.trained_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Mostrar resultados
            results_text = f"""RESULTADOS DEL ENTRENAMIENTO
===========================

CONFIGURACIÓN:
  Random Forest con {self.n_estimators_var.get()} estimadores
  Test size: {self.test_size_var.get():.1%}
  Features utilizadas: {len(self.feature_columns)}
  Muestras de entrenamiento: {len(X_train)}
  Muestras de prueba: {len(X_test)}

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
            
            for i, row in feature_importance.head(15).iterrows():
                results_text += f"  {row['feature'][:40]:40s}: {row['importance']:.4f}\n"
            
            # Interpretación
            results_text += f"""

INTERPRETACIÓN:
  • MAE = Error promedio en unidades de vacancias
  • RMSE = Error cuadrático medio (penaliza errores grandes)
  • R² = Proporción de varianza explicada (1.0 = perfecto)
  
CALIDAD DEL MODELO:
  {'🟢 Excelente' if test_r2 > 0.9 else '🟡 Bueno' if test_r2 > 0.7 else '🔴 Mejorable'} (R² = {test_r2:.3f})
  {'🟢 Bajo error' if test_mae < 5 else '🟡 Error moderado' if test_mae < 10 else '🔴 Error alto'} (MAE = {test_mae:.1f})
"""
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results_text)
            
            # Habilitar botón de guardado
            self.save_btn.config(state="normal")
            
            # Actualizar interfaz de predicción con features importantes
            self.update_prediction_interface_with_importance(feature_importance)
            
            messagebox.showinfo("Entrenamiento Completado", 
                               f"Modelo entrenado exitosamente!\n\n"
                               f"Test R²: {test_r2:.3f}\n"
                               f"Test MAE: {test_mae:.3f}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error entrenando modelo:\n{str(e)}")
        finally:
            self.train_btn.config(state="normal")
    
    def update_prediction_interface_with_importance(self, feature_importance):
        """Actualizar interfaz de predicción con features más importantes"""
        # Limpiar frame anterior
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        # Mostrar top 10 features más importantes
        top_features = feature_importance.head(10)['feature'].tolist()
        
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
                    # Usar valor promedio del dataset
                    value = self.current_data[feature].mean()
                
                feature_vector.append(value)
            
            # Realizar predicción
            X_pred = np.array(feature_vector).reshape(1, -1)
            prediction = self.trained_model.predict(X_pred)[0]
            
            # Obtener intervalo de confianza aproximado
            # Usar árboles individuales para estimar incertidumbre
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
                    }
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


# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

def main():
    """Función principal"""
    try:
        logger.info("Starting Vacancy Predictor ML Suite v3.1")
        
        app = VacancyPredictorGUI()
        app.run()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        try:
            messagebox.showerror("Application Error", 
                                f"A critical error occurred during startup:\n\n{e}\n\n"
                                f"Check vacancy_predictor.log for details.")
        except:
            print(f"CRITICAL ERROR: {e}")


if __name__ == "__main__":
    main()