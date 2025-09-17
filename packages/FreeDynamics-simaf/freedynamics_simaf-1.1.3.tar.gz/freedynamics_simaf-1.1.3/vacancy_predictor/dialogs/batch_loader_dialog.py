"""
Simple batch loader dialog for LAMMPS dump files
Integrates with existing FreeDynamics-simaf architecture
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import time
from typing import Optional, Callable
import json

class SimpleBatchLoaderDialog:
    """Simple dialog for batch loading LAMMPS dump files"""
    
    def __init__(self, parent, data_processor, callback_on_complete: Optional[Callable] = None):
        self.parent = parent
        self.data_processor = data_processor
        self.callback_on_complete = callback_on_complete
        
        # Variables
        self.directory_path = None
        self.found_files = []
        self.processing_thread = None
        self.is_processing = False
        
        # Configuration variables
        self.atm_total_var = tk.IntVar(value=16384)
        self.energy_min_var = tk.DoubleVar(value=-4.0)
        self.energy_max_var = tk.DoubleVar(value=-3.0)
        self.energy_bins_var = tk.IntVar(value=10)
        self.recursive_var = tk.BooleanVar(value=True)
        
        # Create dialog
        self.create_dialog()
    
    def create_dialog(self):
        """Create the main dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Carga Masiva de Archivos LAMMPS Dump")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Create sections
        self.create_directory_section(main_frame)
        self.create_config_section(main_frame)
        self.create_files_section(main_frame)
        self.create_log_section(main_frame)
        self.create_control_section(main_frame)
    
    def create_directory_section(self, parent):
        """Create directory selection section"""
        dir_frame = ttk.LabelFrame(parent, text="Directorio de Archivos Dump", padding="10")
        dir_frame.pack(fill='x', pady=(0, 10))
        
        # Directory selection
        dir_row = ttk.Frame(dir_frame)
        dir_row.pack(fill='x')
        
        ttk.Button(dir_row, text="Seleccionar Directorio", 
                  command=self.select_directory).pack(side='left', padx=(0, 10))
        
        self.dir_label = ttk.Label(dir_row, text="No se ha seleccionado directorio", 
                                  foreground='gray')
        self.dir_label.pack(side='left', fill='x', expand=True)
        
        ttk.Button(dir_row, text="Escanear", 
                  command=self.scan_directory, state='disabled').pack(side='right')
        
        self.scan_btn = dir_row.winfo_children()[-1]  # Reference to scan button
    
    def create_config_section(self, parent):
        """Create configuration section"""
        config_frame = ttk.LabelFrame(parent, text="Configuración LAMMPS", padding="10")
        config_frame.pack(fill='x', pady=(0, 10))
        
        # Two columns
        col1 = ttk.Frame(config_frame)
        col1.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        col2 = ttk.Frame(config_frame)
        col2.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Column 1
        ttk.Label(col1, text="Átomos totales:").pack(anchor='w')
        ttk.Entry(col1, textvariable=self.atm_total_var, width=15).pack(anchor='w', pady=(0, 5))
        
        ttk.Label(col1, text="Energía mínima:").pack(anchor='w')
        ttk.Entry(col1, textvariable=self.energy_min_var, width=15).pack(anchor='w', pady=(0, 5))
        
        # Column 2  
        ttk.Label(col2, text="Energía máxima:").pack(anchor='w')
        ttk.Entry(col2, textvariable=self.energy_max_var, width=15).pack(anchor='w', pady=(0, 5))
        
        ttk.Label(col2, text="Bins de energía:").pack(anchor='w')
        ttk.Entry(col2, textvariable=self.energy_bins_var, width=15).pack(anchor='w', pady=(0, 5))
        
        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Checkbutton(options_frame, text="Búsqueda recursiva", 
                       variable=self.recursive_var).pack(side='left')
        
        # Quick config buttons
        ttk.Button(options_frame, text="Config por defecto", 
                  command=self.reset_config).pack(side='right', padx=5)
    
    def create_files_section(self, parent):
        """Create files list section"""
        files_frame = ttk.LabelFrame(parent, text="Archivos Encontrados", padding="10")
        files_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Info label
        self.files_info_label = ttk.Label(files_frame, text="0 archivos encontrados")
        self.files_info_label.pack(anchor='w', pady=(0, 5))
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.files_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=6)
        self.files_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.files_listbox.yview)
    
    def create_log_section(self, parent):
        """Create log section"""
        log_frame = ttk.LabelFrame(parent, text="Log de Procesamiento", padding="10")
        log_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(log_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.pack(fill='x', pady=(0, 5))
        
        # Progress label
        self.progress_label = ttk.Label(log_frame, text="Listo para comenzar")
        self.progress_label.pack(anchor='w', pady=(0, 5))
        
        # Log text
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=60)
        self.log_text.pack(fill='both', expand=True)
    
    def create_control_section(self, parent):
        """Create control buttons section"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill='x', pady=(10, 0))
        
        # Main buttons
        self.start_btn = ttk.Button(control_frame, text="Iniciar Procesamiento", 
                                   command=self.start_processing, state='disabled')
        self.start_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = ttk.Button(control_frame, text="Detener", 
                                  command=self.stop_processing, state='disabled')
        self.stop_btn.pack(side='left', padx=(0, 10))
        
        # Export button
        self.export_btn = ttk.Button(control_frame, text="Exportar Dataset", 
                                    command=self.export_dataset, state='disabled')
        self.export_btn.pack(side='left', padx=(0, 20))
        
        # Close button
        ttk.Button(control_frame, text="Cerrar", 
                  command=self.on_close).pack(side='right')
    
    # Event handlers
    def select_directory(self):
        """Select directory containing dump files"""
        directory = filedialog.askdirectory(
            title="Seleccionar directorio con archivos dump LAMMPS"
        )
        
        if directory:
            self.directory_path = Path(directory)
            self.dir_label.config(text=str(self.directory_path), foreground='black')
            self.scan_btn.config(state='normal')
            self.log_message(f"Directorio seleccionado: {self.directory_path}")
    
    def scan_directory(self):
        """Scan directory for dump files"""
        if not self.directory_path:
            messagebox.showwarning("Advertencia", "Seleccione un directorio primero")
            return
        
        try:
            patterns = ["*.dump", "*.dump.gz", "dump.*", "*.lammps", "*.trj"]
            found_files = []
            
            for pattern in patterns:
                if self.recursive_var.get():
                    found_files.extend(self.directory_path.rglob(pattern))
                else:
                    found_files.extend(self.directory_path.glob(pattern))
            
            # Remove duplicates and sort
            self.found_files = sorted(list(set(found_files)))
            
            # Update UI
            self.update_files_list()
            
            if self.found_files:
                self.start_btn.config(state='normal')
                self.log_message(f"Encontrados {len(self.found_files)} archivos dump")
            else:
                self.log_message("No se encontraron archivos dump", "WARNING")
                
        except Exception as e:
            self.log_message(f"Error al escanear directorio: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Error al escanear directorio:\n{str(e)}")
    
    def update_files_list(self):
        """Update the files listbox"""
        self.files_listbox.delete(0, tk.END)
        
        for file_path in self.found_files:
            self.files_listbox.insert(tk.END, file_path.name)
        
        # Update info
        total_size = sum(f.stat().st_size for f in self.found_files) / (1024**3)  # GB
        info_text = f"{len(self.found_files)} archivos encontrados ({total_size:.2f} GB total)"
        self.files_info_label.config(text=info_text)
    
    def start_processing(self):
        """Start processing dump files"""
        if not self.found_files:
            messagebox.showwarning("Advertencia", "No hay archivos para procesar")
            return
        
        if self.is_processing:
            messagebox.showwarning("Advertencia", "Ya hay un procesamiento en curso")
            return
        
        # Update configuration
        self.data_processor.set_lammps_config(
            atm_total=self.atm_total_var.get(),
            energy_min=self.energy_min_var.get(),
            energy_max=self.energy_max_var.get(),
            energy_bins=self.energy_bins_var.get()
        )
        
        # Update UI
        self.is_processing = True
        self.start_btn.config(state='disabled', text='Procesando...')
        self.stop_btn.config(state='normal')
        self.progress_var.set(0)
        self.log_text.delete(1.0, tk.END)
        
        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._processing_worker,
            daemon=True
        )
        self.processing_thread.start()
        
        # Start progress monitoring
        self.monitor_progress()
    
    def _processing_worker(self):
        """Worker thread for processing files"""
        try:
            self.dialog.after(0, lambda: self.log_message("Iniciando procesamiento de archivos dump LAMMPS"))
            
            # Process files
            processed_data = []
            total_files = len(self.found_files)
            
            for i, file_path in enumerate(self.found_files):
                if not self.is_processing:  # Check if stopped
                    break
                
                try:
                    # Update progress
                    progress = (i / total_files) * 100
                    self.dialog.after(0, lambda p=progress, f=file_path.name: 
                                    self._update_progress(p, f"Procesando: {f}"))
                    
                    # Parse dump file
                    df_atoms, n_atoms = self.data_processor._parse_last_frame_dump(file_path)
                    
                    # Extract features  
                    features = self.data_processor._extract_features_from_atoms(df_atoms, n_atoms)
                    features['filename'] = file_path.name
                    
                    processed_data.append(features)
                    
                    self.dialog.after(0, lambda f=file_path.name, n=n_atoms: 
                                    self.log_message(f"✓ {f}: {n} átomos procesados"))
                    
                except Exception as e:
                    error_msg = f"✗ Error en {file_path.name}: {str(e)}"
                    self.dialog.after(0, lambda msg=error_msg: self.log_message(msg, "ERROR"))
            
            # Create final dataset
            if processed_data and self.is_processing:
                import pandas as pd
                dataset = pd.DataFrame(processed_data)
                dataset.set_index('filename', inplace=True)
                
                # Store in data processor
                self.data_processor.data = dataset
                self.data_processor.original_data = dataset.copy()
                
                # Validation
                validation_result = self.data_processor.validate_lammps_dataset()
                
                success_msg = f"Procesamiento completado: {len(dataset)} archivos, {len(dataset.columns)} features"
                self.dialog.after(0, lambda: self.log_message(success_msg, "SUCCESS"))
                
                # Show warnings if any
                if validation_result.get('warnings'):
                    for warning in validation_result['warnings']:
                        self.dialog.after(0, lambda w=warning: self.log_message(f"⚠ {w}", "WARNING"))
                
                self.dialog.after(0, self._processing_complete)
            else:
                self.dialog.after(0, lambda: self.log_message("Procesamiento cancelado o sin resultados", "WARNING"))
                self.dialog.after(0, self._processing_failed)
                
        except Exception as e:
            error_msg = f"Error crítico en procesamiento: {str(e)}"
            self.dialog.after(0, lambda: self.log_message(error_msg, "ERROR"))
            self.dialog.after(0, self._processing_failed)
    
    def _update_progress(self, progress: float, message: str):
        """Update progress in UI thread"""
        self.progress_var.set(progress)
        self.progress_label.config(text=message)
    
    def _processing_complete(self):
        """Handle successful processing completion"""
        self.is_processing = False
        self.start_btn.config(state='normal', text='Iniciar Procesamiento')
        self.stop_btn.config(state='disabled')
        self.export_btn.config(state='normal')
        self.progress_var.set(100)
        self.progress_label.config(text="Procesamiento completado exitosamente")
        
        # Call completion callback
        if self.callback_on_complete and self.data_processor.data is not None:
            self.callback_on_complete(self.data_processor.data)
        
        messagebox.showinfo("Completado", "Procesamiento de archivos dump completado exitosamente")
    
    def _processing_failed(self):
        """Handle processing failure"""
        self.is_processing = False
        self.start_btn.config(state='normal', text='Iniciar Procesamiento')
        self.stop_btn.config(state='disabled')
        self.progress_label.config(text="Error en procesamiento")
        messagebox.showerror("Error", "El procesamiento falló. Revise el log para más detalles.")
    
    def monitor_progress(self):
        """Monitor processing progress"""
        if self.is_processing and self.processing_thread.is_alive():
            # Continue monitoring
            self.dialog.after(1000, self.monitor_progress)
        elif self.is_processing:
            # Thread finished
            self._processing_complete()
    
    def stop_processing(self):
        """Stop current processing"""
        if self.is_processing:
            self.is_processing = False
            self.progress_label.config(text="Deteniendo procesamiento...")
            self.log_message("Procesamiento detenido por el usuario", "WARNING")
    
    def export_dataset(self):
        """Export processed dataset"""
        if self.data_processor.data is None:
            messagebox.showwarning("Advertencia", "No hay dataset para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Exportar dataset procesado"
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    self.data_processor.data.to_excel(file_path)
                else:
                    self.data_processor.data.to_csv(file_path)
                
                # Export summary
                summary_path = Path(file_path).stem + "_summary.json"
                summary = self.data_processor.get_data_summary()
                
                with open(Path(file_path).parent / summary_path, 'w') as f:
                    json.dump(summary, f, indent=2, default=str)
                
                self.log_message(f"Dataset exportado: {file_path}")
                messagebox.showinfo("Exportado", f"Dataset exportado exitosamente:\n{file_path}")
                
            except Exception as e:
                self.log_message(f"Error al exportar: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"Error al exportar dataset:\n{str(e)}")
    
    def reset_config(self):
        """Reset configuration to defaults"""
        self.atm_total_var.set(16384)
        self.energy_min_var.set(-4.0)
        self.energy_max_var.set(-3.0)
        self.energy_bins_var.set(10)
        self.recursive_var.set(True)
        self.log_message("Configuración reseteada a valores por defecto")
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log"""
        timestamp = time.strftime('%H:%M:%S')
        
        # Color coding
        if level == "ERROR":
            tag = "error"
        elif level == "WARNING":
            tag = "warning"
        elif level == "SUCCESS":
            tag = "success"
        else:
            tag = "info"
        
        log_entry = f"[{timestamp}] {message}\n"
        
        # Configure tags if not done
        if not hasattr(self, '_tags_configured'):
            self.log_text.tag_config("error", foreground="red")
            self.log_text.tag_config("warning", foreground="orange")
            self.log_text.tag_config("success", foreground="green")
            self.log_text.tag_config("info", foreground="black")
            self._tags_configured = True
        
        self.log_text.insert(tk.END, log_entry, tag)
        self.log_text.see(tk.END)  # Auto-scroll
    
    def on_close(self):
        """Handle dialog close"""
        if self.is_processing:
            result = messagebox.askyesno(
                "Procesamiento en Curso",
                "Hay un procesamiento en curso. ¿Desea cerrarlo de todas formas?"
            )
            
            if not result:
                return
            
            self.is_processing = False
        
        self.dialog.grab_release()
        self.dialog.destroy()