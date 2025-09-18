"""
status_manager.py
Gestión del estado y barra de estado de la aplicación
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
import logging

from .application_config import ApplicationConfig

logger = logging.getLogger(__name__)

class StatusManager:
    """
    Gestor del estado de la aplicación y barra de estado
    Maneja indicadores de progreso, memoria, datos y features
    """
    
    def __init__(self, root: tk.Tk):
        """
        Inicializar gestor de estado
        
        Args:
            root: Ventana principal de tkinter
        """
        self.root = root
        self.config = ApplicationConfig()
        
        # Variables de estado
        self.status_vars = {}
        self.widgets = {}
        
        # Estado actual de la aplicación
        self.app_state = {
            'current_tab': None,
            'datasets_loaded': 0,
            'total_memory_mb': 0.0,
            'features_selected': 0,
            'features_total': 0,
            'feature_selection_active': False,
            'model_trained': False,
            'processing_active': False
        }
        
        self.create_status_bar()
        logger.info("StatusManager initialized")
    
    def create_status_bar(self):
        """Crear barra de estado principal"""
        # Frame principal de la barra de estado
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x")
        
        # Crear secciones según configuración
        for section in self.config.UI_CONFIG['status_bar_sections']:
            self._create_status_section(section)
        
        # Inicializar valores por defecto
        self._initialize_status_values()
    
    def _create_status_section(self, section_config: Dict):
        """Crear sección individual de la barra de estado"""
        section_name = section_config['name']
        width = section_config['width']
        
        # Crear variable y widget
        self.status_vars[section_name] = tk.StringVar()
        
        widget = ttk.Label(
            self.status_frame,
            textvariable=self.status_vars[section_name],
            relief="sunken",
            anchor="w" if width == -1 else "e",
            width=width if width > 0 else None
        )
        
        # Pack según si es expansible o no
        if width == -1:
            widget.pack(side="left", fill="x", expand=True)
        else:
            widget.pack(side="right")
        
        self.widgets[section_name] = widget
    
    def _initialize_status_values(self):
        """Inicializar valores por defecto de la barra de estado"""
        default_values = {
            'main': self.config.MESSAGES['welcome'],
            'features': "Features: 0 (Auto)",
            'memory': "Memory: 0 MB",
            'datasets': "Datasets: 0"
        }
        
        for section, value in default_values.items():
            if section in self.status_vars:
                self.status_vars[section].set(value)
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - ACTUALIZACIÓN DE ESTADO
    # =============================================================================
    
    def update_status(self, message: str):
        """
        Actualizar mensaje principal de estado
        
        Args:
            message: Mensaje a mostrar
        """
        if 'main' in self.status_vars:
            self.status_vars['main'].set(message)
        
        self.app_state['last_status'] = message
        logger.debug(f"Status updated: {message}")
        
        # Forzar actualización de la interfaz
        self.root.update_idletasks()
    
    def update_data_indicators(self, datasets_info: Dict):
        """
        Actualizar indicadores de datos
        
        Args:
            datasets_info: Información de datasets cargados
        """
        datasets_count = len(datasets_info)
        total_memory = sum(info.get('memory_mb', 0) for info in datasets_info.values())
        
        # Actualizar estado interno
        self.app_state['datasets_loaded'] = datasets_count
        self.app_state['total_memory_mb'] = total_memory
        
        # Actualizar widgets
        if 'datasets' in self.status_vars:
            self.status_vars['datasets'].set(f"Datasets: {datasets_count}")
        
        if 'memory' in self.status_vars:
            self.status_vars['memory'].set(f"Memory: {total_memory:.1f} MB")
    
    def update_feature_indicators(self, feature_info: Dict):
        """
        Actualizar indicadores de features
        
        Args:
            feature_info: Información de features seleccionadas
        """
        selected_count = feature_info.get('selected_count', 0)
        total_count = feature_info.get('total_count', 0)
        selection_active = feature_info.get('selection_active', False)
        
        # Actualizar estado interno
        self.app_state['features_selected'] = selected_count
        self.app_state['features_total'] = total_count
        self.app_state['feature_selection_active'] = selection_active
        
        # Actualizar widget
        if 'features' in self.status_vars:
            if selection_active and selected_count > 0:
                self.status_vars['features'].set(f"Features: {selected_count} (Custom)")
            else:
                self.status_vars['features'].set(f"Features: {total_count} (Auto)")
    
    def update_processing_status(self, is_processing: bool, process_info: Optional[str] = None):
        """
        Actualizar estado de procesamiento
        
        Args:
            is_processing: Si hay procesamiento activo
            process_info: Información adicional del proceso
        """
        self.app_state['processing_active'] = is_processing
        
        if is_processing:
            status_msg = f"Processing... {process_info}" if process_info else "Processing..."
            self.update_status(status_msg)
        else:
            self.update_status("Ready")
    
    def update_model_status(self, model_info: Dict):
        """
        Actualizar estado del modelo
        
        Args:
            model_info: Información del modelo entrenado
        """
        self.app_state['model_trained'] = True
        
        # Formatear mensaje según métricas disponibles
        if 'r2' in model_info and 'mae' in model_info:
            message = self.config.MESSAGES['model_trained'].format(
                r2=model_info['r2'],
                mae=model_info['mae']
            )
        else:
            message = "Modelo entrenado exitosamente"
        
        self.update_status(message)
    
    def update_tab_status(self, tab_name: str):
        """
        Actualizar estado del tab activo
        
        Args:
            tab_name: Nombre del tab activo
        """
        self.app_state['current_tab'] = tab_name
        self.update_status(f"Active tab: {tab_name}")
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - ESTADO DE LA APLICACIÓN
    # =============================================================================
    
    def get_app_state(self) -> Dict:
        """Obtener estado actual completo de la aplicación"""
        return self.app_state.copy()
    
    def is_processing(self) -> bool:
        """Verificar si hay procesamiento activo"""
        return self.app_state['processing_active']
    
    def has_data(self) -> bool:
        """Verificar si hay datos cargados"""
        return self.app_state['datasets_loaded'] > 0
    
    def has_model(self) -> bool:
        """Verificar si hay modelo entrenado"""
        return self.app_state['model_trained']
    
    def has_feature_selection(self) -> bool:
        """Verificar si hay selección de features activa"""
        return self.app_state['feature_selection_active']
    
    # =============================================================================
    # MÉTODOS PÚBLICOS - GESTIÓN DE PROGRESO
    # =============================================================================
    
    def create_progress_dialog(self, title: str, message: str) -> 'ProgressDialog':
        """
        Crear diálogo de progreso
        
        Args:
            title: Título del diálogo
            message: Mensaje inicial
            
        Returns:
            Instancia de ProgressDialog
        """
        return ProgressDialog(self.root, title, message)
    
    def show_temporary_message(self, message: str, duration: int = 3000):
        """
        Mostrar mensaje temporal en la barra de estado
        
        Args:
            message: Mensaje a mostrar
            duration: Duración en milisegundos
        """
        original_message = self.status_vars['main'].get()
        self.update_status(message)
        
        # Restaurar mensaje original después del tiempo especificado
        self.root.after(duration, lambda: self.update_status(original_message))
    
    # =============================================================================
    # MÉTODOS DE LIMPIEZA Y RESET
    # =============================================================================
    
    def reset(self):
        """Reset completo del estado"""
        # Reset estado interno
        self.app_state = {
            'current_tab': None,
            'datasets_loaded': 0,
            'total_memory_mb': 0.0,
            'features_selected': 0,
            'features_total': 0,
            'feature_selection_active': False,
            'model_trained': False,
            'processing_active': False
        }
        
        # Reset widgets
        self._initialize_status_values()
        
        logger.info("StatusManager reset completed")


class ProgressDialog:
    """Diálogo de progreso para operaciones largas"""
    
    def __init__(self, parent: tk.Tk, title: str, message: str):
        """
        Inicializar diálogo de progreso
        
        Args:
            parent: Ventana padre
            title: Título del diálogo
            message: Mensaje inicial
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x150")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables
        self.progress_var = tk.DoubleVar()
        self.message_var = tk.StringVar(value=message)
        self.cancelled = False
        
        self.create_widgets()
        self.center_window()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Mensaje
        message_label = ttk.Label(main_frame, textvariable=self.message_var, 
                                 wraplength=350, justify="center")
        message_label.pack(pady=(0, 20))
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(pady=(0, 20))
        
        # Botón cancelar
        self.cancel_button = ttk.Button(main_frame, text="Cancelar", 
                                       command=self.cancel)
        self.cancel_button.pack()
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.window.update_idletasks()
        
        # Obtener dimensiones
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Calcular posición central
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def update_progress(self, value: float, message: str = None):
        """
        Actualizar progreso
        
        Args:
            value: Valor de progreso (0-100)
            message: Mensaje opcional a actualizar
        """
        self.progress_var.set(value)
        
        if message:
            self.message_var.set(message)
        
        self.window.update_idletasks()
    
    def set_indeterminate(self, active: bool = True):
        """
        Configurar barra de progreso indeterminada
        
        Args:
            active: Si activar o desactivar modo indeterminado
        """
        if active:
            self.progress_bar.config(mode='indeterminate')
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.config(mode='determinate')
    
    def cancel(self):
        """Cancelar operación"""
        self.cancelled = True
        self.close()
    
    def close(self):
        """Cerrar diálogo"""
        try:
            self.window.grab_release()
            self.window.destroy()
        except:
            pass
    
    def is_cancelled(self) -> bool:
        """Verificar si fue cancelado"""
        return self.cancelled


class NotificationManager:
    """Gestor de notificaciones y mensajes temporales"""
    
    def __init__(self, parent: tk.Tk):
        """
        Inicializar gestor de notificaciones
        
        Args:
            parent: Ventana principal
        """
        self.parent = parent
        self.notifications = []
        self.notification_queue = []
    
    def show_notification(self, message: str, notification_type: str = "info", 
                         duration: int = 3000, position: str = "top-right"):
        """
        Mostrar notificación temporal
        
        Args:
            message: Mensaje a mostrar
            notification_type: Tipo ('info', 'success', 'warning', 'error')
            duration: Duración en milisegundos
            position: Posición en pantalla
        """
        notification = NotificationWindow(
            self.parent, message, notification_type, duration, position
        )
        
        self.notifications.append(notification)
        
        # Limpiar notificaciones cerradas después del tiempo especificado
        self.parent.after(duration + 500, lambda: self._cleanup_notifications())
    
    def _cleanup_notifications(self):
        """Limpiar notificaciones cerradas"""
        self.notifications = [n for n in self.notifications if not n.is_closed()]
    
    def clear_all_notifications(self):
        """Cerrar todas las notificaciones"""
        for notification in self.notifications:
            notification.close()
        self.notifications.clear()


class NotificationWindow:
    """Ventana de notificación temporal"""
    
    def __init__(self, parent: tk.Tk, message: str, notification_type: str,
                 duration: int, position: str):
        """
        Inicializar ventana de notificación
        
        Args:
            parent: Ventana padre
            message: Mensaje a mostrar
            notification_type: Tipo de notificación
            duration: Duración en milisegundos
            position: Posición en pantalla
        """
        self.parent = parent
        self.closed = False
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.withdraw()  # Ocultar inicialmente
        
        # Configurar ventana
        self.window.overrideredirect(True)  # Sin bordes
        self.window.attributes('-topmost', True)  # Siempre encima
        
        # Colores según tipo
        colors = {
            'info': {'bg': '#e3f2fd', 'fg': '#1976d2'},
            'success': {'bg': '#e8f5e8', 'fg': '#388e3c'},
            'warning': {'bg': '#fff3e0', 'fg': '#f57c00'},
            'error': {'bg': '#ffebee', 'fg': '#d32f2f'}
        }
        
        color_scheme = colors.get(notification_type, colors['info'])
        
        # Frame principal
        main_frame = tk.Frame(
            self.window,
            bg=color_scheme['bg'],
            relief='raised',
            bd=1
        )
        main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Mensaje
        label = tk.Label(
            main_frame,
            text=message,
            bg=color_scheme['bg'],
            fg=color_scheme['fg'],
            font=('Arial', 9),
            wraplength=250,
            justify='left'
        )
        label.pack(padx=10, pady=8)
        
        # Posicionar y mostrar
        self._position_window(position)
        self._show_with_animation()
        
        # Auto-cerrar
        self.parent.after(duration, self.close)
    
    def _position_window(self, position: str):
        """Posicionar ventana según posición especificada"""
        self.window.update_idletasks()
        
        # Obtener dimensiones
        width = self.window.winfo_reqwidth()
        height = self.window.winfo_reqheight()
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Calcular posición
        if position == "top-right":
            x = screen_width - width - 20
            y = 20
        elif position == "top-left":
            x = 20
            y = 20
        elif position == "bottom-right":
            x = screen_width - width - 20
            y = screen_height - height - 60
        elif position == "bottom-left":
            x = 20
            y = screen_height - height - 60
        else:  # center
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _show_with_animation(self):
        """Mostrar ventana con animación de fade-in"""
        self.window.deiconify()
        self.window.attributes('-alpha', 0.0)
        
        # Animación de fade-in
        alpha = 0.0
        def fade_in():
            nonlocal alpha
            alpha += 0.1
            if alpha <= 1.0:
                self.window.attributes('-alpha', alpha)
                self.parent.after(50, fade_in)
            else:
                self.window.attributes('-alpha', 1.0)
        
        fade_in()
    
    def close(self):
        """Cerrar notificación con animación"""
        if self.closed:
            return
        
        self.closed = True
        
        # Animación de fade-out
        alpha = 1.0
        def fade_out():
            nonlocal alpha
            alpha -= 0.2
            if alpha >= 0.0:
                try:
                    self.window.attributes('-alpha', alpha)
                    self.parent.after(50, fade_out)
                except:
                    pass
            else:
                try:
                    self.window.destroy()
                except:
                    pass
        
        fade_out()
    
    def is_closed(self) -> bool:
        """Verificar si está cerrada"""
        return self.closed


class StateValidator:
    """Validador de estado de la aplicación"""
    
    @staticmethod
    def validate_data_state(datasets_info: Dict) -> Dict:
        """
        Validar estado de los datos
        
        Args:
            datasets_info: Información de datasets
            
        Returns:
            Resultado de validación
        """
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        if not datasets_info:
            validation['valid'] = False
            validation['errors'].append("No hay datasets cargados")
            validation['recommendations'].append("Cargue al menos un dataset")
            return validation
        
        for dataset_id, info in datasets_info.items():
            # Validar tamaño
            rows, cols = info['shape']
            
            if rows < 10:
                validation['warnings'].append(f"Dataset {dataset_id} tiene pocas muestras ({rows})")
            
            if cols < 5:
                validation['warnings'].append(f"Dataset {dataset_id} tiene pocas features ({cols})")
            
            # Validar validez
            if not info.get('valid', True):
                validation['errors'].append(f"Dataset {dataset_id} tiene errores de validación")
        
        return validation
    
    @staticmethod
    def validate_ml_state(model_info: Dict, feature_info: Dict) -> Dict:
        """
        Validar estado del modelo ML
        
        Args:
            model_info: Información del modelo
            feature_info: Información de features
            
        Returns:
            Resultado de validación
        """
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Validar features
        if feature_info.get('selected_count', 0) < 5:
            validation['warnings'].append("Pocas features seleccionadas para el modelo")
            validation['recommendations'].append("Considere incluir más features")
        
        # Validar modelo si existe
        if model_info.get('trained', False):
            r2 = model_info.get('r2', 0)
            mae = model_info.get('mae', 0)
            
            if r2 < 0.5:
                validation['warnings'].append(f"R² bajo ({r2:.3f})")
                validation['recommendations'].append("Ajuste features o parámetros del modelo")
            
            if mae > 10:
                validation['warnings'].append(f"MAE alto ({mae:.1f})")
                validation['recommendations'].append("Revise calidad de los datos")
        
        return validation