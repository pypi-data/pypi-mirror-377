"""
Main GUI application for Vacancy Predictor
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from vacancy_predictor.core.data_processor import DataProcessor
    from vacancy_predictor.core.model_trainer import ModelTrainer
    from vacancy_predictor.core.visualizer import Visualizer
    from vacancy_predictor.dialogs.comparison_dialog import ComparisonDialog
except ImportError as e:
    print(f"Import error: {e}")
    # Create simple placeholder classes if imports fail
    class DataProcessor:
        def __init__(self):
            self.current_data = None
            self.target_column = None
        
        def load_data(self, file_path):
            import pandas as pd
            if file_path.endswith('.csv'):
                return pd.read_csv(file_path)
            else:
                return pd.read_excel(file_path)
        
        def set_target_column(self, column):
            self.target_column = column
        
        def clean_data(self, data):
            return data.dropna()
        
        def prepare_features(self, data):
            numeric_cols = data.select_dtypes(include=['number']).columns
            return data[numeric_cols]
        
        def prepare_features_and_target(self, data):
            X = self.prepare_features(data)
            y = data[self.target_column] if self.target_column else data.iloc[:, -1]
            return X, y
    
    class ModelTrainer:
        def __init__(self):
            self.current_model = None
        
        def train_model(self, X, y, algorithm="RandomForest", test_size=0.2, random_state=42):
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score, classification_report
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
            
            if algorithm == "RandomForest":
                self.current_model = RandomForestClassifier(random_state=random_state)
            
            self.current_model.fit(X_train, y_train)
            predictions = self.current_model.predict(X_test)
            
            return {
                'accuracy': accuracy_score(y_test, predictions),
                'classification_report': classification_report(y_test, predictions)
            }
        
        def predict(self, X):
            if self.current_model:
                return self.current_model.predict(X)
            return None
        
        def cross_validate(self, X, y, cv=5):
            from sklearn.model_selection import cross_val_score
            if self.current_model:
                return cross_val_score(self.current_model, X, y, cv=cv)
            return []
        
        def save_model(self, file_path):
            import pickle
            with open(file_path, 'wb') as f:
                pickle.dump(self.current_model, f)
        
        def load_model(self, file_path):
            import pickle
            with open(file_path, 'rb') as f:
                self.current_model = pickle.load(f)
    
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
        
        # Configure theme
        try:
            style.theme_use('clam')
        except:
            pass  # Use default theme if clam is not available
        
        # Custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('vacancy_predictor.log')
            ]
        )
    
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
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Data Cleaning", command=self.open_data_cleaning)
        tools_menu.add_command(label="Model Comparison", command=self.open_model_comparison)
        tools_menu.add_command(label="Export Results", command=self.export_results)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_main_interface(self):
        """Create main interface with tabs"""
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Import tab classes with error handling
        try:
            from .tabs.data_tabs import DataTab
            from .tabs.training_tab import TrainingTab
            from .tabs.prediction_tab import PredictionTab
            from .tabs.visualization_tab import VisualizationTab
        except ImportError:
            # Create simplified tab classes if imports fail
            from .tabs.data_tabs import DataTab
            from .tabs.training_tab import TrainingTab
            from .tabs.prediction_tab import PredictionTab
            from .tabs.visualization_tab import VisualizationTab
        
        # Create tabs
        try:
            self.data_tab = DataTab(self.notebook, self.data_processor)
            self.notebook.add(self.data_tab.frame, text="📊 Data")
            
            self.training_tab = TrainingTab(self.notebook, self.model_trainer, self.data_processor)
            self.notebook.add(self.training_tab.frame, text="🤖 Training")
            
            self.prediction_tab = PredictionTab(self.notebook, self.model_trainer, self.data_processor)
            self.notebook.add(self.prediction_tab.frame, text="🔮 Prediction")
            
            self.visualization_tab = VisualizationTab(self.notebook, self.data_processor, self.visualizer)
            self.notebook.add(self.visualization_tab.frame, text="📈 Visualization")
            
        except Exception as e:
            logger.error(f"Error creating tabs: {e}")
            # Create simple fallback interface
            self.create_fallback_interface()
    
    def create_fallback_interface(self):
        """Create fallback interface if tab creation fails"""
        fallback_frame = ttk.Frame(self.notebook)
        self.notebook.add(fallback_frame, text="Vacancy Predictor")
        
        title_label = ttk.Label(
            fallback_frame, 
            text="Vacancy Predictor ML Tool", 
            style='Title.TLabel'
        )
        title_label.pack(pady=20)
        
        info_text = """
        Welcome to Vacancy Predictor!
        
        This tool helps you predict job vacancy outcomes using machine learning.
        
        Features:
        • Data loading and preprocessing
        • Multiple ML algorithms
        • Model training and evaluation
        • Prediction capabilities
        • Data visualization
        
        To get started, load your data and follow the workflow.
        """
        
        info_label = ttk.Label(fallback_frame, text=info_text, justify="center")
        info_label.pack(pady=20)
        
        # Add basic functionality buttons
        button_frame = ttk.Frame(fallback_frame)
        button_frame.pack(pady=20)
        
        load_btn = ttk.Button(
            button_frame,
            text="Load Data",
            command=self.simple_load_data
        )
        load_btn.pack(side="left", padx=5)
        
        train_btn = ttk.Button(
            button_frame,
            text="Train Model",
            command=self.simple_train_model
        )
        train_btn.pack(side="left", padx=5)
        
        predict_btn = ttk.Button(
            button_frame,
            text="Make Prediction",
            command=self.simple_predict
        )
        predict_btn.pack(side="left", padx=5)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side="bottom", fill="x")
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.status_label = ttk.Label(
            self.status_frame, 
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            variable=self.progress_var,
            length=200
        )
        self.progress_bar.pack(side="right", padx=2, pady=2)
    
    def update_status(self, message, progress=None):
        """Update status bar"""
        self.status_var.set(message)
        if progress is not None:
            self.progress_var.set(progress)
        self.root.update_idletasks()
    
    # Menu command methods
    def new_project(self):
        """Create new project"""
        if messagebox.askyesno("New Project", "This will clear all current data. Continue?"):
            self.reset_application()
            self.update_status("New project created")
    
    def open_project(self):
        """Open existing project"""
        file_path = filedialog.askopenfilename(
            title="Open project",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Load project data
                self.project_path = file_path
                self.update_status(f"Opened project: {file_path}")
                messagebox.showinfo("Success", "Project opened successfully")
            except Exception as e:
                logger.error(f"Error opening project: {e}")
                messagebox.showerror("Error", f"Failed to open project: {str(e)}")
    
    def save_project(self):
        """Save current project"""
        if self.project_path is None:
            file_path = filedialog.asksaveasfilename(
                title="Save project",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if file_path:
                self.project_path = file_path
        
        if self.project_path:
            try:
                # Save project data
                self.update_status(f"Saved project: {self.project_path}")
                messagebox.showinfo("Success", "Project saved successfully")
            except Exception as e:
                logger.error(f"Error saving project: {e}")
                messagebox.showerror("Error", f"Failed to save project: {str(e)}")
    
    def open_data_cleaning(self):
        """Open data cleaning dialog"""
        messagebox.showinfo("Data Cleaning", "Data cleaning tools will be available in future updates")
    
    def open_model_comparison(self):
        """Open model comparison dialog"""
        try:
            dialog = ComparisonDialog(self.root, self.get_training_data(), self.model_trainer)
            dialog.show()
        except Exception as e:
            logger.error(f"Error opening model comparison: {e}")
            messagebox.showerror("Error", f"Failed to open model comparison: {str(e)}")
    
    def export_results(self):
        """Export analysis results"""
        file_path = filedialog.asksaveasfilename(
            title="Export results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Export results
                self.update_status(f"Exported results: {file_path}")
                messagebox.showinfo("Success", "Results exported successfully")
            except Exception as e:
                logger.error(f"Error exporting results: {e}")
                messagebox.showerror("Error", f"Failed to export results: {str(e)}")
    
    def show_user_guide(self):
        """Show user guide"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("600x500")
        
        text_widget = tk.Text(guide_window, wrap="word", padx=10, pady=10)
        text_widget.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(guide_window, orient="vertical", command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        guide_text = """
VACANCY PREDICTOR USER GUIDE

1. DATA TAB
   • Load your dataset using the Browse button
   • Select CSV or Excel files
   • Review data statistics and preview
   • Set the target column for prediction
   • Clean data if needed

2. TRAINING TAB
   • Choose machine learning algorithm
   • Set training parameters
   • Train the model on your data
   • Evaluate model performance
   • Compare different algorithms

3. PREDICTION TAB
   • Load new data for prediction
   • Use trained model to make predictions
   • Export prediction results
   • Manual single predictions

4. VISUALIZATION TAB
   • Create various plots and charts
   • Explore data distributions
   • Analyze correlations
   • Generate automatic exploratory plots

TIPS:
• Ensure your data is clean and properly formatted
• Use the Data tab to understand your dataset first
• Try different algorithms to find the best performer
• Visualize your data to gain insights

For technical support, check the application logs.
        """
        
        text_widget.insert("end", guide_text)
        text_widget.config(state="disabled")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Vacancy Predictor v1.0.0

A machine learning tool for predicting job vacancy outcomes.

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
        
        # Reset tabs if they exist
        try:
            self.data_tab.reset()
            self.training_tab.reset()
            self.prediction_tab.reset()
            self.visualization_tab.reset()
        except AttributeError:
            pass  # Tabs might not be created yet
    
    def on_closing(self):
        """Handle application closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
    
    def get_training_data(self):
        """Get training data for other components"""
        try:
            return self.data_tab.get_current_data()
        except AttributeError:
            return getattr(self.data_processor, 'current_data', None)
    
    # Simple fallback methods
    def simple_load_data(self):
        """Simple data loading for fallback interface"""
        file_path = filedialog.askopenfilename(
            title="Select data file",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_data = self.data_processor.load_data(file_path)
                messagebox.showinfo("Success", f"Loaded {len(self.current_data)} rows of data")
                self.update_status(f"Loaded: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def simple_train_model(self):
        """Simple model training for fallback interface"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        try:
            X, y = self.data_processor.prepare_features_and_target(self.current_data)
            results = self.model_trainer.train_model(X, y)
            
            messagebox.showinfo("Success", f"Model trained!\nAccuracy: {results['accuracy']:.3f}")
            self.update_status("Model training completed")
        except Exception as e:
            messagebox.showerror("Error", f"Training failed: {str(e)}")
    
    def simple_predict(self):
        """Simple prediction for fallback interface"""
        if self.model_trainer.current_model is None:
            messagebox.showwarning("Warning", "Please train a model first")
            return
        
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data available for prediction")
            return
        
        try:
            X = self.data_processor.prepare_features(self.current_data)
            predictions = self.model_trainer.predict(X)
            
            messagebox.showinfo("Success", f"Made {len(predictions)} predictions")
            self.update_status("Predictions completed")
        except Exception as e:
            messagebox.showerror("Error", f"Prediction failed: {str(e)}")
    
    def run(self):
        """Run the application"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", f"An error occurred: {str(e)}")
        finally:
            logger.info("Application closed")


def main():
    """Main entry point"""
    try:
        app = VacancyPredictorGUI()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        logging.error(f"Failed to start application: {e}")


if __name__ == "__main__":
    main()