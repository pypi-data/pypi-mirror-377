#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación simplificada - Vacancy Predictor ML Suite
Versión mínima funcional sin dependencias innecesarias
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
import sys

# Importar solo los tabs esenciales que existen
from .tabs.batch_processor_tab import BatchProcessingTab
from .tabs.advanced_ml_tab import AdvancedMLTabWithPlots

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

class VacancyPredictorApp:
    """Aplicación principal simplificada"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacancy Predictor - ML Suite v3.0")
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
        
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        logger.info("Vacancy Predictor ML Suite initialized")
    
    def setup_styles(self):
        """Configurar estilos básicos"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), foreground='navy')
    
    def create_menu(self):
        """Crear menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Dataset", command=self.import_dataset)
        file_menu.add_command(label="Export Dataset", command=self.export_dataset)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Menú Tools
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Data Statistics", command=self.show_data_statistics)
        tools_menu.add_command(label="Clear All Data", command=self.clear_all_data)
        
        # Menú Help
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Crear interfaz principal con tabs"""
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # 1. TAB DE PROCESAMIENTO BATCH
        try:
            self.batch_tab = BatchProcessingTab(self.notebook, self.on_batch_data_loaded)
            self.notebook.add(self.batch_tab.frame, text="Batch Processing")
        except Exception as e:
            logger.error(f"Error creating batch tab: {e}")
            self.create_error_tab("Batch Processing Error", str(e))
        
        # 2. TAB DE ADVANCED ML
        try:
            self.advanced_ml_tab = AdvancedMLTabWithPlots(self.notebook, self.on_advanced_data_loaded)
            self.notebook.add(self.advanced_ml_tab.frame, text="Advanced ML")
        except Exception as e:
            logger.error(f"Error creating ML tab: {e}")
            self.create_error_tab("ML Tab Error", str(e))
        
        # Bind eventos
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_error_tab(self, tab_name, error_message):
        """Crear tab de error cuando falla la importación"""
        error_frame = ttk.Frame(self.notebook)
        self.notebook.add(error_frame, text=tab_name)
        
        error_label = ttk.Label(error_frame, 
                               text=f"Error loading {tab_name}:\n{error_message}",
                               foreground="red", 
                               font=('Arial', 10))
        error_label.pack(expand=True)
    
    def create_status_bar(self):
        """Crear barra de estado"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x")
        
        # Mensaje principal
        self.status_var = tk.StringVar(value="Vacancy Predictor Ready")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                               relief="sunken", anchor="w")
        status_label.pack(side="left", fill="x", expand=True)
        
        # Indicador de datasets
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
        
        # Contar datasets
        for data in [self.current_data, self.current_batch_dataset, self.current_advanced_data]:
            if data is not None:
                datasets += 1
        
        self.datasets_var.set(f"Datasets: {datasets}")
    
    # =============================================================================
    # CALLBACKS DE DATOS
    # =============================================================================
    
    def on_batch_data_loaded(self, data):
        """Callback cuando se cargan datos del procesamiento batch"""
        self.current_batch_dataset = data
        self.current_data = data
        
        self.update_status(f"Batch dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()
        
        # Intentar cargar en Advanced ML si está disponible
        try:
            if hasattr(self.advanced_ml_tab, 'load_dataset_from_dataframe'):
                self.advanced_ml_tab.load_dataset_from_dataframe(data)
                self.update_status("Dataset automatically loaded into Advanced ML tab")
        except Exception as e:
            logger.warning(f"Could not sync batch data to Advanced ML: {e}")
    
    def on_advanced_data_loaded(self, data):
        """Callback para datos del Advanced ML tab"""
        self.current_advanced_data = data
        self.current_data = data
        
        self.update_status(f"Advanced ML dataset loaded: {len(data)} samples, {len(data.columns)} features")
        self.update_indicators()
        
    def on_tab_changed(self, event):
        """Callback cuando cambia el tab activo"""
        try:
            selected_tab = event.widget.tab('current')['text']
            self.update_status(f"Active tab: {selected_tab}")
            self.update_indicators()
        except:
            pass

    # =============================================================================
    # MÉTODOS DE DATOS
    # =============================================================================
    
    def import_dataset(self):
        """Importar dataset desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Import Dataset",
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
                    data = pd.read_csv(file_path, index_col=0)
                
                # Cargar en Advanced ML
                self.on_advanced_data_loaded(data)
                
                # Cambiar al tab Advanced ML
                self.notebook.select(1)
                
                messagebox.showinfo("Success", 
                                   f"Dataset imported successfully:\n{file_path}\n\n"
                                   f"Rows: {len(data)}\nColumns: {len(data.columns)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error importing dataset:\n{str(e)}")
    
    def export_dataset(self):
        """Exportar dataset actual"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No dataset to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Dataset",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    self.current_data.to_excel(file_path, index=False)
                else:
                    self.current_data.to_csv(file_path, index=False)
                
                messagebox.showinfo("Success", f"Dataset exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exporting:\n{str(e)}")

    # =============================================================================
    # MÉTODOS DE INFORMACIÓN
    # =============================================================================
    
    def show_data_statistics(self):
        """Mostrar estadísticas de datos"""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Data Statistics")
        stats_window.geometry("600x400")
        stats_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(stats_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        stats_text = "DATA STATISTICS\n" + "="*30 + "\n\n"
        
        datasets = [
            ("Batch Processing", self.current_batch_dataset),
            ("Advanced ML", self.current_advanced_data)
        ]
        
        for name, data in datasets:
            if data is not None:
                stats_text += f"{name}:\n"
                stats_text += f"  Rows: {len(data)}\n"
                stats_text += f"  Columns: {len(data.columns)}\n"
                stats_text += f"  Memory: {data.memory_usage(deep=True).sum() / (1024*1024):.2f} MB\n"
                stats_text += "-"*30 + "\n\n"
            else:
                stats_text += f"{name}: No data loaded\n\n"
        
        text_widget.insert(1.0, stats_text)
        text_widget.config(state="disabled")
        
        ttk.Button(stats_window, text="Close", 
                  command=stats_window.destroy).pack(pady=10)
    
    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """Vacancy Predictor ML Suite v3.0 (Simplified)
========================================

Machine learning tool for vacancy prediction with simplified architecture.

FEATURES:
• Batch processing of LAMMPS dump files
• Advanced ML training and visualization
• Feature extraction and model training
• Clean, simplified codebase

SUPPORTED FORMATS:
• Input: .dump, .csv, .xlsx files
• Output: CSV, XLSX, JOBLIB models

Version: 3.0.0 - Simplified Architecture
Developed for stable ML workflows
"""
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About Vacancy Predictor")
        about_window.geometry("500x400")
        about_window.transient(self.root)
        
        text_widget = scrolledtext.ScrolledText(about_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        text_widget.insert(1.0, about_text)
        text_widget.config(state="disabled")
        
        ttk.Button(about_window, text="Close", 
                  command=about_window.destroy).pack(pady=10)
    
    def clear_all_data(self):
        """Limpiar todos los datos"""
        if messagebox.askyesno("Confirm", "Clear all loaded data?"):
            self.current_data = None
            self.current_batch_dataset = None
            self.current_advanced_data = None
            
            # Reset tabs si es posible
            try:
                if hasattr(self.batch_tab, 'reset'):
                    self.batch_tab.reset()
            except:
                pass
                
            try:
                if hasattr(self.advanced_ml_tab, 'reset'):
                    self.advanced_ml_tab.reset()
            except:
                pass
            
            self.update_status("All data cleared")
            self.update_indicators()
    
    def on_closing(self):
        """Callback al cerrar aplicación"""
        if messagebox.askokcancel("Quit", "Do you want to quit Vacancy Predictor?"):
            try:
                logger.info("Application closing")
                self.root.destroy()
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
                self.root.destroy()
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            # Configurar atajos de teclado básicos
            self.root.bind('<Control-i>', lambda e: self.import_dataset())
            self.root.bind('<Control-e>', lambda e: self.export_dataset())
            self.root.bind('<Control-q>', lambda e: self.on_closing())
            self.root.bind('<F1>', lambda e: self.show_about())
            
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            messagebox.showerror("Critical Error", f"Application error: {e}")


def main():
    """Función principal"""
    try:
        logger.info("Starting Vacancy Predictor ML Suite v3.0")
        
        app = VacancyPredictorApp()
        app.run()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        try:
            messagebox.showerror("Application Error", 
                                f"Critical error during startup:\n\n{e}")
        except:
            print(f"CRITICAL ERROR: {e}")


if __name__ == "__main__":
    main()