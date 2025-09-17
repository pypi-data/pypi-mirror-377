"""
Training tab for model training and evaluation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

logger = logging.getLogger(__name__)

class TrainingTab:
    """
    Tab for model training and evaluation
    """
    
    def __init__(self, parent, model_trainer, data_processor):
        self.parent = parent
        self.model_trainer = model_trainer
        self.data_processor = data_processor
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Variables
        self.algorithm_var = tk.StringVar(value="RandomForest")
        self.test_size_var = tk.DoubleVar(value=0.2)
        self.random_state_var = tk.IntVar(value=42)
        self.cv_folds_var = tk.IntVar(value=5)
        
        # Training state
        self.training_results = None
        self.current_model = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the training tab"""
        
        # Main container with padding
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Left panel for controls
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        
        # Right panel for results
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Create sections
        self.create_model_selection_section(left_panel)
        self.create_training_parameters_section(left_panel)
        self.create_training_controls_section(left_panel)
        self.create_results_section(right_panel)
    
    def create_model_selection_section(self, parent):
        """Create model selection section"""
        model_frame = ttk.LabelFrame(parent, text="Model Selection", padding="10")
        model_frame.pack(fill="x", pady=(0, 10))
        
        algorithms = [
            "RandomForest",
            "GradientBoosting", 
            "SVM",
            "LogisticRegression",
            "KNeighbors",
            "DecisionTree"
        ]
        
        for algorithm in algorithms:
            radio = ttk.Radiobutton(
                model_frame,
                text=algorithm,
                variable=self.algorithm_var,
                value=algorithm
            )
            radio.pack(anchor="w", pady=2)
    
    def create_training_parameters_section(self, parent):
        """Create training parameters section"""
        params_frame = ttk.LabelFrame(parent, text="Training Parameters", padding="10")
        params_frame.pack(fill="x", pady=(0, 10))
        
        # Test size
        test_frame = ttk.Frame(params_frame)
        test_frame.pack(fill="x", pady=2)
        ttk.Label(test_frame, text="Test Size:").pack(side="left")
        test_spin = ttk.Spinbox(
            test_frame,
            from_=0.1,
            to=0.5,
            increment=0.05,
            textvariable=self.test_size_var,
            width=10
        )
        test_spin.pack(side="right")
        
        # Random state
        random_frame = ttk.Frame(params_frame)
        random_frame.pack(fill="x", pady=2)
        ttk.Label(random_frame, text="Random State:").pack(side="left")
        random_spin = ttk.Spinbox(
            random_frame,
            from_=0,
            to=1000,
            textvariable=self.random_state_var,
            width=10
        )
        random_spin.pack(side="right")
        
        # CV folds
        cv_frame = ttk.Frame(params_frame)
        cv_frame.pack(fill="x", pady=2)
        ttk.Label(cv_frame, text="CV Folds:").pack(side="left")
        cv_spin = ttk.Spinbox(
            cv_frame,
            from_=3,
            to=10,
            textvariable=self.cv_folds_var,
            width=10
        )
        cv_spin.pack(side="right")
    
    def create_training_controls_section(self, parent):
        """Create training controls section"""
        controls_frame = ttk.LabelFrame(parent, text="Training Controls", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Train button
        self.train_btn = ttk.Button(
            controls_frame,
            text="Train Model",
            command=self.train_model
        )
        self.train_btn.pack(fill="x", pady=2)
        
        # Evaluate button
        self.evaluate_btn = ttk.Button(
            controls_frame,
            text="Evaluate Model",
            command=self.evaluate_model,
            state="disabled"
        )
        self.evaluate_btn.pack(fill="x", pady=2)
        
        # Compare models button
        self.compare_btn = ttk.Button(
            controls_frame,
            text="Compare Models",
            command=self.compare_models
        )
        self.compare_btn.pack(fill="x", pady=2)
        
        # Save model button
        self.save_btn = ttk.Button(
            controls_frame,
            text="Save Model",
            command=self.save_model,
            state="disabled"
        )
        self.save_btn.pack(fill="x", pady=2)
        
        # Load model button
        load_btn = ttk.Button(
            controls_frame,
            text="Load Model",
            command=self.load_model
        )
        load_btn.pack(fill="x", pady=2)
    
    def create_results_section(self, parent):
        """Create results display section"""
        results_frame = ttk.LabelFrame(parent, text="Training Results", padding="10")
        results_frame.pack(fill="both", expand=True)
        
        # Create notebook for different result views
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.pack(fill="both", expand=True)
        
        # Metrics tab
        metrics_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(metrics_frame, text="Metrics")
        
        self.metrics_text = tk.Text(
            metrics_frame,
            wrap="word",
            state="disabled"
        )
        self.metrics_text.pack(fill="both", expand=True)
        
        # Add scrollbar
        metrics_scroll = ttk.Scrollbar(metrics_frame, orient="vertical", command=self.metrics_text.yview)
        metrics_scroll.pack(side="right", fill="y")
        self.metrics_text.configure(yscrollcommand=metrics_scroll.set)
        
        # Visualization tab
        viz_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(viz_frame, text="Plots")
        
        # Create matplotlib figure
        self.fig, self.axes = plt.subplots(2, 2, figsize=(10, 8))
        self.fig.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Log tab
        log_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(log_frame, text="Training Log")
        
        self.log_text = tk.Text(
            log_frame,
            wrap="word",
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True)
        
        # Add scrollbar
        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=log_scroll.set)
    
    def train_model(self):
        """Train the selected model"""
        try:
            # Check if data is available
            training_data = self.get_training_data()
            if training_data is None:
                messagebox.showwarning("Warning", "No training data available. Please load data first.")
                return
            
            self.log_message("Starting model training...")
            
            # Get parameters
            algorithm = self.algorithm_var.get()
            test_size = self.test_size_var.get()
            random_state = self.random_state_var.get()
            
            self.log_message(f"Algorithm: {algorithm}")
            self.log_message(f"Test size: {test_size}")
            self.log_message(f"Random state: {random_state}")
            
            # Prepare data
            X, y = self.data_processor.prepare_features_and_target(training_data)
            
            # Train model
            results = self.model_trainer.train_model(
                X, y,
                algorithm=algorithm,
                test_size=test_size,
                random_state=random_state
            )
            
            self.training_results = results
            self.current_model = self.model_trainer.current_model
            
            # Display results
            self.display_training_results()
            
            # Enable buttons
            self.evaluate_btn.config(state="normal")
            self.save_btn.config(state="normal")
            
            self.log_message("Model training completed successfully!")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            messagebox.showerror("Error", f"Training failed: {str(e)}")
            self.log_message(f"Training failed: {str(e)}")
    
    def evaluate_model(self):
        """Evaluate the trained model"""
        try:
            if self.current_model is None:
                messagebox.showwarning("Warning", "No trained model available")
                return
            
            self.log_message("Evaluating model...")
            
            # Get test data
            training_data = self.get_training_data()
            X, y = self.data_processor.prepare_features_and_target(training_data)
            
            # Perform cross-validation
            cv_scores = self.model_trainer.cross_validate(
                X, y, cv=self.cv_folds_var.get()
            )
            
            # Update results
            self.training_results['cv_scores'] = cv_scores
            self.display_training_results()
            
            self.log_message("Model evaluation completed!")
            
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            messagebox.showerror("Error", f"Evaluation failed: {str(e)}")
            self.log_message(f"Evaluation failed: {str(e)}")
    
    def compare_models(self):
        """Compare different models"""
        try:
            training_data = self.get_training_data()
            if training_data is None:
                messagebox.showwarning("Warning", "No training data available")
                return
            
            self.log_message("Comparing models...")
            
            # List of algorithms to compare
            algorithms = ["RandomForest", "GradientBoosting", "SVM", "LogisticRegression"]
            
            X, y = self.data_processor.prepare_features_and_target(training_data)
            
            comparison_results = {}
            
            for algorithm in algorithms:
                try:
                    results = self.model_trainer.train_model(
                        X, y,
                        algorithm=algorithm,
                        test_size=self.test_size_var.get(),
                        random_state=self.random_state_var.get()
                    )
                    comparison_results[algorithm] = results
                    self.log_message(f"Trained {algorithm}")
                except Exception as e:
                    self.log_message(f"Failed to train {algorithm}: {str(e)}")
            
            # Display comparison
            self.display_model_comparison(comparison_results)
            
            self.log_message("Model comparison completed!")
            
        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            messagebox.showerror("Error", f"Comparison failed: {str(e)}")
            self.log_message(f"Comparison failed: {str(e)}")
    
    def save_model(self):
        """Save the trained model"""
        try:
            if self.current_model is None:
                messagebox.showwarning("Warning", "No trained model to save")
                return
            
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                title="Save model",
                defaultextension=".pkl",
                filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
            )
            
            if file_path:
                self.model_trainer.save_model(file_path)
                messagebox.showinfo("Success", f"Model saved to {file_path}")
                self.log_message(f"Model saved to {file_path}")
                
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            messagebox.showerror("Error", f"Failed to save model: {str(e)}")
    
    def load_model(self):
        """Load a saved model"""
        try:
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="Load model",
                filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
            )
            
            if file_path:
                self.model_trainer.load_model(file_path)
                self.current_model = self.model_trainer.current_model
                
                # Enable buttons
                self.evaluate_btn.config(state="normal")
                self.save_btn.config(state="normal")
                
                messagebox.showinfo("Success", f"Model loaded from {file_path}")
                self.log_message(f"Model loaded from {file_path}")
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")
    
    def display_training_results(self):
        """Display training results"""
        if self.training_results is None:
            return
        
        # Display metrics
        self.metrics_text.config(state="normal")
        self.metrics_text.delete(1.0, "end")
        
        results_text = "TRAINING RESULTS\n"
        results_text += "=" * 50 + "\n\n"
        
        # Basic metrics
        if 'accuracy' in self.training_results:
            results_text += f"Accuracy: {self.training_results['accuracy']:.4f}\n"
        if 'precision' in self.training_results:
            results_text += f"Precision: {self.training_results['precision']:.4f}\n"
        if 'recall' in self.training_results:
            results_text += f"Recall: {self.training_results['recall']:.4f}\n"
        if 'f1_score' in self.training_results:
            results_text += f"F1 Score: {self.training_results['f1_score']:.4f}\n"
        
        # Cross-validation scores
        if 'cv_scores' in self.training_results:
            cv_scores = self.training_results['cv_scores']
            results_text += f"\nCross-Validation Scores:\n"
            results_text += f"Mean: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores) * 2:.4f})\n"
            results_text += f"Individual scores: {cv_scores}\n"
        
        # Classification report
        if 'classification_report' in self.training_results:
            results_text += f"\nClassification Report:\n"
            results_text += self.training_results['classification_report']
        
        self.metrics_text.insert("end", results_text)
        self.metrics_text.config(state="disabled")
        
        # Update plots
        self.update_visualization_plots()
    
    def display_model_comparison(self, comparison_results):
        """Display model comparison results"""
        if not comparison_results:
            return
        
        self.metrics_text.config(state="normal")
        self.metrics_text.delete(1.0, "end")
        
        results_text = "MODEL COMPARISON\n"
        results_text += "=" * 50 + "\n\n"
        
        # Create comparison table
        for algorithm, results in comparison_results.items():
            results_text += f"{algorithm}:\n"
            results_text += f"  Accuracy: {results.get('accuracy', 'N/A'):.4f}\n"
            results_text += f"  F1 Score: {results.get('f1_score', 'N/A'):.4f}\n"
            results_text += "-" * 30 + "\n"
        
        self.metrics_text.insert("end", results_text)
        self.metrics_text.config(state="disabled")
    
    def update_visualization_plots(self):
        """Update visualization plots"""
        if self.training_results is None:
            return
        
        # Clear existing plots
        for ax in self.axes.flat:
            ax.clear()
        
        try:
            # Plot 1: Confusion Matrix (if available)
            if 'confusion_matrix' in self.training_results:
                sns.heatmap(
                    self.training_results['confusion_matrix'], 
                    annot=True, 
                    fmt='d',
                    ax=self.axes[0, 0]
                )
                self.axes[0, 0].set_title('Confusion Matrix')
            
            # Plot 2: Feature Importance (if available) 
            if 'feature_importance' in self.training_results:
                importance = self.training_results['feature_importance']
                feature_names = list(range(len(importance)))
                
                self.axes[0, 1].bar(feature_names, importance)
                self.axes[0, 1].set_title('Feature Importance')
                self.axes[0, 1].set_xlabel('Features')
                self.axes[0, 1].set_ylabel('Importance')
            
            # Plot 3: Learning Curve (placeholder)
            self.axes[1, 0].plot([1, 2, 3, 4, 5], [0.6, 0.7, 0.75, 0.8, 0.82])
            self.axes[1, 0].set_title('Learning Curve')
            self.axes[1, 0].set_xlabel('Training Size')
            self.axes[1, 0].set_ylabel('Accuracy')
            
            # Plot 4: ROC Curve (placeholder)
            if 'roc_curve' in self.training_results:
                fpr, tpr, _ = self.training_results['roc_curve']
                self.axes[1, 1].plot(fpr, tpr)
                self.axes[1, 1].plot([0, 1], [0, 1], 'k--')
                self.axes[1, 1].set_title('ROC Curve')
                self.axes[1, 1].set_xlabel('False Positive Rate')
                self.axes[1, 1].set_ylabel('True Positive Rate')
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating plots: {e}")
    
    def log_message(self, message):
        """Add message to training log"""
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
    
    def get_training_data(self):
        """Get training data from data processor"""
        # This should be implemented to get data from the data tab
        # For now, return None
        return getattr(self.data_processor, 'current_data', None)
    
    def reset(self):
        """Reset tab to initial state"""
        self.training_results = None
        self.current_model = None
        
        # Reset controls
        self.algorithm_var.set("RandomForest")
        self.test_size_var.set(0.2)
        self.random_state_var.set(42)
        self.cv_folds_var.set(5)
        
        # Reset displays
        self.metrics_text.config(state="normal")
        self.metrics_text.delete(1.0, "end")
        self.metrics_text.config(state="disabled")
        
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="disabled")
        
        # Clear plots
        for ax in self.axes.flat:
            ax.clear()
        self.canvas.draw()
        
        # Disable buttons
        self.evaluate_btn.config(state="disabled")
        self.save_btn.config(state="disabled")