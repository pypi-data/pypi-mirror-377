"""
Training tab for model training and evaluation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from typing import Callable, Optional, Dict, Any
import threading
import logging

logger = logging.getLogger(__name__)

class TrainingTab:
    """
    Tab for model training, hyperparameter tuning, and evaluation
    """
    
    def __init__(self, parent, model_trainer, get_training_data_callback: Callable, 
                 model_trained_callback: Callable):
        self.parent = parent
        self.model_trainer = model_trainer
        self.get_training_data_callback = get_training_data_callback
        self.model_trained_callback = model_trained_callback
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Variables
        self.algorithm_var = tk.StringVar(value="random_forest")
        self.test_size_var = tk.DoubleVar(value=0.2)
        self.cv_folds_var = tk.IntVar(value=5)
        self.hyperparameter_tuning_var = tk.BooleanVar(value=False)
        self.random_state_var = tk.IntVar(value=42)
        
        # Data info
        self.data_info_text = None
        self.training_results_text = None
        
        # Current training data
        self.current_training_data = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the training tab"""
        
        # Main container with padding
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Data status section
        self.create_data_status_section(main_container)
        
        # Algorithm selection section
        self.create_algorithm_section(main_container)
        
        # Training parameters section
        self.create_parameters_section(main_container)
        
        # Training controls section
        self.create_controls_section(main_container)
        
        # Results section
        self.create_results_section(main_container)
    
    def create_data_status_section(self, parent):
        """Create data status display section"""
        status_frame = ttk.LabelFrame(parent, text="Training Data Status", padding="10")
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.data_info_text = tk.Text(status_frame, height=4, wrap="word", state="disabled")
        self.data_info_text.pack(fill="x")
        
        # Update initial status
        self.update_data_info(None)
    
    def create_algorithm_section(self, parent):
        """Create algorithm selection section"""
        algo_frame = ttk.LabelFrame(parent, text="Algorithm Selection", padding="10")
        algo_frame.pack(fill="x", pady=(0, 10))
        
        # Algorithm selection
        ttk.Label(algo_frame, text="Choose Algorithm:").pack(anchor="w")
        
        # Create algorithm options in columns
        algo_container = ttk.Frame(algo_frame)
        algo_container.pack(fill="x", pady=(5, 0))
        
        # Left column - Regression algorithms
        left_frame = ttk.LabelFrame(algo_container, text="Regression", padding="5")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        regression_algos = [
            ("Linear Regression", "linear_regression"),
            ("Ridge Regression", "ridge"),
            ("Lasso Regression", "lasso"),
            ("Random Forest", "random_forest"),
            ("Gradient Boosting", "gradient_boosting"),
            ("Decision Tree", "decision_tree"),
            ("Support Vector Regression", "svr")
        ]
        
        for text, value in regression_algos:
            ttk.Radiobutton(left_frame, text=text, variable=self.algorithm_var, 
                           value=value).pack(anchor="w")
        
        # Right column - Classification algorithms
        right_frame = ttk.LabelFrame(algo_container, text="Classification", padding="5")
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        classification_algos = [
            ("Logistic Regression", "logistic_regression"),
            ("Random Forest Classifier", "random_forest"),
            ("Gradient Boosting Classifier", "gradient_boosting"),
            ("Decision Tree Classifier", "decision_tree"),
            ("Support Vector Classifier", "svc"),
            ("Naive Bayes", "naive_bayes")
        ]
        
        for text, value in classification_algos:
            ttk.Radiobutton(right_frame, text=text, variable=self.algorithm_var, 
                           value=value).pack(anchor="w")
    
    def create_parameters_section(self, parent):
        """Create training parameters section"""
        params_frame = ttk.LabelFrame(parent, text="Training Parameters", padding="10")
        params_frame.pack(fill="x", pady=(0, 10))
        
        # Parameters in grid layout
        params_grid = ttk.Frame(params_frame)
        params_grid.pack(fill="x")
        
        # Test size
        ttk.Label(params_grid, text="Test Size:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        test_size_scale = ttk.Scale(params_grid, from_=0.1, to=0.5, variable=self.test_size_var,
                                   orient="horizontal", length=200)
        test_size_scale.grid(row=0, column=1, sticky="w", padx=(0, 10))
        
        self.test_size_label = ttk.Label(params_grid, text="0.20")
        self.test_size_label.grid(row=0, column=2, sticky="w")
        
        # CV folds
        ttk.Label(params_grid, text="CV Folds:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        cv_spinbox = ttk.Spinbox(params_grid, from_=3, to=10, width=10, 
                                textvariable=self.cv_folds_var)
        cv_spinbox.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(10, 0))
        
        # Random state
        ttk.Label(params_grid, text="Random State:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        random_state_entry = ttk.Entry(params_grid, width=10, textvariable=self.random_state_var)
        random_state_entry.grid(row=2, column=1, sticky="w", padx=(0, 10), pady=(10, 0))
        
        # Hyperparameter tuning
        ttk.Checkbutton(params_frame, text="Enable Hyperparameter Tuning (slower but better results)",
                       variable=self.hyperparameter_tuning_var).pack(anchor="w", pady=(15, 0))
        
        # Bind scale update
        test_size_scale.bind("<Motion>", self.update_test_size_label)
        test_size_scale.bind("<ButtonRelease-1>", self.update_test_size_label)
    
    def create_controls_section(self, parent):
        """Create training control buttons"""
        controls_frame = ttk.LabelFrame(parent, text="Training Controls", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        button_frame = ttk.Frame(controls_frame)
        button_frame.pack(fill="x")
        
        # Training buttons
        self.train_button = ttk.Button(button_frame, text="Train Model", 
                                      command=self.train_single_model,
                                      style="Action.TButton")
        self.train_button.pack(side="left", padx=(0, 10))
        
        self.compare_button = ttk.Button(button_frame, text="Compare Algorithms", 
                                        command=self.compare_algorithms)
        self.compare_button.pack(side="left", padx=(0, 10))
        
        # Model management buttons
        ttk.Button(button_frame, text="Save Model", 
                  command=self.save_model).pack(side="right", padx=(10, 0))
        
        ttk.Button(button_frame, text="Load Model", 
                  command=self.load_model).pack(side="right")
        
        # Progress bar
        self.progress_frame = ttk.Frame(controls_frame)
        self.progress_frame.pack(fill="x", pady=(10, 0))
        
        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill="x", pady=(5, 0))
    
    def create_results_section(self, parent):
        """Create training results display section"""
        results_frame = ttk.LabelFrame(parent, text="Training Results", padding="10")
        results_frame.pack(fill="both", expand=True)
        
        # Create notebook for different result views
        results_notebook = ttk.Notebook(results_frame)
        results_notebook.pack(fill="both", expand=True)
        
        # Results text tab
        results_text_frame = ttk.Frame(results_notebook)
        results_notebook.add(results_text_frame, text="Results")
        
        self.training_results_text = tk.Text(results_text_frame, wrap="word", state="disabled")
        results_scrollbar = ttk.Scrollbar(results_text_frame, command=self.training_results_text.yview)
        self.training_results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.training_results_text.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Training history tab
        history_frame = ttk.Frame(results_notebook)
        results_notebook.add(history_frame, text="Training History")
        
        # Create treeview for training history
        history_columns = ("Timestamp", "Algorithm", "Test Score", "CV Score", "Features")
        self.history_tree = ttk.Treeview(history_frame, columns=history_columns, show="headings", height=6)
        
        for col in history_columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120, anchor="center")
        
        history_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        history_scrollbar.pack(side="right", fill="y")
        
        # Initialize results display
        self.update_results_display("No training results yet")
    
    def update_test_size_label(self, event=None):
        """Update test size label"""
        value = self.test_size_var.get()
        self.test_size_label.config(text=f"{value:.2f}")
    
    def update_data_info(self, data):
        """Update data information display"""
        if data is None:
            info_text = "No training data available.\nPlease load data and select features/target in the Data tab."
        else:
            training_data = self.get_training_data_callback()
            if training_data is None:
                info_text = "Data loaded but features/target not selected.\nPlease select features and target in the Data tab."
            else:
                features, target = training_data
                info_text = f"Training data ready!\n" \
                           f"Features: {features.shape[1]} columns, {features.shape[0]} samples\n" \
                           f"Target: '{target.name}' - Type: {target.dtype}\n" \
                           f"Target unique values: {target.nunique()}"
        
        self.data_info_text.config(state="normal")
        self.data_info_text.delete(1.0, tk.END)
        self.data_info_text.insert(1.0, info_text)
        self.data_info_text.config(state="disabled")
    
    def train_single_model(self):
        """Train a single model with selected algorithm"""
        training_data = self.get_training_data_callback()
        if training_data is None:
            messagebox.showwarning("Warning", "No training data available. Please prepare data first.")
            return
        
        # Disable buttons and show progress
        self.set_training_state(True)
        
        # Parameters
        params = {
            'algorithm': self.algorithm_var.get(),
            'test_size': self.test_size_var.get(),
            'cv_folds': self.cv_folds_var.get(),
            'random_state': self.random_state_var.get(),
            'hyperparameter_tuning': self.hyperparameter_tuning_var.get()
        }
        
        # Run training in separate thread
        def train_model():
            try:
                self.update_progress("Training model...")
                
                results = self.model_trainer.train(training_data, **params)
                
                # Update UI in main thread
                self.frame.after(0, lambda: self.on_training_complete(results, None))
                
            except Exception as e:
                self.frame.after(0, lambda: self.on_training_complete(None, str(e)))
        
        threading.Thread(target=train_model, daemon=True).start()
    
    def compare_algorithms(self):
        """Compare multiple algorithms"""
        training_data = self.get_training_data_callback()
        if training_data is None:
            messagebox.showwarning("Warning", "No training data available. Please prepare data first.")
            return
        
        # Get algorithm list based on problem type
        target = training_data[1]
        if target.dtype == 'object' or target.nunique() <= 10:
            algorithms = ['logistic_regression', 'random_forest', 'gradient_boosting', 
                         'decision_tree', 'svc', 'naive_bayes']
            problem_type = "classification"
        else:
            algorithms = ['linear_regression', 'ridge', 'lasso', 'random_forest', 
                         'gradient_boosting', 'decision_tree', 'svr']
            problem_type = "regression"
        
        # Disable buttons and show progress
        self.set_training_state(True)
        
        def compare_models():
            try:
                self.update_progress(f"Comparing {len(algorithms)} {problem_type} algorithms...")
                
                params = {
                    'test_size': self.test_size_var.get(),
                    'cv_folds': self.cv_folds_var.get(),
                    'random_state': self.random_state_var.get()
                }
                
                comparison_df = self.model_trainer.compare_algorithms(
                    training_data, algorithms, **params
                )
                
                # Update UI in main thread
                self.frame.after(0, lambda: self.on_comparison_complete(comparison_df, None))
                
            except Exception as e:
                self.frame.after(0, lambda: self.on_comparison_complete(None, str(e)))
        
        threading.Thread(target=compare_models, daemon=True).start()
    
    def on_training_complete(self, results, error):
        """Handle training completion"""
        self.set_training_state(False)
        
        if error:
            messagebox.showerror("Training Error", f"Training failed:\n{error}")
            self.update_results_display(f"Training failed: {error}")
            return
        
        # Update results display
        self.display_training_results(results)
        
        # Update training history
        self.update_training_history()
        
        # Notify parent about trained model
        self.model_trained_callback(self.model_trainer.model, results)
        
        messagebox.showinfo("Success", f"Model trained successfully!\n"
                           f"Algorithm: {results['algorithm']}\n"
                           f"Test Score: {results['test_score']:.4f}")
    
    def on_comparison_complete(self, comparison_df, error):
        """Handle algorithm comparison completion"""
        self.set_training_state(False)
        
        if error:
            messagebox.showerror("Comparison Error", f"Algorithm comparison failed:\n{error}")
            return
        
        # Display comparison results
        self.display_comparison_results(comparison_df)
        
        # Update training history
        self.update_training_history()
        
        # Show comparison window
        self.show_comparison_window(comparison_df)
    
    def display_training_results(self, results):
        """Display training results in text widget"""
        result_lines = [
            f"Training Results - {results['algorithm'].title()}",
            "=" * 50,
            "",
            f"Algorithm: {results['algorithm']}",
            f"Model Type: {results['model_type']}",
            f"Features Used: {results['feature_count']}",
            f"Training Samples: {results['train_samples']}",
            f"Test Samples: {results['test_samples']}",
            "",
            "Performance Metrics:",
            "-" * 20
        ]
        
        if results['model_type'] == 'regression':
            result_lines.extend([
                f"Train R² Score: {results['train_score']:.4f}",
                f"Test R² Score: {results['test_score']:.4f}",
                f"Train RMSE: {results['train_rmse']:.4f}",
                f"Test RMSE: {results['test_rmse']:.4f}",
                f"Train MAE: {results['train_mae']:.4f}",
                f"Test MAE: {results['test_mae']:.4f}"
            ])
        else:
            result_lines.extend([
                f"Train Accuracy: {results['train_score']:.4f}",
                f"Test Accuracy: {results['test_score']:.4f}",
                f"Precision: {results['precision']:.4f}",
                f"Recall: {results['recall']:.4f}",
                f"F1-Score: {results['f1_score']:.4f}"
            ])
        
        result_lines.extend([
            "",
            "Cross-Validation:",
            f"CV Score: {results['cv_score_mean']:.4f} ± {results['cv_score_std']:.4f}"
        ])
        
        # Add feature importance if available
        if 'feature_importance' in results:
            result_lines.extend([
                "",
                "Top 10 Feature Importance:",
                "-" * 30
            ])
            for i, feat in enumerate(results['feature_importance'][:10]):
                result_lines.append(f"{i+1:2d}. {feat['feature']:<20} {feat['importance']:.4f}")
        
        result_text = "\n".join(result_lines)
        self.update_results_display(result_text)
    
    def display_comparison_results(self, comparison_df):
        """Display algorithm comparison results"""
        result_lines = [
            "Algorithm Comparison Results",
            "=" * 40,
            "",
            f"Compared {len(comparison_df)} algorithms",
            f"Best Algorithm: {comparison_df.iloc[0]['algorithm']}",
            f"Best Score: {comparison_df.iloc[0]['test_score']:.4f}",
            "",
            "Results Summary:",
            "-" * 20
        ]
        
        for _, row in comparison_df.iterrows():
            result_lines.append(
                f"{row['algorithm']:<20} Score: {row['test_score']:.4f} "
                f"(CV: {row['cv_score_mean']:.4f} ± {row['cv_score_std']:.4f})"
            )
        
        result_text = "\n".join(result_lines)
        self.update_results_display(result_text)
    
    def show_comparison_window(self, comparison_df):
        """Show detailed comparison window"""
        comparison_window = tk.Toplevel(self.frame)
        comparison_window.title("Algorithm Comparison Results")
        comparison_window.geometry("800x600")
        
        # Create treeview for detailed results
        frame = ttk.Frame(comparison_window, padding="10")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Algorithm Comparison Results", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Treeview
        columns = ("Algorithm", "Test Score", "Train Score", "CV Mean", "CV Std", "Features")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        # Add data
        for _, row in comparison_df.iterrows():
            tree.insert("", "end", values=(
                row['algorithm'],
                f"{row['test_score']:.4f}",
                f"{row['train_score']:.4f}",
                f"{row['cv_score_mean']:.4f}",
                f"{row['cv_score_std']:.4f}",
                row['feature_count']
            ))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Button to use best model
        button_frame = ttk.Frame(comparison_window, padding="10")
        button_frame.pack(fill="x")
        
        def use_best_model():
            best_algorithm = comparison_df.iloc[0]['algorithm']
            self.algorithm_var.set(best_algorithm)
            comparison_window.destroy()
            
            if messagebox.askyesno("Train Best Model", 
                                  f"Train {best_algorithm} model with current parameters?"):
                self.train_single_model()
        
        ttk.Button(button_frame, text="Use Best Algorithm", 
                  command=use_best_model, style="Success.TButton").pack(side="left")
        
        ttk.Button(button_frame, text="Close", 
                  command=comparison_window.destroy).pack(side="right")
    
    def update_training_history(self):
        """Update training history display"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Get training history
        history_df = self.model_trainer.get_training_summary()
        
        if history_df.empty:
            return
        
        # Add history items (most recent first)
        for _, row in history_df.sort_values('timestamp', ascending=False).iterrows():
            self.history_tree.insert("", "end", values=(
                row['timestamp'].strftime("%Y-%m-%d %H:%M"),
                row['algorithm'],
                f"{row['test_score']:.4f}",
                f"{row['cv_score_mean']:.4f}",
                row['feature_count']
            ))
    
    def save_model(self):
        """Save trained model"""
        if self.model_trainer.model is None:
            messagebox.showwarning("Warning", "No model trained yet")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Model",
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("Joblib files", "*.joblib"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.model_trainer.save_model(file_path)
                messagebox.showinfo("Success", f"Model saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save model:\n{str(e)}")
    
    def load_model(self):
        """Load a trained model"""
        file_path = filedialog.askopenfilename(
            title="Load Model",
            filetypes=[("Pickle files", "*.pkl"), ("Joblib files", "*.joblib"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.model_trainer.load_model(file_path)
                messagebox.showinfo("Success", f"Model loaded from:\n{file_path}")
                
                # Update results display
                self.update_results_display("Model loaded successfully")
                
                # Notify parent
                self.model_trained_callback(self.model_trainer.model, {"algorithm": "loaded"})
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model:\n{str(e)}")
    
    def set_training_state(self, training: bool):
        """Enable/disable training controls"""
        state = "disabled" if training else "normal"
        
        self.train_button.config(state=state)
        self.compare_button.config(state=state)
        
        if training:
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()
            self.progress_label.config(text="")
    
    def update_progress(self, message: str):
        """Update progress message"""
        def update():
            self.progress_label.config(text=message)
        
        self.frame.after(0, update)
    
    def update_results_display(self, text: str):
        """Update training results display"""
        self.training_results_text.config(state="normal")
        self.training_results_text.delete(1.0, tk.END)
        self.training_results_text.insert(1.0, text)
        self.training_results_text.config(state="disabled")
    
    def reset(self):
        """Reset the tab to initial state"""
        # Reset variables to defaults
        self.algorithm_var.set("random_forest")
        self.test_size_var.set(0.2)
        self.cv_folds_var.set(5)
        self.hyperparameter_tuning_var.set(False)
        self.random_state_var.set(42)
        
        # Clear displays
        self.update_results_display("No training results yet")
        self.update_data_info(None)
        
        # Clear training history
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Update test size label
        self.update_test_size_label()
        
        # Reset progress
        self.set_training_state(False)