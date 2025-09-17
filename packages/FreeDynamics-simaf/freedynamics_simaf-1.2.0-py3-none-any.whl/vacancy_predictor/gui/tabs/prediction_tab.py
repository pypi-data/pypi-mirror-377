"""
Prediction tab for making predictions with trained models
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PredictionTab:
    """
    Tab for making predictions with trained models
    """
    
    def __init__(self, parent, model_trainer, data_processor):
        self.parent = parent
        self.model_trainer = model_trainer
        self.data_processor = data_processor
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        
        # Variables
        self.prediction_file_var = tk.StringVar()
        self.prediction_mode_var = tk.StringVar(value="batch")
        
        # Data storage
        self.prediction_data = None
        self.predictions = None
        self.manual_values = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the prediction tab"""
        
        # Main container with padding
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Model status section
        self.create_model_status_section(main_container)
        
        # Prediction mode selection
        self.create_mode_selection_section(main_container)
        
        # Batch prediction section
        self.create_batch_prediction_section(main_container)
        
        # Manual prediction section
        self.create_manual_prediction_section(main_container)
        
        # Results section
        self.create_results_section(main_container)
    
    def create_model_status_section(self, parent):
        """Create model status display section"""
        status_frame = ttk.LabelFrame(parent, text="Model Status", padding="10")
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.model_status_text = tk.Text(status_frame, height=3, wrap="word", state="disabled")
        self.model_status_text.pack(fill="x")
        
        # Load model button
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Load Model", 
                  command=self.load_model).pack(side="left")
        
        # Update initial status
        self.update_model_status()
    
    def create_mode_selection_section(self, parent):
        """Create prediction mode selection"""
        mode_frame = ttk.LabelFrame(parent, text="Prediction Mode", padding="10")
        mode_frame.pack(fill="x", pady=(0, 10))
        
        # Radio buttons for mode selection
        ttk.Radiobutton(mode_frame, text="Batch Prediction (from file)", 
                       variable=self.prediction_mode_var, value="batch",
                       command=self.on_mode_change).pack(anchor="w")
        
        ttk.Radiobutton(mode_frame, text="Manual Prediction (enter values)", 
                       variable=self.prediction_mode_var, value="manual",
                       command=self.on_mode_change).pack(anchor="w", pady=(5, 0))
    
    def create_batch_prediction_section(self, parent):
        """Create batch prediction section"""
        self.batch_frame = ttk.LabelFrame(parent, text="Batch Prediction", padding="10")
        self.batch_frame.pack(fill="x", pady=(0, 10))
        
        # File selection
        file_frame = ttk.Frame(self.batch_frame)
        file_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(file_frame, text="Data file:").pack(side="left")
        
        file_entry = ttk.Entry(file_frame, textvariable=self.prediction_file_var, state="readonly")
        file_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_prediction_file).pack(side="right")
        
        # File info
        self.file_info_label = ttk.Label(self.batch_frame, text="No file selected", 
                                        foreground="gray")
        self.file_info_label.pack(anchor="w")
        
        # Data preview
        preview_label = ttk.Label(self.batch_frame, text="Data Preview:", font=("Arial", 10, "bold"))
        preview_label.pack(anchor="w", pady=(10, 5))
        
        # Treeview for data preview
        self.preview_tree = ttk.Treeview(self.batch_frame, height=6, show="headings")
        preview_scrollbar = ttk.Scrollbar(self.batch_frame, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=preview_scrollbar.set)
        
        tree_frame = ttk.Frame(self.batch_frame)
        tree_frame.pack(fill="x", pady=(0, 10))
        
        self.preview_tree.pack(in_=tree_frame, side="left", fill="both", expand=True)
        preview_scrollbar.pack(in_=tree_frame, side="right", fill="y")
        
        # Prediction buttons
        batch_button_frame = ttk.Frame(self.batch_frame)
        batch_button_frame.pack(fill="x")
        
        self.predict_batch_button = ttk.Button(batch_button_frame, text="Make Predictions", 
                                              command=self.make_batch_predictions,
                                              style="Action.TButton", state="disabled")
        self.predict_batch_button.pack(side="left")
        
        ttk.Button(batch_button_frame, text="Export Predictions", 
                  command=self.export_batch_predictions).pack(side="right")
    
    def create_manual_prediction_section(self, parent):
        """Create manual prediction section"""
        self.manual_frame = ttk.LabelFrame(parent, text="Manual Prediction", padding="10")
        self.manual_frame.pack(fill="x", pady=(0, 10))
        
        # Instructions
        ttk.Label(self.manual_frame, text="Enter values for each feature:", 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Scrollable frame for feature inputs
        canvas = tk.Canvas(self.manual_frame, height=200)
        scrollbar = ttk.Scrollbar(self.manual_frame, orient="vertical", command=canvas.yview)
        self.manual_inputs_frame = ttk.Frame(canvas)
        
        self.manual_inputs_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.manual_inputs_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Manual prediction buttons
        manual_button_frame = ttk.Frame(self.manual_frame)
        manual_button_frame.pack(fill="x", pady=(10, 0))
        
        self.predict_manual_button = ttk.Button(manual_button_frame, text="Predict", 
                                               command=self.make_manual_prediction,
                                               style="Success.TButton", state="disabled")
        self.predict_manual_button.pack(side="left")
        
        ttk.Button(manual_button_frame, text="Clear Values", 
                  command=self.clear_manual_values).pack(side="left", padx=(10, 0))
        
        # Initially hide manual frame
        self.manual_frame.pack_forget()
    
    def create_results_section(self, parent):
        """Create prediction results section"""
        results_frame = ttk.LabelFrame(parent, text="Prediction Results", padding="10")
        results_frame.pack(fill="both", expand=True)
        
        # Results display
        self.results_text = tk.Text(results_frame, wrap="word", state="disabled")
        results_scrollbar = ttk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
        
        # Initialize results display
        self.update_results_display("No predictions made yet")
    
    def on_mode_change(self):
        """Handle prediction mode change"""
        mode = self.prediction_mode_var.get()
        
        if mode == "batch":
            self.batch_frame.pack(fill="x", pady=(0, 10), before=self.manual_frame)
            self.manual_frame.pack_forget()
        else:
            self.manual_frame.pack(fill="x", pady=(0, 10), before=self.batch_frame.master.children[list(self.batch_frame.master.children.keys())[-1]])
            self.batch_frame.pack_forget()
            self.setup_manual_inputs()
    
    def update_model_status(self):
        """Update model status display"""
        if self.model_trainer.model is None:
            status_text = "No model loaded.\nPlease train a model in the Training tab or load a saved model."
            self.set_prediction_buttons_state(False)
        else:
            model_type = getattr(self.model_trainer, 'model_type', 'Unknown')
            feature_names = getattr(self.model_trainer, 'feature_names', [])
            
            status_text = f"Model loaded and ready!\n" \
                         f"Type: {model_type.title()}\n" \
                         f"Features required: {len(feature_names)}"
            
            self.set_prediction_buttons_state(True)
        
        self.model_status_text.config(state="normal")
        self.model_status_text.delete(1.0, tk.END)
        self.model_status_text.insert(1.0, status_text)
        self.model_status_text.config(state="disabled")
    
    def set_prediction_buttons_state(self, enabled: bool):
        """Enable/disable prediction buttons"""
        state = "normal" if enabled else "disabled"
        self.predict_batch_button.config(state=state)
        self.predict_manual_button.config(state=state)
    
    def load_model(self):
        """Load a model from file"""
        file_path = filedialog.askopenfilename(
            title="Load Model",
            filetypes=[("Pickle files", "*.pkl"), ("Joblib files", "*.joblib"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.model_trainer.load_model(file_path)
                self.update_model_status()
                self.setup_manual_inputs()  # Refresh manual inputs with new features
                messagebox.showinfo("Success", f"Model loaded from:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model:\n{str(e)}")
    
    def browse_prediction_file(self):
        """Browse for prediction data file"""
        file_types = [
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
            ("JSON files", "*.json"),
            ("All supported", "*.csv *.xlsx *.xls *.json"),
            ("All files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Select prediction data file",
            filetypes=file_types
        )
        
        if file_path:
            self.prediction_file_var.set(file_path)
            self.load_prediction_file(file_path)
    
    def load_prediction_file(self, file_path: str):
        """Load prediction data file"""
        try:
            # Load data based on file extension
            file_path = Path(file_path)
            
            if file_path.suffix.lower() == '.csv':
                self.prediction_data = pd.read_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                self.prediction_data = pd.read_excel(file_path)
            elif file_path.suffix.lower() == '.json':
                self.prediction_data = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path.suffix}")
            
            # Update file info
            info_text = f"Loaded: {self.prediction_data.shape[0]} rows, {self.prediction_data.shape[1]} columns"
            self.file_info_label.config(text=info_text, foreground="green")
            
            # Update preview
            self.update_data_preview()
            
            # Enable prediction button if model is available
            if self.model_trainer.model is not None:
                self.predict_batch_button.config(state="normal")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load prediction file:\n{str(e)}")
            self.file_info_label.config(text=f"Error loading file: {str(e)}", foreground="red")
    
    def update_data_preview(self):
        """Update data preview treeview"""
        if self.prediction_data is None:
            return
        
        # Clear existing data
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # Configure columns
        columns = list(self.prediction_data.columns[:6])  # Show first 6 columns
        self.preview_tree["columns"] = columns
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=100, anchor="w")
        
        # Add data rows (first 10 rows)
        max_rows = min(10, len(self.prediction_data))
        for i in range(max_rows):
            row_data = []
            for col in columns:
                value = self.prediction_data.iloc[i][col]
                if pd.isna(value):
                    formatted_value = "NaN"
                elif isinstance(value, float):
                    formatted_value = f"{value:.3f}"
                else:
                    formatted_value = str(value)[:15]  # Truncate long strings
                row_data.append(formatted_value)
            
            self.preview_tree.insert("", "end", values=row_data)
    
    def setup_manual_inputs(self):
        """Setup manual input fields for features"""
        # Clear existing inputs
        for widget in self.manual_inputs_frame.winfo_children():
            widget.destroy()
        
        self.manual_values = {}
        
        if self.model_trainer.model is None:
            ttk.Label(self.manual_inputs_frame, text="No model loaded", 
                     foreground="gray").pack(pady=20)
            return
        
        # Get feature names (assuming they're stored in the model trainer)
        if hasattr(self.model_trainer, 'features') and self.model_trainer.features is not None:
            feature_names = list(self.model_trainer.features.columns)
        elif hasattr(self.data_processor, 'features') and self.data_processor.features is not None:
            feature_names = list(self.data_processor.features.columns)
        else:
            ttk.Label(self.manual_inputs_frame, text="Feature names not available", 
                     foreground="orange").pack(pady=20)
            return
        
        # Create input fields for each feature
        for i, feature in enumerate(feature_names):
            row_frame = ttk.Frame(self.manual_inputs_frame)
            row_frame.pack(fill="x", pady=2)
            
            # Feature label
            label = ttk.Label(row_frame, text=f"{feature}:", width=20, anchor="w")
            label.pack(side="left", padx=(0, 10))
            
            # Input field
            var = tk.StringVar()
            entry = ttk.Entry(row_frame, textvariable=var, width=15)
            entry.pack(side="left")
            
            self.manual_values[feature] = var
            
            # Add example value if available from training data
            if hasattr(self.data_processor, 'features') and self.data_processor.features is not None:
                if feature in self.data_processor.features.columns:
                    sample_value = self.data_processor.features[feature].iloc[0]
                    example_text = f"e.g., {sample_value}"
                    ttk.Label(row_frame, text=example_text, foreground="gray", 
                             font=("Arial", 8)).pack(side="left", padx=(10, 0))
    
    def make_batch_predictions(self):
        """Make predictions on batch data"""
        if self.model_trainer.model is None:
            messagebox.showwarning("Warning", "No model loaded")
            return
        
        if self.prediction_data is None:
            messagebox.showwarning("Warning", "No prediction data loaded")
            return
        
        try:
            # Make predictions
            predictions = self.model_trainer.predict(self.prediction_data)
            
            # Store predictions
            self.predictions = predictions
            
            # Create results DataFrame
            results_df = self.prediction_data.copy()
            results_df['Prediction'] = predictions
            
            # Display results
            self.display_batch_results(results_df)
            
            messagebox.showinfo("Success", f"Predictions completed!\n"
                               f"Processed {len(predictions)} samples")
            
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed:\n{str(e)}")
    
    def make_manual_prediction(self):
        """Make prediction on manually entered values"""
        if self.model_trainer.model is None:
            messagebox.showwarning("Warning", "No model loaded")
            return
        
        try:
            # Collect input values
            input_data = {}
            missing_fields = []
            
            for feature, var in self.manual_values.items():
                value_str = var.get().strip()
                if not value_str:
                    missing_fields.append(feature)
                else:
                    try:
                        # Try to convert to numeric
                        input_data[feature] = float(value_str)
                    except ValueError:
                        # Keep as string for categorical features
                        input_data[feature] = value_str
            
            if missing_fields:
                messagebox.showwarning("Warning", f"Please fill in all fields.\n"
                                      f"Missing: {', '.join(missing_fields)}")
                return
            
            # Create DataFrame for prediction
            input_df = pd.DataFrame([input_data])
            
            # Make prediction
            prediction = self.model_trainer.predict(input_df)
            
            # Display result
            self.display_manual_result(input_data, prediction[0])
            
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed:\n{str(e)}")
    
    def display_batch_results(self, results_df: pd.DataFrame):
        """Display batch prediction results"""
        result_lines = [
            "Batch Prediction Results",
            "=" * 30,
            "",
            f"Total samples processed: {len(results_df)}",
            "",
            "Sample Results (first 10):",
            "-" * 25
        ]
        
        # Show first 10 results
        for i in range(min(10, len(results_df))):
            prediction = results_df.iloc[i]['Prediction']
            if isinstance(prediction, float):
                result_lines.append(f"Sample {i+1}: {prediction:.4f}")
            else:
                result_lines.append(f"Sample {i+1}: {prediction}")
        
        if len(results_df) > 10:
            result_lines.append("...")
        
        # Add statistics if numeric predictions
        if len(results_df) > 0 and isinstance(results_df['Prediction'].iloc[0], (int, float)):
            predictions = results_df['Prediction']
            result_lines.extend([
                "",
                "Prediction Statistics:",
                f"Mean: {predictions.mean():.4f}",
                f"Std: {predictions.std():.4f}",
                f"Min: {predictions.min():.4f}",
                f"Max: {predictions.max():.4f}"
            ])
        
        result_text = "\n".join(result_lines)
        self.update_results_display(result_text)
    
    def display_manual_result(self, input_data: Dict, prediction):
        """Display manual prediction result"""
        result_lines = [
            "Manual Prediction Result",
            "=" * 25,
            "",
            "Input Values:",
        ]
        
        for feature, value in input_data.items():
            result_lines.append(f"  {feature}: {value}")
        
        result_lines.extend([
            "",
            "Prediction:",
            f"  Result: {prediction}",
        ])
        
        # Add confidence/probability if available
        if hasattr(self.model_trainer.model, 'predict_proba'):
            try:
                input_df = pd.DataFrame([input_data])
                probabilities = self.model_trainer.model.predict_proba(input_df)[0]
                classes = self.model_trainer.model.classes_
                
                result_lines.extend([
                    "",
                    "Prediction Probabilities:",
                ])
                
                for class_label, prob in zip(classes, probabilities):
                    result_lines.append(f"  {class_label}: {prob:.4f} ({prob*100:.1f}%)")
            except:
                pass  # Ignore errors in probability calculation
        
        result_text = "\n".join(result_lines)
        self.update_results_display(result_text)
    
    def export_batch_predictions(self):
        """Export batch predictions to file"""
        if self.predictions is None:
            messagebox.showwarning("Warning", "No predictions to export")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Predictions",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Create results DataFrame
                results_df = self.prediction_data.copy()
                results_df['Prediction'] = self.predictions
                
                # Export based on file extension
                if file_path.endswith('.csv'):
                    results_df.to_csv(file_path, index=False)
                elif file_path.endswith('.xlsx'):
                    results_df.to_excel(file_path, index=False)
                
                messagebox.showinfo("Success", f"Predictions exported to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export predictions:\n{str(e)}")
    
    def clear_manual_values(self):
        """Clear all manual input values"""
        for var in self.manual_values.values():
            var.set("")
    
    def update_results_display(self, text: str):
        """Update results display"""
        self.results_text.config(state="normal")
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        self.results_text.config(state="disabled")
    
    def update_model(self, model):
        """Update when a new model is loaded/trained"""
        self.update_model_status()
        self.setup_manual_inputs()
    
    def reset(self):
        """Reset the tab to initial state"""
        self.prediction_file_var.set("")
        self.prediction_data = None
        self.predictions = None
        
        # Clear displays
        self.file_info_label.config(text="No file selected", foreground="gray")
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        self.clear_manual_values()
        self.update_results_display("No predictions made yet")
        self.update_model_status()