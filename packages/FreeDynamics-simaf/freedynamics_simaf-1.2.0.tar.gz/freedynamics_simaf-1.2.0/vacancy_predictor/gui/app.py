#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main application for ML Pipeline with integrated visualization tabs
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys
import os

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your tabs
from vacancy_predictor.gui.tabs.data_tabs import DataTab
from vacancy_predictor.gui.tabs.training_tab import TrainingTab
from vacancy_predictor.gui.tabs.prediction_tab import PredictionTab
from vacancy_predictor.gui.tabs.visualization_tab import VisualizationTab
from vacancy_predictor.gui.tabs.feature_selector_gui import FeatureSelectorGUI

# Import processors and trainers (you'll need to implement these)
try:
    from vacancy_predictor.core.data_processor import DataProcessor
    from vacancy_predictor.core.model_trainer import ModelTrainer
    from vacancy_predictor.core.visualizer import Visualizer
except ImportError:
    # Create stubs if the modules don't exist
    class DataProcessor:
        def __init__(self):
            self.current_data = None
            self.features = None
            self.target = None
            self.target_column = None
        
        def load_data(self, file_path):
            import pandas as pd
            return pd.read_csv(file_path)
        
        def get_data_summary(self):
            return {
                'shape': (0, 0),
                'memory_usage_mb': 0,
                'numeric_columns': [],
                'categorical_columns': [],
                'missing_data_pct': {}
            }
        
        def get_column_info(self):
            return {}
        
        def select_features(self, feature_columns):
            self.features = self.current_data[feature_columns] if self.current_data is not None else None
        
        def set_target(self, target_column):
            self.target_column = target_column
            self.target = self.current_data[target_column] if self.current_data is not None else None
        
        def preprocess_data(self, handle_missing="drop", encode_categorical=True, scale_numeric=False):
            pass
        
        def prepare_features_and_target(self, data):
            return None, None

    class ModelTrainer:
        def __init__(self):
            self.model = None
            self.current_model = None
            self.features = None
            self.feature_names = []
        
        def train_model(self, X, y, algorithm="RandomForest", test_size=0.2, random_state=42):
            return {}
        
        def predict(self, X):
            return []
        
        def cross_validate(self, X, y, cv=5):
            return []
        
        def save_model(self, file_path):
            pass
        
        def load_model(self, file_path):
            pass

    class Visualizer:
        pass

class VacancyPredictorGUI:
    """Main application class for the ML Pipeline"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ML Pipeline with Visualization")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        self.visualizer = Visualizer()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_tabs()
        
        # Configure styles
        self.configure_styles()
        
        # Bind closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def configure_styles(self):
        """Configure application styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure("Action.TButton", foreground="white", background="#4CAF50")
        style.configure("Success.TButton", foreground="white", background="#2196F3")
        style.configure("Warning.TButton", foreground="white", background="#FF9800")
        style.configure("Danger.TButton", foreground="white", background="#F44336")
        
        # Configure notebook style
        style.configure("TNotebook.Tab", padding=[10, 5])
    
    def create_tabs(self):
        """Create all application tabs"""
        # Data tab
        self.data_tab = DataTab(
            self.notebook, 
            self.data_processor, 
            self.on_data_loaded
        )
        self.notebook.add(self.data_tab.frame, text="📊 Data")
        
        # Feature selector tab
        self.feature_selector_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.feature_selector_tab, text="🔍 Feature Selector")
        self.setup_feature_selector_tab()
        
        # Training tab
        self.training_tab = TrainingTab(
            self.notebook,
            self.model_trainer,
            self.data_processor
        )
        self.notebook.add(self.training_tab.frame, text="🤖 Training")
        
        # Prediction tab
        self.prediction_tab = PredictionTab(
            self.notebook,
            self.model_trainer,
            self.data_processor
        )
        self.notebook.add(self.prediction_tab.frame, text="🔮 Prediction")
        
        # Visualization tab
        self.visualization_tab = VisualizationTab(
            self.notebook,
            self.visualizer,
            self.get_visualization_data
        )
        self.notebook.add(self.visualization_tab.frame, text="📈 Visualization")
    
    def setup_feature_selector_tab(self):
        """Setup the feature selector tab"""
        # Create a container frame
        container = ttk.Frame(self.feature_selector_tab)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add label and button to launch the feature selector
        ttk.Label(
            container, 
            text="Feature Selector GUI", 
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            container, 
            text="Click the button below to open the feature selector in a separate window",
            font=("Arial", 10)
        ).pack(pady=5)
        
        ttk.Button(
            container,
            text="Open Feature Selector",
            command=self.open_feature_selector,
            style="Action.TButton"
        ).pack(pady=20)
        
        # Add some information about the feature selector
        info_text = """
        The Feature Selector allows you to:
        - Load your dataset
        - Categorize features automatically
        - Select/deselect features by category
        - Choose your target variable
        - Save filtered datasets
        - Export/import feature configurations
        """
        
        info_label = ttk.Label(
            container,
            text=info_text,
            justify="left",
            font=("Arial", 9)
        )
        info_label.pack(pady=10, padx=20, fill="x")
    
    def open_feature_selector(self):
        """Open the feature selector in a new window"""
        try:
            # Create a new top-level window
            selector_window = tk.Toplevel(self.root)
            selector_window.title("Feature Selector")
            selector_window.geometry("1200x700")
            
            # Initialize the feature selector
            feature_selector = FeatureSelectorGUI(selector_window)
            
            # Center the window
            self.center_window(selector_window)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open feature selector: {str(e)}")
    
    def center_window(self, window):
        """Center a window on the screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_data_loaded(self, data):
        """Callback when data is loaded in the data tab"""
        self.data_processor.current_data = data
        self.visualization_tab.update_data(data)
        
        # Enable other tabs if data is loaded
        self.enable_tabs()
    
    def get_visualization_data(self):
        """Get data for visualization"""
        return {
            'data': self.data_processor.current_data,
            'model': self.model_trainer.current_model,
            'processor': self.data_processor,
            'results': getattr(self.training_tab, 'training_results', None)
        }
    
    def enable_tabs(self):
        """Enable all tabs when data is loaded"""
        # This is a placeholder - you might want to implement actual tab enabling logic
        pass
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = VacancyPredictorGUI(root)
    
    # Center the main window
    app.center_window(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()