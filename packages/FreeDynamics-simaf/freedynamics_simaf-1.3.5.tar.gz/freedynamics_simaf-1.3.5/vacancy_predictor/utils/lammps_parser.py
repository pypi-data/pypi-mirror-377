#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación principal integrada - Vacancy Predictor con soporte LAMMPS
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json
import sys

# Importar módulos propios
from vacancy_predictor.core.ml_components import DataProcessor, ModelTrainer, Visualizer
from vacancy_predictor.gui.tabs.lammps_tab import LAMMPSTab

# Importar tabs originales - estos necesitarías crear/adaptar desde tu código original
from vacancy_predictor.gui.tabs.data_tabs import DataTab
from vacancy_predictor.gui.tabs.training_tab import TrainingTab
from vacancy_predictor.gui.tabs.prediction_tab import PredictionTab
from vacancy_predictor.gui.tabs.visualization_tab import VisualizationTab
from vacancy_predictor.gui.tabs.feature_selector_gui import FeatureSelectorGUI

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

class VacancyPredictorGUI:
    """Aplicación principal integrada"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacancy Predictor - ML Tool with LAMMPS Support")
        self.root.geometry("1400x900")
        
        # Componentes ML originales
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        self.visualizer = Visualizer()
        
        # Referencias a datos actuales
        self.current_data = None
        self.current_model = None
        self.current_lammps_data = None
        
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        logger.info("Vacancy Predictor GUI with LAMMPS support initialized")
    
    def setup_styles(self):
        """Configurar estilos"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Estilos personalizados
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TButton', foreground='green')
        style.configure('Action.TButton', foreground='blue')
    
    def create_menu(self):
        """Crear menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.reset_application)
        file_menu.add_separator()
        file_menu.add_command(label="Export All Data", command=self.export_all_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Menú LAMMPS
        lammps_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="LAMMPS", menu=lammps_menu)
        lammps_menu.add_command(label="Reset 3D View", command=self.reset_3d_view)
        lammps_menu.add_command(label="Top View", command=lambda: self.set_3d_view(90, 0))
        lammps_menu.add_command(label="Front View", command=lambda: self.set_3d_view(0, 0))
        lammps_menu.add_command(label="Side View", command=lambda: self.set_3d_view(0, 90))
        lammps_menu.add_separator()
        lammps_menu.add_command(label="Save 3D Plot", command=self.save_lammps_plot)
        
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

        # Tabs originales ML
        self.data_tab = DataTab(self.notebook, self.data_processor, self.on_data_loaded)
        self.notebook.add(self.data_tab.frame, text="📊 Data")
        
        self.training_tab = TrainingTab(self.notebook, self.model_trainer, self.data_processor, self.on_model_trained)
    
        self.notebook.add(self.training_tab.frame, text="🤖 Training")
        
        self.prediction_tab = PredictionTab(self.notebook, self.model_trainer, self.data_processor)
        self.notebook.add(self.prediction_tab.frame, text="🔮 Prediction")
        
        self.visualization_tab = VisualizationTab(self.notebook, self.visualizer, self.get_visualization_data)
        self.notebook.add(self.visualization_tab.frame, text="📈 Visualization")

        self.feature_selector_tab = FeatureSelectorGUI(self.notebook)
        self.notebook.add(self.feature_selector_tab.frame, text="⚙️ Feature Selector")
        
        # Nuevo tab LAMMPS
        self.lammps_tab = LAMMPSTab(self.notebook, self.on_lammps_data_loaded)
        self.notebook.add(self.lammps_tab.frame, text="⚛️ LAMMPS")

    def create_status_bar(self):
        """Crear barra de estado"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x")
        
        self.status_var = tk.StringVar(value="Ready - Load data or LAMMPS dump files")
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                               relief="sunken", anchor="w")
        status_label.pack(side="left", fill="x", expand=True)
        
        # Indicador de memoria
        self.memory_var = tk.StringVar(value="Memory: 0 MB")
        memory_label = ttk.Label(self.status_frame, textvariable=self.memory_var, 
                               relief="sunken", anchor="e")
        memory_label.pack(side="right")

    def update_status(self, message):
        """Actualizar mensaje de estado"""
        self.status_var.set(message)
        self.root.update_idletasks()

    # =============================================================================
    # CALLBACKS
    # =============================================================================
    
    def on_data_loaded(self, data):
        """Callback cuando se cargan datos ML"""
        self.current_data = data
        self.update_status(f"Data loaded: {data.shape[0]} rows, {data.shape[1]} columns")
        
        # Actualizar indicador de memoria
        if data is not None:
            memory_mb = data.memory_usage(deep=True).sum() / (1024 * 1024)
            self.memory_var.set(f"Memory: {memory_mb:.1f} MB")
        
    def on_lammps_data_loaded(self, data):
        """Callback cuando se cargan datos LAMMPS"""
        self.current_lammps_data = data
        num_atoms = len(data) if data is not None else 0
        timestep = self.lammps_tab.current_metadata.get('timestep', 'N/A') if self.lammps_tab.current_metadata else 'N/A'
        self.update_status(f"LAMMPS data loaded: {num_atoms} atoms, timestep {timestep}")
        
        # Actualizar memoria
        if data is not None:
            memory_mb = data.memory_usage(deep=True).sum() / (1024 * 1024)
            current_memory = self.memory_var.get()
            if "Memory:" in current_memory:
                try:
                    existing_mb = float(current_memory.split()[1])
                    total_mb = existing_mb + memory_mb
                    self.memory_var.set(f"Memory: {total_mb:.1f} MB")
                except:
                    self.memory_var.set(f"Memory: {memory_mb:.1f} MB")
            else:
                self.memory_var.set(f"Memory: {memory_mb:.1f} MB")
        
    def on_model_trained(self, results):
        """Callback cuando se entrena un modelo"""
        self.current_model = self.model_trainer.model
        algorithm = results.get('algorithm', 'model')
        self.update_status(f"New {algorithm} trained/loaded.")
        # Actualizar tab de predicción
        self.prediction_tab.update_model(self.current_model)
        
    def get_visualization_data(self):
        """Proporcionar datos para visualización"""
        return {
            'data': self.current_data,
            'model': self.current_model,
            'results': self.training_tab.training_results if hasattr(self, 'training_tab') else None,
            'processor': self.data_processor
        }

    # =============================================================================
    # LAMMPS METHODS
    # =============================================================================
    
    def reset_3d_view(self):
        """Resetear vista 3D de LAMMPS"""
        if hasattr(self.lammps_tab, 'visualizer') and self.lammps_tab.visualizer.ax:
            self.lammps_tab.visualizer.ax.view_init(elev=20, azim=45)
            self.lammps_tab.visualizer.canvas.draw()
    
    def set_3d_view(self, elev, azim):
        """Establecer vista 3D específica"""
        if hasattr(self.lammps_tab, 'visualizer') and self.lammps_tab.visualizer.ax:
            self.lammps_tab.visualizer.ax.view_init(elev=elev, azim=azim)
            self.lammps_tab.visualizer.canvas.draw()
    
    def save_lammps_plot(self):
        """Guardar plot 3D de LAMMPS"""
        if self.current_lammps_data is None:
            messagebox.showwarning("Warning", "No LAMMPS data to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save LAMMPS 3D Plot",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg")
            ]
        )
        
        if file_path:
            try:
                self.lammps_tab.visualizer.save_plot(file_path)
                messagebox.showinfo("Success", f"LAMMPS plot saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save plot:\n{str(e)}")

    # =============================================================================
    # EXPORT METHODS
    # =============================================================================
    
    def export_all_data(self):
        """Exportar todos los datos y análisis"""
        directory = filedialog.askdirectory(title="Select directory to export all data")
        if directory:
            try:
                export_dir = Path(directory) / "vacancy_predictor_export"
                export_dir.mkdir(exist_ok=True)
                
                exported_files = []
                
                # Exportar datos ML si existen
                if self.current_data is not None:
                    self.current_data.to_csv(export_dir / "ml_data.csv", index=False)
                    exported_files.append("ml_data.csv")
                
                # Exportar datos LAMMPS si existen
                if self.current_lammps_data is not None:
                    self.current_lammps_data.to_csv(export_dir / "lammps_atoms.csv", index=False)
                    exported_files.append("lammps_atoms.csv")
                    
                    # Exportar metadata de LAMMPS
                    if self.lammps_tab.current_metadata:
                        with open(export_dir / "lammps_metadata.json", 'w') as f:
                            json.dump(self.lammps_tab.current_metadata, f, indent=2, default=str)
                        exported_files.append("lammps_metadata.json")
                    
                    # Exportar visualización 3D
                    try:
                        self.lammps_tab.visualizer.save_plot(str(export_dir / "lammps_structure_3d.png"))
                        exported_files.append("lammps_structure_3d.png")
                    except:
                        pass
                
                # Exportar modelo entrenado si existe
                if self.current_model is not None:
                    try:
                        self.model_trainer.save_model(str(export_dir / "trained_model.pkl"))
                        exported_files.append("trained_model.pkl")
                    except:
                        pass
                
                # Crear reporte de exportación
                report_lines = [
                    "VACANCY PREDICTOR - EXPORT REPORT",
                    "=" * 40,
                    f"Export Date: {pd.Timestamp.now()}",
                    f"Export Directory: {export_dir}",
                    "",
                    "EXPORTED FILES:",
                    "-" * 20
                ]
                
                for file in exported_files:
                    report_lines.append(f"✓ {file}")
                
                if self.current_data is not None:
                    report_lines.extend([
                        "",
                        "ML DATA SUMMARY:",
                        f"  Rows: {self.current_data.shape[0]}",
                        f"  Columns: {self.current_data.shape[1]}",
                        f"  Memory: {self.current_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
                    ])
                
                if self.current_lammps_data is not None:
                    summary = self.lammps_tab.lammps_parser.get_summary()
                    report_lines.extend([
                        "",
                        "LAMMPS DATA SUMMARY:",
                        f"  Atoms: {summary.get('num_atoms', 0)}",
                        f"  Timestep: {summary.get('timestep', 'N/A')}",
                        f"  Atom Types: {summary.get('num_atom_types', 0)}"
                    ])
                
                # Guardar reporte
                with open(export_dir / "export_report.txt", 'w') as f:
                    f.write("\n".join(report_lines))
                
                message = f"Export completed!\n\nFiles exported: {len(exported_files)}\nLocation: {export_dir}"
                messagebox.showinfo("Export Complete", message)
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")

    # =============================================================================
    # OTHER METHODS
    # =============================================================================
    
    def show_about(self):
        """Mostrar información sobre la aplicación"""
        about_text = """
Vacancy Predictor v2.0 - Integrated ML & LAMMPS Tool

A comprehensive application for machine learning analysis and 
LAMMPS molecular dynamics visualization.

FEATURES:
• Machine Learning: Data processing, model training, predictions
• LAMMPS Support: 3D atomic structure visualization and analysis
• Feature Selection: Interactive feature engineering tools
• Visualization: Advanced plotting and data exploration
• Export: Complete project data export capabilities

MACHINE LEARNING CAPABILITIES:
• Multiple algorithms (Random Forest, SVM, Neural Networks, etc.)
• Feature importance analysis
• Cross-validation and model evaluation
• Batch predictions and export

LAMMPS CAPABILITIES:
• .dump file parsing and visualization
• 3D atomic structure rendering with interactive controls
• Atom type filtering and scaling
• Simulation box boundary display
• Multi-timestep support

SUPPORTED FORMATS:
• ML Data: CSV, Excel, JSON
• LAMMPS: .dump files
• Export: CSV, PNG, PDF, PKL

Developed for both machine learning research and 
molecular dynamics simulation analysis.
        """
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About Vacancy Predictor")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        
        # Hacer la ventana modal
        about_window.transient(self.root)
        about_window.grab_set()
        
        text_widget = tk.Text(about_window, wrap="word", padx=20, pady=20, 
                             font=("Arial", 10))
        text_widget.pack(fill="both", expand=True)
        text_widget.insert(1.0, about_text)
        text_widget.config(state="disabled")
        
        # Botón para cerrar
        button_frame = ttk.Frame(about_window)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Close", 
                  command=about_window.destroy).pack()
    
    def reset_application(self):
        """Resetear aplicación completa"""
        if messagebox.askyesno("New Project", 
                              "This will clear all current data and models. Continue?"):
            # Reset componentes
            self.current_data = None
            self.current_model = None
            self.current_lammps_data = None
            self.data_processor = DataProcessor()
            self.model_trainer = ModelTrainer()
            
            # Reset todos los tabs
            self.data_tab.reset()
            self.training_tab.reset()
            self.prediction_tab.reset()
            self.visualization_tab.reset()
            self.lammps_tab.reset()
            
            self.update_status("New project created - Ready for data")
            self.memory_var.set("Memory: 0 MB")
    
    def on_closing(self):
        """Callback al cerrar aplicación"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            self.root.destroy()
            
    def run(self):
        """Ejecutar la aplicación"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

def main():
    """Función principal"""
    try:
        app = VacancyPredictorGUI()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        messagebox.showerror("Application Error", f"A critical error occurred: {e}")


if __name__ == "__main__":
    main()