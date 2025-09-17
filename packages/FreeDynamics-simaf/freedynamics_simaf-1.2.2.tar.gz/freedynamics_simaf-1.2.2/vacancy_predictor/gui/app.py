#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main GUI application for Vacancy Predictor
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import seaborn as sns
from typing import Optional, Dict, Any, Callable, List, Set

# =============================================================================
# 1. SETUP & CORE COMPONENTS
# =============================================================================

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('vacancy_predictor.log')
    ]
)
logger = logging.getLogger(__name__)

# Create simple placeholder classes if full imports fail
class DataProcessor:
    def __init__(self):
        self.current_data = None
        self.target_column = None
        self.features = None
        self.target = None

    def load_data(self, file_path):
        file_path = Path(file_path)
        if file_path.suffix == '.csv':
            self.current_data = pd.read_csv(file_path)
        elif file_path.suffix in ['.xlsx', '.xls']:
            self.current_data = pd.read_excel(file_path)
        elif file_path.suffix == '.json':
            self.current_data = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        return self.current_data

    def get_data_summary(self):
        if self.current_data is None: return {}
        return {
            'shape': self.current_data.shape,
            'memory_usage_mb': self.current_data.memory_usage(deep=True).sum() / 1024**2,
            'numeric_columns': self.current_data.select_dtypes(include=np.number).columns.tolist(),
            'categorical_columns': self.current_data.select_dtypes(include=['object']).columns.tolist(),
            'missing_data_pct': (self.current_data.isnull().sum() / len(self.current_data) * 100).to_dict()
        }
    
    def get_column_info(self):
        if self.current_data is None: return {}
        return self.current_data.dtypes.to_dict()

    def select_features(self, feature_columns):
        self.features = self.current_data[feature_columns]

    def set_target(self, target_column):
        self.target_column = target_column
        self.target = self.current_data[target_column]

    def prepare_features_and_target(self, data):
        if self.features is None or self.target is None:
            raise ValueError("Features and target not set.")
        X = self.features
        y = self.target
        # A simple cleaning step
        X = X.select_dtypes(include=np.number).fillna(0)
        return X, y

class ModelTrainer:
    def __init__(self):
        self.model = None

    def train_model(self, X, y, algorithm="RandomForest", test_size=0.2, random_state=42):
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.svm import SVC
        from sklearn.linear_model import LogisticRegression
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

        models = {
            "RandomForest": RandomForestClassifier(random_state=random_state),
            "GradientBoosting": GradientBoostingClassifier(random_state=random_state),
            "SVM": SVC(probability=True, random_state=random_state),
            "LogisticRegression": LogisticRegression(random_state=random_state),
            "KNeighbors": KNeighborsClassifier(),
            "DecisionTree": DecisionTreeClassifier(random_state=random_state)
        }
        self.model = models.get(algorithm, RandomForestClassifier(random_state=random_state))

        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        
        feature_importances = {}
        if hasattr(self.model, 'feature_importances_'):
            feature_importances = [{'feature': f, 'importance': i} for f, i in zip(X.columns, self.model.feature_importances_)]
            feature_importances = sorted(feature_importances, key=lambda x: x['importance'], reverse=True)


        return {
            'accuracy': accuracy_score(y_test, predictions),
            'precision': precision_score(y_test, predictions, average='weighted'),
            'recall': recall_score(y_test, predictions, average='weighted'),
            'f1_score': f1_score(y_test, predictions, average='weighted'),
            'classification_report': classification_report(y_test, predictions),
            'feature_importance': feature_importances,
            'model_type': 'classification', # Assume classification for now
            'algorithm': algorithm,
        }

    def predict(self, X):
        if self.model:
            # Ensure columns match training data
            if hasattr(self.model, 'feature_names_in_'):
                model_cols = self.model.feature_names_in_
                X = X.reindex(columns=model_cols, fill_value=0)
            return self.model.predict(X)
        return None

    def cross_validate(self, X, y, cv=5):
        from sklearn.model_selection import cross_val_score
        if self.model:
            return cross_val_score(self.model, X, y, cv=cv)
        return []

    def save_model(self, file_path):
        import pickle
        with open(file_path, 'wb') as f:
            pickle.dump(self.model, f)

    def load_model(self, file_path):
        import pickle
        with open(file_path, 'rb') as f:
            self.model = pickle.load(f)

class Visualizer:
    def __init__(self):
        pass
        
class ComparisonDialog:
    def __init__(self, parent, training_data, model_trainer):
        self.parent = parent
        self.training_data = training_data
        self.model_trainer = model_trainer
    
    def show(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Model Comparison")
        dialog.geometry("600x400")
        
        label = tk.Label(dialog, text="Model Comparison Dialog\n(Feature under development)")
        label.pack(pady=20)
        
        close_button = tk.Button(dialog, text="Close", command=dialog.destroy)
        close_button.pack(pady=10)
        
        dialog.transient(self.parent)
        dialog.grab_set()

# =============================================================================
# 2. GUI TAB CLASSES
# =============================================================================

class DataTab:
    """
    Tab for data loading, exploration and preprocessing
    """
    
    def __init__(self, parent, data_processor, data_loaded_callback: Callable):
        self.parent = parent
        self.data_processor = data_processor
        self.data_loaded_callback = data_loaded_callback
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Variables
        self.file_path_var = tk.StringVar()
        self.data_info_var = tk.StringVar()
        self.data_info_var.set("No data loaded")
        
        # Current data reference
        self.current_data = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the data tab"""
        
        # Main container with padding
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # File loading section
        self.create_file_section(main_container)
        
        # Data information section
        self.create_info_section(main_container)
        
        # Data preview section
        self.create_preview_section(main_container)
        
        # Column selection section
        self.create_column_section(main_container)
    
    def create_file_section(self, parent):
        """Create file loading section"""
        file_frame = ttk.LabelFrame(parent, text="Load Data File", padding="10")
        file_frame.pack(fill="x", pady=(0, 10))
        
        # File path frame
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(path_frame, text="File:").pack(side="left")
        
        file_entry = ttk.Entry(path_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        ttk.Button(path_frame, text="Browse", command=self.browse_file).pack(side="right")
        
        # File info and actions
        action_frame = ttk.Frame(file_frame)
        action_frame.pack(fill="x")
        
        ttk.Button(action_frame, text="Load Data", 
                  command=self.load_data).pack(side="left")
    
    def create_info_section(self, parent):
        """Create data information section"""
        info_frame = ttk.LabelFrame(parent, text="Data Information", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Data info display
        info_text = tk.Text(info_frame, height=6, wrap="word", state="disabled")
        info_text.pack(fill="x")
        
        self.info_text = info_text
        
        # Action buttons
        button_frame = ttk.Frame(info_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Refresh Info", 
                  command=self.refresh_data_info).pack(side="left")
        
        ttk.Button(button_frame, text="Export to CSV", 
                  command=self.export_to_csv).pack(side="right")
    
    def create_preview_section(self, parent):
        """Create data preview section"""
        preview_frame = ttk.LabelFrame(parent, text="Data Preview", padding="10")
        preview_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create treeview for data preview
        self.tree = ttk.Treeview(preview_frame, show="headings", height=8)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack everything
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
    
    def create_column_section(self, parent):
        """Create column selection section"""
        column_frame = ttk.LabelFrame(parent, text="Feature & Target Selection", padding="10")
        column_frame.pack(fill="x")
        
        left_frame = ttk.Frame(column_frame)
        left_frame.pack(side="left", fill="both", expand=True)
        
        right_frame = ttk.Frame(column_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(20, 0))
        
        ttk.Label(left_frame, text="Select Features:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        features_frame = ttk.Frame(left_frame)
        features_frame.pack(fill="both", expand=True, pady=(5, 0))
        
        self.features_listbox = tk.Listbox(features_frame, selectmode="multiple", height=6)
        features_scroll = ttk.Scrollbar(features_frame, orient="vertical")
        
        self.features_listbox.configure(yscrollcommand=features_scroll.set)
        features_scroll.configure(command=self.features_listbox.yview)
        
        self.features_listbox.pack(side="left", fill="both", expand=True)
        features_scroll.pack(side="right", fill="y")
        
        features_btn_frame = ttk.Frame(left_frame)
        features_btn_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Button(features_btn_frame, text="Select All", command=self.select_all_features).pack(side="left")
        ttk.Button(features_btn_frame, text="Clear All", command=self.clear_all_features).pack(side="left", padx=(5, 0))
        
        ttk.Label(right_frame, text="Select Target:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(right_frame, textvariable=self.target_var, state="readonly", width=25)
        self.target_combo.pack(anchor="w", pady=(5, 10))
        
        action_btn_frame = ttk.Frame(right_frame)
        action_btn_frame.pack(anchor="w")
        
        ttk.Button(action_btn_frame, text="Set Features & Target", command=self.set_features_target).pack(anchor="w")

    def browse_file(self):
        file_types = [("All supported", "*.csv *.xlsx *.xls *.json"), ("All files", "*.*")]
        file_path = filedialog.askopenfilename(title="Select data file", filetypes=file_types)
        if file_path:
            self.file_path_var.set(file_path)
    
    def load_data(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("Warning", "Please select a file first")
            return
        try:
            self.current_data = self.data_processor.load_data(file_path)
            self.update_data_display(self.current_data)
            self.update_column_lists(self.current_data)
            self.refresh_data_info()
            self.data_loaded_callback(self.current_data)
            messagebox.showinfo("Success", f"Data loaded successfully!\nShape: {self.current_data.shape}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")
            logger.error(f"Error loading data: {str(e)}")

    def update_data_display(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if data is None or data.empty: return

        columns = list(data.columns)
        self.tree["columns"] = columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")

        max_rows = min(100, len(data))
        for i in range(max_rows):
            self.tree.insert("", "end", values=list(data.iloc[i]))

    def update_column_lists(self, data):
        if data is None: return
        columns = list(data.columns)
        self.features_listbox.delete(0, tk.END)
        for col in columns:
            self.features_listbox.insert(tk.END, col)
        self.target_combo["values"] = columns
        if columns:
            self.target_combo.set(columns[-1])

    def refresh_data_info(self):
        if self.current_data is None:
            info_text = "No data loaded"
        else:
            summary = self.data_processor.get_data_summary()
            info_lines = [
                f"Shape: {summary['shape'][0]} rows × {summary['shape'][1]} columns",
                f"Memory: {summary['memory_usage_mb']:.2f} MB",
                f"Numeric Cols: {len(summary['numeric_columns'])}",
                f"Categorical Cols: {len(summary['categorical_columns'])}",
            ]
            info_text = "\n".join(info_lines)
        
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state="disabled")
    
    def export_to_csv(self):
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data to export")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.current_data.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export:\n{str(e)}")

    def select_all_features(self):
        self.features_listbox.selection_set(0, tk.END)
    
    def clear_all_features(self):
        self.features_listbox.selection_clear(0, tk.END)

    def set_features_target(self):
        if self.current_data is None: return
        selected_indices = self.features_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one feature")
            return
        
        feature_columns = [self.features_listbox.get(i) for i in selected_indices]
        target_column = self.target_var.get()
        if not target_column:
            messagebox.showwarning("Warning", "Please select a target column")
            return

        try:
            self.data_processor.select_features(feature_columns)
            self.data_processor.set_target(target_column)
            messagebox.showinfo("Success", "Features and target set successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set features and target:\n{str(e)}")

    def reset(self):
        self.file_path_var.set("")
        self.current_data = None
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.features_listbox.delete(0, tk.END)
        self.target_combo.set("")
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "No data loaded")
        self.info_text.config(state="disabled")

class TrainingTab:
    """
    Tab for model training and evaluation
    """
    
    def __init__(self, parent, model_trainer, data_processor, model_trained_callback: Callable):
        self.parent = parent
        self.model_trainer = model_trainer
        self.data_processor = data_processor
        self.model_trained_callback = model_trained_callback

        self.frame = ttk.Frame(parent)
        
        self.algorithm_var = tk.StringVar(value="RandomForest")
        self.test_size_var = tk.DoubleVar(value=0.2)
        self.random_state_var = tk.IntVar(value=42)
        self.cv_folds_var = tk.IntVar(value=5)
        
        self.training_results = None
        self.current_model = None
        
        self.create_widgets()
    
    def create_widgets(self):
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        self.create_model_selection_section(left_panel)
        self.create_training_parameters_section(left_panel)
        self.create_training_controls_section(left_panel)
        self.create_results_section(right_panel)
    
    def create_model_selection_section(self, parent):
        model_frame = ttk.LabelFrame(parent, text="Model Selection", padding="10")
        model_frame.pack(fill="x", pady=(0, 10))
        algorithms = ["RandomForest", "GradientBoosting", "SVM", "LogisticRegression", "KNeighbors", "DecisionTree"]
        for algorithm in algorithms:
            ttk.Radiobutton(model_frame, text=algorithm, variable=self.algorithm_var, value=algorithm).pack(anchor="w", pady=2)
    
    def create_training_parameters_section(self, parent):
        params_frame = ttk.LabelFrame(parent, text="Training Parameters", padding="10")
        params_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(params_frame, text="Test Size:").grid(row=0, column=0, sticky='w')
        ttk.Spinbox(params_frame, from_=0.1, to=0.5, increment=0.05, textvariable=self.test_size_var, width=8).grid(row=0, column=1, sticky='e')
        
        ttk.Label(params_frame, text="Random State:").grid(row=1, column=0, sticky='w')
        ttk.Spinbox(params_frame, from_=0, to=1000, textvariable=self.random_state_var, width=8).grid(row=1, column=1, sticky='e')

        ttk.Label(params_frame, text="CV Folds:").grid(row=2, column=0, sticky='w')
        ttk.Spinbox(params_frame, from_=3, to=10, textvariable=self.cv_folds_var, width=8).grid(row=2, column=1, sticky='e')

    def create_training_controls_section(self, parent):
        controls_frame = ttk.LabelFrame(parent, text="Training Controls", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        self.train_btn = ttk.Button(controls_frame, text="Train Model", command=self.train_model)
        self.train_btn.pack(fill="x", pady=2)
        
        self.save_btn = ttk.Button(controls_frame, text="Save Model", command=self.save_model, state="disabled")
        self.save_btn.pack(fill="x", pady=2)
        
        load_btn = ttk.Button(controls_frame, text="Load Model", command=self.load_model)
        load_btn.pack(fill="x", pady=2)
    
    def create_results_section(self, parent):
        results_frame = ttk.LabelFrame(parent, text="Training Results", padding="10")
        results_frame.pack(fill="both", expand=True)
        
        self.metrics_text = tk.Text(results_frame, wrap="word", state="disabled", height=10)
        self.metrics_text.pack(fill="both", expand=True)

    def train_model(self):
        try:
            if self.data_processor.current_data is None:
                messagebox.showwarning("Warning", "No training data available.")
                return
            
            algorithm = self.algorithm_var.get()
            test_size = self.test_size_var.get()
            random_state = self.random_state_var.get()
            
            X, y = self.data_processor.prepare_features_and_target(self.data_processor.current_data)
            
            results = self.model_trainer.train_model(X, y, algorithm=algorithm, test_size=test_size, random_state=random_state)
            
            self.training_results = results
            self.current_model = self.model_trainer.model
            
            self.display_training_results()
            self.save_btn.config(state="normal")
            
            # Notify main app
            self.model_trained_callback(results)

        except Exception as e:
            messagebox.showerror("Error", f"Training failed: {str(e)}")

    def save_model(self):
        if self.current_model is None:
            messagebox.showwarning("Warning", "No trained model to save")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pkl", filetypes=[("Pickle files", "*.pkl")])
        if file_path:
            self.model_trainer.save_model(file_path)
            messagebox.showinfo("Success", f"Model saved to {file_path}")

    def load_model(self):
        file_path = filedialog.askopenfilename(filetypes=[("Pickle files", "*.pkl")])
        if file_path:
            self.model_trainer.load_model(file_path)
            self.current_model = self.model_trainer.model
            self.save_btn.config(state="normal")
            # Notify main app of the loaded model
            self.model_trained_callback({'algorithm': 'Loaded Model'})
            messagebox.showinfo("Success", f"Model loaded from {file_path}")

    def display_training_results(self):
        if self.training_results is None: return
        self.metrics_text.config(state="normal")
        self.metrics_text.delete(1.0, "end")
        
        results_text = f"TRAINING RESULTS ({self.training_results.get('algorithm', '')})\n"
        results_text += "=" * 50 + "\n\n"
        if 'accuracy' in self.training_results:
            results_text += f"Accuracy: {self.training_results['accuracy']:.4f}\n"
        if 'classification_report' in self.training_results:
            results_text += f"\nClassification Report:\n{self.training_results['classification_report']}"
        
        self.metrics_text.insert("end", results_text)
        self.metrics_text.config(state="disabled")

    def reset(self):
        self.training_results = None
        self.current_model = None
        self.algorithm_var.set("RandomForest")
        self.test_size_var.set(0.2)
        self.metrics_text.config(state="normal")
        self.metrics_text.delete(1.0, "end")
        self.metrics_text.config(state="disabled")
        self.save_btn.config(state="disabled")

class PredictionTab:
    """
    Tab for making predictions with trained models
    """
    
    def __init__(self, parent, model_trainer, data_processor):
        self.parent = parent
        self.model_trainer = model_trainer
        self.data_processor = data_processor
        
        self.frame = ttk.Frame(parent)
        self.prediction_file_var = tk.StringVar()
        self.prediction_data = None
        self.predictions = None
        
        self.create_widgets()
    
    def create_widgets(self):
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        self.create_model_status_section(main_container)
        self.create_batch_prediction_section(main_container)
        self.create_results_section(main_container)
    
    def create_model_status_section(self, parent):
        status_frame = ttk.LabelFrame(parent, text="Model Status", padding="10")
        status_frame.pack(fill="x", pady=(0, 10))
        self.model_status_label = ttk.Label(status_frame, text="No model loaded.")
        self.model_status_label.pack()

    def create_batch_prediction_section(self, parent):
        batch_frame = ttk.LabelFrame(parent, text="Batch Prediction", padding="10")
        batch_frame.pack(fill="x", pady=(0, 10))
        
        file_frame = ttk.Frame(batch_frame)
        file_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(file_frame, text="Data file:").pack(side="left")
        ttk.Entry(file_frame, textvariable=self.prediction_file_var, state="readonly").pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_prediction_file).pack(side="right")
        
        self.predict_batch_button = ttk.Button(batch_frame, text="Make Predictions", command=self.make_batch_predictions, state="disabled")
        self.predict_batch_button.pack(side="left")
        ttk.Button(batch_frame, text="Export Predictions", command=self.export_batch_predictions).pack(side="right")

    def create_results_section(self, parent):
        results_frame = ttk.LabelFrame(parent, text="Prediction Results", padding="10")
        results_frame.pack(fill="both", expand=True)
        self.results_text = tk.Text(results_frame, wrap="word", state="disabled")
        self.results_text.pack(side="left", fill="both", expand=True)
        
    def update_model(self, model):
        """Called by the main app when a model is trained or loaded."""
        if self.model_trainer.model:
            self.model_status_label.config(text="Model is loaded and ready for predictions.")
            self.predict_batch_button.config(state="normal")
        else:
            self.model_status_label.config(text="No model loaded.")
            self.predict_batch_button.config(state="disabled")

    def browse_prediction_file(self):
        file_path = filedialog.askopenfilename(title="Select prediction data file", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.prediction_file_var.set(file_path)
            self.load_prediction_file(file_path)

    def load_prediction_file(self, file_path):
        try:
            self.prediction_data = pd.read_csv(file_path)
            messagebox.showinfo("Success", f"Loaded {len(self.prediction_data)} rows for prediction.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load prediction file:\n{str(e)}")

    def make_batch_predictions(self):
        if self.model_trainer.model is None or self.prediction_data is None:
            messagebox.showwarning("Warning", "Model or prediction data not available.")
            return
        try:
            # Ensure only numeric columns are used for prediction if they were for training
            numeric_features = self.prediction_data.select_dtypes(include=np.number)
            self.predictions = self.model_trainer.predict(numeric_features)
            
            results_df = self.prediction_data.copy()
            results_df['Prediction'] = self.predictions
            
            self.display_batch_results(results_df)
            messagebox.showinfo("Success", "Predictions completed!")
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed:\n{str(e)}")

    def display_batch_results(self, results_df):
        preview = results_df.head(20).to_string()
        self.update_results_display(f"Prediction Results (Preview):\n\n{preview}")

    def export_batch_predictions(self):
        if self.predictions is None:
            messagebox.showwarning("Warning", "No predictions to export")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            results_df = self.prediction_data.copy()
            results_df['Prediction'] = self.predictions
            results_df.to_csv(file_path, index=False)
            messagebox.showinfo("Success", f"Predictions exported to:\n{file_path}")

    def update_results_display(self, text: str):
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        self.results_text.config(state="disabled")

    def reset(self):
        self.prediction_file_var.set("")
        self.prediction_data = None
        self.predictions = None
        self.update_results_display("No predictions made yet.")
        self.update_model(None)
        
class VisualizationTab:
    """
    Tab for creating various visualizations of data and model results
    """
    
    def __init__(self, parent, visualizer, get_visualization_data_callback: Callable):
        self.parent = parent
        self.visualizer = visualizer
        self.get_visualization_data_callback = get_visualization_data_callback
        
        self.frame = ttk.Frame(parent)
        self.chart_type_var = tk.StringVar(value="data_overview")
        
        self.current_data = None
        self.current_results = None
        
        plt.style.use('default')
        sns.set_palette("husl")
        
        self.create_widgets()
    
    def create_widgets(self):
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        self.create_controls_section(main_container)
        self.create_visualization_section(main_container)
    
    def create_controls_section(self, parent):
        controls_frame = ttk.LabelFrame(parent, text="Visualization Controls", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        options_frame = ttk.Frame(controls_frame)
        options_frame.pack(fill="x", pady=(5, 0))
        
        data_frame = ttk.LabelFrame(options_frame, text="Data Exploration", padding="5")
        data_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        data_charts = [("Data Overview", "data_overview"), ("Target Distribution", "target_distribution"), ("Feature Correlation", "feature_correlation")]
        for text, value in data_charts:
            ttk.Radiobutton(data_frame, text=text, variable=self.chart_type_var, value=value).pack(anchor="w")
        
        model_frame = ttk.LabelFrame(options_frame, text="Model Evaluation", padding="5")
        model_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        model_charts = [("Feature Importance", "feature_importance")]
        for text, value in model_charts:
            ttk.Radiobutton(model_frame, text=text, variable=self.chart_type_var, value=value).pack(anchor="w")

        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill="x", pady=(10,0))
        ttk.Button(button_frame, text="Generate Visualization", command=self.generate_visualization).pack(side="left")
        ttk.Button(button_frame, text="Save Chart", command=self.save_chart).pack(side="left", padx=10)

    def create_visualization_section(self, parent):
        viz_frame = ttk.LabelFrame(parent, text="Visualization", padding="10")
        viz_frame.pack(fill="both", expand=True)
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, viz_frame)
        self.toolbar.update()
        self.show_initial_message()
    
    def show_initial_message(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'Select a chart type and click "Generate Visualization"', ha='center', va='center', fontsize=12)
        ax.set_axis_off()
        self.canvas.draw()
    
    def generate_visualization(self):
        chart_type = self.chart_type_var.get()
        viz_data = self.get_visualization_data_callback()
        
        self.current_data = viz_data.get('data')
        self.current_results = viz_data.get('results')
        data_processor = viz_data.get('processor')

        if self.current_data is None and "data" in chart_type:
            messagebox.showwarning("Warning", "No data available for visualization")
            return
            
        if self.current_results is None and "feature_importance" in chart_type:
             messagebox.showwarning("Warning", "No model results available for visualization")
             return

        try:
            self.fig.clear()
            if chart_type == "data_overview":
                self.create_data_overview()
            elif chart_type == "target_distribution":
                self.create_target_distribution(data_processor)
            elif chart_type == "feature_correlation":
                self.create_feature_correlation()
            elif chart_type == "feature_importance":
                self.create_feature_importance_chart()
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate visualization:\n{str(e)}")

    def create_data_overview(self):
        ax = self.fig.add_subplot(111)
        self.current_data.info(buf=sys.stdout) # Simple overview for now
        sns.heatmap(self.current_data.select_dtypes(include=np.number).corr(), ax=ax, annot=False, cmap='coolwarm')
        ax.set_title('Data Overview - Correlation Heatmap')
        self.fig.tight_layout()

    def create_target_distribution(self, data_processor):
        if data_processor is None or data_processor.target is None:
            messagebox.showwarning("Warning", "Target variable not set.")
            return
        ax = self.fig.add_subplot(111)
        sns.countplot(x=data_processor.target, ax=ax)
        ax.set_title(f'Distribution of Target: {data_processor.target_column}')
        self.fig.tight_layout()

    def create_feature_correlation(self):
        ax = self.fig.add_subplot(111)
        numeric_data = self.current_data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) < 2:
            ax.text(0.5, 0.5, 'Not enough numeric columns for correlation matrix.', ha='center')
            return
        corr_matrix = numeric_data.corr()
        sns.heatmap(corr_matrix, ax=ax, annot=True, cmap='coolwarm', fmt=".2f")
        ax.set_title('Feature Correlation Matrix')
        self.fig.tight_layout()

    def create_feature_importance_chart(self):
        if 'feature_importance' not in self.current_results or not self.current_results['feature_importance']:
            messagebox.showwarning("Warning", "Feature importance data not available for this model.")
            return
        
        feature_importance = self.current_results['feature_importance']
        top_features = feature_importance[:15]
        
        features = [item['feature'] for item in top_features]
        importances = [item['importance'] for item in top_features]
        
        ax = self.fig.add_subplot(111)
        ax.barh(features, importances, color='skyblue')
        ax.set_xlabel('Importance')
        ax.set_title('Top 15 Feature Importances')
        ax.invert_yaxis()
        self.fig.tight_layout()

    def save_chart(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.fig.savefig(file_path, dpi=300)
            messagebox.showinfo("Success", f"Chart saved to:\n{file_path}")
            
    def reset(self):
        self.show_initial_message()

class FeatureSelectorTab:
    """
    Integrated version of the FeatureSelectorGUI to work as a tab.
    """
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent) # Main frame for the tab content
        
        # Variables
        self.dataset_path = None
        self.df = None
        self.selected_features = set()
        self.feature_vars = {}
        self.target_column = None
        
        # Crear interfaz
        self.create_widgets()
        
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.frame, padding="10")
        main_frame.pack(fill="both", expand=True)

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Seccion superior: Carga de archivo
        load_frame = ttk.LabelFrame(main_frame, text="Cargar Dataset", padding="10")
        load_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        ttk.Button(load_frame, text="Seleccionar archivo CSV", command=self.load_dataset).grid(row=0, column=0, padx=5)
        self.file_label = ttk.Label(load_frame, text="No se ha cargado ningún archivo")
        self.file_label.grid(row=0, column=1, padx=10)
        
        # Seccion central: Lista de features
        feature_frame = ttk.LabelFrame(main_frame, text="Features disponibles", padding="10")
        feature_frame.grid(row=1, column=1, sticky="nsew", padx=5)
        feature_frame.columnconfigure(0, weight=1)
        feature_frame.rowconfigure(0, weight=1)
        
        canvas = tk.Canvas(feature_frame, bg='white')
        scrollbar = ttk.Scrollbar(feature_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Seccion derecha: Estadisticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas", padding="10")
        stats_frame.grid(row=1, column=2, sticky="nsew", padx=(5, 0))
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(1, weight=1)
        
        self.stats_text = tk.Text(stats_frame, width=40, height=15, wrap=tk.WORD)
        self.stats_text.grid(row=1, column=0, pady=10, sticky="nsew")

        # Seccion inferior: Acciones
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        self.counter_label = ttk.Label(action_frame, text="Features seleccionadas: 0/0")
        self.counter_label.pack(side="left", padx=10)
        
        ttk.Button(action_frame, text="Guardar dataset filtrado", command=self.save_filtered_dataset).pack(side="left", padx=5)
        
    def load_dataset(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            try:
                self.df = pd.read_csv(filename)
                self.dataset_path = filename
                self.file_label.config(text=Path(filename).name)
                self.display_features()
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo:\n{str(e)}")
    
    def display_features(self):
        if self.df is None: return
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.feature_vars = {}
        self.selected_features = set()
        
        features = list(self.df.columns)
        num_cols = 3 
        
        for i, feat in enumerate(features):
            var = tk.BooleanVar(value=True)
            self.feature_vars[feat] = var
            self.selected_features.add(feat)
            
            cb = ttk.Checkbutton(self.scrollable_frame, text=feat, variable=var, command=self.update_selection)
            cb.grid(row=i // num_cols, column=i % num_cols, sticky=tk.W, padx=5, pady=2)
        
        self.update_selection()
    
    def update_selection(self):
        self.selected_features = {feat for feat, var in self.feature_vars.items() if var.get()}
        total = len(self.feature_vars)
        selected = len(self.selected_features)
        self.counter_label.config(text=f"Features seleccionadas: {selected}/{total}")
        self.update_statistics()

    def update_statistics(self):
        self.stats_text.config(state="normal")
        self.stats_text.delete(1.0, tk.END)
        if self.df is None or not self.selected_features:
            self.stats_text.insert(tk.END, "No hay features seleccionadas")
        else:
            stats_df = self.df[list(self.selected_features)]
            self.stats_text.insert(tk.END, str(stats_df.describe()))
        self.stats_text.config(state="disabled")

    def save_filtered_dataset(self):
        if self.df is None or not self.selected_features: return
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            filtered_df = self.df[list(self.selected_features)]
            filtered_df.to_csv(filename, index=False)
            messagebox.showinfo("Éxito", f"Dataset guardado con {len(self.selected_features)} columnas")

# =============================================================================
# 3. MAIN APPLICATION CLASS
# =============================================================================

class VacancyPredictorGUI:
    """
    Main GUI application class
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vacancy Predictor - ML Tool")
        self.root.geometry("1200x800")
        
        self.data_processor = DataProcessor()
        self.model_trainer = ModelTrainer()
        self.visualizer = Visualizer()
        
        self.current_data = None
        self.current_model = None
        
        self.setup_styles()
        self.create_menu()
        self.create_main_interface()
        self.create_status_bar()
        
        logger.info("Vacancy Predictor GUI initialized")
    
    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.reset_application)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
    
    def create_main_interface(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)

        # Instantiate and add tabs
        # Note the use of callbacks to link tabs together via the main app
        self.data_tab = DataTab(self.notebook, self.data_processor, self.on_data_loaded)
        self.notebook.add(self.data_tab.frame, text="📊 Data")
        
        self.training_tab = TrainingTab(self.notebook, self.model_trainer, self.data_processor, self.on_model_trained)
        self.notebook.add(self.training_tab.frame, text="🤖 Training")
        
        self.prediction_tab = PredictionTab(self.notebook, self.model_trainer, self.data_processor)
        self.notebook.add(self.prediction_tab.frame, text="🔮 Prediction")
        
        self.visualization_tab = VisualizationTab(self.notebook, self.visualizer, self.get_visualization_data)
        self.notebook.add(self.visualization_tab.frame, text="📈 Visualization")

        self.feature_selector_tab = FeatureSelectorTab(self.notebook)
        self.notebook.add(self.feature_selector_tab.frame, text="⚙️ Feature Selector")

    def create_status_bar(self):
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.status_frame, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x")

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    # --- Callback Methods ---
    def on_data_loaded(self, data):
        """Callback function for when data is loaded in the DataTab."""
        self.current_data = data
        self.update_status(f"Data loaded: {data.shape[0]} rows, {data.shape[1]} columns")
        # You can add logic here to notify other tabs if necessary
        
    def on_model_trained(self, results):
        """Callback function for when a model is trained in TrainingTab."""
        self.current_model = self.model_trainer.model
        algorithm = results.get('algorithm', 'model')
        self.update_status(f"New {algorithm} trained/loaded.")
        # Update the prediction tab with the new model
        self.prediction_tab.update_model(self.current_model)
        
    def get_visualization_data(self) -> Dict:
        """Callback to provide all necessary data to the VisualizationTab."""
        return {
            'data': self.current_data,
            'model': self.current_model,
            'results': self.training_tab.training_results if hasattr(self, 'training_tab') else None,
            'processor': self.data_processor
        }

    # --- Other Methods ---
    def reset_application(self):
        if messagebox.askyesno("New Project", "This will clear all current data. Continue?"):
            self.current_data = None
            self.current_model = None
            self.data_processor = DataProcessor()
            self.model_trainer = ModelTrainer()
            
            # Reset tabs
            self.data_tab.reset()
            self.training_tab.reset()
            self.prediction_tab.reset()
            self.visualization_tab.reset()
            self.update_status("New project created")
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

# =============================================================================
# 4. SCRIPT EXECUTION
# =============================================================================

def main():
    try:
        app = VacancyPredictorGUI()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        messagebox.showerror("Application Error", f"A critical error occurred: {e}")

if __name__ == "__main__":
    main()