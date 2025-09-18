"""
Tab para procesamiento batch de archivos LAMMPS dump
Genera datasets CSV con features para machine learning
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
import logging
import threading
from typing import Callable, Optional

# Importar el procesador batch
from vacancy_predictor.core.batch_processor import BatchDumpProcessor

logger = logging.getLogger(__name__)

class BatchProcessingTab:
    """Tab para procesamiento batch de archivos LAMMPS dump"""
    
    def __init__(self, parent, data_loaded_callback: Callable):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        
        # Procesador batch
        self.processor = BatchDumpProcessor()
        self.processor.set_progress_callback(self.update_progress)
        
        self.frame = ttk.Frame(parent)
        
        # Variables
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
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del tab"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Crear paneles
        self.create_input_section(main_container)
        self.create_configuration_section(main_container)
        self.create_processing_section(main_container)
        self.create_results_section(main_container)
    
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
        
        # Columna izquierda - Parámetros básicos
        left_config = ttk.Frame(main_config_frame)
        left_config.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Átomos totales
        ttk.Label(left_config, text="Número total de átomos:").pack(anchor="w")
        atm_spinbox = ttk.Spinbox(left_config, from_=1000, to=100000, 
                                 textvariable=self.atm_total_var, width=15)
        atm_spinbox.pack(anchor="w", pady=(2, 10))
        
        # Energía mínima
        ttk.Label(left_config, text="Energía mínima (eV):").pack(anchor="w")
        ttk.Entry(left_config, textvariable=self.energy_min_var, width=15).pack(anchor="w", pady=(2, 10))
        
        # Columna derecha - Parámetros de energía
        right_config = ttk.Frame(main_config_frame)
        right_config.pack(side="right", fill="x", expand=True)
        
        # Energía máxima  
        ttk.Label(right_config, text="Energía máxima (eV):").pack(anchor="w")
        ttk.Entry(right_config, textvariable=self.energy_max_var, width=15).pack(anchor="w", pady=(2, 10))
        
        # Bins de energía
        ttk.Label(right_config, text="Bins de energía:").pack(anchor="w")
        ttk.Spinbox(right_config, from_=5, to=50, 
                   textvariable=self.energy_bins_var, width=15).pack(anchor="w", pady=(2, 10))
        
        # Botón para aplicar configuración
        ttk.Button(config_frame, text="Aplicar Configuración", 
                  command=self.apply_configuration).pack(pady=(10, 0))
        
        # Información sobre features
        info_text = ("Features extraídas: coordinación, energía potencial, stress, "
                    "histogramas, estadísticos agregados")
        ttk.Label(config_frame, text=info_text, font=("Arial", 8), 
                 foreground="gray", wraplength=400).pack(pady=(5, 0))
    
    def create_processing_section(self, parent):
        """Sección de procesamiento y progreso"""
        process_frame = ttk.LabelFrame(parent, text="🚀 Procesamiento", padding="10")
        process_frame.pack(fill="x", pady=(0, 10))
        
        # Botones de control
        button_frame = ttk.Frame(process_frame)
        button_frame.pack(fill="x", pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Iniciar Procesamiento", 
                                      command=self.start_processing)
        self.start_button.pack(side="left")
        
        self.stop_button = ttk.Button(button_frame, text="Detener", 
                                     command=self.stop_processing, state="disabled")
        self.stop_button.pack(side="left", padx=(10, 0))
        
        ttk.Button(button_frame, text="Limpiar Resultados", 
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
    
    def create_results_section(self, parent):
        """Sección de resultados"""
        results_frame = ttk.LabelFrame(parent, text="📊 Resultados", padding="10")
        results_frame.pack(fill="both", expand=True)
        
        # Frame para información de resultados
        info_frame = ttk.Frame(results_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Texto de información
        self.results_text = tk.Text(info_frame, height=8, wrap="word", 
                                   state="disabled", font=("Courier", 9))
        
        # Scrollbar para el texto
        results_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", 
                                        command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Botones de exportación
        export_frame = ttk.Frame(results_frame)
        export_frame.pack(fill="x")
        
        ttk.Button(export_frame, text="Exportar CSV",
                  command=self.export_dataset).pack(side="left")
        
        ttk.Button(export_frame, text="Ver Dataset", 
                  command=self.view_dataset).pack(side="left", padx=(10, 0))
        
        ttk.Button(export_frame, text="Cargar en ML", 
                  command=self.load_to_ml).pack(side="left", padx=(10, 0))
    
    def browse_directory(self):
        """Seleccionar directorio con archivos .dump"""
        directory = filedialog.askdirectory(title="Seleccionar directorio con archivos .dump")
        if directory:
            self.directory_var.set(directory)
            # Contar archivos encontrados
            try:
                dump_files = self.processor.find_dump_files(directory)
                message = f"Directorio seleccionado: {len(dump_files)} archivos .dump encontrados"
                self.update_status(message)
            except Exception as e:
                logger.error(f"Error explorando directorio: {e}")
    
    def browse_output_directory(self):
        """Seleccionar directorio de salida"""
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if directory:
            self.output_dir_var.set(directory)
    
    def apply_configuration(self):
        """Aplicar configuración al procesador"""
        try:
            self.processor.set_parameters(
                atm_total=self.atm_total_var.get(),
                energy_min=self.energy_min_var.get(),
                energy_max=self.energy_max_var.get(),
                energy_bins=self.energy_bins_var.get()
            )
            self.update_status("Configuración aplicada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error en configuración: {str(e)}")
    
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
        
        # Cambiar estado de botones
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.processing = True
        
        # Limpiar resultados previos
        self.current_dataset = None
        self.update_results_display("Iniciando procesamiento...\n")
        
        # Iniciar thread de procesamiento
        self.processing_thread = threading.Thread(target=self._process_files, daemon=True)
        self.processing_thread.start()
    
    def _process_files(self):
        """Procesamiento en thread separado"""
        try:
            directory = self.directory_var.get()
            
            # Procesar archivos
            self.update_status("Procesando archivos...")
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
            
            # Actualizar interfaz en main thread
            self.frame.after(0, self._processing_completed, dataset, summary, csv_path)
            
        except Exception as e:
            error_msg = f"Error durante procesamiento: {str(e)}"
            logger.error(error_msg)
            self.frame.after(0, self._processing_failed, error_msg)
    
    def _processing_completed(self, dataset, summary, csv_path):
        """Callback cuando el procesamiento se completa exitosamente"""
        self.current_dataset = dataset
        
        # Actualizar display de resultados
        results_text = self.format_processing_results(summary, csv_path)
        self.update_results_display(results_text)
        
        # Resetear controles
        self._reset_processing_controls()
        
        # Notificar completación
        self.update_status(f"Procesamiento completado: {len(dataset)} archivos procesados")
        
        # Mostrar mensaje de éxito
        messagebox.showinfo("Éxito", 
                           f"Dataset generado exitosamente!\n\n"
                           f"Archivos procesados: {len(dataset)}\n"
                           f"Features extraídas: {len(dataset.columns)-1}\n"
                           f"Archivo guardado: {csv_path}")
    
    def _processing_failed(self, error_msg):
        """Callback cuando el procesamiento falla"""
        self.update_results_display(f"ERROR: {error_msg}\n")
        self._reset_processing_controls()
        self.update_status("Procesamiento fallido")
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
            self._reset_processing_controls()
    
    def update_progress(self, current, total, message=""):
        """Callback para actualizar progreso"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        
        if message:
            self.update_status(f"({current}/{total}) {message}")
        
        # Actualizar interfaz
        self.frame.update_idletasks()
    
    def update_status(self, message):
        """Actualizar mensaje de estado"""
        self.status_var.set(message)
        logger.info(message)
    
    def update_results_display(self, text):
        """Actualizar display de resultados"""
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        self.results_text.config(state="disabled")
        self.results_text.see(tk.END)
    
    def format_processing_results(self, summary, csv_path):
        """Formatear resultados para mostrar"""
        lines = [
            "PROCESAMIENTO COMPLETADO",
            "=" * 40,
            f"Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Archivo CSV: {csv_path}",
            "",
            "RESUMEN DEL DATASET:",
            f"  Archivos procesados: {summary['total_files']}",
            f"  Features extraídas: {summary['total_features']}",
            "",
            "CATEGORÍAS DE FEATURES:",
            f"  Coordinación: {summary['feature_categories']['coordination']}",
            f"  Energía potencial: {summary['feature_categories']['potential_energy']}",
            f"  Stress: {summary['feature_categories']['stress']}",
            f"  Otros: {summary['feature_categories']['other']}",
            ""
        ]
        
        # Agregar estadísticas de vacancias si están disponibles
        if summary['vacancy_stats']:
            vac_stats = summary['vacancy_stats']
            lines.extend([
                "ESTADÍSTICAS DE VACANCIAS (TARGET):",
                f"  Mínimo: {vac_stats['min']} vacancias",
                f"  Máximo: {vac_stats['max']} vacancias", 
                f"  Promedio: {vac_stats['mean']:.1f} vacancias",
                f"  Desv. estándar: {vac_stats['std']:.1f}",
                ""
            ])
        
        lines.extend([
            "CONFIGURACIÓN UTILIZADA:",
            f"  Átomos totales: {self.atm_total_var.get()}",
            f"  Rango energía: [{self.energy_min_var.get()}, {self.energy_max_var.get()}] eV",
            f"  Bins energía: {self.energy_bins_var.get()}",
            "",
            "NOTAS IMPORTANTES:",
            "- Dataset sin fuga de información (no incluye n_atoms)",
            "- Columna 'vacancies' solo para usar como target/label",
            "- Features basadas en propiedades físicas reales",
            "- Listo para entrenamiento de modelos ML"
        ])
        
        return "\n".join(lines)
    
    def export_dataset(self):
        """Exportar dataset actual"""
        if self.current_dataset is None:
            messagebox.showwarning("Advertencia", "No hay dataset para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Dataset",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    self.current_dataset.to_excel(file_path)
                else:
                    self.current_dataset.to_csv(file_path)
                
                messagebox.showinfo("Éxito", f"Dataset exportado a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")
    
    def view_dataset(self):
        """Mostrar dataset en ventana separada"""
        if self.current_dataset is None:
            messagebox.showwarning("Advertencia", "No hay dataset para mostrar")
            return
        
        # Crear ventana de visualización
        view_window = tk.Toplevel(self.frame)
        view_window.title("Vista del Dataset")
        view_window.geometry("800x600")
        
        # Frame principal
        main_frame = ttk.Frame(view_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Información del dataset
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        info_text = f"Dataset: {len(self.current_dataset)} filas × {len(self.current_dataset.columns)} columnas"
        ttk.Label(info_frame, text=info_text, font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Crear Treeview para mostrar datos
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        tree = ttk.Treeview(tree_frame, 
                           yscrollcommand=v_scrollbar.set,
                           xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.config(command=tree.yview)
        h_scrollbar.config(command=tree.xview)
        
        # Configurar columnas (mostrar solo primeras 20 por rendimiento)
        columns = list(self.current_dataset.columns)[:20]
        tree["columns"] = columns
        tree["show"] = "tree headings"
        
        # Configurar headers
        tree.heading("#0", text="Archivo")
        tree.column("#0", width=150)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Insertar datos (primeras 100 filas por rendimiento)
        for i, (index, row) in enumerate(self.current_dataset.head(100).iterrows()):
            values = [f"{row[col]:.3f}" if pd.api.types.is_numeric_dtype(type(row[col])) 
                     else str(row[col]) for col in columns]
            tree.insert("", "end", text=index, values=values)
        
        # Pack scrollbars y treeview
        tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=view_window.destroy).pack(pady=(10, 0))
    
    def load_to_ml(self):
        """Cargar dataset actual al módulo de ML"""
        if self.current_dataset is None:
            messagebox.showwarning("Advertencia", "No hay dataset para cargar")
            return
        
        try:
            # Excluir columnas que no son features
            feature_columns = [col for col in self.current_dataset.columns 
                             if col not in ['vacancies', 'file_path']]
            
            ml_dataset = self.current_dataset[feature_columns].copy()
            
            # Notificar al callback principal
            self.data_loaded_callback(ml_dataset)
            
            messagebox.showinfo("Éxito", 
                               f"Dataset cargado al módulo ML\n\n"
                               f"Features: {len(feature_columns)}\n"
                               f"Muestras: {len(ml_dataset)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar dataset:\n{str(e)}")
    
    def clear_results(self):
        """Limpiar resultados"""
        if messagebox.askyesno("Confirmar", "¿Limpiar todos los resultados?"):
            self.current_dataset = None
            self.update_results_display("Resultados limpiados. Listo para nuevo procesamiento.")
            self.update_status("Resultados limpiados")
            self.progress_var.set(0)
    
    def reset(self):
        """Reset completo del tab"""
        self.directory_var.set("")
        self.output_dir_var.set("ml_dataset_output")
        
        # Reset parámetros a valores por defecto
        self.atm_total_var.set(16384)
        self.energy_min_var.set(-4.0)
        self.energy_max_var.set(-3.0)
        self.energy_bins_var.set(10)
        
        # Reset estado
        self.current_dataset = None
        self.processing = False
        self._reset_processing_controls()
        
        # Limpiar displays
        self.update_results_display("Tab reiniciado. Listo para procesar archivos.")
        self.update_status("Listo para procesar archivos")