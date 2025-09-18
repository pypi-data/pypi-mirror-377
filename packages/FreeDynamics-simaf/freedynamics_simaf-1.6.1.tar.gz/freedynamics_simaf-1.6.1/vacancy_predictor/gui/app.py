#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación mejorada - Vacancy Predictor con Feature Selection
Incluye tab de selección interactiva de features para optimización del modelo
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
from vacancy_predictor.gui.tabs.advanced_ml_tab import AdvancedMLTabWithPlots

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

class VacancyPredictorGUIEnhanced:
    """Aplicación mejorada con Feature Selection integrado"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacancy Predictor - ML Suite v4.0 (Enhanced)")
        self.root.geometry("1600x1000")  # Ventana más grande para acomodar nuevas funcionalidades
        
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
        
        # Variables para feature selection
        self.selected_features = None
        self.feature_selection_active = False
        
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        logger.info("Vacancy Predictor ML Suite v4.0 Enhanced initialized")
    
    def setup_styles(self):
        """Configurar estilos mejorados"""
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
        style.configure('Feature.TButton', foreground='darkblue')
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='navy')
        style.configure('Enhanced.TLabel', font=('Arial', 10, 'bold'), foreground='darkgreen')
    
    def create_menu(self):
        """Crear menú principal mejorado"""
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
        
        # Menú Advanced ML (mejorado)
        ml_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Advanced ML", menu=ml_menu)
        ml_menu.add_command(label="Load Dataset & Train", command=self.focus_advanced_ml_tab)
        ml_menu.add_separator()
        ml_menu.add_command(label="Feature Selection", command=self.focus_feature_selection_tab)
        ml_menu.add_command(label="Export Model", command=self.export_models)
        ml_menu.add_command(label="Export Feature Selection", command=self.export_feature_selection)
        
        # Menú Tools (ampliado)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Data Statistics", command=self.show_data_statistics)
        tools_menu.add_command(label="Feature Analysis", command=self.show_feature_analysis)
        tools_menu.add_command(label="Model Comparison", command=self.show_model_comparison)
        tools_menu.add_command(label="Memory Usage", command=self.show_memory_usage)
        
        # Menú Help
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="Feature Selection Guide", command=self.show_feature_selection_guide)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Crear interfaz principal con tabs mejorados"""
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # 1. PROCESAMIENTO BATCH
        self.batch_tab = BatchProcessingTab(self.notebook, self.on_batch_data_loaded)
        self.notebook.add(self.batch_tab.frame, text="📄 Batch Processing")
        
        # 2. ADVANCED ML CON FEATURE SELECTION INTEGRADO
        self.advanced_ml_tab = AdvancedMLTabWithPlots(self.notebook, self.on_advanced_data_loaded)
        self.notebook.add(self.advanced_ml_tab.frame, text="🧠 Enhanced ML")
        
        # Vincular eventos
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_status_bar(self):
        """Crear barra de estado mejorada"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x")
        
        # Mensaje principal
        self.status_var = tk.StringVar(value="Vacancy Predictor v4.0 Enhanced Ready - Advanced Feature Selection Available")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                               relief="sunken", anchor="w")
        status_label.pack(side="left", fill="x", expand=True)
        
        # Indicador de feature selection
        self.feature_selection_var = tk.StringVar(value="Features: Auto")
        feature_label = ttk.Label(self.status_frame, textvariable=self.feature_selection_var,
                                relief="sunken", anchor="e", width=20)
        feature_label.pack(side="right")
        
        # Indicadores existentes
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
        
        # Actualizar indicadores
        self.datasets_var.set(f"Datasets: {datasets}")
        self.memory_var.set(f"Memory: {total_memory:.1f} MB")
        
        # Actualizar indicador de feature selection
        if hasattr(self.advanced_ml_tab, 'using_custom_features') and self.advanced_ml_tab.using_custom_features:
            feature_count = len(self.advanced_ml_tab.custom_features) if self.advanced_ml_tab.custom_features else 0
            self.feature_selection_var.set(f"Features: {feature_count} (Custom)")
        else:
            feature_count = len(self.advanced_ml_tab.feature_columns) if hasattr(self.advanced_ml_tab, 'feature_columns') else 0
            self.feature_selection_var.set(f"Features: {feature_count} (Auto)")

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
                self.update_status("Dataset automatically loaded into Enhanced ML tab")
        except Exception as e:
            logger.warning(f"Could not sync batch data to Advanced ML: {e}")
    
    def on_advanced_data_loaded(self, data):
        """Callback para datos del Advanced ML tab"""
        self.current_advanced_data = data
        self.current_data = data
        
        self.update_status(f"Enhanced ML dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()
        
    def on_tab_changed(self, event):
        """Callback cuando cambia el tab activo"""
        try:
            selected_tab = event.widget.tab('current')['text']
            self.update_status(f"Active tab: {selected_tab}")
            
            # Actualizar indicadores cuando se cambia de tab
            self.update_indicators()
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
    
    def focus_feature_selection_tab(self):
        """Enfocar el sub-tab de selección de features"""
        # Primero ir al tab de Enhanced ML
        self.notebook.select(1)
        # Luego ir al sub-tab de Feature Selection
        if hasattr(self.advanced_ml_tab, 'notebook'):
            self.advanced_ml_tab.notebook.select(1)  # Tab de selección de features
        self.update_status("Feature Selection tab activated - Customize your model features")

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
                
                # Cargar directamente en Enhanced ML
                self.on_advanced_data_loaded(data)
                
                # Cambiar al tab Enhanced ML
                self.focus_advanced_ml_tab()
                
                messagebox.showinfo("Éxito", f"Dataset importado exitosamente:\n{file_path}\n\n"
                                           f"Filas: {len(data)}\nColumnas: {len(data.columns)}\n\n"
                                           f"Tip: Use la pestaña 'Selección Features' para optimizar el modelo")
                
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
    
    def export_feature_selection(self):
        """Exportar configuración de selección de features"""
        if hasattr(self.advanced_ml_tab, 'feature_selection_tab'):
            self.advanced_ml_tab.feature_selection_tab.save_feature_selection()
        else:
            messagebox.showwarning("Advertencia", "No hay selección de features para exportar")

    # =============================================================================
    # MÉTODOS DE INFORMACIÓN MEJORADOS
    # =============================================================================
    
    def show_data_statistics(self):
        """Mostrar estadísticas de todos los datasets"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estadísticas de Datos")
        stats_window.geometry("800x600")
        stats_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(stats_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        stats_text = "ESTADÍSTICAS DETALLADAS DE DATASETS\n" + "="*50 + "\n\n"
        
        datasets = [
            ("Batch Processing", self.current_batch_dataset),
            ("Enhanced ML", self.current_advanced_data)
        ]
        
        for name, data in datasets:
            if data is not None:
                try:
                    memory_mb = data.memory_usage(deep=True).sum() / (1024*1024)
                    dtype_counts = dict(data.dtypes.value_counts())
                    
                    # Estadísticas adicionales
                    numeric_cols = data.select_dtypes(include=[np.number]).columns
                    text_cols = data.select_dtypes(include=['object']).columns
                    
                except:
                    memory_mb = sys.getsizeof(data) / (1024*1024)
                    dtype_counts = "N/A"
                    numeric_cols = []
                    text_cols = []
                
                stats_text += f"{name}:\n"
                stats_text += f"  Filas: {len(data)}\n"
                stats_text += f"  Columnas: {len(data.columns)}\n"
                stats_text += f"  Columnas numéricas: {len(numeric_cols)}\n"
                stats_text += f"  Columnas de texto: {len(text_cols)}\n"
                stats_text += f"  Memoria: {memory_mb:.2f} MB\n"
                stats_text += f"  Tipos de datos: {dtype_counts}\n"
                
                # Valores faltantes
                if len(data) > 0:
                    missing_pct = (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
                    stats_text += f"  Valores faltantes: {missing_pct:.2f}%\n"
                
                stats_text += "-"*40 + "\n\n"
            else:
                stats_text += f"{name}: No cargado\n\n"
        
        # Información de feature selection si está disponible
        if hasattr(self.advanced_ml_tab, 'using_custom_features') and self.advanced_ml_tab.using_custom_features:
            stats_text += "FEATURE SELECTION ACTIVA:\n"
            stats_text += f"  Features seleccionadas: {len(self.advanced_ml_tab.custom_features)}\n"
            stats_text += f"  Features disponibles: {len(self.advanced_ml_tab.feature_columns)}\n"
            stats_text += f"  Reducción: {(1 - len(self.advanced_ml_tab.custom_features)/len(self.advanced_ml_tab.feature_columns))*100:.1f}%\n"
        
        text_widget.insert(1.0, stats_text)
        text_widget.config(state="disabled")
        
        ttk.Button(stats_window, text="Cerrar", 
                  command=stats_window.destroy).pack(pady=10)
    
    def show_feature_analysis(self):
        """Mostrar análisis detallado de features"""
        if hasattr(self.advanced_ml_tab, 'feature_selection_tab'):
            self.advanced_ml_tab.feature_selection_tab.show_detailed_analysis()
        else:
            messagebox.showwarning("Advertencia", "No hay análisis de features disponible")
    
    def show_model_comparison(self):
        """Mostrar comparación de modelos con/sin feature selection"""
        comparison_window = tk.Toplevel(self.root)
        comparison_window.title("Comparación de Modelos")
        comparison_window.geometry("700x500")
        comparison_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(comparison_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        comparison_text = "COMPARACIÓN DE MODELOS\n" + "="*30 + "\n\n"
        
        if hasattr(self.advanced_ml_tab, 'trained_model') and self.advanced_ml_tab.trained_model is not None:
            comparison_text += "MODELO ACTUAL:\n"
            
            if hasattr(self.advanced_ml_tab, 'using_custom_features') and self.advanced_ml_tab.using_custom_features:
                comparison_text += f"  Tipo: Con feature selection personalizada\n"
                comparison_text += f"  Features utilizadas: {len(self.advanced_ml_tab.custom_features)}\n"
            else:
                comparison_text += f"  Tipo: Con todas las features\n"
                comparison_text += f"  Features utilizadas: {len(self.advanced_ml_tab.feature_columns)}\n"
            
            comparison_text += f"  Estimadores: {self.advanced_ml_tab.trained_model.n_estimators}\n"
            
            # Métricas si están disponibles
            if hasattr(self.advanced_ml_tab, 'y_test') and self.advanced_ml_tab.y_test is not None:
                from sklearn.metrics import mean_absolute_error, r2_score
                mae = mean_absolute_error(self.advanced_ml_tab.y_test, self.advanced_ml_tab.test_predictions)
                r2 = r2_score(self.advanced_ml_tab.y_test, self.advanced_ml_tab.test_predictions)
                comparison_text += f"  MAE: {mae:.4f}\n"
                comparison_text += f"  R²: {r2:.4f}\n"
            
            comparison_text += "\nRECOMENDACIONES:\n"
            comparison_text += "• Prueba diferentes combinaciones de features\n"
            comparison_text += "• Compara métricas con/sin feature selection\n"
            comparison_text += "• Usa el análisis de importancia para guiar la selección\n"
            comparison_text += "• Considera el balance entre precisión y simplicidad\n"
            
        else:
            comparison_text += "No hay modelos entrenados para comparar.\n"
            comparison_text += "Entrena un modelo primero para ver las comparaciones."
        
        text_widget.insert(1.0, comparison_text)
        text_widget.config(state="disabled")
        
        ttk.Button(comparison_window, text="Cerrar", 
                  command=comparison_window.destroy).pack(pady=10)
    
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
            ("Enhanced ML", self.current_advanced_data)
        ]
        
        total_memory = 0
        for name, data in datasets:
            if data is not None:
                try:
                    size_mb = data.memory_usage(deep=True).sum() / (1024*1024)
                    total_memory += size_mb
                except:
                    size_mb = sys.getsizeof(data) / (1024*1024)
                    total_memory += size_mb
                memory_text += f"  {name}: {size_mb:.2f} MB\n"
            else:
                memory_text += f"  {name}: 0 MB\n"
        
        memory_text += f"\nTotal memoria datasets: {total_memory:.2f} MB\n"
        
        # Información de feature selection
        if hasattr(self.advanced_ml_tab, 'using_custom_features') and self.advanced_ml_tab.using_custom_features:
            reduction = len(self.advanced_ml_tab.feature_columns) - len(self.advanced_ml_tab.custom_features)
            memory_text += f"\nOptimización con Feature Selection:\n"
            memory_text += f"  Features eliminadas: {reduction}\n"
            memory_text += f"  Reducción estimada: {reduction * 8 / 1024:.1f} KB por muestra\n"
        
        messagebox.showinfo("Uso de Memoria", memory_text)

    # =============================================================================
    # EXPORT METHODS
    # =============================================================================
    
    def export_all_data(self):
        """Exportar todos los datos y análisis"""
        directory = filedialog.askdirectory(title="Select directory to export all data")
        if directory:
            try:
                export_dir = Path(directory) / "vacancy_predictor_enhanced_export"
                export_dir.mkdir(exist_ok=True)
                
                exported_files = []
                
                # Exportar datasets disponibles
                datasets = [
                    ("batch_dataset.csv", self.current_batch_dataset),
                    ("enhanced_ml_data.csv", self.current_advanced_data)
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
                        
                        # Modelo con metadatos completos
                        model_package = {
                            'model': self.advanced_ml_tab.trained_model,
                            'feature_columns': self.advanced_ml_tab.feature_columns,
                            'selected_features': self.advanced_ml_tab.custom_features if hasattr(self.advanced_ml_tab, 'custom_features') else None,
                            'using_custom_features': getattr(self.advanced_ml_tab, 'using_custom_features', False),
                            'feature_importance': getattr(self.advanced_ml_tab, 'feature_importance', None),
                            'export_timestamp': pd.Timestamp.now().isoformat()
                        }
                        
                        joblib.dump(model_package, models_dir / "enhanced_vacancy_model.joblib")
                        exported_files.append("models/enhanced_vacancy_model.joblib")
                    except Exception as e:
                        logger.warning(f"Could not save model: {e}")
                
                # Exportar configuración de feature selection
                if hasattr(self.advanced_ml_tab, 'feature_selection_tab'):
                    try:
                        feature_config = {
                            'selected_features': self.advanced_ml_tab.feature_selection_tab.get_selected_features(),
                            'all_features': self.advanced_ml_tab.feature_selection_tab.all_features,
                            'feature_stats': self.advanced_ml_tab.feature_selection_tab.feature_stats,
                            'export_timestamp': pd.Timestamp.now().isoformat()
                        }
                        
                        with open(export_dir / "feature_selection_config.json", 'w') as f:
                            json.dump(feature_config, f, indent=2, default=str)
                        exported_files.append("feature_selection_config.json")
                        
                    except Exception as e:
                        logger.warning(f"Could not export feature selection: {e}")
                
                # Crear reporte de exportación
                report_lines = [
                    "VACANCY PREDICTOR ENHANCED - EXPORT REPORT",
                    "=" * 45,
                    f"Export Date: {pd.Timestamp.now()}",
                    f"Export Directory: {export_dir}",
                    f"Application Version: v4.0 Enhanced",
                    "",
                    "EXPORTED FILES:",
                    "-" * 20
                ]
                
                for file in exported_files:
                    report_lines.append(f"✓ {file}")
                
                # Información de feature selection si está activa
                if hasattr(self.advanced_ml_tab, 'using_custom_features') and self.advanced_ml_tab.using_custom_features:
                    report_lines.extend([
                        "",
                        "FEATURE SELECTION INFO:",
                        "-" * 25,
                        f"Features selected: {len(self.advanced_ml_tab.custom_features)}",
                        f"Features available: {len(self.advanced_ml_tab.feature_columns)}",
                        f"Reduction: {(1 - len(self.advanced_ml_tab.custom_features)/len(self.advanced_ml_tab.feature_columns))*100:.1f}%"
                    ])
                
                # Guardar reporte
                with open(export_dir / "export_report.txt", 'w') as f:
                    f.write("\n".join(report_lines))
                
                messagebox.showinfo("Export Complete", 
                                   f"Enhanced export finished!\n\n"
                                   f"Files exported: {len(exported_files)}\n"
                                   f"Location: {export_dir}\n\n"
                                   f"Includes feature selection configuration!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

    # =============================================================================
    # GUÍAS DE USUARIO
    # =============================================================================
    
    def show_user_guide(self):
        """Mostrar guía del usuario"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Guía del Usuario v4.0")
        guide_window.geometry("900x700")
        guide_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(guide_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        guide_text = """GUÍA DEL USUARIO - VACANCY PREDICTOR v4.0 ENHANCED
================================================

NUEVAS FUNCIONALIDADES EN v4.0:
✓ Selección interactiva de features
✓ Análisis detallado de importancia
✓ Comparación de modelos optimizados
✓ Exportación avanzada de configuraciones

WORKFLOW RECOMENDADO:

OPCIÓN 1 - PROCESAMIENTO COMPLETO:
1. Use "Batch Processing" para procesar archivos .dump
2. Vaya al tab "Enhanced ML" 
3. Use "Selección Features" para optimizar el modelo
4. Configure parámetros de entrenamiento
5. Entrene y compare resultados

OPCIÓN 2 - DATASET EXISTENTE:
1. Use "File → Import Dataset" para cargar CSV
2. Vaya al tab "Enhanced ML"
3. Analice features en "Selección Features"
4. Seleccione features óptimas
5. Entrene modelo optimizado

CARACTERÍSTICAS DEL ENHANCED ML:
• Selección interactiva de features con tabla
• Filtros por categoría e importancia
• Análisis de correlaciones automático
• Comparación de modelos con/sin selección
• Exportación de configuraciones

TAB DE SELECCIÓN DE FEATURES:
• Tabla interactiva con estadísticas
• Filtros por búsqueda, categoría, importancia
• Selección masiva y por criterios
• Análisis detallado de correlaciones
• Exportación de selecciones

OPTIMIZACIÓN DEL MODELO:
• Use feature importance para guiar selección
• Pruebe diferentes combinaciones
• Compare métricas R² y MAE
• Balance entre precisión y simplicidad
• Exporte configuraciones exitosas

TIPS AVANZADOS:
• Comience con top 20 features por importancia
• Elimine features con baja correlación (<0.05)
• Analice distribución por categorías
• Use análisis detallado para insights
• Guarde selecciones exitosas para reutilizar
"""
        
        text_widget.insert(1.0, guide_text)
        text_widget.config(state="disabled")
        
        ttk.Button(guide_window, text="Cerrar", 
                  command=guide_window.destroy).pack(pady=10)
    
    def show_feature_selection_guide(self):
        """Mostrar guía específica de selección de features"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Guía de Selección de Features")
        guide_window.geometry("800x600")
        guide_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(guide_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        guide_text = """GUÍA DE SELECCIÓN DE FEATURES
===============================

¿QUÉ ES LA SELECCIÓN DE FEATURES?
La selección de features es el proceso de elegir las variables más relevantes para entrenar el modelo, eliminando las redundantes o poco informativas.

BENEFICIOS:
• Mejora la precisión del modelo
• Reduce el overfitting
• Acelera el entrenamiento
• Facilita la interpretación
• Reduce el uso de memoria

CÓMO USAR LA TABLA INTERACTIVA:

1. FILTROS DISPONIBLES:
   • Búsqueda: Filtre por nombre de feature
   • Categoría: Coordinación, Energía, Stress, etc.
   • Importancia: Alta (>0.05), Media (0.01-0.05), Baja (<0.01)

2. SELECCIÓN:
   • Click doble: Activar/desactivar feature individual
   • Seleccionar todas: Todas las features visibles
   • Top N: Seleccionar N features con mayor importancia
   • Invertir: Invertir selección actual

3. MÉTRICAS EN LA TABLA:
   • Importancia: Contribución al modelo (0-1)
   • Correlación: Relación lineal con target (-1 a +1)
   • % Faltantes: Porcentaje de valores perdidos
   • Min/Max/Media: Estadísticas descriptivas

ESTRATEGIAS DE SELECCIÓN:

1. BASADA EN IMPORTANCIA:
   • Comience con top 20-30 features
   • Elimine features con importancia < 0.001
   • Mantenga al menos 10-15 features

2. BASADA EN CORRELACIÓN:
   • Elimine features con |correlación| < 0.05
   • Priorice correlaciones moderadas-altas
   • Considere correlaciones negativas

3. BASADA EN CALIDAD:
   • Elimine features con >20% valores faltantes
   • Revise features con rango muy pequeño
   • Considere distribución por categorías

4. ITERATIVA:
   • Pruebe diferentes combinaciones
   • Compare métricas del modelo
   • Refine basado en resultados

INTERPRETACIÓN DE RESULTADOS:
• R² > 0.8: Excelente selección
• MAE < 5: Buena precisión
• Reducción 30-70%: Optimización efectiva

ANÁLISIS DETALLADO:
Use el botón "Análisis Detallado" para obtener:
• Distribución por categorías
• Top features por importancia
• Estadísticas de correlación
• Recomendaciones automáticas

GUARDAR Y CARGAR:
• Exporte selecciones exitosas
• Reutilice configuraciones
• Documente mejores prácticas
• Compare diferentes enfoques
"""
        
        text_widget.insert(1.0, guide_text)
        text_widget.config(state="disabled")
        
        ttk.Button(guide_window, text="Cerrar", 
                  command=guide_window.destroy).pack(pady=10)
    
    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """Vacancy Predictor ML Suite v4.0 Enhanced
========================================

Suite avanzada para predicción de vacancias con selección inteligente de features.

NUEVAS CARACTERÍSTICAS v4.0:
• Selección interactiva de features con tabla avanzada
• Análisis de importancia y correlaciones automático
• Filtros dinámicos por categoría e importancia
• Comparación de modelos optimizados vs. completos
• Exportación avanzada de configuraciones y modelos

CAPACIDADES MEJORADAS:
• Extracción automática de 160+ features
• Random Forest con optimización inteligente
• Predicciones con features seleccionadas
• Visualizaciones de feature importance
• Análisis detallado de calidad de features
• Export completo de modelos y configuraciones

WORKFLOW OPTIMIZADO:
• Procesamiento batch → Análisis features → Selección → Entrenamiento optimizado

FORMATOS SOPORTADOS:
• Input: archivos .dump, CSV, Excel
• Output: CSV, XLSX, JOBLIB, JSON (configuraciones)
• Export: Modelos completos con metadatos

SELECCIÓN DE FEATURES:
• Tabla interactiva con métricas avanzadas
• Filtros por importancia, correlación, categoría
• Selección masiva y criterios automáticos
• Análisis detallado y recomendaciones
• Configuraciones reutilizables

Version: 4.0.0 - Enhanced ML Suite with Feature Selection
Desarrollado para optimización inteligente de modelos ML
"""
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About Vacancy Predictor v4.0")
        about_window.geometry("600x500")
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
                              "This will clear all current data, models and feature selections. Continue?"):
            # Reset datos
            self.current_data = None
            self.current_batch_dataset = None
            self.current_advanced_data = None
            
            # Reset tabs
            if hasattr(self.batch_tab, 'reset'):
                self.batch_tab.reset()
            if hasattr(self.advanced_ml_tab, 'reset'):
                self.advanced_ml_tab.reset()
            
            self.update_status("New project created - Enhanced ML with Feature Selection ready")
            self.update_indicators()
    
    def on_closing(self):
        """Callback al cerrar aplicación"""
        if messagebox.askokcancel("Quit", "Do you want to quit Vacancy Predictor Enhanced?"):
            try:
                logger.info("Enhanced application closing gracefully")
                self.root.destroy()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
                self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            # Configurar atajos de teclado mejorados
            self.root.bind('<Control-n>', lambda e: self.reset_application())
            self.root.bind('<Control-i>', lambda e: self.import_dataset())
            self.root.bind('<Control-e>', lambda e: self.export_all_data())
            self.root.bind('<Control-f>', lambda e: self.focus_feature_selection_tab())  # Nuevo atajo
            self.root.bind('<Control-q>', lambda e: self.on_closing())
            self.root.bind('<F1>', lambda e: self.show_user_guide())
            self.root.bind('<F2>', lambda e: self.show_data_statistics())
            self.root.bind('<F3>', lambda e: self.show_memory_usage())
            self.root.bind('<F4>', lambda e: self.show_feature_analysis())  # Nuevo atajo
            
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            messagebox.showerror("Critical Error", f"Enhanced application encountered a critical error: {e}")


# =============================================================================
# UTILIDADES ADICIONALES PARA FEATURE SELECTION
# =============================================================================

def create_feature_selection_report(feature_selection_tab, model_results=None):
    """
    Crear reporte detallado de la selección de features
    
    Args:
        feature_selection_tab: Instancia del tab de selección de features
        model_results: Diccionario con resultados del modelo (opcional)
    
    Returns:
        str: Reporte formateado
    """
    
    report_lines = [
        "REPORTE DE SELECCIÓN DE FEATURES",
        "=" * 40,
        f"Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Features disponibles: {len(feature_selection_tab.all_features)}",
        f"Features seleccionadas: {len(feature_selection_tab.selected_features)}",
        f"Reducción: {(1 - len(feature_selection_tab.selected_features)/len(feature_selection_tab.all_features))*100:.1f}%",
        ""
    ]
    
    # Análisis por categorías
    category_counts = {}
    importance_by_category = {}
    
    for feature in feature_selection_tab.selected_features:
        stats = feature_selection_tab.feature_stats[feature]
        category = stats['category']
        
        if category not in category_counts:
            category_counts[category] = 0
            importance_by_category[category] = []
        
        category_counts[category] += 1
        importance_by_category[category].append(stats['importance'])
    
    report_lines.extend([
        "DISTRIBUCIÓN POR CATEGORÍAS:",
        "-" * 30
    ])
    
    for category, count in sorted(category_counts.items()):
        avg_importance = np.mean(importance_by_category[category]) if importance_by_category[category] else 0
        report_lines.append(f"{category}: {count} features (importancia avg: {avg_importance:.4f})")
    
    # Top features
    selected_by_importance = sorted(feature_selection_tab.selected_features,
                                  key=lambda f: feature_selection_tab.feature_stats[f]['importance'],
                                  reverse=True)
    
    report_lines.extend([
        "",
        "TOP 10 FEATURES SELECCIONADAS:",
        "-" * 35
    ])
    
    for i, feature in enumerate(selected_by_importance[:10]):
        stats = feature_selection_tab.feature_stats[feature]
        report_lines.append(f"{i+1:2d}. {feature[:35]:35s} | {stats['importance']:.4f} | {stats['correlation']:+.3f}")
    
    # Estadísticas de calidad
    correlations = [feature_selection_tab.feature_stats[f]['correlation'] for f in feature_selection_tab.selected_features]
    importances = [feature_selection_tab.feature_stats[f]['importance'] for f in feature_selection_tab.selected_features]
    
    report_lines.extend([
        "",
        "ESTADÍSTICAS DE CALIDAD:",
        "-" * 25,
        f"Correlación promedio: {np.mean([abs(c) for c in correlations]):.4f}",
        f"Importancia promedio: {np.mean(importances):.4f}",
        f"Features con alta correlación (>0.3): {sum(1 for c in correlations if abs(c) > 0.3)}",
        f"Features con alta importancia (>0.01): {sum(1 for i in importances if i > 0.01)}"
    ])
    
    # Resultados del modelo si están disponibles
    if model_results:
        report_lines.extend([
            "",
            "RESULTADOS DEL MODELO:",
            "-" * 22,
            f"R² Score: {model_results.get('r2', 'N/A')}",
            f"MAE: {model_results.get('mae', 'N/A')}",
            f"RMSE: {model_results.get('rmse', 'N/A')}"
        ])
    
    return "\n".join(report_lines)


def validate_feature_selection(feature_selection_tab, min_features=5, max_correlation_threshold=0.95):
    """
    Validar la selección de features y dar recomendaciones
    
    Args:
        feature_selection_tab: Instancia del tab de selección
        min_features: Número mínimo recomendado de features
        max_correlation_threshold: Umbral para detectar features muy correlacionadas
    
    Returns:
        dict: Resultado de validación con warnings y recomendaciones
    """
    
    validation_result = {
        'valid': True,
        'warnings': [],
        'recommendations': [],
        'score': 0  # Score de 0-100
    }
    
    selected_features = feature_selection_tab.selected_features
    feature_stats = feature_selection_tab.feature_stats
    
    # Validación 1: Número mínimo de features
    if len(selected_features) < min_features:
        validation_result['valid'] = False
        validation_result['warnings'].append(f"Muy pocas features seleccionadas ({len(selected_features)} < {min_features})")
        validation_result['recommendations'].append("Considera incluir más features para mejorar la capacidad predictiva")
    else:
        validation_result['score'] += 20
    
    # Validación 2: Features con muy baja importancia
    if feature_selection_tab.feature_importance is not None:
        low_importance = [f for f in selected_features if feature_stats[f]['importance'] < 0.001]
        if len(low_importance) > len(selected_features) * 0.3:
            validation_result['warnings'].append(f"{len(low_importance)} features tienen muy baja importancia")
            validation_result['recommendations'].append("Considera remover features con importancia < 0.001")
        else:
            validation_result['score'] += 25
    
    # Validación 3: Features con baja correlación
    low_correlation = [f for f in selected_features if abs(feature_stats[f]['correlation']) < 0.05]
    if len(low_correlation) > len(selected_features) * 0.4:
        validation_result['warnings'].append(f"{len(low_correlation)} features tienen muy baja correlación con el target")
        validation_result['recommendations'].append("Revisa features con |correlación| < 0.05")
    else:
        validation_result['score'] += 20
    
    # Validación 4: Distribución por categorías
    categories = set(feature_stats[f]['category'] for f in selected_features)
    if len(categories) >= 3:
        validation_result['score'] += 15
        validation_result['recommendations'].append("Buena diversidad de categorías de features")
    else:
        validation_result['recommendations'].append("Considera incluir features de más categorías")
    
    # Validación 5: Calidad de datos
    high_missing = [f for f in selected_features if feature_stats[f]['missing_pct'] > 20]
    if len(high_missing) > 0:
        validation_result['warnings'].append(f"{len(high_missing)} features tienen >20% valores faltantes")
        validation_result['recommendations'].append("Revisa la calidad de features con muchos valores faltantes")
    else:
        validation_result['score'] += 20
    
    # Score final
    if validation_result['score'] >= 80:
        validation_result['quality'] = "Excelente"
    elif validation_result['score'] >= 60:
        validation_result['quality'] = "Buena"
    elif validation_result['score'] >= 40:
        validation_result['quality'] = "Aceptable"
    else:
        validation_result['quality'] = "Necesita mejoras"
    
    return validation_result


def suggest_optimal_features(feature_selection_tab, target_count=20, importance_weight=0.4, correlation_weight=0.4, quality_weight=0.2):
    """
    Sugerir selección óptima de features basada en múltiples criterios
    
    Args:
        feature_selection_tab: Instancia del tab de selección
        target_count: Número objetivo de features
        importance_weight: Peso de la importancia en el score
        correlation_weight: Peso de la correlación en el score
        quality_weight: Peso de la calidad en el score
    
    Returns:
        list: Lista de features sugeridas ordenadas por score
    """
    
    feature_scores = {}
    
    for feature in feature_selection_tab.all_features:
        stats = feature_selection_tab.feature_stats[feature]
        
        # Score de importancia (normalizado 0-1)
        importance_score = stats['importance'] if stats['importance'] > 0 else 0
        
        # Score de correlación (absoluta, normalizado 0-1)
        correlation_score = min(abs(stats['correlation']), 1.0)
        
        # Score de calidad (basado en valores faltantes)
        quality_score = max(0, 1 - stats['missing_pct'] / 100)
        
        # Score combinado
        combined_score = (
            importance_score * importance_weight +
            correlation_score * correlation_weight +
            quality_score * quality_weight
        )
        
        feature_scores[feature] = {
            'total_score': combined_score,
            'importance_score': importance_score,
            'correlation_score': correlation_score,
            'quality_score': quality_score
        }
    
    # Ordenar por score total
    suggested_features = sorted(feature_scores.keys(), 
                              key=lambda f: feature_scores[f]['total_score'], 
                              reverse=True)
    
    return suggested_features[:target_count]


# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

def main():
    """Función principal mejorada"""
    try:
        logger.info("Starting Vacancy Predictor ML Suite v4.0 Enhanced")
        
        app = VacancyPredictorGUIEnhanced()
        app.run()
        
    except Exception as e:
        logger.error(f"Failed to start enhanced application: {e}", exc_info=True)
        try:
            messagebox.showerror("Application Error", 
                                f"A critical error occurred during startup:\n\n{e}\n\n"
                                f"Check vacancy_predictor.log for details.")
        except:
            print(f"CRITICAL ERROR: {e}")


if __name__ == "__main__":
    main()