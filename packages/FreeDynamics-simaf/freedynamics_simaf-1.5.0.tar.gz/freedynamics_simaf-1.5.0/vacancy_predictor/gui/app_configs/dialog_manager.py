"""
dialog_manager.py
Gestión centralizada de diálogos y ventanas emergentes
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from .application_config import ApplicationConfig

logger = logging.getLogger(__name__)

class DialogManager:
    """
    Gestor centralizado de diálogos y ventanas emergentes
    Proporciona una interfaz consistente para todos los diálogos de la aplicación
    """
    
    def __init__(self, parent: tk.Tk):
        """
        Inicializar gestor de diálogos
        
        Args:
            parent: Ventana principal de la aplicación
        """
        self.parent = parent
        self.config = ApplicationConfig()
        self.active_dialogs = []
        
        logger.info("DialogManager initialized")
    
    # =============================================================================
    # DIÁLOGOS DE ARCHIVOS
    # =============================================================================
    
    def open_file_dialog(self, title: str = "Abrir archivo", 
                        filetypes: Optional[List] = None,
                        initialdir: Optional[str] = None) -> Optional[str]:
        """
        Mostrar diálogo para abrir archivo
        
        Args:
            title: Título del diálogo
            filetypes: Lista de tipos de archivo permitidos
            initialdir: Directorio inicial
            
        Returns:
            Ruta del archivo seleccionado o None si se canceló
        """
        if filetypes is None:
            filetypes = self.config.get_file_types_for_dialog()
        
        try:
            file_path = filedialog.askopenfilename(
                title=title,
                filetypes=filetypes,
                initialdir=initialdir
            )
            
            return file_path if file_path else None
            
        except Exception as e:
            logger.error(f"Error in open file dialog: {e}")
            self.show_error(f"Error abriendo diálogo de archivo: {e}")
            return None
    
    def save_file_dialog(self, title: str = "Guardar archivo",
                        defaultextension: str = ".csv",
                        filetypes: Optional[List] = None,
                        initialdir: Optional[str] = None,
                        initialfile: Optional[str] = None) -> Optional[str]:
        """
        Mostrar diálogo para guardar archivo
        
        Args:
            title: Título del diálogo
            defaultextension: Extensión por defecto
            filetypes: Lista de tipos de archivo
            initialdir: Directorio inicial
            initialfile: Nombre de archivo inicial
            
        Returns:
            Ruta del archivo a guardar o None si se canceló
        """
        if filetypes is None:
            filetypes = self.config.get_file_types_for_dialog()
        
        try:
            file_path = filedialog.asksaveasfilename(
                title=title,
                defaultextension=defaultextension,
                filetypes=filetypes,
                initialdir=initialdir,
                initialfile=initialfile
            )
            
            return file_path if file_path else None
            
        except Exception as e:
            logger.error(f"Error in save file dialog: {e}")
            self.show_error(f"Error abriendo diálogo de guardado: {e}")
            return None
    
    def select_directory(self, title: str = "Seleccionar directorio",
                        initialdir: Optional[str] = None) -> Optional[str]:
        """
        Mostrar diálogo para seleccionar directorio
        
        Args:
            title: Título del diálogo
            initialdir: Directorio inicial
            
        Returns:
            Ruta del directorio seleccionado o None si se canceló
        """
        try:
            directory = filedialog.askdirectory(
                title=title,
                initialdir=initialdir
            )
            
            return directory if directory else None
            
        except Exception as e:
            logger.error(f"Error in directory dialog: {e}")
            self.show_error(f"Error abriendo diálogo de directorio: {e}")
            return None
    
    # =============================================================================
    # DIÁLOGOS DE MENSAJE
    # =============================================================================
    
    def show_info(self, title: str, message: str):
        """Mostrar diálogo de información"""
        try:
            messagebox.showinfo(title, message, parent=self.parent)
        except Exception as e:
            logger.error(f"Error showing info dialog: {e}")
    
    def show_success(self, message: str, title: str = "Éxito"):
        """Mostrar diálogo de éxito"""
        try:
            messagebox.showinfo(title, message, parent=self.parent)
        except Exception as e:
            logger.error(f"Error showing success dialog: {e}")
    
    def show_warning(self, message: str, title: str = "Advertencia"):
        """Mostrar diálogo de advertencia"""
        try:
            messagebox.showwarning(title, message, parent=self.parent)
        except Exception as e:
            logger.error(f"Error showing warning dialog: {e}")
    
    def show_error(self, message: str, title: str = "Error"):
        """Mostrar diálogo de error"""
        try:
            messagebox.showerror(title, message, parent=self.parent)
        except Exception as e:
            logger.error(f"Error showing error dialog: {e}")
    
    def ask_confirmation(self, title: str, message: str) -> bool:
        """
        Mostrar diálogo de confirmación
        
        Args:
            title: Título del diálogo
            message: Mensaje de confirmación
            
        Returns:
            True si el usuario confirma, False en caso contrario
        """
        try:
            return messagebox.askyesno(title, message, parent=self.parent)
        except Exception as e:
            logger.error(f"Error showing confirmation dialog: {e}")
            return False
    
    def ask_ok_cancel(self, title: str, message: str) -> bool:
        """
        Mostrar diálogo OK/Cancelar
        
        Args:
            title: Título del diálogo
            message: Mensaje
            
        Returns:
            True si OK, False si Cancelar
        """
        try:
            return messagebox.askokcancel(title, message, parent=self.parent)
        except Exception as e:
            logger.error(f"Error showing ok/cancel dialog: {e}")
            return False
    
    # =============================================================================
    # DIÁLOGOS ESPECIALIZADOS
    # =============================================================================
    
    def show_statistics_dialog(self, stats_data: Dict):
        """
        Mostrar diálogo de estadísticas
        
        Args:
            stats_data: Datos estadísticos a mostrar
        """
        dialog = StatisticsDialog(self.parent, stats_data)
        self.active_dialogs.append(dialog)
        return dialog
    
    def show_memory_dialog(self, memory_info: Dict):
        """
        Mostrar diálogo de uso de memoria
        
        Args:
            memory_info: Información de memoria
        """
        dialog = MemoryDialog(self.parent, memory_info)
        self.active_dialogs.append(dialog)
        return dialog
    
    def show_user_guide(self):
        """Mostrar guía del usuario"""
        dialog = UserGuideDialog(self.parent)
        self.active_dialogs.append(dialog)
        return dialog
    
    def show_feature_selection_guide(self):
        """Mostrar guía de selección de features"""
        dialog = FeatureSelectionGuideDialog(self.parent)
        self.active_dialogs.append(dialog)
        return dialog
    
    def show_about_dialog(self):
        """Mostrar diálogo About"""
        dialog = AboutDialog(self.parent)
        self.active_dialogs.append(dialog)
        return dialog
    
    def show_model_comparison_dialog(self, comparison_data: Dict):
        """
        Mostrar diálogo de comparación de modelos
        
        Args:
            comparison_data: Datos de comparación
        """
        dialog = ModelComparisonDialog(self.parent, comparison_data)
        self.active_dialogs.append(dialog)
        return dialog
    
    # =============================================================================
    # GESTIÓN DE DIÁLOGOS ACTIVOS
    # =============================================================================
    
    def close_all_dialogs(self):
        """Cerrar todos los diálogos activos"""
        for dialog in self.active_dialogs:
            try:
                if hasattr(dialog, 'close'):
                    dialog.close()
                elif hasattr(dialog, 'window') and dialog.window.winfo_exists():
                    dialog.window.destroy()
            except Exception as e:
                logger.error(f"Error closing dialog: {e}")
        
        self.active_dialogs.clear()
    
    def cleanup_closed_dialogs(self):
        """Limpiar diálogos que ya están cerrados"""
        active = []
        for dialog in self.active_dialogs:
            try:
                if hasattr(dialog, 'window') and dialog.window.winfo_exists():
                    active.append(dialog)
            except:
                pass
        
        self.active_dialogs = active


class BaseDialog:
    """Clase base para diálogos personalizados"""
    
    def __init__(self, parent: tk.Tk, title: str, size: str = "600x400"):
        """
        Inicializar diálogo base
        
        Args:
            parent: Ventana padre
            title: Título del diálogo
            size: Tamaño del diálogo
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry(size)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centrar ventana
        self.center_window()
        
        # Configurar protocolo de cierre
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.window.update_idletasks()
        
        # Obtener dimensiones
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Calcular posición central
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        
        self.window.geometry(f"+{x}+{y}")
    
    def close(self):
        """Cerrar diálogo"""
        try:
            self.window.grab_release()
            self.window.destroy()
        except Exception as e:
            logger.error(f"Error closing dialog: {e}")


class StatisticsDialog(BaseDialog):
    """Diálogo para mostrar estadísticas de datos"""
    
    def __init__(self, parent: tk.Tk, stats_data: Dict):
        super().__init__(parent, "Estadísticas de Datos", "800x600")
        self.stats_data = stats_data
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Área de texto con scroll
        text_widget = scrolledtext.ScrolledText(main_frame, wrap="word")
        text_widget.pack(fill="both", expand=True, pady=(0, 10))
        
        # Generar texto de estadísticas
        stats_text = self.format_statistics()
        text_widget.insert(1.0, stats_text)
        text_widget.config(state="disabled")
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cerrar", command=self.close).pack(side="right")
        ttk.Button(button_frame, text="Exportar", command=self.export_stats).pack(side="right", padx=(0, 10))
    
    def format_statistics(self) -> str:
        """Formatear estadísticas para mostrar"""
        lines = [
            "ESTADÍSTICAS DETALLADAS DE DATOS",
            "=" * 50,
            ""
        ]
        
        # Estadísticas globales
        if 'global' in self.stats_data:
            global_stats = self.stats_data['global']
            lines.extend([
                "RESUMEN GLOBAL:",
                f"  Datasets cargados: {global_stats.get('datasets_loaded', 0)}",
                f"  Total de muestras: {global_stats.get('total_samples', 0)}",
                f"  Total de features: {global_stats.get('total_features', 0)}",
                f"  Memoria total: {global_stats.get('total_memory_mb', 0):.2f} MB",
                ""
            ])
        
        # Estadísticas por dataset
        if 'datasets' in self.stats_data:
            lines.append("DETALLES POR DATASET:")
            lines.append("-" * 30)
            
            for dataset_id, dataset_stats in self.stats_data['datasets'].items():
                lines.append(f"\n{dataset_id.upper()}:")
                
                basic_info = dataset_stats.get('basic_info', {})
                lines.extend([
                    f"  Filas: {basic_info.get('rows', 0)}",
                    f"  Columnas: {basic_info.get('columns', 0)}",
                    f"  Memoria: {basic_info.get('memory_mb', 0):.2f} MB",
                    f"  Valores faltantes: {basic_info.get('missing_values_pct', 0):.2f}%"
                ])
                
                # Tipos de columnas
                if 'column_types' in dataset_stats:
                    lines.append("  Tipos de columnas:")
                    for dtype, count in dataset_stats['column_types'].items():
                        lines.append(f"    {dtype}: {count}")
                
                # Estadísticas del target
                if 'target_stats' in dataset_stats:
                    target_stats = dataset_stats['target_stats']
                    lines.extend([
                        "  Estadísticas del target:",
                        f"    Media: {target_stats.get('mean', 0):.2f}",
                        f"    Desv. estándar: {target_stats.get('std', 0):.2f}",
                        f"    Rango: {target_stats.get('min', 0):.0f} - {target_stats.get('max', 0):.0f}"
                    ])
        
        return "\n".join(lines)
    
    def export_stats(self):
        """Exportar estadísticas a archivo"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Estadísticas",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    import json
                    with open(file_path, 'w') as f:
                        json.dump(self.stats_data, f, indent=2, default=str)
                else:
                    with open(file_path, 'w') as f:
                        f.write(self.format_statistics())
                
                messagebox.showinfo("Éxito", f"Estadísticas exportadas a:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando estadísticas:\n{e}")


class MemoryDialog(BaseDialog):
    """Diálogo para mostrar uso de memoria"""
    
    def __init__(self, parent: tk.Tk, memory_info: Dict):
        super().__init__(parent, "Uso de Memoria", "500x400")
        self.memory_info = memory_info
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Área de texto
        text_widget = scrolledtext.ScrolledText(main_frame, wrap="word")
        text_widget.pack(fill="both", expand=True, pady=(0, 10))
        
        # Formatear información de memoria
        memory_text = self.format_memory_info()
        text_widget.insert(1.0, memory_text)
        text_widget.config(state="disabled")
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=self.close).pack()
    
    def format_memory_info(self) -> str:
        """Formatear información de memoria"""
        lines = [
            "USO DE MEMORIA DETALLADO",
            "=" * 30,
            ""
        ]
        
        # Información del proceso
        if 'process' in self.memory_info:
            process_info = self.memory_info['process']
            if 'rss_mb' in process_info:
                lines.extend([
                    "PROCESO ACTUAL:",
                    f"  RSS: {process_info['rss_mb']:.2f} MB",
                    f"  VMS: {process_info['vms_mb']:.2f} MB",
                    f"  Porcentaje: {process_info.get('percent', 0):.1f}%",
                    ""
                ])
            else:
                lines.extend([
                    "PROCESO ACTUAL:",
                    f"  {process_info.get('status', 'Información no disponible')}",
                    ""
                ])
        
        # Memoria de datasets
        lines.extend([
            "DATASETS EN MEMORIA:",
            f"  Total: {self.memory_info.get('total_datasets_mb', 0):.2f} MB",
            ""
        ])
        
        if 'datasets' in self.memory_info:
            for dataset_id, dataset_info in self.memory_info['datasets'].items():
                lines.extend([
                    f"  {dataset_id}:",
                    f"    Memoria: {dataset_info.get('memory_mb', 0):.2f} MB",
                    f"    Muestras: {dataset_info.get('samples', 0)}",
                    f"    Features: {dataset_info.get('features', 0)}",
                    f"    MB por muestra: {dataset_info.get('mb_per_sample', 0):.4f}",
                    ""
                ])
        
        return "\n".join(lines)


class UserGuideDialog(BaseDialog):
    """Diálogo con la guía del usuario"""
    
    def __init__(self, parent: tk.Tk):
        super().__init__(parent, "Guía del Usuario v4.0", "900x700")
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets de la guía"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Notebook para diferentes secciones
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Secciones de la guía
        self.create_overview_tab(notebook)
        self.create_workflow_tab(notebook)
        self.create_features_tab(notebook)
        self.create_shortcuts_tab(notebook)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=self.close).pack()
    
    def create_overview_tab(self, notebook):
        """Crear tab de overview"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Descripción General")
        
        text_widget = scrolledtext.ScrolledText(frame, wrap="word", padding=10)
        text_widget.pack(fill="both", expand=True)
        
        overview_text = """VACANCY PREDICTOR ML SUITE v4.0 ENHANCED
========================================

DESCRIPCIÓN GENERAL:
Suite avanzada para predicción de vacancias con selección inteligente de features.

CARACTERÍSTICAS PRINCIPALES:
• Procesamiento batch de archivos LAMMPS dump
• Extracción automática de 160+ features físicas
• Selección interactiva de features con análisis estadístico
• Entrenamiento optimizado con Random Forest
• Visualizaciones avanzadas de resultados
• Exportación completa de modelos y configuraciones

NUEVAS FUNCIONALIDADES v4.0:
• Tabla interactiva para selección de features
• Filtros dinámicos por categoría e importancia
• Análisis automático de correlaciones
• Comparación de modelos con/sin selección
• Exportación avanzada de configuraciones

BENEFICIOS:
• Mejora la precisión de predicción
• Reduce el overfitting
• Acelera el entrenamiento
• Facilita la interpretación del modelo
• Permite experimentación ágil

PÚBLICO OBJETIVO:
• Investigadores en ciencia de materiales
• Científicos de datos en simulaciones
• Estudiantes de machine learning aplicado
• Profesionales en modelado predictivo"""
        
        text_widget.insert(1.0, overview_text)
        text_widget.config(state="disabled")
    
    def create_workflow_tab(self, notebook):
        """Crear tab de workflow"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Flujo de Trabajo")
        
        text_widget = scrolledtext.ScrolledText(frame, wrap="word", padding=10)
        text_widget.pack(fill="both", expand=True)
        
        workflow_text = """FLUJO DE TRABAJO RECOMENDADO
============================

OPCIÓN 1 - PROCESAMIENTO COMPLETO DESDE DUMPS:
1. Vaya al tab "Batch Processing"
2. Seleccione directorio con archivos .dump
3. Configure parámetros (átomos totales, rango energía)
4. Ejecute procesamiento batch
5. Los datos se cargarán automáticamente en "Enhanced ML"
6. Vaya al sub-tab "Selección Features"
7. Analice y seleccione features óptimas
8. Regrese al tab "Entrenamiento"
9. Configure parámetros del modelo
10. Entrene y evalúe el modelo

OPCIÓN 2 - DATASET EXISTENTE:
1. Use "File → Import Dataset" para cargar CSV/Excel
2. Vaya al tab "Enhanced ML"
3. Use el sub-tab "Selección Features" para optimizar
4. Seleccione features relevantes
5. Configure y entrene el modelo
6. Analice resultados en "Resultados"

FLUJO ITERATIVO DE OPTIMIZACIÓN:
1. Cargue datos iniciales
2. Analice importancia de features
3. Seleccione subset óptimo
4. Entrene modelo
5. Evalúe métricas (R², MAE)
6. Ajuste selección de features
7. Re-entrene y compare
8. Repita hasta obtener resultados satisfactorios

MEJORES PRÁCTICAS:
• Comience con análisis exploratorio
• Use feature importance para guiar selección
• Pruebe diferentes combinaciones
• Compare métricas sistemáticamente
• Documente configuraciones exitosas
• Exporte modelos finales"""
        
        text_widget.insert(1.0, workflow_text)
        text_widget.config(state="disabled")
    
    def create_features_tab(self, notebook):
        """Crear tab de features"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Selección de Features")
        
        text_widget = scrolledtext.ScrolledText(frame, wrap="word", padding=10)
        text_widget.pack(fill="both", expand=True)
        
        features_text = """GUÍA DE SELECCIÓN DE FEATURES
=============================

CONCEPTOS FUNDAMENTALES:
La selección de features es crucial para:
• Eliminar ruido y redundancia
• Mejorar precisión del modelo
• Reducir overfitting
• Acelerar entrenamiento
• Facilitar interpretación

TABLA INTERACTIVA:
Columnas principales:
• Selección: Activar/desactivar feature
• Feature: Nombre de la variable
• Categoría: Tipo de feature (Coordinación, Energía, etc.)
• Importancia: Contribución al modelo (0-1)
• Correlación: Relación lineal con target (-1 a +1)
• % Faltantes: Porcentaje de valores perdidos
• Estadísticas: Min, Max, Media, Desviación

FILTROS DISPONIBLES:
• Búsqueda: Filtrar por nombre de feature
• Categoría: Coordinación, Energía, Stress, Histogramas
• Importancia: Alta (>0.05), Media (0.01-0.05), Baja (<0.01)

HERRAMIENTAS DE SELECCIÓN:
• Click doble: Activar/desactivar individual
• Seleccionar todas: Todas las features visibles
• Top N: Seleccionar N features más importantes
• Invertir selección: Alternar selección actual
• Limpiar: Deseleccionar todas

ESTRATEGIAS RECOMENDADAS:

1. BASADA EN IMPORTANCIA:
   • Comience con top 20-30 features
   • Elimine features con importancia < 0.001
   • Mantenga balance entre categorías

2. BASADA EN CORRELACIÓN:
   • Elimine features con |correlación| < 0.05
   • Priorice correlaciones moderadas-altas
   • Considere correlaciones negativas válidas

3. BASADA EN CALIDAD:
   • Elimine features con >20% valores faltantes
   • Revise features con rango muy pequeño
   • Considere distribución uniforme

4. ITERATIVA:
   • Pruebe diferentes combinaciones
   • Compare métricas del modelo
   • Refine basado en resultados
   • Documente mejores configuraciones

INTERPRETACIÓN DE MÉTRICAS:
• Importancia > 0.05: Feature muy relevante
• 0.01 < Importancia < 0.05: Moderadamente relevante
• Importancia < 0.01: Poco relevante
• |Correlación| > 0.3: Relación fuerte con target
• |Correlación| < 0.05: Relación débil

ANÁLISIS DETALLADO:
Use "Análisis Detallado" para obtener:
• Distribución por categorías
• Top features por importancia
• Estadísticas de correlación
• Recomendaciones automáticas
• Métricas de calidad global"""
        
        text_widget.insert(1.0, features_text)
        text_widget.config(state="disabled")
    
    def create_shortcuts_tab(self, notebook):
        """Crear tab de atajos"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Atajos de Teclado")
        
        text_widget = scrolledtext.ScrolledText(frame, wrap="word", padding=10)
        text_widget.pack(fill="both", expand=True)
        
        shortcuts_text = """ATAJOS DE TECLADO
================

GESTIÓN DE ARCHIVOS:
Ctrl+N     Nuevo proyecto
Ctrl+I     Importar dataset
Ctrl+S     Guardar proyecto
Ctrl+E     Exportar todos los datos
Ctrl+Q     Salir de la aplicación

NAVEGACIÓN:
Ctrl+F     Ir a selección de features
Tab        Cambiar entre tabs
F1         Mostrar esta guía
F2         Estadísticas de datos
F3         Uso de memoria
F4         Análisis de features

OPERACIONES ML:
F5         Entrenar modelo
F6         Validación cruzada
F7         Predicción individual
F8         Análisis de resultados

SELECCIÓN DE FEATURES:
Ctrl+A     Seleccionar todas las features visibles
Ctrl+D     Deseleccionar todas
Ctrl+I     Invertir selección
Ctrl+T     Seleccionar top features
Enter      Aplicar selección al modelo

VISUALIZACIÓN:
Ctrl+G     Mostrar gráficos
Ctrl+R     Actualizar visualizaciones
Ctrl+P     Exportar gráficos

BÚSQUEDA Y FILTROS:
Ctrl+F     Enfocar búsqueda
Esc        Limpiar filtros
Ctrl+L     Limpiar búsqueda

CONSEJOS:
• Use F1 en cualquier momento para ayuda
• Los atajos funcionan en contexto apropiado
• Hover sobre botones muestra atajos
• Algunos atajos requieren datos cargados"""
        
        text_widget.insert(1.0, shortcuts_text)
        text_widget.config(state="disabled")


class FeatureSelectionGuideDialog(BaseDialog):
    """Diálogo específico para guía de selección de features"""
    
    def __init__(self, parent: tk.Tk):
        super().__init__(parent, "Guía de Selección de Features", "800x600")
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets de la guía"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Área de texto con scroll
        text_widget = scrolledtext.ScrolledText(main_frame, wrap="word")
        text_widget.pack(fill="both", expand=True, pady=(0, 10))
        
        guide_text = """GUÍA AVANZADA DE SELECCIÓN DE FEATURES
=====================================

¿QUÉ ES LA SELECCIÓN DE FEATURES?
La selección de features es el proceso de identificar y elegir las variables más relevantes para el modelo predictivo, eliminando aquellas que son redundantes, irrelevantes o introducen ruido.

BENEFICIOS CIENTÍFICOS:
• Mejora la precisión predictiva
• Reduce el overfitting
• Acelera el entrenamiento
• Facilita la interpretación física
• Reduce el costo computacional
• Mejora la generalización

METODOLOGÍA EN VACANCY PREDICTOR:

1. ANÁLISIS EXPLORATORIO:
   • Examine la distribución de features
   • Identifique valores faltantes
   • Analice correlaciones con el target
   • Revise estadísticas descriptivas

2. FILTRADO POR CALIDAD:
   • Elimine features con >20% valores faltantes
   • Remueva features con varianza cero
   • Identifique outliers extremos
   • Verifique rangos físicamente válidos

3. SELECCIÓN POR RELEVANCIA:
   • Use feature importance del Random Forest
   • Analice correlaciones con 'vacancies'
   • Considere conocimiento del dominio
   • Mantenga diversidad de categorías

4. VALIDACIÓN ITERATIVA:
   • Entrene modelo con subset seleccionado
   • Compare métricas (R², MAE, RMSE)
   • Ajuste selección basado en resultados
   • Documente configuraciones exitosas

CRITERIOS DE SELECCIÓN:

IMPORTANCIA (Random Forest):
• Alta (>0.05): Mantener siempre
• Media (0.01-0.05): Evaluar caso por caso
• Baja (<0.01): Considerar eliminación

CORRELACIÓN CON TARGET:
• |r| > 0.3: Correlación fuerte, muy relevante
• 0.1 < |r| < 0.3: Correlación moderada, relevante
• |r| < 0.1: Correlación débil, evaluar eliminación

CALIDAD DE DATOS:
• 0-5% faltantes: Excelente calidad
• 5-15% faltantes: Buena calidad, usar con precaución
• >15% faltantes: Considerar eliminación o imputación

CATEGORÍAS DE FEATURES:

COORDINACIÓN:
• Número de vecinos cercanos
• Parámetros de orden local
• Medidas de conectividad
• Relevancia: Alta para defectos puntuales

ENERGÍA:
• Energía potencial por átomo
• Energía cinética
• Variaciones locales de energía
• Relevancia: Crítica para estabilidad

STRESS:
• Tensiones locales
• Componentes del tensor de stress
• Medidas de deformación
• Relevancia: Importante para propiedades mecánicas

HISTOGRAMAS:
• Distribuciones de coordinación
• Distribuciones de energía
• Perfiles espaciales
• Relevancia: Capturan patrones globales

ESTRATEGIAS AVANZADAS:

SELECCIÓN INCREMENTAL:
1. Comience con top 10 features más importantes
2. Agregue features por categoría
3. Evalúe mejora incremental
4. Pare cuando no haya mejora significativa

SELECCIÓN POR CATEGORÍA:
1. Mantenga al menos 2-3 features por categoría
2. Balance entre diferentes tipos físicos
3. Asegure representación completa del sistema

VALIDACIÓN CRUZADA:
1. Use diferentes subsets en validación cruzada
2. Evalúe estabilidad de la selección
3. Identifique features consistentemente importantes

OPTIMIZACIÓN AUTOMÁTICA:
1. Use el botón "Top N" para selección rápida
2. Aplique filtros por importancia
3. Use análisis detallado para refinamiento

INTERPRETACIÓN FÍSICA:
• Relacione features seleccionadas con fenómenos físicos
• Verifique coherencia con teoría de defectos
• Considere escalas espaciales y temporales
• Valide con conocimiento experimental

TROUBLESHOOTING:

MODELO CON BAJA PRECISIÓN:
• Incremente número de features
• Revise calidad de datos
• Considere features de interacción
• Verifique representatividad del dataset

OVERFITTING:
• Reduzca número de features
• Use validación cruzada más estricta
• Incremente regularización
• Verifique tamaño del dataset

FEATURES IMPORTANTES INESPERADAS:
• Investigue correlaciones espurias
• Verifique data leakage
• Analice distribución temporal
• Valide con conocimiento físico

RECOMENDACIONES FINALES:
• Documente todas las decisiones
• Mantenga trazabilidad de experimentos
• Compare múltiples estrategias
• Valide resultados con expertos del dominio
• Exporte configuraciones exitosas"""
        
        text_widget.insert(1.0, guide_text)
        text_widget.config(state="disabled")
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=self.close).pack()


class AboutDialog(BaseDialog):
    """Diálogo About de la aplicación"""
    
    def __init__(self, parent: tk.Tk):
        super().__init__(parent, "About Vacancy Predictor v4.0", "600x500")
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del About"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Logo/Título
        title_label = ttk.Label(main_frame, text="Vacancy Predictor", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ttk.Label(main_frame, text="ML Suite v4.0 Enhanced", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(0, 20))
        
        # Información
        info_text = scrolledtext.ScrolledText(main_frame, wrap="word", height=15)
        info_text.pack(fill="both", expand=True, pady=(0, 20))
        
        about_text = """Suite avanzada para predicción de vacancias con selección inteligente de features.

CARACTERÍSTICAS v4.0:
• Selección interactiva de features con tabla avanzada
• Análisis automático de importancia y correlaciones
• Filtros dinámicos por categoría e importancia
• Comparación de modelos optimizados vs. completos
• Exportación avanzada de configuraciones y modelos

CAPACIDADES TÉCNICAS:
• Extracción automática de 160+ features físicas
• Random Forest con optimización inteligente
• Predicciones con features seleccionadas
• Visualizaciones de feature importance
• Análisis detallado de calidad de features
• Export completo de modelos y configuraciones

FORMATOS SOPORTADOS:
• Input: archivos .dump, CSV, Excel
• Output: CSV, XLSX, JOBLIB, JSON (configuraciones)
• Export: Modelos completos con metadatos

ARQUITECTURA MODULAR:
• Procesamiento batch → Análisis features → Selección → Entrenamiento optimizado
• Gestión centralizada de datos y estado
• Interfaz modular y extensible
• Validación automática de calidad

DESARROLLADO PARA:
• Investigadores en ciencia de materiales
• Científicos de datos en simulaciones atómicas
• Profesionales en machine learning aplicado
• Estudiantes de modelado predictivo

Version: 4.0.0 - Enhanced ML Suite with Feature Selection
Desarrollado con arquitectura modular para optimización inteligente de modelos ML"""
        
        info_text.insert(1.0, about_text)
        info_text.config(state="disabled")
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", command=self.close).pack()


class ModelComparisonDialog(BaseDialog):
    """Diálogo para comparación de modelos"""
    
    def __init__(self, parent: tk.Tk, comparison_data: Dict):
        super().__init__(parent, "Comparación de Modelos", "700x500")
        self.comparison_data = comparison_data
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets de comparación"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Área de texto
        text_widget = scrolledtext.ScrolledText(main_frame, wrap="word")
        text_widget.pack(fill="both", expand=True, pady=(0, 10))
        
        # Formatear datos de comparación
        comparison_text = self.format_comparison()
        text_widget.insert(1.0, comparison_text)
        text_widget.config(state="disabled")
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cerrar", command=self.close).pack(side="right")
        ttk.Button(button_frame, text="Exportar Comparación", 
                  command=self.export_comparison).pack(side="right", padx=(0, 10))
    
    def format_comparison(self) -> str:
        """Formatear datos de comparación"""
        lines = [
            "COMPARACIÓN DE MODELOS",
            "=" * 30,
            ""
        ]
        
        # Agregar información de comparación
        for model_name, model_info in self.comparison_data.items():
            lines.extend([
                f"{model_name.upper()}:",
                f"  Features utilizadas: {model_info.get('features_count', 'N/A')}",
                f"  R² Score: {model_info.get('r2', 'N/A')}",
                f"  MAE: {model_info.get('mae', 'N/A')}",
                f"  RMSE: {model_info.get('rmse', 'N/A')}",
                f"  Tiempo entrenamiento: {model_info.get('training_time', 'N/A')}",
                ""
            ])
        
        return "\n".join(lines)
    
    def export_comparison(self):
        """Exportar comparación a archivo"""
        from tkinter import filedialog
        import json
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Comparación",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w') as f:
                        json.dump(self.comparison_data, f, indent=2, default=str)
                else:
                    with open(file_path, 'w') as f:
                        f.write(self.format_comparison())
                
                messagebox.showinfo("Éxito", f"Comparación exportada a:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando:\n{e}")