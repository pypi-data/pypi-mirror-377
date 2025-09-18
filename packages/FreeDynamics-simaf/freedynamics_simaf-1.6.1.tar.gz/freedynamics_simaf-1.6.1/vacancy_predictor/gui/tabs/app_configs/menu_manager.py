"""
menu_manager.py
Gestión centralizada de menús y atajos de teclado
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, List, Callable, Optional
import platform
import sys
import time

from .application_config import ApplicationConfig

logger = logging.getLogger(__name__)

class MenuManager:
    """
    Gestor centralizado de menús y atajos de teclado
    Proporciona una interfaz consistente para todos los menús de la aplicación
    """
    
    def __init__(self, parent: tk.Tk, app_controller):
        """
        Inicializar gestor de menús
        
        Args:
            parent: Ventana principal de tkinter
            app_controller: Controlador principal de la aplicación
        """
        self.parent = parent
        self.app_controller = app_controller
        self.config = ApplicationConfig()
        
        # Referencias a menús
        self.menubar = None
        self.menus = {}
        self.recent_files = []
        self.recent_projects = []
        
        # Estado de menús
        self.menu_state = {
            'data_loaded': False,
            'model_trained': False,
            'processing_active': False,
            'feature_selection_active': False
        }
        
        # Gestores auxiliares
        self.context_menu_manager = None
        self.state_manager = None
        
        self.create_menubar()
        self._create_auxiliary_managers()
        logger.info("MenuManager initialized")
    
    def _create_auxiliary_managers(self):
        """Crear gestores auxiliares"""
        self.context_menu_manager = ContextMenuManager(self)
        self.state_manager = MenuStateManager(self)
    
    def create_menubar(self):
        """Crear barra de menús principal"""
        self.menubar = tk.Menu(self.parent)
        self.parent.config(menu=self.menubar)
        
        # Crear menús principales
        self.create_file_menu()
        self.create_data_menu()
        self.create_ml_menu()
        self.create_tools_menu()
        self.create_view_menu()
        self.create_help_menu()
        
        # Configurar atajos de teclado
        self.setup_keyboard_shortcuts()
        
        logger.info("Menubar created with all menus")
    
    def create_file_menu(self):
        """Crear menú File"""
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=file_menu)
        self.menus['file'] = file_menu
        
        # Nuevo proyecto
        file_menu.add_command(
            label="New Project",
            command=self.app_controller.reset_application,
            accelerator="Ctrl+N"
        )
        
        file_menu.add_separator()
        
        # Importar/Exportar
        file_menu.add_command(
            label="Import Dataset...",
            command=self.app_controller.import_dataset,
            accelerator="Ctrl+I"
        )
        
        file_menu.add_command(
            label="Import Configuration...",
            command=self.import_configuration
        )
        
        file_menu.add_separator()
        
        # Submenu de archivos recientes
        self.recent_files_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_files_menu)
        self.update_recent_files_menu()
        
        file_menu.add_separator()
        
        # Exportar
        export_submenu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Export", menu=export_submenu)
        
        export_submenu.add_command(
            label="Export All Data...",
            command=self.app_controller.export_all_data,
            accelerator="Ctrl+E"
        )
        
        export_submenu.add_command(
            label="Export Current Dataset...",
            command=self.export_current_dataset
        )
        
        export_submenu.add_command(
            label="Export Configuration...",
            command=self.export_configuration
        )
        
        file_menu.add_separator()
        
        # Salir
        file_menu.add_command(
            label="Exit",
            command=self.app_controller.on_closing,
            accelerator="Ctrl+Q"
        )
    
    def create_data_menu(self):
        """Crear menú Data"""
        data_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Data", menu=data_menu)
        self.menus['data'] = data_menu
        
        # Procesamiento batch
        data_menu.add_command(
            label="Batch Processing",
            command=self.app_controller.focus_batch_tab
        )
        
        data_menu.add_command(
            label="Load Batch Dataset...",
            command=self.load_batch_dataset
        )
        
        data_menu.add_separator()
        
        # Análisis de datos
        data_menu.add_command(
            label="Data Statistics",
            command=self.app_controller.show_data_statistics,
            accelerator="F2"
        )
        
        data_menu.add_command(
            label="Data Quality Report",
            command=self.show_data_quality_report
        )
        
        data_menu.add_command(
            label="Memory Usage",
            command=self.app_controller.show_memory_usage,
            accelerator="F3"
        )
        
        data_menu.add_separator()
        
        # Validación
        data_menu.add_command(
            label="Validate Dataset",
            command=self.validate_current_dataset
        )
        
        data_menu.add_command(
            label="Clean Dataset",
            command=self.clean_current_dataset
        )
    
    def create_ml_menu(self):
        """Crear menú Machine Learning"""
        ml_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Machine Learning", menu=ml_menu)
        self.menus['ml'] = ml_menu
        
        # Navegación
        ml_menu.add_command(
            label="Go to Enhanced ML",
            command=self.app_controller.focus_advanced_ml_tab
        )
        
        ml_menu.add_command(
            label="Feature Selection",
            command=self.app_controller.focus_feature_selection,
            accelerator="Ctrl+F"
        )
        
        ml_menu.add_separator()
        
        # Entrenamiento
        train_submenu = tk.Menu(ml_menu, tearoff=0)
        ml_menu.add_cascade(label="Training", menu=train_submenu)
        
        train_submenu.add_command(
            label="Train Model",
            command=self.train_model,
            accelerator="F5"
        )
        
        train_submenu.add_command(
            label="Cross Validation",
            command=self.cross_validate_model,
            accelerator="F6"
        )
        
        train_submenu.add_command(
            label="Hyperparameter Tuning",
            command=self.hyperparameter_tuning
        )
        
        # Evaluación
        eval_submenu = tk.Menu(ml_menu, tearoff=0)
        ml_menu.add_cascade(label="Evaluation", menu=eval_submenu)
        
        eval_submenu.add_command(
            label="Model Performance",
            command=self.show_model_performance
        )
        
        eval_submenu.add_command(
            label="Feature Importance",
            command=self.app_controller.show_feature_analysis,
            accelerator="F4"
        )
        
        eval_submenu.add_command(
            label="Model Comparison",
            command=self.show_model_comparison
        )
        
        ml_menu.add_separator()
        
        # Predicción
        predict_submenu = tk.Menu(ml_menu, tearoff=0)
        ml_menu.add_cascade(label="Prediction", menu=predict_submenu)
        
        predict_submenu.add_command(
            label="Single Prediction",
            command=self.single_prediction,
            accelerator="F7"
        )
        
        predict_submenu.add_command(
            label="Batch Prediction",
            command=self.batch_prediction
        )
        
        ml_menu.add_separator()
        
        # Modelos
        model_submenu = tk.Menu(ml_menu, tearoff=0)
        ml_menu.add_cascade(label="Models", menu=model_submenu)
        
        model_submenu.add_command(
            label="Save Model...",
            command=self.save_model
        )
        
        model_submenu.add_command(
            label="Load Model...",
            command=self.load_model
        )
        
        model_submenu.add_command(
            label="Export Model Package...",
            command=self.export_model_package
        )
    
    def create_tools_menu(self):
        """Crear menú Tools"""
        tools_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Tools", menu=tools_menu)
        self.menus['tools'] = tools_menu
        
        # Análisis
        analysis_submenu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Analysis", menu=analysis_submenu)
        
        analysis_submenu.add_command(
            label="Feature Analysis",
            command=self.app_controller.show_feature_analysis
        )
        
        analysis_submenu.add_command(
            label="Correlation Matrix",
            command=self.show_correlation_matrix
        )
        
        analysis_submenu.add_command(
            label="Data Distribution",
            command=self.show_data_distribution
        )
        
        # Utilidades
        tools_menu.add_separator()
        
        tools_menu.add_command(
            label="Feature Calculator",
            command=self.open_feature_calculator
        )
        
        tools_menu.add_command(
            label="Data Transformer",
            command=self.open_data_transformer
        )
        
        tools_menu.add_command(
            label="Configuration Editor",
            command=self.open_configuration_editor
        )
        
        tools_menu.add_separator()
        
        # Diagnósticos
        diagnostics_submenu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Diagnostics", menu=diagnostics_submenu)
        
        diagnostics_submenu.add_command(
            label="System Information",
            command=self.show_system_info
        )
        
        diagnostics_submenu.add_command(
            label="Performance Monitor",
            command=self.show_performance_monitor
        )
        
        diagnostics_submenu.add_command(
            label="Debug Information",
            command=self.show_debug_info
        )
        
        # Automatización
        tools_menu.add_separator()
        
        automation_submenu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Automation", menu=automation_submenu)
        
        automation_submenu.add_command(
            label="Create Workflow...",
            command=self.create_workflow
        )
        
        automation_submenu.add_command(
            label="Run Saved Workflow...",
            command=self.run_workflow
        )
        
        automation_submenu.add_command(
            label="Schedule Analysis...",
            command=self.schedule_analysis
        )
    
    def create_view_menu(self):
        """Crear menú View"""
        view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=view_menu)
        self.menus['view'] = view_menu
        
        # Zoom y diseño
        view_menu.add_command(
            label="Zoom In",
            command=self.zoom_in,
            accelerator="Ctrl+Plus"
        )
        
        view_menu.add_command(
            label="Zoom Out",
            command=self.zoom_out,
            accelerator="Ctrl+Minus"
        )
        
        view_menu.add_command(
            label="Reset Zoom",
            command=self.reset_zoom,
            accelerator="Ctrl+0"
        )
        
        view_menu.add_separator()
        
        # Paneles
        panels_submenu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Panels", menu=panels_submenu)
        
        self.status_bar_var = tk.BooleanVar(value=True)
        panels_submenu.add_checkbutton(
            label="Status Bar",
            variable=self.status_bar_var,
            command=self.toggle_status_bar
        )
        
        self.toolbar_var = tk.BooleanVar(value=False)
        panels_submenu.add_checkbutton(
            label="Toolbar",
            variable=self.toolbar_var,
            command=self.toggle_toolbar
        )
        
        # Temas
        view_menu.add_separator()
        
        theme_submenu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_submenu)
        
        self.theme_var = tk.StringVar(value="default")
        themes = ["default", "clam", "alt", "classic"]
        
        for theme in themes:
            theme_submenu.add_radiobutton(
                label=theme.title(),
                variable=self.theme_var,
                value=theme,
                command=lambda t=theme: self.change_theme(t)
            )
        
        # Layouts predefinidos
        view_menu.add_separator()
        
        layout_submenu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Layouts", menu=layout_submenu)
        
        layout_submenu.add_command(
            label="Data Analysis Layout",
            command=self.apply_data_analysis_layout
        )
        
        layout_submenu.add_command(
            label="ML Training Layout",
            command=self.apply_ml_training_layout
        )
        
        layout_submenu.add_command(
            label="Feature Selection Layout",
            command=self.apply_feature_selection_layout
        )
        
        layout_submenu.add_separator()
        
        layout_submenu.add_command(
            label="Save Current Layout...",
            command=self.save_current_layout
        )
        
        layout_submenu.add_command(
            label="Load Custom Layout...",
            command=self.load_custom_layout
        )
    
    def create_help_menu(self):
        """Crear menú Help"""
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        self.menus['help'] = help_menu
        
        # Documentación
        help_menu.add_command(
            label="User Guide",
            command=self.app_controller.show_user_guide,
            accelerator="F1"
        )
        
        help_menu.add_command(
            label="Feature Selection Guide",
            command=self.show_feature_selection_guide
        )
        
        help_menu.add_command(
            label="ML Training Guide",
            command=self.show_ml_training_guide
        )
        
        help_menu.add_separator()
        
        # Tutoriales
        tutorials_submenu = tk.Menu(help_menu, tearoff=0)
        help_menu.add_cascade(label="Tutorials", menu=tutorials_submenu)
        
        tutorials_submenu.add_command(
            label="Quick Start Tutorial",
            command=self.show_quick_start_tutorial
        )
        
        tutorials_submenu.add_command(
            label="Advanced Features Tutorial",
            command=self.show_advanced_tutorial
        )
        
        tutorials_submenu.add_command(
            label="Batch Processing Tutorial",
            command=self.show_batch_tutorial
        )
        
        # Referencias
        help_menu.add_separator()
        
        references_submenu = tk.Menu(help_menu, tearoff=0)
        help_menu.add_cascade(label="Reference", menu=references_submenu)
        
        references_submenu.add_command(
            label="Keyboard Shortcuts",
            command=self.show_keyboard_shortcuts
        )
        
        references_submenu.add_command(
            label="Feature Glossary",
            command=self.show_feature_glossary
        )
        
        references_submenu.add_command(
            label="Troubleshooting",
            command=self.show_troubleshooting
        )
        
        # Soporte
        help_menu.add_separator()
        
        help_menu.add_command(
            label="Check for Updates",
            command=self.check_for_updates
        )
        
        help_menu.add_command(
            label="Report Bug",
            command=self.report_bug
        )
        
        help_menu.add_command(
            label="Send Feedback",
            command=self.send_feedback
        )
        
        help_menu.add_separator()
        
        help_menu.add_command(
            label="About",
            command=self.show_about
        )
    
    def setup_keyboard_shortcuts(self):
        """Configurar atajos de teclado"""
        shortcuts = self.config.KEYBOARD_SHORTCUTS
        
        for shortcut, description in shortcuts.items():
            # Mapear atajos a métodos del controlador
            if shortcut == '<Control-n>':
                self.parent.bind(shortcut, lambda e: self.app_controller.reset_application())
            elif shortcut == '<Control-i>':
                self.parent.bind(shortcut, lambda e: self.app_controller.import_dataset())
            elif shortcut == '<Control-e>':
                self.parent.bind(shortcut, lambda e: self.app_controller.export_all_data())
            elif shortcut == '<Control-f>':
                self.parent.bind(shortcut, lambda e: self.app_controller.focus_feature_selection())
            elif shortcut == '<Control-q>':
                self.parent.bind(shortcut, lambda e: self.app_controller.on_closing())
            elif shortcut == '<F1>':
                self.parent.bind(shortcut, lambda e: self.app_controller.show_user_guide())
            elif shortcut == '<F2>':
                self.parent.bind(shortcut, lambda e: self.app_controller.show_data_statistics())
            elif shortcut == '<F3>':
                self.parent.bind(shortcut, lambda e: self.app_controller.show_memory_usage())
            elif shortcut == '<F4>':
                self.parent.bind(shortcut, lambda e: self.app_controller.show_feature_analysis())
            elif shortcut == '<F5>':
                self.parent.bind(shortcut, lambda e: self.train_model())
            elif shortcut == '<F6>':
                self.parent.bind(shortcut, lambda e: self.cross_validate_model())
            elif shortcut == '<F7>':
                self.parent.bind(shortcut, lambda e: self.single_prediction())
        
        logger.info(f"Configured {len(shortcuts)} keyboard shortcuts")
    
    # =============================================================================
    # MÉTODOS DE ESTADO DE MENÚS
    # =============================================================================
    
    def update_menu_state(self, state_changes: Dict):
        """
        Actualizar estado de menús basado en cambios en la aplicación
        
        Args:
            state_changes: Diccionario con cambios de estado
        """
        self.menu_state.update(state_changes)
        self.refresh_menu_states()
    
    def refresh_menu_states(self):
        """Refrescar estados de elementos de menú"""
        try:
            # Estado basado en datos cargados
            data_dependent_state = "normal" if self.menu_state['data_loaded'] else "disabled"
            
            # Menú ML
            ml_menu = self.menus.get('ml')
            if ml_menu:
                # Deshabilitar opciones ML si no hay datos
                for i in range(ml_menu.index('end') + 1):
                    try:
                        if 'Training' in str(ml_menu.entrycget(i, 'label')):
                            ml_menu.entryconfig(i, state=data_dependent_state)
                    except:
                        pass
            
            # Estado basado en modelo entrenado
            model_dependent_state = "normal" if self.menu_state['model_trained'] else "disabled"
            
            # Estado durante procesamiento
            if self.menu_state['processing_active']:
                self.disable_processing_sensitive_menus()
            else:
                self.enable_processing_sensitive_menus()
                
        except Exception as e:
            logger.error(f"Error refreshing menu states: {e}")
    
    def disable_processing_sensitive_menus(self):
        """Deshabilitar menús sensibles durante procesamiento"""
        sensitive_menus = ['file', 'data']
        
        for menu_name in sensitive_menus:
            if menu_name in self.menus:
                try:
                    menu = self.menus[menu_name]
                    # Deshabilitar elementos específicos como importar/exportar
                    for i in range(menu.index('end') + 1):
                        try:
                            label = menu.entrycget(i, 'label')
                            if any(word in label for word in ['Import', 'Export', 'Load']):
                                menu.entryconfig(i, state="disabled")
                        except:
                            pass
                except Exception as e:
                    logger.error(f"Error disabling menu {menu_name}: {e}")
    
    def enable_processing_sensitive_menus(self):
        """Habilitar menús después del procesamiento"""
        sensitive_menus = ['file', 'data']
        
        for menu_name in sensitive_menus:
            if menu_name in self.menus:
                try:
                    menu = self.menus[menu_name]
                    # Rehabilitar elementos
                    for i in range(menu.index('end') + 1):
                        try:
                            menu.entryconfig(i, state="normal")
                        except:
                            pass
                except Exception as e:
                    logger.error(f"Error enabling menu {menu_name}: {e}")
    
    # =============================================================================
    # MÉTODOS DE ARCHIVOS RECIENTES
    # =============================================================================
    
    def add_recent_file(self, file_path: str):
        """
        Agregar archivo a la lista de recientes
        
        Args:
            file_path: Ruta del archivo
        """
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        # Mantener solo los últimos 10
        if len(self.recent_files) > 10:
            self.recent_files = self.recent_files[:10]
        
        self.update_recent_files_menu()
    
    def update_recent_files_menu(self):
        """Actualizar menú de archivos recientes"""
        # Limpiar menú actual
        self.recent_files_menu.delete(0, 'end')
        
        if not self.recent_files:
            self.recent_files_menu.add_command(label="(No recent files)", state="disabled")
        else:
            for i, file_path in enumerate(self.recent_files):
                # Mostrar solo el nombre del archivo para brevedad
                display_name = f"{i+1}. {file_path.split('/')[-1]}"
                self.recent_files_menu.add_command(
                    label=display_name,
                    command=lambda path=file_path: self.open_recent_file(path)
                )
            
            self.recent_files_menu.add_separator()
            self.recent_files_menu.add_command(
                label="Clear Recent Files",
                command=self.clear_recent_files
            )
    
    def open_recent_file(self, file_path: str):
        """Abrir archivo reciente"""
        try:
            # Delegar al controlador principal
            self.app_controller.load_file(file_path)
        except Exception as e:
            logger.error(f"Error opening recent file {file_path}: {e}")
            self.app_controller.show_error(f"Error abriendo archivo reciente:\n{e}")
    
    def clear_recent_files(self):
        """Limpiar lista de archivos recientes"""
        self.recent_files.clear()
        self.update_recent_files_menu()
    
    # =============================================================================
    # IMPLEMENTACIÓN DE COMANDOS DE MENÚ
    # =============================================================================
    
    # File Menu Commands
    def import_configuration(self):
        """Importar configuración desde archivo"""
        try:
            file_path = self.app_controller.dialog_manager.open_file_dialog(
                title="Importar Configuración",
                filetypes=[("JSON files", "*.json"), ("Config files", "*.cfg")]
            )
            
            if file_path:
                self.app_controller.show_info("Funcionalidad en desarrollo", 
                                            "La importación de configuración estará disponible próximamente")
        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
    
    def export_configuration(self):
        """Exportar configuración actual"""
        try:
            file_path = self.app_controller.dialog_manager.save_file_dialog(
                title="Exportar Configuración",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            
            if file_path:
                self.app_controller.show_info("Funcionalidad en desarrollo",
                                            "La exportación de configuración estará disponible próximamente")
        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
    
    def export_current_dataset(self):
        """Exportar dataset actual"""
        if hasattr(self.app_controller, 'main_interface'):
            try:
                current_tab_info = self.app_controller.main_interface.get_current_tab_info()
                self.app_controller.show_info("Exportación", "Implementar exportación de dataset actual")
            except Exception as e:
                logger.error(f"Error exporting current dataset: {e}")
    
    # Data Menu Commands
    def load_batch_dataset(self):
        """Cargar dataset batch"""
        self.app_controller.import_dataset()
    
    def show_data_quality_report(self):
        """Mostrar reporte de calidad de datos"""
        try:
            self.app_controller.show_info("Reporte de Calidad", 
                                        "Funcionalidad de reporte de calidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing data quality report: {e}")
    
    def validate_current_dataset(self):
        """Validar dataset actual"""
        try:
            self.app_controller.show_info("Validación", 
                                        "Funcionalidad de validación en desarrollo")
        except Exception as e:
            logger.error(f"Error validating dataset: {e}")
    
    def clean_current_dataset(self):
        """Limpiar dataset actual"""
        try:
            self.app_controller.show_info("Limpieza", 
                                        "Funcionalidad de limpieza en desarrollo")
        except Exception as e:
            logger.error(f"Error cleaning dataset: {e}")
    
    # ML Menu Commands
    def train_model(self):
        """Entrenar modelo"""
        try:
            self.app_controller.focus_advanced_ml_tab()
            if hasattr(self.app_controller, 'main_interface'):
                ml_tab = self.app_controller.main_interface.tabs.get('enhanced_ml')
                if ml_tab and hasattr(ml_tab, 'train_model'):
                    ml_tab.train_model()
                else:
                    self.app_controller.show_warning("Modelo", "Cargue datos primero")
        except Exception as e:
            logger.error(f"Error training model: {e}")
    
    def cross_validate_model(self):
        """Validación cruzada del modelo"""
        try:
            self.app_controller.show_info("Validación Cruzada", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error in cross validation: {e}")
    
    def hyperparameter_tuning(self):
        """Ajuste de hiperparámetros"""
        try:
            self.app_controller.show_info("Hiperparámetros", 
                                        "Funcionalidad de ajuste de hiperparámetros en desarrollo")
        except Exception as e:
            logger.error(f"Error in hyperparameter tuning: {e}")
    
    def show_model_performance(self):
        """Mostrar rendimiento del modelo"""
        try:
            self.app_controller.show_info("Rendimiento", 
                                        "Funcionalidad de análisis de rendimiento en desarrollo")
        except Exception as e:
            logger.error(f"Error showing model performance: {e}")
    
    def show_model_comparison(self):
        """Mostrar comparación de modelos"""
        try:
            self.app_controller.show_info("Comparación", 
                                        "Funcionalidad de comparación de modelos en desarrollo")
        except Exception as e:
            logger.error(f"Error showing model comparison: {e}")
    
    def single_prediction(self):
        """Predicción individual"""
        try:
            self.app_controller.focus_advanced_ml_tab()
        except Exception as e:
            logger.error(f"Error in single prediction: {e}")
    
    def batch_prediction(self):
        """Predicción por lotes"""
        try:
            self.app_controller.show_info("Predicción por Lotes", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error in batch prediction: {e}")
    
    def save_model(self):
        """Guardar modelo"""
        try:
            if hasattr(self.app_controller, 'main_interface'):
                ml_tab = self.app_controller.main_interface.tabs.get('enhanced_ml')
                if ml_tab and hasattr(ml_tab, 'save_model'):
                    ml_tab.save_model()
                else:
                    self.app_controller.show_warning("Modelo", "No hay modelo entrenado para guardar")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Cargar modelo"""
        try:
            if hasattr(self.app_controller, 'main_interface'):
                ml_tab = self.app_controller.main_interface.tabs.get('enhanced_ml')
                if ml_tab and hasattr(ml_tab, 'load_model'):
                    ml_tab.load_model()
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def export_model_package(self):
        """Exportar paquete completo del modelo"""
        try:
            self.app_controller.show_info("Exportar Modelo", 
                                        "Funcionalidad de exportación completa en desarrollo")
        except Exception as e:
            logger.error(f"Error exporting model package: {e}")
    
    # Tools Menu Commands
    def show_correlation_matrix(self):
        """Mostrar matriz de correlación"""
        try:
            self.app_controller.show_info("Matriz de Correlación", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing correlation matrix: {e}")
    
    def show_data_distribution(self):
        """Mostrar distribución de datos"""
        try:
            self.app_controller.show_info("Distribución de Datos", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing data distribution: {e}")
    
    def open_feature_calculator(self):
        """Abrir calculadora de features"""
        try:
            self.app_controller.show_info("Calculadora de Features", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error opening feature calculator: {e}")
    
    def open_data_transformer(self):
        """Abrir transformador de datos"""
        try:
            self.app_controller.show_info("Transformador de Datos", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error opening data transformer: {e}")
    
    def open_configuration_editor(self):
        """Abrir editor de configuración"""
        try:
            self.app_controller.show_info("Editor de Configuración", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error opening configuration editor: {e}")
    
    # View Menu Commands
    def zoom_in(self):
        """Aumentar zoom"""
        try:
            # Implementar zoom in - podría usar una variable de escala
            current_font = self.parent.option_get('font', 'TkDefaultFont')
            logger.info("Zoom in functionality - to be implemented")
        except Exception as e:
            logger.error(f"Error in zoom in: {e}")
    
    def zoom_out(self):
        """Reducir zoom"""
        try:
            # Implementar zoom out
            logger.info("Zoom out functionality - to be implemented")
        except Exception as e:
            logger.error(f"Error in zoom out: {e}")
    
    def reset_zoom(self):
        """Resetear zoom"""
        try:
            # Implementar reset zoom
            logger.info("Reset zoom functionality - to be implemented")
        except Exception as e:
            logger.error(f"Error in reset zoom: {e}")
    
    def toggle_status_bar(self):
        """Alternar barra de estado"""
        try:
            if hasattr(self.app_controller, 'status_bar'):
                if self.status_bar_var.get():
                    self.app_controller.status_bar.pack(side='bottom', fill='x')
                else:
                    self.app_controller.status_bar.pack_forget()
        except Exception as e:
            logger.error(f"Error toggling status bar: {e}")
    
    def toggle_toolbar(self):
        """Alternar toolbar"""
        try:
            if hasattr(self.app_controller, 'toolbar'):
                if self.toolbar_var.get():
                    self.app_controller.toolbar.pack(side='top', fill='x')
                else:
                    self.app_controller.toolbar.pack_forget()
        except Exception as e:
            logger.error(f"Error toggling toolbar: {e}")
    
    def change_theme(self, theme_name: str):
        """Cambiar tema de la aplicación"""
        try:
            style = ttk.Style()
            style.theme_use(theme_name)
            logger.info(f"Theme changed to: {theme_name}")
        except Exception as e:
            logger.error(f"Error changing theme: {e}")
    
    # Layout Methods
    def apply_data_analysis_layout(self):
        """Aplicar layout de análisis de datos"""
        self.app_controller.focus_batch_tab()
    
    def apply_ml_training_layout(self):
        """Aplicar layout de entrenamiento ML"""
        self.app_controller.focus_advanced_ml_tab()
    
    def apply_feature_selection_layout(self):
        """Aplicar layout de selección de features"""
        self.app_controller.focus_feature_selection()
    
    def save_current_layout(self):
        """Guardar layout actual"""
        try:
            self.app_controller.show_info("Guardar Layout", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error saving layout: {e}")
    
    def load_custom_layout(self):
        """Cargar layout personalizado"""
        try:
            self.app_controller.show_info("Cargar Layout", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error loading layout: {e}")
    
    # Help Menu Commands
    def show_feature_selection_guide(self):
        """Mostrar guía de selección de features"""
        try:
            self.app_controller.dialog_manager.show_feature_selection_guide()
        except Exception as e:
            logger.error(f"Error showing feature selection guide: {e}")
    
    def show_ml_training_guide(self):
        """Mostrar guía de entrenamiento ML"""
        try:
            self.app_controller.show_info("Guía de ML", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing ML guide: {e}")
    
    def show_quick_start_tutorial(self):
        """Mostrar tutorial de inicio rápido"""
        try:
            self.app_controller.show_info("Tutorial", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing tutorial: {e}")
    
    def show_advanced_tutorial(self):
        """Mostrar tutorial avanzado"""
        try:
            self.app_controller.show_info("Tutorial Avanzado", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing advanced tutorial: {e}")
    
    def show_batch_tutorial(self):
        """Mostrar tutorial de procesamiento batch"""
        try:
            self.app_controller.show_info("Tutorial Batch", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing batch tutorial: {e}")
    
    def show_keyboard_shortcuts(self):
        """Mostrar atajos de teclado"""
        try:
            shortcuts_text = "ATAJOS DE TECLADO\n" + "="*20 + "\n\n"
            for shortcut, description in self.config.KEYBOARD_SHORTCUTS.items():
                shortcuts_text += f"{shortcut:<15} {description}\n"
            
            self.app_controller.dialog_manager.show_info("Atajos de Teclado", shortcuts_text)
        except Exception as e:
            logger.error(f"Error showing keyboard shortcuts: {e}")
    
    def show_feature_glossary(self):
        """Mostrar glosario de features"""
        try:
            self.app_controller.show_info("Glosario", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing glossary: {e}")
    
    def show_troubleshooting(self):
        """Mostrar guía de solución de problemas"""
        try:
            self.app_controller.show_info("Troubleshooting", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing troubleshooting: {e}")
    
    def check_for_updates(self):
        """Verificar actualizaciones"""
        try:
            self.app_controller.show_info("Actualizaciones", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error checking updates: {e}")
    
    def report_bug(self):
        """Reportar bug"""
        try:
            self.app_controller.show_info("Reportar Bug", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error reporting bug: {e}")
    
    def send_feedback(self):
        """Enviar feedback"""
        try:
            self.app_controller.show_info("Feedback", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error sending feedback: {e}")
    
    def show_about(self):
        """Mostrar información About"""
        try:
            self.app_controller.dialog_manager.show_about_dialog()
        except Exception as e:
            logger.error(f"Error showing about: {e}")
    
    # Automation and Workflow Methods
    def create_workflow(self):
        """Crear workflow automatizado"""
        try:
            self.app_controller.show_info("Crear Workflow", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
    
    def run_workflow(self):
        """Ejecutar workflow guardado"""
        try:
            self.app_controller.show_info("Ejecutar Workflow", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error running workflow: {e}")
    
    def schedule_analysis(self):
        """Programar análisis automático"""
        try:
            self.app_controller.show_info("Programar Análisis", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error scheduling analysis: {e}")
    
    # Diagnostic Methods
    def show_system_info(self):
        """Mostrar información del sistema"""
        try:
            info_text = f"""INFORMACIÓN DEL SISTEMA
=======================

Sistema Operativo: {platform.system()} {platform.release()}
Arquitectura: {platform.architecture()[0]}
Procesador: {platform.processor()}
Python: {sys.version}
Tkinter: {tk.TkVersion}

Aplicación: {self.config.APP_NAME} {self.config.VERSION}
"""
            
            self.app_controller.dialog_manager.show_info("Información del Sistema", info_text)
        except Exception as e:
            logger.error(f"Error showing system info: {e}")
    
    def show_performance_monitor(self):
        """Mostrar monitor de rendimiento"""
        try:
            self.app_controller.show_info("Monitor de Rendimiento", 
                                        "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing performance monitor: {e}")
    
    def show_debug_info(self):
        """Mostrar información de debug"""
        try:
            debug_text = f"""INFORMACIÓN DE DEBUG
===================

Estado de la aplicación:
- Datos cargados: {self.menu_state['data_loaded']}
- Modelo entrenado: {self.menu_state['model_trained']}
- Procesamiento activo: {self.menu_state['processing_active']}
- Feature selection activa: {self.menu_state['feature_selection_active']}

Archivos recientes: {len(self.recent_files)}
Menús creados: {list(self.menus.keys())}

Versión: {self.config.VERSION}
Configuración cargada: True
"""
            
            self.app_controller.dialog_manager.show_info("Información de Debug", debug_text)
        except Exception as e:
            logger.error(f"Error showing debug info: {e}")
    
    # =============================================================================
    # MÉTODOS PÚBLICOS PARA INTEGRACIÓN
    # =============================================================================
    
    def get_context_menu_manager(self) -> 'ContextMenuManager':
        """Obtener gestor de menús contextuales"""
        return self.context_menu_manager
    
    def get_state_manager(self) -> 'MenuStateManager':
        """Obtener gestor de estado"""
        return self.state_manager
    
    def reset(self):
        """Reset completo del gestor de menús"""
        try:
            # Reset estado
            self.menu_state = {
                'data_loaded': False,
                'model_trained': False,
                'processing_active': False,
                'feature_selection_active': False
            }
            
            # Limpiar archivos recientes
            self.recent_files.clear()
            self.update_recent_files_menu()
            
            # Refrescar estados de menús
            self.refresh_menu_states()
            
            logger.info("MenuManager reset completed")
            
        except Exception as e:
            logger.error(f"Error resetting MenuManager: {e}")
    
    def cleanup(self):
        """Limpieza antes del cierre"""
        try:
            # Guardar configuración si es necesario
            # Cleanup de gestores auxiliares
            if self.context_menu_manager:
                self.context_menu_manager.cleanup()
            
            logger.info("MenuManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during MenuManager cleanup: {e}")


class ContextMenuManager:
    """
    Gestor de menús contextuales para diferentes elementos de la interfaz
    """
    
    def __init__(self, menu_manager: MenuManager):
        """
        Inicializar gestor de menús contextuales
        
        Args:
            menu_manager: Referencia al gestor principal de menús
        """
        self.menu_manager = menu_manager
        self.app_controller = menu_manager.app_controller
        self.context_menus = {}
        self.create_context_menus()
    
    def create_context_menus(self):
        """Crear todos los menús contextuales"""
        self.create_data_context_menu()
        self.create_feature_context_menu()
        self.create_model_context_menu()
    
    def create_data_context_menu(self) -> tk.Menu:
        """Crear menú contextual para datos"""
        context_menu = tk.Menu(self.menu_manager.parent, tearoff=0)
        
        context_menu.add_command(
            label="View Data",
            command=self.view_selected_data
        )
        
        context_menu.add_command(
            label="Export Data",
            command=self.export_selected_data
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="Statistics",
            command=self.show_data_statistics
        )
        
        context_menu.add_command(
            label="Quality Report",
            command=self.show_data_quality
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="Delete",
            command=self.delete_selected_data
        )
        
        self.context_menus['data'] = context_menu
        return context_menu
    
    def create_feature_context_menu(self) -> tk.Menu:
        """Crear menú contextual para features"""
        context_menu = tk.Menu(self.menu_manager.parent, tearoff=0)
        
        context_menu.add_command(
            label="Select Feature",
            command=self.select_feature
        )
        
        context_menu.add_command(
            label="Deselect Feature",
            command=self.deselect_feature
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="View Statistics",
            command=self.view_feature_statistics
        )
        
        context_menu.add_command(
            label="Show Distribution",
            command=self.show_feature_distribution
        )
        
        context_menu.add_command(
            label="Correlation Analysis",
            command=self.analyze_feature_correlation
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="Add to Bookmark",
            command=self.bookmark_feature
        )
        
        self.context_menus['feature'] = context_menu
        return context_menu
    
    def create_model_context_menu(self) -> tk.Menu:
        """Crear menú contextual para modelos"""
        context_menu = tk.Menu(self.menu_manager.parent, tearoff=0)
        
        context_menu.add_command(
            label="Train Model",
            command=self.train_selected_model
        )
        
        context_menu.add_command(
            label="Evaluate Model",
            command=self.evaluate_selected_model
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="Save Model",
            command=self.save_selected_model
        )
        
        context_menu.add_command(
            label="Export Model",
            command=self.export_selected_model
        )
        
        context_menu.add_separator()
        
        context_menu.add_command(
            label="Model Details",
            command=self.show_model_details
        )
        
        self.context_menus['model'] = context_menu
        return context_menu
    
    def show_context_menu(self, menu_type: str, event, **kwargs):
        """
        Mostrar menú contextual
        
        Args:
            menu_type: Tipo de menú ('data', 'feature', 'model')
            event: Evento de mouse
            **kwargs: Parámetros adicionales específicos del contexto
        """
        try:
            if menu_type in self.context_menus:
                menu = self.context_menus[menu_type]
                
                # Actualizar estado del menú según contexto
                self.update_context_menu_state(menu_type, **kwargs)
                
                # Mostrar menú en la posición del mouse
                menu.tk_popup(event.x_root, event.y_root)
            
        except Exception as e:
            logger.error(f"Error showing context menu {menu_type}: {e}")
        finally:
            # Asegurar que el menú se cierre correctamente
            try:
                menu.grab_release()
            except:
                pass
    
    def update_context_menu_state(self, menu_type: str, **kwargs):
        """
        Actualizar estado de menú contextual
        
        Args:
            menu_type: Tipo de menú
            **kwargs: Contexto específico
        """
        try:
            menu = self.context_menus.get(menu_type)
            if not menu:
                return
            
            # Lógica específica por tipo de menú
            if menu_type == 'data':
                data_available = kwargs.get('data_available', False)
                state = "normal" if data_available else "disabled"
                
                for i in range(menu.index('end') + 1):
                    try:
                        menu.entryconfig(i, state=state)
                    except:
                        pass
            
            elif menu_type == 'feature':
                feature_selected = kwargs.get('feature_selected', False)
                state = "normal" if feature_selected else "disabled"
                
                # Actualizar opciones específicas de feature
                for i in range(menu.index('end') + 1):
                    try:
                        label = menu.entrycget(i, 'label')
                        if label in ['Select Feature', 'Deselect Feature']:
                            menu.entryconfig(i, state=state)
                    except:
                        pass
            
            elif menu_type == 'model':
                model_available = kwargs.get('model_available', False)
                state = "normal" if model_available else "disabled"
                
                for i in range(menu.index('end') + 1):
                    try:
                        menu.entryconfig(i, state=state)
                    except:
                        pass
                        
        except Exception as e:
            logger.error(f"Error updating context menu state: {e}")
    
    # Implementación de comandos del menú contextual
    def view_selected_data(self):
        """Ver datos seleccionados"""
        try:
            self.app_controller.show_info("Ver Datos", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error viewing data: {e}")
    
    def export_selected_data(self):
        """Exportar datos seleccionados"""
        try:
            self.menu_manager.export_current_dataset()
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
    
    def show_data_statistics(self):
        """Mostrar estadísticas de datos"""
        self.app_controller.show_data_statistics()
    
    def show_data_quality(self):
        """Mostrar calidad de datos"""
        try:
            self.app_controller.show_info("Calidad de Datos", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing data quality: {e}")
    
    def delete_selected_data(self):
        """Eliminar datos seleccionados"""
        try:
            if self.app_controller.dialog_manager.ask_confirmation(
                "Eliminar Datos", 
                "¿Está seguro de que desea eliminar los datos seleccionados?"
            ):
                self.app_controller.show_info("Eliminar", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error deleting data: {e}")
    
    def select_feature(self):
        """Seleccionar feature"""
        try:
            self.app_controller.show_info("Seleccionar Feature", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error selecting feature: {e}")
    
    def deselect_feature(self):
        """Deseleccionar feature"""
        try:
            self.app_controller.show_info("Deseleccionar Feature", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error deselecting feature: {e}")
    
    def view_feature_statistics(self):
        """Ver estadísticas de feature"""
        try:
            self.app_controller.show_info("Estadísticas de Feature", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error viewing feature statistics: {e}")
    
    def show_feature_distribution(self):
        """Mostrar distribución de feature"""
        try:
            self.app_controller.show_info("Distribución de Feature", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing feature distribution: {e}")
    
    def analyze_feature_correlation(self):
        """Analizar correlación de feature"""
        try:
            self.app_controller.show_info("Correlación de Feature", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error analyzing correlation: {e}")
    
    def bookmark_feature(self):
        """Marcar feature como favorita"""
        try:
            self.app_controller.show_info("Bookmark Feature", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error bookmarking feature: {e}")
    
    def train_selected_model(self):
        """Entrenar modelo seleccionado"""
        self.menu_manager.train_model()
    
    def evaluate_selected_model(self):
        """Evaluar modelo seleccionado"""
        try:
            self.app_controller.show_info("Evaluar Modelo", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
    
    def save_selected_model(self):
        """Guardar modelo seleccionado"""
        self.menu_manager.save_model()
    
    def export_selected_model(self):
        """Exportar modelo seleccionado"""
        self.menu_manager.export_model_package()
    
    def show_model_details(self):
        """Mostrar detalles del modelo"""
        try:
            self.app_controller.show_info("Detalles del Modelo", "Funcionalidad en desarrollo")
        except Exception as e:
            logger.error(f"Error showing model details: {e}")
    
    def cleanup(self):
        """Limpieza de menús contextuales"""
        try:
            for menu in self.context_menus.values():
                try:
                    menu.destroy()
                except:
                    pass
            self.context_menus.clear()
            logger.info("ContextMenuManager cleanup completed")
        except Exception as e:
            logger.error(f"Error in ContextMenuManager cleanup: {e}")


class MenuStateManager:
    """
    Gestor de estado de menús que mantiene sincronización con el estado de la aplicación
    """
    
    def __init__(self, menu_manager: MenuManager):
        """
        Inicializar gestor de estado de menús
        
        Args:
            menu_manager: Referencia al gestor de menús
        """
        self.menu_manager = menu_manager
        self.state_listeners = []
        self.state_history = []
        self.max_history = 50
    
    def add_state_listener(self, callback: Callable):
        """
        Agregar listener para cambios de estado
        
        Args:
            callback: Función a llamar cuando cambie el estado
        """
        if callback not in self.state_listeners:
            self.state_listeners.append(callback)
    
    def remove_state_listener(self, callback: Callable):
        """
        Remover listener de cambios de estado
        
        Args:
            callback: Función a remover
        """
        if callback in self.state_listeners:
            self.state_listeners.remove(callback)
    
    def notify_state_change(self, state_changes: Dict):
        """
        Notificar cambio de estado a todos los listeners
        
        Args:
            state_changes: Cambios de estado
        """
        # Registrar cambio en historial
        self.state_history.append({
            'timestamp': time.time(),
            'changes': state_changes.copy(),
            'full_state': self.menu_manager.menu_state.copy()
        })
        
        # Mantener historial limitado
        if len(self.state_history) > self.max_history:
            self.state_history.pop(0)
        
        # Actualizar estado del menu manager
        self.menu_manager.update_menu_state(state_changes)
        
        # Notificar a listeners
        for listener in self.state_listeners:
            try:
                listener(state_changes)
            except Exception as e:
                logger.error(f"Error in state listener: {e}")
    
    def get_menu_requirements(self, menu_item: str) -> Dict:
        """
        Obtener requerimientos para habilitar un elemento de menú
        
        Args:
            menu_item: Identificador del elemento de menú
            
        Returns:
            Diccionario con requerimientos
        """
        requirements = {
            'train_model': {
                'data_loaded': True, 
                'processing_active': False
            },
            'save_model': {
                'model_trained': True
            },
            'export_data': {
                'data_loaded': True
            },
            'feature_selection': {
                'data_loaded': True
            },
            'cross_validation': {
                'model_trained': True,
                'processing_active': False
            },
            'single_prediction': {
                'model_trained': True
            },
            'batch_prediction': {
                'model_trained': True
            },
            'data_statistics': {
                'data_loaded': True
            },
            'feature_analysis': {
                'data_loaded': True,
                'feature_selection_active': True
            }
        }
        
        return requirements.get(menu_item, {})
    
    def check_menu_item_enabled(self, menu_item: str) -> bool:
        """
        Verificar si un elemento de menú debe estar habilitado
        
        Args:
            menu_item: Identificador del elemento de menú
            
        Returns:
            True si debe estar habilitado
        """
        requirements = self.get_menu_requirements(menu_item)
        current_state = self.menu_manager.menu_state
        
        for requirement, required_value in requirements.items():
            if current_state.get(requirement) != required_value:
                return False
        
        return True
    
    def get_state_history(self) -> List[Dict]:
        """
        Obtener historial de cambios de estado
        
        Returns:
            Lista con historial de estados
        """
        return self.state_history.copy()
    
    def get_current_state(self) -> Dict:
        """
        Obtener estado actual completo
        
        Returns:
            Estado actual del menú
        """
        return self.menu_manager.menu_state.copy()
    
    def validate_state_consistency(self) -> Dict:
        """
        Validar consistencia del estado actual
        
        Returns:
            Diccionario con resultados de validación
        """
        validation_results = {
            'is_consistent': True,
            'issues': [],
            'warnings': []
        }
        
        current_state = self.menu_manager.menu_state
        
        # Validaciones lógicas
        if current_state.get('model_trained') and not current_state.get('data_loaded'):
            validation_results['is_consistent'] = False