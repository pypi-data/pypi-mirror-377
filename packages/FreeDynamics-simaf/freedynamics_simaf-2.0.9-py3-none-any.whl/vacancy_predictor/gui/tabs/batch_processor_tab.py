"""
Tab para procesamiento batch de archivos LAMMPS dump con selección de features
Incluye tabla integrada para seleccionar features antes del entrenamiento
VERSIÓN COMPLETA Y CORREGIDA
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
import numpy as np
import logging
import threading
import json
from typing import Callable, Optional, Dict, List, Set

# Importar el procesador batch
from vacancy_predictor.core.batch_processor import BatchDumpProcessor

logger = logging.getLogger(__name__)

class BatchProcessingTab:
    """Tab para procesamiento batch con selección de features integrada"""
    
    def __init__(self, parent, data_loaded_callback: Callable):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        
        # Procesador batch
        self.processor = BatchDumpProcessor()
        self.processor.set_progress_callback(self.update_progress)
        
        self.frame = ttk.Frame(parent)
        
        # Variables de procesamiento
        self.directory_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value="ml_dataset_output")
        
        # Variables de configuración
        self.atm_total_var = tk.IntVar(value=16384)
        self.energy_min_var = tk.DoubleVar(value=-4.0)
        self.energy_max_var = tk.DoubleVar(value=-3.0)
        self.energy_bins_var = tk.IntVar(value=10)
        
        # Variables de estado
        self.current_dataset = None
        self.processing = False
        
        # Variables de progreso
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Listo para procesar archivos")
        
        # Variables para selección de features
        self.selected_features = set()
        self.feature_vars = {}
        self.target_column = "vacancies"
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del tab con notebook interno"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Crear notebook para sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab 1: Procesamiento
        self.create_processing_tab()
        
        # Tab 2: Selección de Features  
        self.create_feature_selection_tab()
        
        # Tab 3: Resultados y Exportación
        self.create_results_tab()
    
    def create_processing_tab(self):
        """Tab de procesamiento de archivos"""
        process_frame = ttk.Frame(self.notebook)
        self.notebook.add(process_frame, text="🔄 Procesamiento")
        
        # Sección de selección de directorio
        self.create_input_section(process_frame)
        
        # Sección de configuración
        self.create_configuration_section(process_frame)
        
        # Sección de procesamiento y progreso
        self.create_processing_section(process_frame)
    
    def create_input_section(self, parent):
        """Sección de selección de directorio"""
        input_frame = ttk.LabelFrame(parent, text="📁 Selección de Archivos", padding="10")
        input_frame.pack(fill="x", pady=(0, 10))
        
        # Directorio de entrada
        dir_frame = ttk.Frame(input_frame)
        dir_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(dir_frame, text="Directorio con archivos .dump:").pack(anchor="w")
        
        entry_frame = ttk.Frame(dir_frame)
        entry_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Entry(entry_frame, textvariable=self.directory_var, 
                 state="readonly", width=50).pack(side="left", fill="x", expand=True)
        
        ttk.Button(entry_frame, text="Explorar...", 
                  command=self.browse_directory).pack(side="right", padx=(5, 0))
        
        # Directorio de salida
        output_frame = ttk.Frame(input_frame)
        output_frame.pack(fill="x")
        
        ttk.Label(output_frame, text="Directorio de salida:").pack(anchor="w")
        
        output_entry_frame = ttk.Frame(output_frame)
        output_entry_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Entry(output_entry_frame, textvariable=self.output_dir_var, 
                 width=50).pack(side="left", fill="x", expand=True)
        
        ttk.Button(output_entry_frame, text="Cambiar...", 
                  command=self.browse_output_directory).pack(side="right", padx=(5, 0))
        
        # Información
        info_label = ttk.Label(input_frame, 
                              text="Se procesarán todos los archivos *.dump, dump.*, *.dump.gz encontrados", 
                              font=("Arial", 8), foreground="gray")
        info_label.pack(anchor="w", pady=(5, 0))
    
    def create_configuration_section(self, parent):
        """Sección de configuración de parámetros"""
        config_frame = ttk.LabelFrame(parent, text="⚙️ Configuración de Procesamiento", padding="10")
        config_frame.pack(fill="x", pady=(0, 10))
        
        # Frame principal con dos columnas
        main_config_frame = ttk.Frame(config_frame)
        main_config_frame.pack(fill="x")
        
        # Columna izquierda
        left_config = ttk.Frame(main_config_frame)
        left_config.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ttk.Label(left_config, text="Número total de átomos:").pack(anchor="w")
        atm_spinbox = ttk.Spinbox(left_config, from_=1000, to=100000, 
                                 textvariable=self.atm_total_var, width=15)
        atm_spinbox.pack(anchor="w", pady=(2, 10))
        
        ttk.Label(left_config, text="Energía mínima (eV):").pack(anchor="w")
        ttk.Entry(left_config, textvariable=self.energy_min_var, width=15).pack(anchor="w", pady=(2, 10))
        
        # Columna derecha
        right_config = ttk.Frame(main_config_frame)
        right_config.pack(side="right", fill="x", expand=True)
        
        ttk.Label(right_config, text="Energía máxima (eV):").pack(anchor="w")
        ttk.Entry(right_config, textvariable=self.energy_max_var, width=15).pack(anchor="w", pady=(2, 10))
        
        ttk.Label(right_config, text="Bins de energía:").pack(anchor="w")
        ttk.Spinbox(right_config, from_=5, to=50, 
                   textvariable=self.energy_bins_var, width=15).pack(anchor="w", pady=(2, 10))
        
        # Botón aplicar configuración
        ttk.Button(config_frame, text="Aplicar Configuración", 
                  command=self.apply_configuration).pack(pady=(10, 0))
        
        # Información de seguridad
        security_text = "🔒 SIN FUGA: No se incluyen n_atoms, vacancy_fraction ni features que revelen vacancias directamente"
        ttk.Label(config_frame, text=security_text, font=("Arial", 8), 
                 foreground="green", wraplength=400).pack(pady=(5, 0))
    
    def create_processing_section(self, parent):
        """Sección de procesamiento y progreso"""
        process_frame = ttk.LabelFrame(parent, text="🚀 Procesamiento", padding="10")
        process_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Botones de control
        button_frame = ttk.Frame(process_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Iniciar Procesamiento", 
                                      command=self.start_processing)
        self.start_button.pack(side="left")
        
        self.stop_button = ttk.Button(button_frame, text="Detener", 
                                     command=self.stop_processing, state="disabled")
        self.stop_button.pack(side="left", padx=(10, 0))
        
        ttk.Button(button_frame, text="Limpiar", 
                  command=self.clear_results).pack(side="right")
        
        # Barra de progreso
        progress_frame = ttk.Frame(process_frame)
        progress_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(progress_frame, text="Progreso:").pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.pack(fill="x", pady=(5, 0))
        
        # Estado
        self.status_label = ttk.Label(process_frame, textvariable=self.status_var, 
                                     font=("Arial", 9))
        self.status_label.pack(anchor="w")
        
        # Área de log
        log_frame = ttk.Frame(process_frame)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        ttk.Label(log_frame, text="Log de procesamiento:").pack(anchor="w")
        
        self.log_text = tk.Text(log_frame, height=8, wrap="word", font=("Courier", 9))
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
    
    def create_feature_selection_tab(self):
        """Tab de selección de features"""
        feature_frame = ttk.Frame(self.notebook)
        self.notebook.add(feature_frame, text="🎯 Selección Features")
        
        # Frame principal con tres paneles
        main_feature_frame = ttk.Frame(feature_frame, padding="10")
        main_feature_frame.pack(fill="both", expand=True)
        
        # Configurar grid
        main_feature_frame.columnconfigure(1, weight=1)
        main_feature_frame.rowconfigure(0, weight=1)
        
        # Panel izquierdo - Categorías
        self.create_categories_panel(main_feature_frame)
        
        # Panel central - Tabla de features
        self.create_features_table(main_feature_frame)
        
        # Panel derecho - Estadísticas
        self.create_statistics_panel(main_feature_frame)
        
        # Panel inferior - Controles
        self.create_feature_controls(main_feature_frame)
    
    def create_categories_panel(self, parent):
        """Panel de categorías de features"""
        cat_frame = ttk.LabelFrame(parent, text="Categorías", padding="10")
        cat_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Colores por categoría
        self.colors = {
            'coord': '#4CAF50',      # Verde
            'pe': '#2196F3',         # Azul
            'stress': '#FF9800',     # Naranja
            'voro': '#9C27B0',       # Púrpura
            'vacancy': '#F44336',    # Rojo
            'other': '#607D8B'       # Gris
        }
        
        # Botones de categorías
        self.category_buttons = {}
        categories = [
            ("Coordinación", 'coord'),
            ("Energía", 'pe'),
            ("Stress", 'stress'),
            ("Voronoi", 'voro'),
            ("Vacancias", 'vacancy'),
            ("Otros", 'other')
        ]
        
        for i, (label, key) in enumerate(categories):
            btn = ttk.Button(cat_frame, text=f"{label} (0/0)", 
                           command=lambda k=key: self.toggle_category(k))
            btn.grid(row=i, column=0, pady=2, sticky=(tk.W, tk.E))
            self.category_buttons[key] = btn
        
        # Separador
        ttk.Separator(cat_frame, orient='horizontal').grid(row=len(categories), 
                                                          column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Botones de selección rápida
        ttk.Button(cat_frame, text="✓ Seleccionar todo", 
                  command=self.select_all_features).grid(row=len(categories)+1, column=0, pady=2, 
                                                        sticky=(tk.W, tk.E))
        ttk.Button(cat_frame, text="✗ Deseleccionar todo", 
                  command=self.deselect_all_features).grid(row=len(categories)+2, column=0, pady=2, 
                                                          sticky=(tk.W, tk.E))
    
    def create_features_table(self, parent):
        """Panel central con tabla de features"""
        table_frame = ttk.LabelFrame(parent, text="Features Disponibles", padding="10")
        table_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Crear Treeview para la tabla
        columns = ('selected', 'feature', 'category', 'type', 'missing', 'unique')
        self.features_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.features_tree.heading('selected', text='✓')
        self.features_tree.heading('feature', text='Feature')
        self.features_tree.heading('category', text='Categoría')
        self.features_tree.heading('type', text='Tipo')
        self.features_tree.heading('missing', text='Faltantes')
        self.features_tree.heading('unique', text='Únicos')
        
        # Configurar anchos
        self.features_tree.column('selected', width=40, anchor='center')
        self.features_tree.column('feature', width=200, anchor='w')
        self.features_tree.column('category', width=100, anchor='center')
        self.features_tree.column('type', width=80, anchor='center')
        self.features_tree.column('missing', width=80, anchor='center')
        self.features_tree.column('unique', width=80, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.features_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.features_tree.xview)
        
        self.features_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Layout
        self.features_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind eventos
        self.features_tree.bind('<Button-1>', self.on_tree_click)
        self.features_tree.bind('<Double-1>', self.toggle_feature_selection)
    
    def create_statistics_panel(self, parent):
        """Panel de estadísticas"""
        stats_frame = ttk.LabelFrame(parent, text="Estadísticas", padding="10")
        stats_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Target selector
        target_frame = ttk.Frame(stats_frame)
        target_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(target_frame, text="Target:").pack(anchor="w")
        self.target_combo = ttk.Combobox(target_frame, state="readonly", width=20)
        self.target_combo.pack(fill="x", pady=(2, 0))
        self.target_combo.bind('<<ComboboxSelected>>', self.on_target_change)
        
        # Estadísticas
        self.stats_text = tk.Text(stats_frame, width=30, height=20, wrap=tk.WORD, 
                                 font=("Courier", 8))
        stats_scroll = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_text.pack(side="left", fill="both", expand=True)
        stats_scroll.pack(side="right", fill="y")
    
    def create_feature_controls(self, parent):
        """Panel de controles para features"""
        controls_frame = ttk.Frame(parent, padding="10")
        controls_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Contador de features
        self.feature_counter_label = ttk.Label(controls_frame, text="Features seleccionadas: 0/0", 
                                              font=('Arial', 11, 'bold'))
        self.feature_counter_label.pack(side="left")
        
        # Botones de configuración
        ttk.Button(controls_frame, text="📥 Importar Config Features", 
                  command=self.import_feature_config).pack(side="right", padx=5)
        
        ttk.Button(controls_frame, text="🔄 Actualizar Tabla", 
                  command=self.update_features_table).pack(side="right", padx=5)
    
    def create_results_tab(self):
        """Tab de resultados y exportación"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📊 Resultados")
        
        results_container = ttk.Frame(results_frame, padding="10")
        results_container.pack(fill="both", expand=True)
        
        # Información de resultados
        info_frame = ttk.LabelFrame(results_container, text="Información del Dataset", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.results_info_text = tk.Text(info_frame, height=12, wrap="word", 
                                        state="disabled", font=("Courier", 9))
        
        results_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", 
                                        command=self.results_info_text.yview)
        self.results_info_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_info_text.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Botones de exportación y ML
        export_frame = ttk.LabelFrame(results_container, text="Acciones", padding="10")
        export_frame.pack(fill="x")
        
        button_container = ttk.Frame(export_frame)
        button_container.pack()
        
        ttk.Button(button_container, text="💾 Exportar CSV Completo",
                  command=self.export_full_dataset).pack(side="left", padx=5)
        
        ttk.Button(button_container, text="🎯 Exportar Features Seleccionadas", 
                  command=self.export_selected_features).pack(side="left", padx=5)
        
        ttk.Button(button_container, text="🤖 Cargar en Advanced ML", 
                  command=self.load_to_advanced_ml).pack(side="left", padx=5)
        
        ttk.Button(button_container, text="📋 Exportar Config Features", 
                  command=self.export_feature_config).pack(side="left", padx=5)
    
    # =====================================================================
    # MÉTODOS DE PROCESAMIENTO
    # =====================================================================
    
    def browse_directory(self):
        """Seleccionar directorio con archivos .dump"""
        directory = filedialog.askdirectory(title="Seleccionar directorio con archivos .dump")
        if directory:
            self.directory_var.set(directory)
            try:
                dump_files = self.processor.find_dump_files(directory)
                message = f"Directorio seleccionado: {len(dump_files)} archivos .dump encontrados"
                self.update_status(message)
                self.log_message(message)
            except Exception as e:
                logger.error(f"Error explorando directorio: {e}")
                self.log_message(f"Error: {e}")
    
    def browse_output_directory(self):
        """Seleccionar directorio de salida"""
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if directory:
            self.output_dir_var.set(directory)
            self.log_message(f"Directorio de salida cambiado: {directory}")
    
    def apply_configuration(self):
        """Aplicar configuración al procesador"""
        try:
            self.processor.set_parameters(
                atm_total=self.atm_total_var.get(),
                energy_min=self.energy_min_var.get(),
                energy_max=self.energy_max_var.get(),
                energy_bins=self.energy_bins_var.get()
            )
            message = "Configuración aplicada correctamente"
            self.update_status(message)
            self.log_message(message)
        except Exception as e:
            messagebox.showerror("Error", f"Error en configuración: {str(e)}")
            self.log_message(f"Error en configuración: {e}")
    
    def start_processing(self):
        """Iniciar procesamiento en thread separado"""
        if not self.directory_var.get():
            messagebox.showwarning("Advertencia", "Por favor selecciona un directorio primero")
            return
        
        if self.processing:
            messagebox.showwarning("Advertencia", "Ya hay un procesamiento en curso")
            return
        
        # Aplicar configuración
        self.apply_configuration()
        
        # Cambiar estado
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.processing = True
        
        # Limpiar resultados previos
        self.current_dataset = None
        self.log_message("=== INICIANDO PROCESAMIENTO SIN FUGA ===")
        
        # Iniciar thread
        self.processing_thread = threading.Thread(target=self._process_files, daemon=True)
        self.processing_thread.start()
    
    def _process_files(self):
        """Procesamiento en thread separado"""
        try:
            directory = self.directory_var.get()
            
            self.update_status("Procesando archivos SIN FUGA...")
            dataset = self.processor.process_directory(directory)
            
            if not self.processing:  # Verificar si se canceló
                return
            
            # Guardar dataset
            output_dir = Path(self.output_dir_var.get())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            csv_path = output_dir / "dataset.csv"
            dataset.to_csv(csv_path)
            
            # Generar resumen
            summary = self.processor.get_feature_summary(dataset)
            
            # Actualizar interfaz
            self.frame.after(0, self._processing_completed, dataset, summary, csv_path)
            
        except Exception as e:
            error_msg = f"Error durante procesamiento: {str(e)}"
            logger.error(error_msg)
            self.frame.after(0, self._processing_failed, error_msg)
    
    def _processing_completed(self, dataset, summary, csv_path):
        """Callback cuando se completa el procesamiento"""
        self.current_dataset = dataset
        
        # Resetear controles
        self._reset_processing_controls()
        
        # Actualizar tabla de features
        self.populate_features_table()
        
        # Cambiar al tab de selección de features
        self.notebook.select(1)
        
        # Actualizar resultados
        results_text = self.format_processing_results(summary, csv_path)
        self.update_results_display(results_text)
        
        self.update_status(f"Procesamiento completado: {len(dataset)} archivos procesados")
        self.log_message(f"=== PROCESAMIENTO COMPLETADO: {len(dataset)} archivos ===")
        
        messagebox.showinfo("Éxito", 
                           f"Dataset generado exitosamente!\n\n"
                           f"Archivos: {len(dataset)}\n"
                           f"Features: {summary['total_features']}\n"
                           f"Cambie al tab 'Selección Features' para continuar")
    
    def _processing_failed(self, error_msg):
        """Callback cuando falla el procesamiento"""
        self._reset_processing_controls()
        self.update_status("Procesamiento fallido")
        self.log_message(f"ERROR: {error_msg}")
        messagebox.showerror("Error", error_msg)
    
    def _reset_processing_controls(self):
        """Resetear controles de procesamiento"""
        self.processing = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_var.set(0)
    
    def stop_processing(self):
        """Detener procesamiento"""
        if self.processing:
            self.processing = False
            self.update_status("Deteniendo procesamiento...")
            self.log_message("Procesamiento detenido por usuario")
            self._reset_processing_controls()
    
    def clear_results(self):
        """Limpiar resultados"""
        self.current_dataset = None
        self.selected_features.clear()
        self.feature_vars.clear()
        self.progress_var.set(0)
        self.update_status("Resultados limpiados")
        self.log_text.delete(1.0, tk.END)
        
        # Limpiar tabla de features
        if hasattr(self, 'features_tree'):
            for item in self.features_tree.get_children():
                self.features_tree.delete(item)
        
        # Limpiar estadísticas
        if hasattr(self, 'stats_text'):
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "Procese archivos para ver estadísticas")
        
        # Limpiar resultados
        if hasattr(self, 'results_info_text'):
            self.update_results_display("Resultados limpiados")
    
    def update_progress(self, current, total, message=""):
        """Callback para actualizar progreso"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        
        if message:
            status_msg = f"({current}/{total}) {message}"
            self.update_status(status_msg)
            self.log_message(message)
        
        self.frame.update_idletasks()
    
    def update_status(self, message):
        """Actualizar mensaje de estado"""
        self.status_var.set(message)
        logger.info(message)
    
    def log_message(self, message):
        """Añadir mensaje al log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.frame.update_idletasks()
    
    # =====================================================================
    # MÉTODOS DE SELECCIÓN DE FEATURES
    # =====================================================================
    
    def categorize_feature(self, feature_name: str) -> str:
        """Categorizar una feature basándose en su nombre"""
        feature_lower = feature_name.lower()
        
        if 'coord' in feature_lower:
            return 'coord'
        elif 'pe' in feature_lower or 'energy' in feature_lower:
            return 'pe'
        elif 'stress' in feature_lower or 'vm' in feature_lower or 'pressure' in feature_lower:
            return 'stress'
        elif 'voro' in feature_lower:
            return 'voro'
        elif 'vacan' in feature_lower or 'vac' in feature_lower:
            return 'vacancy'
        else:
            return 'other'
    
    def populate_features_table(self):
        """Poblar tabla de features"""
        if self.current_dataset is None:
            return
        
        # Limpiar tabla anterior
        for item in self.features_tree.get_children():
            self.features_tree.delete(item)
        
        # Resetear variables
        self.feature_vars = {}
        self.selected_features = set()
        
        # IMPORTANTE: Excluir SOLO metadata, NO el target 'vacancies'
        # 'vacancies' se exportará pero no se mostrará como feature seleccionable
        exclude_cols = ['file_path']  # Solo excluir metadata
        features = [col for col in self.current_dataset.columns if col not in exclude_cols]
        
        # SEPARAR: features de target 
        # Target candidates (vacancies debe estar disponible pero no seleccionable como feature)
        target_candidates = [col for col in features if 'vacan' in col.lower()]
        
        # Features reales (todo excepto target candidates)
        actual_features = [col for col in features if col not in target_candidates]
        
        # Actualizar target combo
        if target_candidates:
            self.target_combo['values'] = target_candidates
            self.target_combo.set('vacancies' if 'vacancies' in target_candidates else target_candidates[0])
            self.target_column = 'vacancies' if 'vacancies' in target_candidates else target_candidates[0]
        else:
            # Fallback si no hay columnas de vacancias
            self.target_combo['values'] = ['vacancies']
            self.target_combo.set('vacancies')
            self.target_column = 'vacancies'
        
        # Poblar tabla SOLO con features reales (sin target)
        for feature in sorted(actual_features):
            category = self.categorize_feature(feature)
            dtype = str(self.current_dataset[feature].dtype)
            missing = int(self.current_dataset[feature].isnull().sum())
            unique = int(self.current_dataset[feature].nunique())
            
            # Insertar en tabla (seleccionado por defecto)
            item_id = self.features_tree.insert('', 'end', values=(
                '✓', feature, category, dtype, missing, unique
            ))
            
            # Agregar a seleccionados
            self.feature_vars[feature] = True
            self.selected_features.add(feature)
        
        # Actualizar contadores
        self.update_category_counts()
        self.update_feature_counter()
        self.update_statistics()
    
    def on_tree_click(self, event):
        """Manejar click en la tabla"""
        region = self.features_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.features_tree.identify_column(event.x, event.y)
            if column == '#1':  # Columna de selección
                self.toggle_feature_selection(event)
    
    def toggle_feature_selection(self, event):
        """Toggle selección de feature"""
        item = self.features_tree.selection()[0] if self.features_tree.selection() else None
        if not item:
            return
        
        values = list(self.features_tree.item(item, 'values'))
        feature = values[1]  # Nombre de la feature
        
        # Toggle selección
        if feature in self.selected_features:
            self.selected_features.remove(feature)
            self.feature_vars[feature] = False
            values[0] = '✗'
        else:
            self.selected_features.add(feature)
            self.feature_vars[feature] = True
            values[0] = '✓'
        
        # Actualizar tabla
        self.features_tree.item(item, values=values)
        
        # Actualizar contadores
        self.update_category_counts()
        self.update_feature_counter()
        self.update_statistics()
    
    def toggle_category(self, category):
        """Toggle todas las features de una categoría"""
        if not self.feature_vars:
            return
        
        # Obtener features de la categoría
        cat_features = [f for f in self.feature_vars.keys() if self.categorize_feature(f) == category]
        
        # Verificar si todas están seleccionadas
        all_selected = all(f in self.selected_features for f in cat_features)
        
        # Toggle
        for feature in cat_features:
            if all_selected:
                self.selected_features.discard(feature)
                self.feature_vars[feature] = False
            else:
                self.selected_features.add(feature)
                self.feature_vars[feature] = True
        
        # Actualizar tabla
        self.update_features_table()
    
    def select_all_features(self):
        """Seleccionar todas las features"""
        self.selected_features = set(self.feature_vars.keys())
        for feature in self.feature_vars:
            self.feature_vars[feature] = True
        
        self.update_features_table()
    
    def deselect_all_features(self):
        """Deseleccionar todas las features"""
        self.selected_features.clear()
        for feature in self.feature_vars:
            self.feature_vars[feature] = False
        
        self.update_features_table()
    
    def update_features_table(self):
        """Actualizar tabla de features"""
        for item in self.features_tree.get_children():
            values = list(self.features_tree.item(item, 'values'))
            feature = values[1]
            
            if feature in self.selected_features:
                values[0] = '✓'
            else:
                values[0] = '✗'
            
            self.features_tree.item(item, values=values)
        
        self.update_category_counts()
        self.update_feature_counter()
        self.update_statistics()
    
    def update_category_counts(self):
        """Actualizar contadores en botones de categorías"""
        if not self.feature_vars:
            return
        
        counts = {cat: 0 for cat in self.colors.keys()}
        totals = {cat: 0 for cat in self.colors.keys()}
        
        for feat, _ in self.feature_vars.items():
            cat = self.categorize_feature(feat)
            totals[cat] += 1
            if feat in self.selected_features:
                counts[cat] += 1
        
        for cat, btn in self.category_buttons.items():
            selected = counts.get(cat, 0)
            total = totals.get(cat, 0)
            
            label = cat.capitalize()
            if cat == 'pe':
                label = "Energía"
            elif cat == 'coord':
                label = "Coordinación"
            elif cat == 'voro':
                label = "Voronoi"
            elif cat == 'vacancy':
                label = "Vacancias"
            elif cat == 'other':
                label = "Otros"
            
            btn.config(text=f"{label} ({selected}/{total})")
    
    def update_feature_counter(self):
        """Actualizar contador de features seleccionadas"""
        total = len(self.feature_vars)
        selected = len(self.selected_features)
        self.feature_counter_label.config(text=f"Features seleccionadas: {selected}/{total}")
    
    def on_target_change(self, event):
        """Manejar cambio de columna target"""
        self.target_column = self.target_combo.get()
        self.update_statistics()
    
    def update_statistics(self):
        """Actualizar panel de estadísticas"""
        self.stats_text.delete(1.0, tk.END)
        
        if self.current_dataset is None or not self.selected_features:
            self.stats_text.insert(tk.END, "No hay features seleccionadas")
            return
        
        stats_info = []
        stats_info.append("="*30)
        stats_info.append("RESUMEN FEATURES")
        stats_info.append("="*30)
        stats_info.append(f"\nSeleccionadas: {len(self.selected_features)}")
        stats_info.append(f"Target: {self.target_column}")
        
        # VERIFICAR que el target esté presente
        target_available = self.target_column in self.current_dataset.columns
        stats_info.append(f"Target disponible: {'✓' if target_available else '✗'}")
        
        # Estadísticas del target
        if target_available:
            target_data = self.current_dataset[self.target_column]
            stats_info.append(f"\nEstadísticas target:")
            stats_info.append(f"  Min: {target_data.min():.2f}")
            stats_info.append(f"  Max: {target_data.max():.2f}")
            stats_info.append(f"  Media: {target_data.mean():.2f}")
            stats_info.append(f"  Std: {target_data.std():.2f}")
        else:
            stats_info.append(f"\n⚠️ TARGET NO ENCONTRADO")
        
        # Features por categoría
        stats_info.append(f"\nPor categoría:")
        for cat in ['coord', 'pe', 'stress', 'voro', 'vacancy', 'other']:
            count = sum(1 for f in self.selected_features if self.categorize_feature(f) == cat)
            if count > 0:
                stats_info.append(f"  {cat}: {count}")
        
        # NOTA IMPORTANTE sobre exportación
        stats_info.append(f"\n💡 NOTA:")
        stats_info.append(f"Al exportar se incluirán:")
        stats_info.append(f"  • Features: {len(self.selected_features)}")
        stats_info.append(f"  • Target: {self.target_column}")
        stats_info.append(f"  • Total: {len(self.selected_features) + (1 if target_available else 0)}")
        
        # Top features por varianza
        if len(self.selected_features) > 0:
            stats_info.append(f"\nTop 8 (por varianza):")
            variances = {}
            for feat in self.selected_features:
                if feat in self.current_dataset.columns:
                    try:
                        var = self.current_dataset[feat].var()
                        if not np.isnan(var):
                            variances[feat] = var
                    except:
                        pass
            
            sorted_vars = sorted(variances.items(), key=lambda x: x[1], reverse=True)[:8]
            for feat, var in sorted_vars:
                stats_info.append(f"  {feat[:18]}: {var:.4f}")
        
        self.stats_text.insert(tk.END, "\n".join(stats_info))
    
    # =====================================================================
    # MÉTODOS DE EXPORTACIÓN Y RESULTADOS
    # =====================================================================
    
    def update_results_display(self, text):
        """Actualizar display de resultados"""
        self.results_info_text.config(state="normal")
        self.results_info_text.delete(1.0, tk.END)
        self.results_info_text.insert(1.0, text)
        self.results_info_text.config(state="disabled")
    
    def format_processing_results(self, summary, csv_path):
        """Formatear resultados del procesamiento"""
        text = f"✅ PROCESAMIENTO SIN FUGA COMPLETADO\n\n"
        text += f"📊 RESUMEN DEL DATASET:\n"
        text += f"   • Archivos procesados: {summary['total_files']}\n"
        text += f"   • Features extraídas: {summary['total_features']}\n"
        text += f"   • Archivo guardado: {csv_path}\n\n"
        
        text += f"📈 DISTRIBUCIÓN DE FEATURES:\n"
        for category, count in summary['feature_categories'].items():
            text += f"   • {category.capitalize()}: {count}\n"
        
        text += f"\n🔒 CARACTERÍSTICAS DE SEGURIDAD:\n"
        text += f"   • SIN FUGA: No se incluyen n_atoms, vacancy_fraction\n"
        text += f"   • SIN FUGA: No se incluyen features que revelen vacancias\n"
        text += f"   • Todas las estadísticas calculadas solo sobre átomos presentes\n"
        
        if summary.get('vacancy_stats'):
            vac_stats = summary['vacancy_stats']
            text += f"\nℹ️ INFORMACIÓN DE VACANCIAS (SOLO METADATA):\n"
            text += f"   • Mínimo: {vac_stats['min']}\n"
            text += f"   • Máximo: {vac_stats['max']}\n"
            text += f"   • Promedio: {vac_stats['mean']:.1f}\n"
            text += f"   • Desviación: {vac_stats['std']:.1f}\n"
        
        text += f"\n💡 NOTA: Use el tab 'Selección Features' para elegir features específicas\n"
        
        return text
    
    def export_full_dataset(self):
        """Exportar dataset completo"""
        if self.current_dataset is None:
            messagebox.showwarning("Advertencia", "No hay dataset para exportar")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
            )
            
            if filename:
                if filename.endswith('.xlsx'):
                    self.current_dataset.to_excel(filename)
                else:
                    self.current_dataset.to_csv(filename)
                
                messagebox.showinfo("Éxito", f"Dataset completo exportado:\n{filename}")
                self.log_message(f"Dataset completo exportado: {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando dataset: {str(e)}")
            self.log_message(f"Error exportando: {e}")
    
    def export_selected_features(self):
        """Exportar features seleccionadas + target vacancies SIEMPRE"""
        if self.current_dataset is None or not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
            )
            
            if filename:
                # CRÍTICO: Incluir features seleccionadas + target SIEMPRE
                columns = list(self.selected_features)
                
                # ASEGURAR que vacancies esté incluido para entrenamiento
                if self.target_column and self.target_column in self.current_dataset.columns:
                    if self.target_column not in columns:
                        columns.append(self.target_column)
                else:
                    # Fallback: buscar vacancies si target_column no está definido
                    if 'vacancies' in self.current_dataset.columns and 'vacancies' not in columns:
                        columns.append('vacancies')
                        messagebox.showinfo("Información", 
                                           "Se añadió automáticamente la columna 'vacancies' como target")
                
                filtered_dataset = self.current_dataset[columns]
                
                if filename.endswith('.xlsx'):
                    filtered_dataset.to_excel(filename)
                else:
                    filtered_dataset.to_csv(filename)
                
                # Separar features de target en el mensaje
                feature_count = len([col for col in columns if col != self.target_column])
                
                messagebox.showinfo("Éxito", 
                                   f"Dataset para ML exportado:\n{filename}\n\n"
                                   f"Features: {feature_count}\n"
                                   f"Target: {self.target_column}\n"
                                   f"Total columnas: {len(columns)}\n"
                                   f"Muestras: {len(filtered_dataset)}")
                
                self.log_message(f"Features seleccionadas exportadas: {filename}")
                self.log_message(f"Features: {feature_count}, Target: {self.target_column}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando features: {str(e)}")
            self.log_message(f"Error exportando features: {e}")
    
    def load_to_advanced_ml(self):
        """Cargar dataset al Advanced ML tab con target incluido"""
        if self.current_dataset is None:
            messagebox.showwarning("Advertencia", "No hay dataset para cargar")
            return
        
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        try:
            # CRÍTICO: Preparar dataset con features + target
            columns = list(self.selected_features)
            
            # ASEGURAR que el target esté incluido
            if self.target_column and self.target_column in self.current_dataset.columns:
                if self.target_column not in columns:
                    columns.append(self.target_column)
            else:
                # Fallback
                if 'vacancies' in self.current_dataset.columns and 'vacancies' not in columns:
                    columns.append('vacancies')
            
            filtered_dataset = self.current_dataset[columns]
            
            # Verificar que el target esté presente
            target_present = self.target_column in filtered_dataset.columns
            if not target_present and 'vacancies' in filtered_dataset.columns:
                target_present = True
                self.target_column = 'vacancies'
            
            # Llamar callback
            if self.data_loaded_callback:
                self.data_loaded_callback(filtered_dataset)
                
                feature_count = len([col for col in columns if col not in ['vacancies', self.target_column]])
                
                messagebox.showinfo("Éxito", 
                                   f"Dataset cargado en Advanced ML:\n\n"
                                   f"Features: {feature_count}\n"
                                   f"Target: {self.target_column}\n"
                                   f"Target incluido: {'Sí' if target_present else 'No'}\n"
                                   f"Total columnas: {len(columns)}\n"
                                   f"Muestras: {len(filtered_dataset)}")
                
                self.log_message(f"Dataset cargado en Advanced ML: {len(columns)} columnas")
                
                if not target_present:
                    messagebox.showwarning("Advertencia", 
                                         "¡ATENCIÓN! No se encontró columna target.\n"
                                         "El entrenamiento puede fallar.")
            else:
                messagebox.showwarning("Advertencia", "Callback no disponible")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando a ML: {str(e)}")
            self.log_message(f"Error cargando a ML: {e}")
    
    def export_feature_config(self):
        """Exportar configuración de features seleccionadas"""
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            
            if filename:
                config = {
                    'selected_features': list(self.selected_features),
                    'target_column': self.target_column,
                    'total_features': len(self.feature_vars),
                    'processing_params': {
                        'atm_total': self.atm_total_var.get(),
                        'energy_min': self.energy_min_var.get(),
                        'energy_max': self.energy_max_var.get(),
                        'energy_bins': self.energy_bins_var.get()
                    },
                    'dataset_info': {
                        'rows': len(self.current_dataset) if self.current_dataset is not None else 0,
                        'original_columns': len(self.current_dataset.columns) if self.current_dataset is not None else 0
                    },
                    'export_timestamp': pd.Timestamp.now().isoformat()
                }
                
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=4)
                
                messagebox.showinfo("Éxito", f"Configuración exportada:\n{filename}")
                self.log_message(f"Configuración exportada: {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando configuración: {str(e)}")
            self.log_message(f"Error exportando config: {e}")
    
    def import_feature_config(self):
        """Importar configuración de features"""
        if self.current_dataset is None:
            messagebox.showwarning("Advertencia", "Primero procese un dataset")
            return
        
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                if 'selected_features' in config:
                    # Verificar que las features existan
                    available_features = set(self.feature_vars.keys())
                    config_features = set(config['selected_features'])
                    
                    missing_features = config_features - available_features
                    if missing_features:
                        messagebox.showwarning("Advertencia", 
                                             f"Algunas features no están disponibles:\n{missing_features}")
                    
                    # Aplicar configuración
                    self.selected_features = config_features & available_features
                    
                    # Actualizar feature_vars
                    for feature in self.feature_vars:
                        self.feature_vars[feature] = feature in self.selected_features
                    
                    # Actualizar target si existe
                    if 'target_column' in config:
                        target = config['target_column']
                        if target in self.current_dataset.columns:
                            self.target_column = target
                            self.target_combo.set(target)
                    
                    # Actualizar tabla
                    self.update_features_table()
                    
                    messagebox.showinfo("Éxito", 
                                       f"Configuración importada:\n\n"
                                       f"Features aplicadas: {len(self.selected_features)}\n"
                                       f"Features faltantes: {len(missing_features)}")
                    
                    self.log_message(f"Configuración importada: {filename}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error importando configuración: {str(e)}")
            self.log_message(f"Error importando config: {e}")
    
    def reset(self):
        """Reset completo del tab"""
        # Reset variables de procesamiento
        self.directory_var.set("")
        self.output_dir_var.set("ml_dataset_output")
        self.atm_total_var.set(16384)
        self.energy_min_var.set(-4.0)
        self.energy_max_var.set(-3.0)
        self.energy_bins_var.set(10)
        
        # Reset estado
        self.current_dataset = None
        self.processing = False
        
        # Reset features
        self.selected_features = set()
        self.feature_vars = {}
        self.target_column = "vacancies"
        
        # Reset controles
        self._reset_processing_controls()
        
        # Limpiar displays
        self.update_status("Listo para procesar archivos")
        self.log_text.delete(1.0, tk.END)
        self.log_message("Tab reiniciado")
        
        # Limpiar tabla
        if hasattr(self, 'features_tree'):
            for item in self.features_tree.get_children():
                self.features_tree.delete(item)
        
        # Limpiar estadísticas
        if hasattr(self, 'stats_text'):
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "Procese archivos para ver estadísticas")
        
        # Limpiar resultados
        if hasattr(self, 'results_info_text'):
            self.update_results_display("No hay resultados")
        
        # Volver al primer tab
        self.notebook.select(0)
    
    def get_frame(self):
        """Obtener frame del tab"""
        return self.frame