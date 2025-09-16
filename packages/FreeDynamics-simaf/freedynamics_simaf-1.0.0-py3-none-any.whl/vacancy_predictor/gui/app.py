"""
Main GUI application for Vacancy Predictor
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from vacancy_predictor.gui.tabs.data_tabs import DataTab

from ..core.data_processor import DataProcessor
from ..core.model_trainer import ModelTrainer
from ..core.visualizer import Visualizer

from .tabs.training_tab import TrainingTab
from .tabs.prediction_tab import PredictionTab
from .tabs.visualization_tab import VisualizationTab

logger = logging.getLogger(__name__)

class VacancyPredictorGUI:
    """
    Main GUI application class
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacancy Predictor - ML Tool")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Initialize core components
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        self.visualizer = Visualizer()
        
        # Application state
        self.current_data = None
        self.current_model = None
        self.project_path = None
        
        # Setup GUI
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        # Configure logging
        self.setup_logging()
        
        logger.info("Vacancy Predictor GUI initialized")
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        
        # Configure notebook style
        style.configure('Custom.TNotebook', tabposition='n')
        style.configure('Custom.TNotebook.Tab', padding=[20, 10])
        
        # Configure button styles
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        style.configure('Success.TButton', font=('Arial', 10, 'bold'))
        
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_command(label="Export Model", command=self.export_model)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Data Validator", command=self.open_data_validator)
        tools_menu.add_command(label="Model Comparison", command=self.open_model_comparison)
        tools_menu.add_separator()
        tools_menu.add_command(label="Settings", command=self.open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.open_documentation)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Create the main interface with tabs"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame, style='Custom.TNotebook')
        self.notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Create tabs
        self.create_tabs()
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_tabs(self):
        """Create all application tabs"""
        
        # Data tab
        self.data_tab = DataTab(
            self.notebook, 
            self.data_processor, 
            self.on_data_loaded
        )
        self.notebook.add(self.data_tab.frame, text="📊 Data")
        
        # Training tab
        self.training_tab = TrainingTab(
            self.notebook,
            self.model_trainer,
            self.get_training_data,
            self.on_model_trained
        )
        self.notebook.add(self.training_tab.frame, text="🤖 Training")
        
        # Prediction tab
        self.prediction_tab = PredictionTab(
            self.notebook,
            self.model_trainer,
            self.data_processor
        )
        self.notebook.add(self.prediction_tab.frame, text="🎯 Prediction")
        
        # Visualization tab
        self.visualization_tab = VisualizationTab(
            self.notebook,
            self.visualizer,
            self.get_visualization_data
        )
        self.notebook.add(self.visualization_tab.frame, text="📈 Visualization")
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(
            self.status_frame, 
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.status_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(side="right", padx=(10, 0))
    
    def setup_logging(self):
        """Setup logging configuration"""
        # Create a custom handler for GUI
        class GUILogHandler(logging.Handler):
            def __init__(self, status_callback):
                super().__init__()
                self.status_callback = status_callback
                
            def emit(self, record):
                msg = self.format(record)
                self.status_callback(msg)
        
        # Add GUI handler to logger
        gui_handler = GUILogHandler(self.update_status)
        gui_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        gui_handler.setFormatter(formatter)
        
        logger.addHandler(gui_handler)
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_progress(self, show: bool = True):
        """Show/hide progress bar"""
        if show:
            self.progress.start(10)
        else:
            self.progress.stop()
    
    # Event handlers
    def on_data_loaded(self, data):
        """Called when data is loaded"""
        self.current_data = data
        self.training_tab.update_data_info(data)
        self.visualization_tab.update_data(data)
        self.update_status(f"Data loaded: {data.shape[0]} rows, {data.shape[1]} columns")
    
    def on_model_trained(self, model, results):
        """Called when model is trained"""
        self.current_model = model
        self.prediction_tab.update_model(model)
        self.visualization_tab.update_model_results(results)
        self.update_status(f"Model trained: {results['algorithm']} - Score: {results['test_score']:.3f}")
    
    def get_training_data(self):
        """Get data for training"""
        if self.data_processor.features is None or self.data_processor.target is None:
            return None
        return self.data_processor.get_training_data()
    
    def get_visualization_data(self):
        """Get data for visualization"""
        return {
            'data': self.current_data,
            'processor': self.data_processor,
            'model': self.current_model
        }
    
    def on_tab_changed(self, event):
        """Handle tab change"""
        selection = event.widget.selection()
        tab_name = event.widget.tab(selection, "text")
        self.update_status(f"Switched to {tab_name} tab")
    
    # Menu handlers
    def new_project(self):
        """Create new project"""
        result = messagebox.askyesnocancel(
            "New Project",
            "Create a new project? Unsaved changes will be lost."
        )
        if result:
            self.reset_application()
            self.update_status("New project created")
    
    def open_project(self):
        """Open existing project"""
        file_path = filedialog.askopenfilename(
            title="Open Project",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Load project data
                import joblib
                project_data = joblib.load(file_path)
                
                # Restore application state
                if 'data' in project_data:
                    self.data_processor.data = project_data['data']
                    self.current_data = project_data['data']
                    self.data_tab.update_data_display(self.current_data)
                
                if 'model' in project_data:
                    self.current_model = project_data['model']
                    self.prediction_tab.update_model(self.current_model)
                
                self.project_path = file_path
                self.update_status(f"Project loaded: {Path(file_path).name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load project: {str(e)}")
    
    def save_project(self):
        """Save current project"""
        if not self.project_path:
            file_path = filedialog.asksaveasfilename(
                title="Save Project",
                defaultextension=".pkl",
                filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
            )
            if file_path:
                self.project_path = file_path
        
        if self.project_path:
            try:
                project_data = {
                    'data': self.current_data,
                    'model': self.current_model,
                    'processor_state': {
                        'features': self.data_processor.features,
                        'target': self.data_processor.target,
                        'target_column': self.data_processor.target_column
                    }
                }
                
                import joblib
                joblib.dump(project_data, self.project_path)
                self.update_status(f"Project saved: {Path(self.project_path).name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save project: {str(e)}")
    
    def export_data(self):
        """Export current data"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.current_data.to_csv(file_path, index=False)
                elif file_path.endswith('.xlsx'):
                    self.current_data.to_excel(file_path, index=False)
                
                self.update_status(f"Data exported: {Path(file_path).name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def export_model(self):
        """Export current model"""
        if self.current_model is None:
            messagebox.showwarning("Warning", "No model to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Model",
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("Joblib files", "*.joblib"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.model_trainer.save_model(file_path)
                self.update_status(f"Model exported: {Path(file_path).name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export model: {str(e)}")
    
    def open_data_validator(self):
        """Open data validation dialog"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
        
        # Create validation window
        #from dialogs.validation_dialog import ValidationDialog
        #dialog = ValidationDialog(self.root, self.current_data)
        #dialog.show()
    
    def open_model_comparison(self):
        """Open model comparison dialog"""
        if self.get_training_data() is None:
            messagebox.showwarning("Warning", "No training data available")
            return
        
        # Create comparison window
        from dialogs.comparison_dialog import ComparisonDialog
        dialog = ComparisonDialog(self.root, self.get_training_data(), self.model_trainer)
        dialog.show()
    
    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog not implemented yet")
    
    def open_documentation(self):
        """Open documentation"""
        import webbrowser
        webbrowser.open("https://vacancy-predictor.readthedocs.io")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Vacancy Predictor v1.0.0

A comprehensive machine learning tool for vacancy prediction 
with an intuitive GUI interface.

Features:
• Multiple ML algorithms
• Data visualization
• Model comparison
• Export capabilities

Developed with Python, scikit-learn, and tkinter.
        """
        messagebox.showinfo("About Vacancy Predictor", about_text.strip())
    
    def reset_application(self):
        """Reset application to initial state"""
        self.current_data = None
        self.current_model = None
        self.project_path = None
        
        # Reset processors
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        
        # Reset tabs
        self.data_tab.reset()
        self.training_tab.reset()
        self.prediction_tab.reset()
        self.visualization_tab.reset()
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Main entry point for GUI application"""
    app = VacancyPredictorGUI()
    app.run()

if __name__ == "__main__":
    main()