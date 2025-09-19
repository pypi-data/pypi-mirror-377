"""
Aplicación principal de Vacancy Predictor con Multi-Model support
Versión corregida para tu estructura de proyecto
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ===== IMPORTS CORREGIDOS PARA TU ESTRUCTURA =====

# Inicializar variables de disponibilidad
MULTI_MODEL_AVAILABLE = False
BATCH_TAB_AVAILABLE = False
ADVANCED_ML_TAB_AVAILABLE = False
MULTI_MODEL_TAB_AVAILABLE = False

# 1. Multi-Model Processor
try:
    from vacancy_predictor.core.enhanced_ml.multi_model_processor import MultiModelProcessor
    MULTI_MODEL_AVAILABLE = True
    logger.info("Multi-Model processor available")
except ImportError as e:
    logger.warning(f"Multi-Model functionality not available: {e}")
    MultiModelProcessor = None

# 2. Batch Processing Tab (CORRECTO PARA TU ESTRUCTURA)
try:
    from vacancy_predictor.gui.tabs.batch_processor_tab import BatchProcessingTab
    BATCH_TAB_AVAILABLE = True
    logger.info("Batch processing tab available")
except ImportError as e:
    logger.warning(f"Batch processing tab not available: {e}")
    BatchProcessingTab = None

# 3. Advanced ML Tab (CORRECTO PARA TU ESTRUCTURA)
try:
    from vacancy_predictor.gui.tabs.advanced_ml_tab import AdvancedMLTabWithPlots
    ADVANCED_ML_TAB_AVAILABLE = True
    logger.info("Advanced ML tab available")
except ImportError as e:
    logger.warning(f"Advanced ML tab not available: {e}")
    AdvancedMLTabWithPlots = None

# 4. Multi-Model Tab (AHORA CORRECTO)
try:
    from vacancy_predictor.gui.tabs.multi_model_tab import MultiModelTab
    MULTI_MODEL_TAB_AVAILABLE = True
    logger.info("Multi-Model tab available")
except ImportError as e:
    logger.warning(f"Multi-Model tab not available: {e}")
    
    # Crear placeholder cuando no esté disponible
    class MultiModelTab:
        def __init__(self, parent, callback, processor=None):
            self.frame = ttk.Frame(parent)
            self.processor = processor
            
            info_frame = ttk.Frame(self.frame, padding="20")
            info_frame.pack(expand=True, fill="both")
            
            title_label = ttk.Label(info_frame, 
                                   text="Multi-Model Tab No Disponible",
                                   font=('Arial', 16, 'bold'))
            title_label.pack(pady=(0, 20))
            
            info_text = """Archivo requerido: vacancy_predictor/gui/tabs/multi_model_tab.py

Este archivo contiene la interfaz para comparar múltiples modelos ML.
Cree el archivo con el contenido proporcionado para habilitar esta funcionalidad."""
            
            info_label = ttk.Label(info_frame, text=info_text, 
                                  font=('Arial', 11), justify="center")
            info_label.pack()
            
        def load_dataset_from_dataframe(self, data):
            pass
            
        def reset(self):
            pass
class VacancyPredictorApp:
    """Aplicación principal con Multi-Model support"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacancy Predictor - ML Suite v3.0 Enhanced")
        self.root.geometry("1400x900")
        
        # Maximizar ventana según SO
        try:
            if sys.platform == 'win32':
                self.root.state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except:
            pass
        
        # Variables de datos
        self.current_data = None
        self.current_batch_dataset = None
        self.current_advanced_data = None
        
        # NUEVO: Procesador multi-modelo
        if MULTI_MODEL_AVAILABLE:
            try:
                self.multi_model_processor = MultiModelProcessor()
                logger.info("Multi-Model processor initialized")
            except Exception as e:
                logger.error(f"Error initializing multi-model processor: {e}")
                self.multi_model_processor = None
        else:
            self.multi_model_processor = None
        
        # Inicializar interfaz
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        logger.info("Vacancy Predictor ML Suite initialized")
    
    def setup_styles(self):
        """Configurar estilos de la aplicación"""
        try:
            style = ttk.Style()
            style.theme_use('clam')
            
            style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
            style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
            style.configure('Info.TLabel', font=('Arial', 9), foreground='gray')
            style.configure('TNotebook.Tab', padding=[12, 8])
            style.configure('Action.TButton', font=('Arial', 9, 'bold'))
            
        except Exception as e:
            logger.warning(f"Could not set custom styles: {e}")

    def create_menu(self):
        """Crear barra de menú"""
        try:
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)
            
            # Menú Archivo
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Archivo", menu=file_menu)
            file_menu.add_command(label="Nuevo Proyecto", command=self.new_project)
            file_menu.add_separator()
            file_menu.add_command(label="Exportar Resultados", command=self.export_results)
            file_menu.add_separator()
            file_menu.add_command(label="Salir", command=self.root.quit)
            
            # Menú Herramientas
            tools_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Herramientas", menu=tools_menu)
            tools_menu.add_command(label="Validar Datos", command=self.validate_current_data)
            
            # Menú Ayuda
            help_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Ayuda", menu=help_menu)
            help_menu.add_command(label="Acerca de", command=self.show_about)
            
        except Exception as e:
            logger.error(f"Error creating menu: {e}")

    def create_main_interface(self):
        """Crear interfaz principal con tabs"""
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # 1. TAB DE PROCESAMIENTO BATCH
        if BATCH_TAB_AVAILABLE:
            try:
                self.batch_tab = BatchProcessingTab(self.notebook, self.on_batch_data_loaded)
                self.notebook.add(self.batch_tab.frame, text="Batch Processing")
                logger.info("Batch processing tab created")
            except Exception as e:
                logger.error(f"Error creating batch tab: {e}")
                self.create_error_tab("Batch Processing", str(e))
        else:
            self.create_unavailable_tab("Batch Processing", "BatchProcessingTab no disponible")
        
        # 2. TAB DE ADVANCED ML
        if ADVANCED_ML_TAB_AVAILABLE:
            try:
                self.advanced_ml_tab = AdvancedMLTabWithPlots(self.notebook, self.on_advanced_data_loaded)
                self.notebook.add(self.advanced_ml_tab.frame, text="Advanced ML (Legacy)")
                logger.info("Advanced ML tab created")
            except Exception as e:
                logger.error(f"Error creating ML tab: {e}")
                self.create_error_tab("Advanced ML", str(e))
        else:
            self.create_unavailable_tab("Advanced ML", "AdvancedMLTabWithPlots no disponible")
        
        # 3. NUEVO TAB MULTI-MODEL
        if MULTI_MODEL_TAB_AVAILABLE and self.multi_model_processor:
            try:
                self.multi_model_tab = MultiModelTab(
                    self.notebook, 
                    self.on_multi_model_data_loaded,
                    processor=self.multi_model_processor
                )
                self.notebook.add(self.multi_model_tab.frame, text="🤖 Multi-Model ML")
                logger.info("Multi-Model tab created successfully")
            except Exception as e:
                logger.error(f"Error creating Multi-Model tab: {e}")
                self.create_error_tab("Multi-Model", str(e))
        else:
            # Crear tab informativo si no está disponible
            self.create_multi_model_unavailable_tab()
        
        # Bind eventos
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def create_unavailable_tab(self, tab_name, reason):
        """Crear tab cuando un componente no está disponible"""
        unavailable_frame = ttk.Frame(self.notebook)
        self.notebook.add(unavailable_frame, text=f"{tab_name} (N/A)")
        
        info_frame = ttk.Frame(unavailable_frame, padding="20")
        info_frame.pack(expand=True, fill="both")
        
        title_label = ttk.Label(info_frame, 
                               text=f"{tab_name} No Disponible",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        reason_label = ttk.Label(info_frame, text=reason, 
                                font=('Arial', 11), justify="left")
        reason_label.pack()

    def create_multi_model_unavailable_tab(self):
        """Crear tab informativo cuando Multi-Model no está disponible"""
        unavailable_frame = ttk.Frame(self.notebook)
        self.notebook.add(unavailable_frame, text="Multi-Model (N/A)")
        
        info_frame = ttk.Frame(unavailable_frame, padding="20")
        info_frame.pack(expand=True, fill="both")
        
        title_label = ttk.Label(info_frame, 
                               text="Multi-Model ML No Disponible",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        info_text = """Para habilitar la funcionalidad Multi-Model ML, verifique:

1. Que el archivo multi_model_processor.py esté en:
   vacancy_predictor/core/enhanced_ml/

2. Que el archivo multi_model_tab.py esté en:
   vacancy_predictor/tabs/

3. Para XGBoost (recomendado):
   pip install xgboost

4. Para Redes Neuronales (opcional):
   pip install tensorflow

5. Reinicie la aplicación después de instalar

Funcionalidades disponibles con Multi-Model:
• Comparación automática entre Random Forest, XGBoost y Redes Neuronales
• Grid Search optimizado para cada modelo
• Visualizaciones comparativas avanzadas
• Exportación de modelos entrenados
"""
        
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=('Arial', 11), justify="left")
        info_label.pack()
        
        # Botón para reintentar carga
        retry_button = ttk.Button(info_frame, text="Reintentar Carga", 
                                 command=self.retry_multi_model_load)
        retry_button.pack(pady=(20, 0))

    def create_error_tab(self, tab_name, error_message):
        """Crear tab de error cuando algo falla"""
        error_frame = ttk.Frame(self.notebook)
        self.notebook.add(error_frame, text=f"{tab_name} (Error)")
        
        error_container = ttk.Frame(error_frame, padding="20")
        error_container.pack(expand=True, fill="both")
        
        error_title = ttk.Label(error_container, text=f"Error en {tab_name}", 
                               font=('Arial', 14, 'bold'), foreground="red")
        error_title.pack(pady=(0, 10))
        
        error_text = tk.Text(error_container, height=10, wrap='word', 
                            font=('Courier', 10))
        error_text.pack(fill="both", expand=True, pady=(0, 10))
        error_text.insert(1.0, f"Error details:\n\n{error_message}")
        error_text.config(state='disabled')

    def create_status_bar(self):
        """Crear barra de estado"""
        try:
            status_frame = ttk.Frame(self.root)
            status_frame.pack(side="bottom", fill="x", padx=5, pady=2)
            
            self.status_var = tk.StringVar()
            self.status_var.set("Listo - Vacancy Predictor ML Suite v3.0")
            self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
            self.status_label.pack(side="left")
            
            # Indicadores de estado
            self.indicators_frame = ttk.Frame(status_frame)
            self.indicators_frame.pack(side="right")
            
            self.data_indicator_var = tk.StringVar()
            self.data_indicator_var.set("Sin datos")
            self.data_indicator = ttk.Label(self.indicators_frame, textvariable=self.data_indicator_var,
                                           foreground="red")
            self.data_indicator.pack(side="right", padx=5)
            
        except Exception as e:
            logger.error(f"Error creating status bar: {e}")

    # Callback methods
    def on_batch_data_loaded(self, data):
        """Callback cuando se cargan datos del batch processing"""
        self.current_batch_dataset = data
        self.current_data = data
        
        self.update_status(f"Batch dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()
        
        # Sincronizar con otros tabs
        try:
            if hasattr(self, 'advanced_ml_tab') and hasattr(self.advanced_ml_tab, 'load_dataset_from_dataframe'):
                self.advanced_ml_tab.load_dataset_from_dataframe(data)
        except Exception as e:
            logger.warning(f"Could not sync batch data to Advanced ML: {e}")
        
        if MULTI_MODEL_TAB_AVAILABLE and hasattr(self, 'multi_model_tab'):
            try:
                self.multi_model_tab.load_dataset_from_dataframe(data)
            except Exception as e:
                logger.warning(f"Could not sync batch data to Multi-Model: {e}")

    def on_advanced_data_loaded(self, data):
        """Callback para datos del Advanced ML tab"""
        self.current_advanced_data = data
        self.current_data = data
        
        self.update_status(f"Advanced ML dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()

    def on_multi_model_data_loaded(self, data):
        """Callback para el tab multi-modelo"""
        self.current_data = data
        
        self.update_status(f"Multi-Model dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()

    def on_tab_changed(self, event):
        """Callback cuando cambia el tab activo"""
        try:
            selected_tab = event.widget.tab('current')['text']
            self.update_status(f"Active tab: {selected_tab}")
        except:
            pass

    # Utility methods
    def update_status(self, message):
        """Actualizar mensaje de estado"""
        try:
            self.status_var.set(message)
            self.root.update_idletasks()
            logger.info(f"Status: {message}")
        except Exception as e:
            logger.error(f"Error updating status: {e}")

    def update_indicators(self):
        """Actualizar indicadores de estado"""
        try:
            if self.current_data is not None:
                rows = len(self.current_data)
                cols = len(self.current_data.columns)
                self.data_indicator_var.set(f"Datos: {rows}x{cols}")
                self.data_indicator.config(foreground="green")
            else:
                self.data_indicator_var.set("Sin datos")
                self.data_indicator.config(foreground="red")
                
        except Exception as e:
            logger.error(f"Error updating indicators: {e}")

    def retry_multi_model_load(self):
        """Reintentar cargar funcionalidad multi-modelo"""
        try:
            global MULTI_MODEL_AVAILABLE, MULTI_MODEL_TAB_AVAILABLE
            
            # Reintentar imports
            from vacancy_predictor.core.enhanced_ml.multi_model_processor import MultiModelProcessor
            from vacancy_predictor.core.enhanced_ml.model_configuration_tab import ModelConfigurationTab
            
            MULTI_MODEL_AVAILABLE = True
            MULTI_MODEL_TAB_AVAILABLE = True
            
            # Crear procesador
            self.multi_model_processor = MultiModelProcessor()
            
            messagebox.showinfo("Éxito", 
                               "Multi-Model cargado exitosamente!\n"
                               "Reinicie la aplicación para ver el tab completo.")
            
        except Exception as e:
            messagebox.showerror("Error", 
                                f"No se pudo cargar Multi-Model:\n{str(e)}\n\n"
                                "Verifique que los archivos existan y las dependencias estén instaladas.")

    # Menu methods
    def new_project(self):
        """Crear nuevo proyecto"""
        try:
            result = messagebox.askyesno("Nuevo Proyecto", 
                                       "¿Está seguro de que desea crear un nuevo proyecto?\n"
                                       "Se perderán todos los datos y modelos actuales.")
            if result:
                self.current_data = None
                self.current_batch_dataset = None
                self.current_advanced_data = None
                
                if self.multi_model_processor:
                    self.multi_model_processor = MultiModelProcessor()
                
                # Reiniciar tabs
                if hasattr(self, 'batch_tab') and hasattr(self.batch_tab, 'reset'):
                    self.batch_tab.reset()
                if hasattr(self, 'advanced_ml_tab') and hasattr(self.advanced_ml_tab, 'reset'):
                    self.advanced_ml_tab.reset()
                if hasattr(self, 'multi_model_tab') and hasattr(self.multi_model_tab, 'reset'):
                    self.multi_model_tab.reset()
                
                self.update_status("Nuevo proyecto creado")
                self.update_indicators()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error creando nuevo proyecto: {str(e)}")

    def export_results(self):
        """Exportar resultados globales"""
        try:
            if self.current_data is None:
                messagebox.showwarning("Advertencia", "No hay datos para exportar")
                return
            
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
            )
            
            if filename:
                if filename.endswith('.xlsx'):
                    self.current_data.to_excel(filename, index=False)
                else:
                    self.current_data.to_csv(filename, index=False)
                
                messagebox.showinfo("Éxito", f"Datos exportados a: {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando: {str(e)}")

    def validate_current_data(self):
        """Validar datos actuales"""
        try:
            if self.current_data is None:
                messagebox.showwarning("Advertencia", "No hay datos cargados")
                return
            
            total_rows = len(self.current_data)
            total_cols = len(self.current_data.columns)
            missing_values = self.current_data.isnull().sum().sum()
            memory_usage = self.current_data.memory_usage(deep=True).sum() / 1024**2
            
            numeric_cols = len(self.current_data.select_dtypes(include=['number']).columns)
            object_cols = len(self.current_data.select_dtypes(include=['object']).columns)
            
            validation_message = f"""Validación de Datos:

📊 Estadísticas Generales:
• Filas: {total_rows:,}
• Columnas: {total_cols}
• Valores faltantes: {missing_values:,}
• Uso de memoria: {memory_usage:.2f} MB

📈 Tipos de Datos:
• Columnas numéricas: {numeric_cols}
• Columnas de texto: {object_cols}

✅ Estado: {'Datos válidos para ML' if missing_values < total_rows * 0.1 else 'Revisar valores faltantes'}
"""
            
            messagebox.showinfo("Validación de Datos", validation_message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error validando datos: {str(e)}")

    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """Vacancy Predictor ML Suite v3.0

🎯 Aplicación para predicción de vacantes usando Machine Learning

👨‍💻 Desarrollado con Python
📅 Versión: 3.0 Enhanced
🐍 Soporte para múltiples algoritmos ML

📦 COMPONENTES:
   • Multi-Model Processor
   • Batch Processing Engine  
   • Advanced Visualization Suite
   • Grid Search Optimization

🔬 ALGORITMOS SOPORTADOS:
   • Random Forest (siempre disponible)
   • XGBoost (si está instalado)
   • Redes Neuronales (con TensorFlow)

© 2024 - Vacancy Predictor Project"""
        
        messagebox.showinfo("Acerca de", about_text)

    def run(self):
        """Ejecutar la aplicación"""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Application runtime error: {e}")
            messagebox.showerror("Error Fatal", f"Error en la aplicación: {str(e)}")
        finally:
            logger.info("Application closed")


# Función para inicializar la aplicación
def main():
    """Función principal para ejecutar la aplicación"""
    try:
        app = VacancyPredictorApp()
        app.run()
    except Exception as e:
        print(f"Error fatal inicializando aplicación: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()