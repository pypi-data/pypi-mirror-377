#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main_application.py
Clase principal de la aplicación Vacancy Predictor refactorizada
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys
from pathlib import Path

# Importar componentes modulares
from .app_configs.application_config import ApplicationConfig
from .app_configs.data_manager import DataManager
from .app_configs.status_manager import StatusManager
from vacancy_predictor.gui.app_configs.menu_manager import MenuManager
from vacancy_predictor.gui.app_configs.main_interface import MainInterface
from .app_configs.dialog_manager import DialogManager

logger = logging.getLogger(__name__)

class VacancyPredictorApplication:
    """
    Clase principal de la aplicación Vacancy Predictor
    Orquesta todos los componentes de la aplicación
    """
    
    def __init__(self):
        """Inicializar aplicación principal"""
        # Configuración de la aplicación
        self.config = ApplicationConfig()
        
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title(f"Vacancy Predictor - {self.config.APP_TITLE}")
        self.root.geometry(self.config.WINDOW_GEOMETRY)
        
        # Maximizar ventana según SO
        self._setup_window()
        
        # Inicializar managers
        self.data_manager = DataManager()
        self.status_manager = StatusManager(self.root)
        self.menu_manager = MenuManager(self.root, self)
        self.dialog_manager = DialogManager(self.root)
        
        # Interfaz principal
        self.main_interface = MainInterface(self.root, self.data_manager, self)
        
        # Setup inicial
        self._setup_application()
        
        logger.info(f"Vacancy Predictor {self.config.VERSION} initialized")
    
    def _setup_window(self):
        """Configurar ventana principal"""
        try:
            if sys.platform == 'win32':
                self.root.state('zoomed')
            else:
                self.root.attributes('-zoomed', True)
        except:
            pass
        
        # Configurar protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _setup_application(self):
        """Setup inicial de la aplicación"""
        # Configurar estilos
        self._setup_styles()
        
        # Configurar atajos de teclado
        self._setup_keyboard_shortcuts()
        
        # Inicializar status
        self.status_manager.update_status("Vacancy Predictor Ready - Load dataset or process batch files")
    
    def _setup_styles(self):
        """Configurar estilos TTK"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Aplicar estilos desde configuración
        for style_name, style_config in self.config.TTK_STYLES.items():
            style.configure(style_name, **style_config)
    
    def _setup_keyboard_shortcuts(self):
        """Configurar atajos de teclado"""
        shortcuts = {
            '<Control-n>': lambda e: self.reset_application(),
            '<Control-i>': lambda e: self.import_dataset(),
            '<Control-e>': lambda e: self.export_all_data(),
            '<Control-f>': lambda e: self.focus_feature_selection(),
            '<Control-q>': lambda e: self.on_closing(),
            '<F1>': lambda e: self.show_user_guide(),
            '<F2>': lambda e: self.show_data_statistics(),
            '<F3>': lambda e: self.show_memory_usage(),
            '<F4>': lambda e: self.show_feature_analysis()
        }
        
        for shortcut, handler in shortcuts.items():
            self.root.bind(shortcut, handler)
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - NAVEGACIÓN
    # =============================================================================
    
    def focus_batch_tab(self):
        """Enfocar tab de procesamiento batch"""
        self.main_interface.focus_batch_tab()
        self.status_manager.update_status("Batch Processing tab active")
    
    def focus_advanced_ml_tab(self):
        """Enfocar tab de ML avanzado"""
        self.main_interface.focus_advanced_ml_tab()
        self.status_manager.update_status("Enhanced ML tab active")
    
    def focus_feature_selection(self):
        """Enfocar tab de selección de features"""
        self.main_interface.focus_feature_selection_tab()
        self.status_manager.update_status("Feature Selection activated")
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - GESTIÓN DE DATOS
    # =============================================================================
    
    def import_dataset(self):
        """Importar dataset desde archivo"""
        file_path = self.dialog_manager.open_file_dialog(
            title="Importar Dataset",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                # Cargar datos usando DataManager
                data = self.data_manager.load_dataset_from_file(file_path)
                
                # Notificar a la interfaz
                self.main_interface.on_data_loaded(data, 'imported')
                
                # Cambiar al tab Enhanced ML
                self.focus_advanced_ml_tab()
                
                self.dialog_manager.show_success(
                    f"Dataset importado exitosamente:\n{file_path}\n\n"
                    f"Filas: {len(data)}\nColumnas: {len(data.columns)}\n\n"
                    f"Tip: Use la pestaña 'Selección Features' para optimizar el modelo"
                )
                
            except Exception as e:
                self.dialog_manager.show_error(f"Error importando dataset:\n{str(e)}")
    
    def export_all_data(self):
        """Exportar todos los datos"""
        directory = self.dialog_manager.select_directory("Seleccionar directorio para exportar datos")
        if directory:
            try:
                export_info = self.data_manager.export_all_data(
                    directory, 
                    self.main_interface.get_export_data()
                )
                
                self.dialog_manager.show_success(
                    f"Exportación completada!\n\n"
                    f"Archivos exportados: {export_info['files_count']}\n"
                    f"Ubicación: {export_info['directory']}"
                )
                
            except Exception as e:
                self.dialog_manager.show_error(f"Error en exportación:\n{str(e)}")
    
    def reset_application(self):
        """Resetear aplicación completa"""
        if self.dialog_manager.ask_confirmation(
            "Nuevo Proyecto", 
            "Esto limpiará todos los datos, modelos y selecciones de features. ¿Continuar?"
        ):
            # Reset data manager
            self.data_manager.reset()
            
            # Reset interfaz
            self.main_interface.reset()
            
            # Reset status
            self.status_manager.reset()
            
            self.status_manager.update_status("Nuevo proyecto creado - Enhanced ML ready")
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - INFORMACIÓN Y ANÁLISIS
    # =============================================================================
    
    def show_data_statistics(self):
        """Mostrar estadísticas de datos"""
        stats_data = self.data_manager.get_comprehensive_statistics()
        interface_stats = self.main_interface.get_interface_statistics()
        
        # Combinar estadísticas
        combined_stats = {**stats_data, **interface_stats}
        
        self.dialog_manager.show_statistics_dialog(combined_stats)
    
    def show_feature_analysis(self):
        """Mostrar análisis de features"""
        self.main_interface.show_feature_analysis()
    
    def show_memory_usage(self):
        """Mostrar uso de memoria"""
        memory_info = self.data_manager.get_memory_usage()
        self.dialog_manager.show_memory_dialog(memory_info)
    
    def show_user_guide(self):
        """Mostrar guía del usuario"""
        self.dialog_manager.show_user_guide()
    
    # =============================================================================
    # CALLBACKS Y EVENTOS
    # =============================================================================
    
    def on_data_loaded(self, data, source):
        """Callback cuando se cargan datos"""
        # Actualizar data manager
        self.data_manager.add_dataset(data, source)
        
        # Actualizar status
        self.status_manager.update_data_indicators(self.data_manager.get_datasets_info())
        self.status_manager.update_status(f"Dataset cargado desde {source}: {len(data)} muestras")
    
    def on_feature_selection_changed(self, feature_info):
        """Callback cuando cambia la selección de features"""
        self.status_manager.update_feature_indicators(feature_info)
    
    def on_model_trained(self, model_info):
        """Callback cuando se entrena un modelo"""
        self.status_manager.update_status(f"Modelo entrenado: {model_info}")
    
    def on_closing(self):
        """Callback al cerrar aplicación"""
        if self.dialog_manager.ask_confirmation("Salir", "¿Deseas salir de Vacancy Predictor Enhanced?"):
            try:
                logger.info("Application closing gracefully")
                
                # Cleanup si es necesario
                self.data_manager.cleanup()
                
                self.root.destroy()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
                self.root.destroy()
    
    # =============================================================================
    # MÉTODO PRINCIPAL
    # =============================================================================
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            self.dialog_manager.show_error(f"Error crítico en la aplicación: {e}")


def main():
    """Función principal de entrada"""
    try:
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('vacancy_predictor.log')
            ]
        )
        
        logger.info("Starting Vacancy Predictor ML Suite Enhanced")
        
        # Crear y ejecutar aplicación
        app = VacancyPredictorApplication()
        app.run()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        try:
            messagebox.showerror("Error de Aplicación", 
                                f"Error crítico durante el inicio:\n\n{e}\n\n"
                                f"Revisa vacancy_predictor.log para más detalles.")
        except:
            print(f"CRITICAL ERROR: {e}")


if __name__ == "__main__":
    main()