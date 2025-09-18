#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación principal integrada - Vacancy Predictor con todas las funcionalidades
Incluye: LAMMPS, Batch Processing, Advanced ML, Feature Selection
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
import sys

# Importar módulos propios
try:
    from vacancy_predictor.core.ml_components import DataProcessor, ModelTrainer, Visualizer
    from vacancy_predictor.gui.tabs.lammps_tab import LAMMPSTab
    from vacancy_predictor.gui.tabs.data_tabs import DataTab
    from vacancy_predictor.gui.tabs.training_tab import TrainingTab
    from vacancy_predictor.gui.tabs.prediction_tab import PredictionTab
    from vacancy_predictor.gui.tabs.visualization_tab import VisualizationTab
except ImportError as e:
    logging.warning(f"Could not import original modules: {e}")
    # Definir clases básicas si no están disponibles
    class DataProcessor:
        def __init__(self):
            self.current_data = None
        def prepare_features_and_target(self, data):
            if 'vacancies' in data.columns:
                X = data.drop('vacancies', axis=1)
                y = data['vacancies']
                return X, y
            return data, None
    
    class ModelTrainer:
        def __init__(self):
            self.model = None
        def save_model(self, path):
            import joblib
            joblib.dump(self.model, path)
    
    class Visualizer:
        def __init__(self):
            pass

# Importar nuevos tabs
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
    """Aplicación principal integrada con todas las funcionalidades"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacancy Predictor - Complete ML & LAMMPS Suite")
        self.root.geometry("1500x1000")
        
        # Maximizar ventana según SO
        try:
            if sys.platform == 'win32':
                self.root.state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except:
            pass
        
        # Componentes ML
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        self.visualizer = Visualizer()
        
        # Referencias a datos actuales
        self.current_data = None
        self.current_model = None
        self.current_lammps_data = None
        self.current_batch_dataset = None
        self.current_advanced_data = None
        
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        logger.info("Vacancy Predictor Complete Suite initialized")
    
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
        
        # Menú LAMMPS
        lammps_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="LAMMPS", menu=lammps_menu)
        lammps_menu.add_command(label="Reset 3D View", command=self.reset_3d_view)
        lammps_menu.add_command(label="Top View", command=lambda: self.set_3d_view(90, 0))
        lammps_menu.add_command(label="Front View", command=lambda: self.set_3d_view(0, 0))
        lammps_menu.add_command(label="Side View", command=lambda: self.set_3d_view(0, 90))
        lammps_menu.add_separator()
        lammps_menu.add_command(label="Export 3D Plot", command=self.save_lammps_plot)
        
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
        ml_menu.add_command(label="Process & Train", command=self.focus_advanced_ml_tab)
        ml_menu.add_separator()
        ml_menu.add_command(label="Model Comparison", command=self.compare_all_models)
        ml_menu.add_command(label="Export Models", command=self.export_all_models)
        
        # Menú Tools
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Data Statistics", command=self.show_data_statistics)
        tools_menu.add_command(label="Memory Usage", command=self.show_memory_usage)
        tools_menu.add_separator()
        tools_menu.add_command(label="Preferences", command=self.show_preferences)
        
        # Menú Help
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
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
        
        # 2. ADVANCED ML
        self.advanced_ml_tab = AdvancedMLTab(self.notebook, self.on_advanced_data_loaded)
        self.notebook.add(self.advanced_ml_tab.frame, text="🧠 Advanced ML")
        
        # 3. TABS ORIGINALES (solo si están disponibles)
        try:
            self.data_tab = DataTab(self.notebook, self.data_processor, self.on_data_loaded)
            self.notebook.add(self.data_tab.frame, text="📊 Data")
            
            self.training_tab = TrainingTab(self.notebook, self.model_trainer, self.data_processor, self.on_model_trained)
            self.notebook.add(self.training_tab.frame, text="🤖 Training")
            
            self.prediction_tab = PredictionTab(self.notebook, self.model_trainer, self.data_processor)
            self.notebook.add(self.prediction_tab.frame, text="🔮 Prediction")
            
            self.visualization_tab = VisualizationTab(self.notebook, self.visualizer, self.get_visualization_data)
            self.notebook.add(self.visualization_tab.frame, text="📈 Visualization")
            
        except Exception as e:
            logger.warning(f"Could not load original tabs: {e}")
            self.data_tab = None
            self.training_tab = None
            self.prediction_tab = None
            self.visualization_tab = None
        
        # 4. LAMMPS (solo si está disponible)
        try:
            self.lammps_tab = LAMMPSTab(parent=self.notebook, data_loaded_callback=self.on_lammps_data_loaded)
            self.notebook.add(self.lammps_tab.frame, text="⚛️ LAMMPS")
        except Exception as e:
            logger.warning(f"Could not load LAMMPS tab: {e}")
            self.lammps_tab = None
        
        # Vincular eventos
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_status_bar(self):
        """Crear barra de estado"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x")
        
        # Mensaje principal
        self.status_var = tk.StringVar(value="Vacancy Predictor Ready - Select processing method")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                               relief="sunken", anchor="w")
        status_label.pack(side="left", fill="x", expand=True)
        
        # Indicadores
        self.memory_var = tk.StringVar(value="Memory: 0 MB")
        memory_label = ttk.Label(self.status_frame, textvariable=self.memory_var, 
                               relief="sunken", anchor="e", width=15)
        memory_label.pack(side="right")
        
        self.active_models_var = tk.StringVar(value="Models: 0")
        models_label = ttk.Label(self.status_frame, textvariable=self.active_models_var,
                               relief="sunken", anchor="e", width=12)
        models_label.pack(side="right")
        
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
        for data in [self.current_data, self.current_batch_dataset, 
                    self.current_advanced_data, self.current_lammps_data]:
            if data is not None:
                datasets += 1
                try:
                    total_memory += data.memory_usage(deep=True).sum() / (1024 * 1024)
                except:
                    total_memory += sys.getsizeof(data) / (1024 * 1024)
        
        # Contar modelos
        models = 0
        if self.current_model is not None:
            models += 1
        if hasattr(self.advanced_ml_tab, 'trained_model') and self.advanced_ml_tab.trained_model is not None:
            models += 1
        
        # Actualizar
        self.datasets_var.set(f"Datasets: {datasets}")
        self.memory_var.set(f"Memory: {total_memory:.1f} MB")
        self.active_models_var.set(f"Models: {models}")

    # =============================================================================
    # CALLBACKS
    # =============================================================================
    
    def on_data_loaded(self, data):
        """Callback cuando se cargan datos ML originales"""
        self.current_data = data
        self.update_status(f"Data loaded: {data.shape[0]} rows, {data.shape[1]} columns")
        self.update_indicators()
        
    def on_lammps_data_loaded(self, data):
        """Callback cuando se cargan datos LAMMPS"""
        self.current_lammps_data = data
        num_atoms = len(data) if data is not None else 0
        if self.lammps_tab and hasattr(self.lammps_tab, 'current_metadata'):
            timestep = self.lammps_tab.current_metadata.get('timestep', 'N/A')
        else:
            timestep = 'N/A'
        self.update_status(f"LAMMPS data loaded: {num_atoms} atoms, timestep {timestep}")
        self.update_indicators()
    
    def on_batch_data_loaded(self, data):
        """Callback cuando se cargan datos del procesamiento batch"""
        self.current_batch_dataset = data
        self.current_data = data
        
        self.update_status(f"Batch dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()
        
        # Sincronizar con otros tabs si están disponibles
        try:
            if self.data_tab and hasattr(self.data_tab, 'load_data_directly'):
                self.data_tab.load_data_directly(data)
        except Exception as e:
            logger.warning(f"Could not sync batch data: {e}")
    
    def on_advanced_data_loaded(self, data):
        """Callback para datos del Advanced ML tab"""
        self.current_advanced_data = data
        self.current_data = data
        
        self.update_status(f"Advanced ML dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()
        
        # Sincronizar con otros tabs si están disponibles
        try:
            if self.data_tab and hasattr(self.data_tab, 'load_data_directly'):
                self.data_tab.load_data_directly(data)
        except Exception as e:
            logger.warning(f"Could not sync advanced ML data: {e}")
        
    def on_model_trained(self, results):
        """Callback cuando se entrena un modelo"""
        self.current_model = self.model_trainer.model
        algorithm = results.get('algorithm', 'model')
        self.update_status(f"New {algorithm} trained/loaded")
        self.update_indicators()
        
        # Actualizar tab de predicción si está disponible
        try:
            if self.prediction_tab and hasattr(self.prediction_tab, 'update_model'):
                self.prediction_tab.update_model(self.current_model)
        except Exception as e:
            logger.warning(f"Could not update prediction tab: {e}")
        
    def on_tab_changed(self, event):
        """Callback cuando cambia el tab activo"""
        try:
            selected_tab = event.widget.tab('current')['text']
            self.update_status(f"Active tab: {selected_tab}")
        except:
            pass
        
    def get_visualization_data(self):
        """Proporcionar datos para visualización"""
        return {
            'data': self.current_data,
            'model': self.current_model,
            'results': getattr(self.training_tab, 'training_results', None) if self.training_tab else None,
            'processor': self.data_processor
        }

    # =============================================================================
    # MÉTODOS DE NAVEGACIÓN
    # =============================================================================
    
    def focus_batch_tab(self):
        """Enfocar el tab de procesamiento batch"""
        for i in range(self.notebook.index("end")):
            if "Batch" in self.notebook.tab(i, "text"):
                self.notebook.select(i)
                break
    
    def focus_advanced_ml_tab(self):
        """Enfocar el tab de Advanced ML"""
        for i in range(self.notebook.index("end")):
            if "Advanced ML" in self.notebook.tab(i, "text"):
                self.notebook.select(i)
                break

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
                    data = pd.read_csv(file_path)
                
                # Preguntar qué tipo de datos son
                choice = messagebox.askyesno(
                    "Tipo de Dataset",
                    f"Dataset cargado: {len(data)} filas, {len(data.columns)} columnas\n\n"
                    "¿Es un dataset procesado para ML (Sí) o datos raw (No)?"
                )
                
                if choice:
                    self.on_batch_data_loaded(data)
                else:
                    self.on_data_loaded(data)
                
                messagebox.showinfo("Éxito", f"Dataset importado exitosamente desde:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error importando dataset:\n{str(e)}")
    
    def load_batch_dataset(self):
        """Cargar dataset batch específico"""
        if hasattr(self.batch_tab, 'export_dataset'):
            self.batch_tab.export_dataset()
        else:
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

    # =============================================================================
    # MÉTODOS AVANZADOS
    # =============================================================================
    
    def compare_all_models(self):
        """Comparar todos los modelos disponibles"""
        models = {}
        
        # Recopilar modelos disponibles
        if self.current_model is not None:
            models['Standard ML'] = self.current_model
        
        if hasattr(self.advanced_ml_tab, 'trained_model') and self.advanced_ml_tab.trained_model is not None:
            models['Advanced ML'] = self.advanced_ml_tab.trained_model
        
        if not models:
            messagebox.showwarning("Advertencia", "No hay modelos entrenados para comparar")
            return
        
        self.show_model_comparison(models)
    
    def show_model_comparison(self, models):
        """Mostrar ventana de comparación de modelos"""
        comparison_window = tk.Toplevel(self.root)
        comparison_window.title("Comparación de Modelos")
        comparison_window.geometry("800x600")
        comparison_window.transient(self.root)
        
        # Contenido de comparación
        text_widget = scrolledtext.ScrolledText(comparison_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        comparison_text = "COMPARACIÓN DE MODELOS\n" + "="*50 + "\n\n"
        
        for name, model in models.items():
            comparison_text += f"MODELO: {name}\n"
            comparison_text += f"Tipo: {type(model).__name__}\n"
            
            if hasattr(model, 'named_steps'):
                steps = list(model.named_steps.keys())
                comparison_text += f"Pipeline steps: {steps}\n"
            
            comparison_text += "-"*30 + "\n\n"
        
        text_widget.insert(1.0, comparison_text)
        text_widget.config(state="disabled")
        
        ttk.Button(comparison_window, text="Cerrar", 
                  command=comparison_window.destroy).pack(pady=10)
    
    def export_all_models(self):
        """Exportar todos los modelos entrenados"""
        directory = filedialog.askdirectory(title="Seleccionar directorio para exportar modelos")
        if not directory:
            return
            
        export_dir = Path(directory) / "exported_models"
        export_dir.mkdir(exist_ok=True)
        
        exported = []
        
        try:
            # Exportar modelo estándar
            if self.current_model is not None:
                model_path = export_dir / "standard_model.pkl"
                self.model_trainer.save_model(str(model_path))
                exported.append("standard_model.pkl")
            
            # Exportar modelo avanzado
            if hasattr(self.advanced_ml_tab, 'trained_model') and self.advanced_ml_tab.trained_model is not None:
                import joblib
                model_path = export_dir / "advanced_model.joblib"
                joblib.dump(self.advanced_ml_tab.trained_model, model_path)
                exported.append("advanced_model.joblib")
            
            if exported:
                messagebox.showinfo("Éxito", 
                                   f"Modelos exportados:\n" + "\n".join(f"• {f}" for f in exported) + 
                                   f"\n\nUbicación: {export_dir}")
            else:
                messagebox.showwarning("Advertencia", "No hay modelos para exportar")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando modelos:\n{str(e)}")

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
            ("ML Estándar", self.current_data),
            ("Batch Processing", self.current_batch_dataset),
            ("Advanced ML", self.current_advanced_data),
            ("LAMMPS", self.current_lammps_data)
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
            ("ML Estándar", self.current_data),
            ("Batch Processing", self.current_batch_dataset), 
            ("Advanced ML", self.current_advanced_data),
            ("LAMMPS", self.current_lammps_data)
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
    
    def show_preferences(self):
        """Mostrar ventana de preferencias"""
        prefs_window = tk.Toplevel(self.root)
        prefs_window.title("Preferencias")
        prefs_window.geometry("500x400")
        prefs_window.transient(self.root)
        
        ttk.Label(prefs_window, text="Preferencias del usuario", 
                 font=('Arial', 12, 'bold')).pack(pady=20)
        
        ttk.Label(prefs_window, text="Configuraciones disponibles en futuras versiones").pack(pady=50)
        
        ttk.Button(prefs_window, text="Cerrar", 
                  command=prefs_window.destroy).pack(pady=20)
    
    def show_user_guide(self):
        """Mostrar guía del usuario"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Guía del Usuario")
        guide_window.geometry("800x600")
        guide_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(guide_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        guide_text = """GUÍA DEL USUARIO - VACANCY PREDICTOR
====================================

WORKFLOW RECOMENDADO:

1. PROCESAMIENTO DE DATOS:
   • Use "Batch Processing" para procesar directorios con archivos .dump
   • O use "Advanced ML" para procesamiento personalizado con histogramas
   • O cargue datos existentes con "Import Dataset"

2. ENTRENAMIENTO:
   • Use "Advanced ML" para Random Forest con métricas detalladas
   • O use tabs originales si están disponibles

3. EVALUACIÓN:
   • Revise métricas y visualizaciones
   • Use validación cruzada
   • Analice feature importance

4. PREDICCIÓN:
   • Use "Advanced ML" para predicciones individuales o por lotes
   • Exporte resultados

TIPS:
• Mantenga datasets organizados por tipo
• Use nombres descriptivos al exportar
• Revise memoria y rendimiento regularmente
• Guarde modelos entrenados para reutilizar

RESOLUCIÓN DE PROBLEMAS:
• Si hay errores de importación, verifique las dependencias
• Si hay errores de memoria, reduzca el tamaño del dataset
• Para archivos .dump corruptos, use validación previa
• Si las predicciones son malas, revise la selección de features
"""
        
        text_widget.insert(1.0, guide_text)
        text_widget.config(state="disabled")
        
        ttk.Button(guide_window, text="Cerrar", 
                  command=guide_window.destroy).pack(pady=10)
    
    def show_shortcuts(self):
        """Mostrar atajos de teclado"""
        shortcuts_text = """ATAJOS DE TECLADO
================

Ctrl+N : Nuevo proyecto
Ctrl+I : Importar dataset
Ctrl+E : Exportar todo
Ctrl+Q : Salir

F1 : Ayuda
F2 : Estadísticas
F3 : Uso de memoria
F4 : Comparar modelos

Tab : Siguiente campo
Shift+Tab : Campo anterior
Enter : Ejecutar acción principal
Esc : Cancelar operación
"""
        messagebox.showinfo("Atajos de Teclado", shortcuts_text)

    # =============================================================================
    # MÉTODOS LAMMPS
    # =============================================================================
    
    def reset_3d_view(self):
        """Resetear vista 3D de LAMMPS"""
        if self.lammps_tab and hasattr(self.lammps_tab, 'visualizer') and self.lammps_tab.visualizer.ax:
            self.lammps_tab.visualizer.ax.view_init(elev=20, azim=45)
            self.lammps_tab.visualizer.canvas.draw()
    
    def set_3d_view(self, elev, azim):
        """Establecer vista 3D específica"""
        if self.lammps_tab and hasattr(self.lammps_tab, 'visualizer') and self.lammps_tab.visualizer.ax:
            self.lammps_tab.visualizer.ax.view_init(elev=elev, azim=azim)
            self.lammps_tab.visualizer.canvas.draw()
    
    def save_lammps_plot(self):
        """Guardar plot 3D de LAMMPS"""
        if self.current_lammps_data is None:
            messagebox.showwarning("Warning", "No LAMMPS data to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save LAMMPS 3D Plot",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg")
            ]
        )
        
        if file_path:
            try:
                if self.lammps_tab and hasattr(self.lammps_tab, 'visualizer'):
                    self.lammps_tab.visualizer.save_plot(file_path)
                    messagebox.showinfo("Success", f"LAMMPS plot saved to:\n{file_path}")
                else:
                    messagebox.showwarning("Warning", "LAMMPS visualizer not available")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plot:\n{str(e)}")

    # =============================================================================
    # EXPORT METHODS
    # =============================================================================
    
    def export_all_data(self):
        """Exportar todos los datos y análisis"""
        directory = filedialog.askdirectory(title="Select directory to export all data")
        if directory:
            try:
                export_dir = Path(directory) / "vacancy_predictor_complete_export"
                export_dir.mkdir(exist_ok=True)
                
                exported_files = []
                
                # Exportar todos los datasets disponibles
                datasets = [
                    ("ml_standard_data.csv", self.current_data),
                    ("batch_dataset.csv", self.current_batch_dataset),
                    ("advanced_ml_data.csv", self.current_advanced_data),
                    ("lammps_atoms.csv", self.current_lammps_data)
                ]
                
                for filename, data in datasets:
                    if data is not None:
                        try:
                            if filename.endswith('_atoms.csv'):
                                data.to_csv(export_dir / filename, index=False)
                            else:
                                data.to_csv(export_dir / filename)
                            exported_files.append(filename)
                        except Exception as e:
                            logger.warning(f"Could not export {filename}: {e}")
                
                # Exportar modelos
                models_dir = export_dir / "models"
                models_dir.mkdir(exist_ok=True)
                
                if self.current_model is not None:
                    try:
                        self.model_trainer.save_model(str(models_dir / "standard_model.pkl"))
                        exported_files.append("models/standard_model.pkl")
                    except Exception as e:
                        logger.warning(f"Could not save standard model: {e}")
                
                if hasattr(self.advanced_ml_tab, 'trained_model') and self.advanced_ml_tab.trained_model is not None:
                    try:
                        import joblib
                        joblib.dump(self.advanced_ml_tab.trained_model, models_dir / "advanced_model.joblib")
                        exported_files.append("models/advanced_model.joblib")
                    except Exception as e:
                        logger.warning(f"Could not save advanced model: {e}")
                
                # Exportar metadatos LAMMPS
                if self.current_lammps_data is not None and self.lammps_tab and hasattr(self.lammps_tab, 'current_metadata'):
                    try:
                        with open(export_dir / "lammps_metadata.json", 'w') as f:
                            json.dump(self.lammps_tab.current_metadata, f, indent=2, default=str)
                        exported_files.append("lammps_metadata.json")
                    except Exception as e:
                        logger.warning(f"Could not save LAMMPS metadata: {e}")
                
                # Exportar visualizaciones
                viz_dir = export_dir / "visualizations"
                viz_dir.mkdir(exist_ok=True)
                
                try:
                    if (self.lammps_tab and hasattr(self.lammps_tab, 'visualizer') and 
                        self.current_lammps_data is not None):
                        self.lammps_tab.visualizer.save_plot(str(viz_dir / "lammps_3d.png"))
                        exported_files.append("visualizations/lammps_3d.png")
                except Exception as e:
                    logger.warning(f"Could not save LAMMPS visualization: {e}")
                
                # Crear reporte de exportación completo
                report_lines = [
                    "VACANCY PREDICTOR - COMPLETE EXPORT REPORT",
                    "=" * 50,
                    f"Export Date: {pd.Timestamp.now()}",
                    f"Export Directory: {export_dir}",
                    "",
                    "EXPORTED FILES:",
                    "-" * 20
                ]
                
                for file in exported_files:
                    report_lines.append(f"✓ {file}")
                
                # Estadísticas detalladas
                for name, data in datasets:
                    if data is not None:
                        try:
                            memory_mb = data.memory_usage(deep=True).sum() / 1024**2
                            dtype_counts = dict(data.dtypes.value_counts())
                        except:
                            memory_mb = sys.getsizeof(data) / 1024**2
                            dtype_counts = "N/A"
                        
                        report_lines.extend([
                            "",
                            f"{name.upper().replace('_', ' ').replace('.CSV', '')} SUMMARY:",
                            f"  Rows: {len(data)}",
                            f"  Columns: {len(data.columns)}",
                            f"  Memory: {memory_mb:.2f} MB",
                            f"  Data types: {dtype_counts}"
                        ])
                
                # Información de modelos
                models_info = []
                if self.current_model is not None:
                    models_info.append("Standard ML Model")
                if hasattr(self.advanced_ml_tab, 'trained_model') and self.advanced_ml_tab.trained_model is not None:
                    models_info.append("Advanced ML Model")
                
                if models_info:
                    report_lines.extend([
                        "",
                        "EXPORTED MODELS:",
                        "-" * 15
                    ] + [f"✓ {model}" for model in models_info])
                
                # Guardar reporte
                with open(export_dir / "complete_export_report.txt", 'w') as f:
                    f.write("\n".join(report_lines))
                
                messagebox.showinfo("Export Complete", 
                                   f"Complete export finished!\n\n"
                                   f"Files exported: {len(exported_files)}\n"
                                   f"Location: {export_dir}\n\n"
                                   f"Check 'complete_export_report.txt' for details")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
                logger.error(f"Export failed: {e}")

    # =============================================================================
    # OTROS MÉTODOS
    # =============================================================================
    
    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """Vacancy Predictor v3.0 - Complete ML & LAMMPS Suite
===================================================

Una suite completa para análisis de machine learning, visualización de dinámicas 
moleculares LAMMPS, y procesamiento batch de archivos dump para extracción de features.

CARACTERÍSTICAS PRINCIPALES:
• Machine Learning: Procesamiento de datos, entrenamiento, predicciones
• LAMMPS: Visualización 3D de estructuras atómicas y análisis
• Batch Processing: Procesamiento de directorios completos de archivos .dump
• Advanced ML: Pipeline integrado con histogramas y métricas avanzadas
• Visualización: Plotting avanzado y exploración de datos
• Export: Capacidades completas de exportación de proyectos

CAPACIDADES ML:
• Múltiples algoritmos (Random Forest, SVM, Neural Networks, etc.)
• Análisis de importancia de features
• Validación cruzada y evaluación de modelos
• Predicciones batch y export

CAPACIDADES BATCH:
• Procesar directorios completos de archivos .dump
• Extraer 200+ features por archivo
• Prevención de data leakage
• Bins de energía y totales de átomos configurables

ADVANCED ML:
• Pipeline integrado de procesamiento → entrenamiento → predicción
• Histogramas configurables de coordinación y energía
• Visualizaciones automáticas de distribuciones e importancia
• Predicciones individuales y por lotes con métricas detalladas

FORMATOS SOPORTADOS:
• Datos ML: CSV, Excel, JSON
• LAMMPS: archivos .dump (comprimidos o no)
• Export: CSV, PNG, PDF, PKL, XLSX, JOBLIB

Desarrollado para investigación en machine learning y 
análisis de simulaciones de dinámicas moleculares.

Version: 3.0.0 - Complete Suite
"""
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About Vacancy Predictor v3.0")
        about_window.geometry("700x600")
        about_window.resizable(False, False)
        
        about_window.transient(self.root)
        about_window.grab_set()
        
        text_widget = scrolledtext.ScrolledText(about_window, wrap="word", padx=20, pady=20, 
                                               font=("Arial", 10))
        text_widget.pack(fill="both", expand=True)
        text_widget.insert(1.0, about_text)
        text_widget.config(state="disabled")
        
        button_frame = ttk.Frame(about_window)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Close", 
                  command=about_window.destroy).pack()
    
    def reset_application(self):
        """Resetear aplicación completa"""
        if messagebox.askyesno("New Project", 
                              "This will clear all current data and models. Continue?"):
            # Reset componentes
            self.current_data = None
            self.current_model = None
            self.current_lammps_data = None
            self.current_batch_dataset = None
            self.current_advanced_data = None
            self.data_processor = DataProcessor()
            self.model_trainer = ModelTrainer()
            
            # Reset todos los tabs disponibles
            try:
                if self.data_tab and hasattr(self.data_tab, 'reset'):
                    self.data_tab.reset()
                if self.training_tab and hasattr(self.training_tab, 'reset'):
                    self.training_tab.reset()
                if self.prediction_tab and hasattr(self.prediction_tab, 'reset'):
                    self.prediction_tab.reset()
                if self.visualization_tab and hasattr(self.visualization_tab, 'reset'):
                    self.visualization_tab.reset()
                if self.lammps_tab and hasattr(self.lammps_tab, 'reset'):
                    self.lammps_tab.reset()
            except Exception as e:
                logger.warning(f"Could not reset some tabs: {e}")
            
            # Reset tabs principales
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
            self.root.bind('<F4>', lambda e: self.compare_all_models())
            
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            messagebox.showerror("Critical Error", f"Application encountered a critical error: {e}")


# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

def main():
    """Función principal"""
    try:
        logger.info("Starting Vacancy Predictor Complete Suite v3.0")
        
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