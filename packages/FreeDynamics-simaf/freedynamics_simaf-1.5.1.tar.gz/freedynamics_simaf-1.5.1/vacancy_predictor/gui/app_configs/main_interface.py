"""
main_interface.py
Interfaz principal de la aplicación - Gestión del notebook y tabs principales
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Optional, Callable

from vacancy_predictor.gui.app_configs.application_config import ApplicationConfig
from  vacancy_predictor.gui.tabs.batch_processor_tab import BatchProcessingTab
from  vacancy_predictor.gui.tabs.advanced_ml_tab import AdvancedMLTabWithPlots

logger = logging.getLogger(__name__)

class MainInterface:
    """
    Interfaz principal de la aplicación
    Gestiona el notebook principal y la coordinación entre tabs
    """
    
    def __init__(self, parent: tk.Tk, data_manager, app_controller):
        """
        Inicializar interfaz principal
        
        Args:
            parent: Ventana principal de tkinter
            data_manager: Instancia del gestor de datos
            app_controller: Controlador principal de la aplicación
        """
        self.parent = parent
        self.data_manager = data_manager
        self.app_controller = app_controller
        self.config = ApplicationConfig()
        
        # Referencias a tabs
        self.tabs = {}
        self.notebook = None
        
        # Estado de la interfaz
        self.current_tab_index = 0
        self.interface_state = {
            'tabs_created': False,
            'data_synced': False,
            'active_tab': None
        }
        
        self.create_interface()
        logger.info("MainInterface initialized")
    
    def create_interface(self):
        """Crear interfaz principal con notebook y tabs"""
        # Contenedor principal
        self.main_container = ttk.Frame(self.parent)
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Crear notebook principal
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Crear tabs
        self.create_tabs()
        
        # Configurar eventos
        self.setup_events()
        
        self.interface_state['tabs_created'] = True
    
    def create_tabs(self):
        """Crear y configurar todos los tabs"""
        # 1. Tab de Procesamiento Batch
        self.create_batch_processing_tab()
        
        # 2. Tab de ML Avanzado con Feature Selection
        self.create_enhanced_ml_tab()
        
        logger.info(f"Created {len(self.tabs)} main tabs")
    
    def create_batch_processing_tab(self):
        """Crear tab de procesamiento batch"""
        try:
            self.tabs['batch'] = BatchProcessingTab(
                self.notebook, 
                self.on_batch_data_loaded
            )
            
            self.notebook.add(
                self.tabs['batch'].frame, 
                text="📄 Batch Processing"
            )
            
            logger.info("Batch processing tab created")
            
        except Exception as e:
            logger.error(f"Error creating batch processing tab: {e}")
            self.app_controller.show_error(f"Error creando tab de procesamiento: {e}")
    
    def create_enhanced_ml_tab(self):
        """Crear tab de ML avanzado"""
        try:
            self.tabs['enhanced_ml'] = AdvancedMLTabWithPlots(
                self.notebook,
                self.on_advanced_data_loaded
            )
            
            self.notebook.add(
                self.tabs['enhanced_ml'].frame,
                text="🧠 Enhanced ML"
            )
            
            logger.info("Enhanced ML tab created")
            
        except Exception as e:
            logger.error(f"Error creating enhanced ML tab: {e}")
            self.app_controller.show_error(f"Error creando tab de ML: {e}")
    
    def setup_events(self):
        """Configurar eventos del notebook"""
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        self.notebook.bind("<Button-3>", self.on_tab_right_click)  # Click derecho en tabs
    
    # =============================================================================
    # EVENTOS Y CALLBACKS
    # =============================================================================
    
    def on_tab_changed(self, event):
        """Callback cuando cambia el tab activo"""
        try:
            current_tab = self.notebook.select()
            tab_index = self.notebook.index(current_tab)
            
            # Obtener nombre del tab
            tab_text = self.notebook.tab(current_tab, 'text')
            
            # Actualizar estado
            self.current_tab_index = tab_index
            self.interface_state['active_tab'] = tab_text
            
            # Notificar al controlador principal
            self.app_controller.on_tab_changed(tab_text)
            
            # Sincronizar datos si es necesario
            self.sync_tab_data(tab_index)
            
            logger.debug(f"Tab changed to: {tab_text} (index: {tab_index})")
            
        except Exception as e:
            logger.error(f"Error in tab change event: {e}")
    
    def on_tab_right_click(self, event):
        """Callback para click derecho en tabs"""
        try:
            # Identificar tab clickeado
            tab_index = self.notebook.tk.call(self.notebook._w, "identify", "tab", event.x, event.y)
            
            if tab_index != "":
                self.show_tab_context_menu(event, int(tab_index))
                
        except Exception as e:
            logger.error(f"Error in tab right click: {e}")
    
    def on_batch_data_loaded(self, data):
        """Callback cuando se cargan datos desde batch processing"""
        try:
            # Registrar datos en el data manager
            dataset_id = self.data_manager.add_dataset(data, 'batch_processing')
            
            # Sincronizar con tab de ML si está disponible
            if 'enhanced_ml' in self.tabs:
                self.sync_data_to_ml_tab(data)
            
            # Notificar al controlador principal
            self.app_controller.on_data_loaded(data, 'batch')
            
            logger.info(f"Batch data loaded and synced: {len(data)} samples")
            
        except Exception as e:
            logger.error(f"Error handling batch data: {e}")
            self.app_controller.show_error(f"Error procesando datos batch: {e}")
    
    def on_advanced_data_loaded(self, data):
        """Callback cuando se cargan datos en ML avanzado"""
        try:
            # Registrar datos en el data manager
            dataset_id = self.data_manager.add_dataset(data, 'enhanced_ml')
            
            # Notificar al controlador principal
            self.app_controller.on_data_loaded(data, 'enhanced_ml')
            
            logger.info(f"Enhanced ML data loaded: {len(data)} samples")
            
        except Exception as e:
            logger.error(f"Error handling advanced ML data: {e}")
            self.app_controller.show_error(f"Error procesando datos ML: {e}")
    
    # =============================================================================
    # MÉTODOS DE NAVEGACIÓN
    # =============================================================================
    
    def focus_batch_tab(self):
        """Enfocar tab de procesamiento batch"""
        if 'batch' in self.tabs:
            batch_frame = self.tabs['batch'].frame
            self.notebook.select(batch_frame)
    
    def focus_advanced_ml_tab(self):
        """Enfocar tab de ML avanzado"""
        if 'enhanced_ml' in self.tabs:
            ml_frame = self.tabs['enhanced_ml'].frame
            self.notebook.select(ml_frame)
    
    def focus_feature_selection_tab(self):
        """Enfocar sub-tab de selección de features"""
        # Primero ir al tab de Enhanced ML
        self.focus_advanced_ml_tab()
        
        # Luego navegar al sub-tab de feature selection
        if 'enhanced_ml' in self.tabs:
            enhanced_ml_tab = self.tabs['enhanced_ml']
            if hasattr(enhanced_ml_tab, 'notebook'):
                # Buscar el sub-tab de feature selection
                for i in range(enhanced_ml_tab.notebook.index('end')):
                    tab_text = enhanced_ml_tab.notebook.tab(i, 'text')
                    if 'Selección' in tab_text or 'Features' in tab_text:
                        enhanced_ml_tab.notebook.select(i)
                        break
    
    def get_current_tab_info(self) -> Dict:
        """Obtener información del tab actual"""
        if not self.notebook:
            return {}
        
        try:
            current_tab = self.notebook.select()
            tab_index = self.notebook.index(current_tab)
            tab_text = self.notebook.tab(current_tab, 'text')
            
            return {
                'index': tab_index,
                'text': tab_text,
                'widget': current_tab,
                'total_tabs': self.notebook.index('end')
            }
            
        except Exception as e:
            logger.error(f"Error getting current tab info: {e}")
            return {}
    
    # =============================================================================
    # MÉTODOS DE SINCRONIZACIÓN DE DATOS
    # =============================================================================
    
    def sync_data_to_ml_tab(self, data):
        """Sincronizar datos al tab de ML"""
        if 'enhanced_ml' in self.tabs:
            try:
                enhanced_ml_tab = self.tabs['enhanced_ml']
                if hasattr(enhanced_ml_tab, 'load_dataset_from_dataframe'):
                    enhanced_ml_tab.load_dataset_from_dataframe(data)
                    self.interface_state['data_synced'] = True
                    logger.info("Data synced to Enhanced ML tab")
                    
            except Exception as e:
                logger.error(f"Error syncing data to ML tab: {e}")
    
    def sync_tab_data(self, tab_index: int):
        """Sincronizar datos cuando se cambia de tab"""
        try:
            # Obtener datasets disponibles
            datasets_info = self.data_manager.get_datasets_info()
            
            if not datasets_info:
                return
            
            # Sincronizar según el tab activo
            current_tab_widget = self.notebook.nametowidget(self.notebook.select())
            
            # Determinar tipo de tab y sincronizar apropiadamente
            # Esto se puede expandir según las necesidades específicas
            
        except Exception as e:
            logger.error(f"Error syncing tab data: {e}")
    
    def sync_all_tabs(self):
        """Sincronizar datos en todos los tabs"""
        datasets_info = self.data_manager.get_datasets_info()
        
        for tab_name, tab_instance in self.tabs.items():
            try:
                if hasattr(tab_instance, 'sync_data'):
                    tab_instance.sync_data(datasets_info)
                    
            except Exception as e:
                logger.error(f"Error syncing data for tab {tab_name}: {e}")
    
    # =============================================================================
    # MÉTODOS DE CONFIGURACIÓN Y PERSONALIZACIÓN
    # =============================================================================
    
    def show_tab_context_menu(self, event, tab_index: int):
        """Mostrar menú contextual para tab"""
        try:
            context_menu = tk.Menu(self.parent, tearoff=0)
            
            # Obtener información del tab
            tab_text = self.notebook.tab(tab_index, 'text')
            
            # Opciones del menú contextual
            context_menu.add_command(
                label=f"Refresh {tab_text}", 
                command=lambda: self.refresh_tab(tab_index)
            )
            
            context_menu.add_separator()
            
            context_menu.add_command(
                label="Export Tab Data", 
                command=lambda: self.export_tab_data(tab_index)
            )
            
            context_menu.add_command(
                label="Tab Statistics", 
                command=lambda: self.show_tab_statistics(tab_index)
            )
            
            # Mostrar menú
            context_menu.tk_popup(event.x_root, event.y_root)
            
        except Exception as e:
            logger.error(f"Error showing tab context menu: {e}")
    
    def refresh_tab(self, tab_index: int):
        """Refrescar tab específico"""
        try:
            # Determinar qué tab refrescar
            tab_name = list(self.tabs.keys())[tab_index]
            tab_instance = self.tabs[tab_name]
            
            if hasattr(tab_instance, 'refresh'):
                tab_instance.refresh()
            elif hasattr(tab_instance, 'update_display'):
                tab_instance.update_display()
                
            logger.info(f"Tab {tab_name} refreshed")
            
        except Exception as e:
            logger.error(f"Error refreshing tab {tab_index}: {e}")
    
    def export_tab_data(self, tab_index: int):
        """Exportar datos específicos de un tab"""
        try:
            tab_name = list(self.tabs.keys())[tab_index]
            tab_instance = self.tabs[tab_name]
            
            if hasattr(tab_instance, 'export_data'):
                tab_instance.export_data()
            else:
                # Fallback: usar data manager para exportar
                datasets = self.data_manager.get_datasets_info()
                if datasets:
                    self.app_controller.export_all_data()
                    
        except Exception as e:
            logger.error(f"Error exporting tab data: {e}")
            self.app_controller.show_error(f"Error exportando datos del tab: {e}")
    
    def show_tab_statistics(self, tab_index: int):
        """Mostrar estadísticas específicas de un tab"""
        try:
            tab_name = list(self.tabs.keys())[tab_index]
            
            if hasattr(self.tabs[tab_name], 'get_statistics'):
                stats = self.tabs[tab_name].get_statistics()
                self.app_controller.show_statistics_dialog(stats)
            else:
                # Fallback: mostrar estadísticas generales
                self.app_controller.show_data_statistics()
                
        except Exception as e:
            logger.error(f"Error showing tab statistics: {e}")
    
    # =============================================================================
    # MÉTODOS DE INFORMACIÓN Y ESTADO
    # =============================================================================
    
    def get_interface_statistics(self) -> Dict:
        """Obtener estadísticas de la interfaz"""
        stats = {
            'interface_state': self.interface_state.copy(),
            'current_tab': self.get_current_tab_info(),
            'tabs_info': {}
        }
        
        # Obtener estadísticas de cada tab
        for tab_name, tab_instance in self.tabs.items():
            try:
                if hasattr(tab_instance, 'get_statistics'):
                    stats['tabs_info'][tab_name] = tab_instance.get_statistics()
                else:
                    # Información básica
                    stats['tabs_info'][tab_name] = {
                        'type': type(tab_instance).__name__,
                        'active': tab_name == self.interface_state.get('active_tab', '').lower()
                    }
                    
            except Exception as e:
                logger.error(f"Error getting statistics for tab {tab_name}: {e}")
                stats['tabs_info'][tab_name] = {'error': str(e)}
        
        return stats
    
    def get_export_data(self) -> Dict:
        """Obtener datos para exportación desde todos los tabs"""
        export_data = {}
        
        for tab_name, tab_instance in self.tabs.items():
            try:
                if hasattr(tab_instance, 'get_export_data'):
                    export_data[tab_name] = tab_instance.get_export_data()
                elif hasattr(tab_instance, 'current_data') and tab_instance.current_data is not None:
                    export_data[tab_name] = {
                        'data_shape': tab_instance.current_data.shape,
                        'columns': list(tab_instance.current_data.columns)
                    }
                    
            except Exception as e:
                logger.error(f"Error getting export data from tab {tab_name}: {e}")
                export_data[tab_name] = {'error': str(e)}
        
        return export_data
    
    def show_feature_analysis(self):
        """Mostrar análisis de features desde el tab apropiado"""
        if 'enhanced_ml' in self.tabs:
            enhanced_ml_tab = self.tabs['enhanced_ml']
            if hasattr(enhanced_ml_tab, 'feature_selection_tab'):
                enhanced_ml_tab.feature_selection_tab.show_detailed_analysis()
            else:
                self.app_controller.show_warning("Análisis de features no disponible", 
                                                "Cargue datos primero para habilitar el análisis")
        else:
            self.app_controller.show_error("Tab de ML no disponible")
    
    # =============================================================================
    # MÉTODOS DE LIMPIEZA Y RESET
    # =============================================================================
    
    def reset(self):
        """Reset completo de la interfaz"""
        try:
            # Reset de todos los tabs
            for tab_name, tab_instance in self.tabs.items():
                if hasattr(tab_instance, 'reset'):
                    tab_instance.reset()
            
            # Reset del estado de la interfaz
            self.interface_state = {
                'tabs_created': True,
                'data_synced': False,
                'active_tab': None
            }
            
            # Volver al primer tab
            if self.notebook and self.notebook.index('end') > 0:
                self.notebook.select(0)
            
            logger.info("MainInterface reset completed")
            
        except Exception as e:
            logger.error(f"Error resetting interface: {e}")
    
    def cleanup(self):
        """Limpieza antes del cierre"""
        try:
            # Cleanup de tabs
            for tab_instance in self.tabs.values():
                if hasattr(tab_instance, 'cleanup'):
                    tab_instance.cleanup()
            
            logger.info("MainInterface cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during interface cleanup: {e}")


class TabManager:
    """Gestor auxiliar para operaciones avanzadas de tabs"""
    
    def __init__(self, main_interface: MainInterface):
        """
        Inicializar gestor de tabs
        
        Args:
            main_interface: Referencia a la interfaz principal
        """
        self.main_interface = main_interface
        self.tab_history = []
        self.tab_bookmarks = {}
    
    def add_tab_to_history(self, tab_info: Dict):
        """Agregar tab al historial de navegación"""
        self.tab_history.append({
            'timestamp': tk.time.time(),
            'tab_info': tab_info
        })
        
        # Mantener solo los últimos 10 elementos
        if len(self.tab_history) > 10:
            self.tab_history.pop(0)
    
    def bookmark_current_tab(self, bookmark_name: str):
        """Crear bookmark del tab actual"""
        current_tab = self.main_interface.get_current_tab_info()
        if current_tab:
            self.tab_bookmarks[bookmark_name] = current_tab
    
    def go_to_bookmark(self, bookmark_name: str):
        """Navegar a un bookmark"""
        if bookmark_name in self.tab_bookmarks:
            bookmark = self.tab_bookmarks[bookmark_name]
            try:
                self.main_interface.notebook.select(bookmark['index'])
            except:
                logger.warning(f"Bookmark {bookmark_name} no longer valid")
    
    def get_tab_navigation_history(self) -> list:
        """Obtener historial de navegación"""
        return self.tab_history.copy()