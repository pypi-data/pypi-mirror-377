"""
Componentes de Machine Learning originales
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import tkinter as tk

logger = logging.getLogger(__name__)

class DataProcessor:
    """Procesador de datos para machine learning"""
    
    def __init__(self):
        self.current_data = None
        self.target_column = None
        self.features = None
        self.target = None

    def load_data(self, file_path):
        """Cargar datos desde archivo"""
        file_path = Path(file_path)
        
        if file_path.suffix == '.csv':
            self.current_data = pd.read_csv(file_path)
        elif file_path.suffix in ['.xlsx', '.xls']:
            self.current_data = pd.read_excel(file_path)
        elif file_path.suffix == '.json':
            self.current_data = pd.read_json(file_path)
        else:
            raise ValueError(f"Formato de archivo no soportado: {file_path.suffix}")
            
        return self.current_data

    def get_data_summary(self):
        """Obtener resumen de datos"""
        if self.current_data is None: 
            return {}
            
        return {
            'shape': self.current_data.shape,
            'memory_usage_mb': self.current_data.memory_usage(deep=True).sum() / 1024**2,
            'numeric_columns': self.current_data.select_dtypes(include=np.number).columns.tolist(),
            'categorical_columns': self.current_data.select_dtypes(include=['object']).columns.tolist(),
            'missing_data_pct': (self.current_data.isnull().sum() / len(self.current_data) * 100).to_dict()
        }
    
    def get_column_info(self):
        """Obtener información de columnas"""
        if self.current_data is None: 
            return {}
        return self.current_data.dtypes.to_dict()

    def select_features(self, feature_columns):
        """Seleccionar columnas de características"""
        self.features = self.current_data[feature_columns]

    def set_target(self, target_column):
        """Establecer columna objetivo"""
        self.target_column = target_column
        self.target = self.current_data[target_column]

    def prepare_features_and_target(self, data):
        """Preparar características y objetivo para entrenamiento"""
        if self.features is None or self.target is None:
            raise ValueError("Características y objetivo no establecidos.")
            
        X = self.features
        y = self.target
        
        # Paso de limpieza simple
        X = X.select_dtypes(include=np.number).fillna(0)
        
        return X, y


class ModelTrainer:
    """Entrenador de modelos de machine learning"""
    
    def __init__(self):
        self.model = None

    def train_model(self, X, y, algorithm="RandomForest", test_size=0.2, random_state=42):
        """Entrenar modelo con algoritmo especificado"""
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.svm import SVC
        from sklearn.linear_model import LogisticRegression
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.tree import DecisionTreeClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report, precision_score, recall_score, f1_score

        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Modelos disponibles
        models = {
            "RandomForest": RandomForestClassifier(random_state=random_state),
            "GradientBoosting": GradientBoostingClassifier(random_state=random_state),
            "SVM": SVC(probability=True, random_state=random_state),
            "LogisticRegression": LogisticRegression(random_state=random_state),
            "KNeighbors": KNeighborsClassifier(),
            "DecisionTree": DecisionTreeClassifier(random_state=random_state)
        }
        
        self.model = models.get(algorithm, RandomForestClassifier(random_state=random_state))

        # Entrenar modelo
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        
        # Calcular importancia de características
        feature_importances = []
        if hasattr(self.model, 'feature_importances_'):
            feature_importances = [
                {'feature': f, 'importance': i} 
                for f, i in zip(X.columns, self.model.feature_importances_)
            ]
            feature_importances = sorted(
                feature_importances, 
                key=lambda x: x['importance'], 
                reverse=True
            )

        # Retornar resultados
        return {
            'accuracy': accuracy_score(y_test, predictions),
            'precision': precision_score(y_test, predictions, average='weighted'),
            'recall': recall_score(y_test, predictions, average='weighted'),
            'f1_score': f1_score(y_test, predictions, average='weighted'),
            'classification_report': classification_report(y_test, predictions),
            'feature_importance': feature_importances,
            'model_type': 'classification',
            'algorithm': algorithm,
        }

    def predict(self, X):
        """Realizar predicciones"""
        if self.model:
            # Asegurar que las columnas coincidan con los datos de entrenamiento
            if hasattr(self.model, 'feature_names_in_'):
                model_cols = self.model.feature_names_in_
                X = X.reindex(columns=model_cols, fill_value=0)
            return self.model.predict(X)
        return None

    def cross_validate(self, X, y, cv=5):
        """Validación cruzada"""
        from sklearn.model_selection import cross_val_score
        if self.model:
            return cross_val_score(self.model, X, y, cv=cv)
        return []

    def save_model(self, file_path):
        """Guardar modelo"""
        import pickle
        with open(file_path, 'wb') as f:
            pickle.dump(self.model, f)

    def load_model(self, file_path):
        """Cargar modelo"""
        import pickle
        with open(file_path, 'rb') as f:
            self.model = pickle.load(f)


class Visualizer:
    """Clase para visualizaciones ML"""
    
    def __init__(self):
        pass


class ComparisonDialog:
    """Diálogo para comparación de modelos"""
    
    def __init__(self, parent, training_data, model_trainer):
        self.parent = parent
        self.training_data = training_data
        self.model_trainer = model_trainer
    
    def show(self):
        """Mostrar diálogo de comparación"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Model Comparison")
        dialog.geometry("600x400")
        
        # Hacer ventana modal
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Contenido del diálogo
        main_frame = tk.Frame(dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(main_frame, text="Model Comparison", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Mensaje
        message_label = tk.Label(main_frame, 
                                text="Model comparison feature is under development.\n\n"
                                     "This will allow you to:\n"
                                     "• Compare multiple algorithms simultaneously\n"
                                     "• View performance metrics side by side\n"
                                     "• Generate comparison charts\n"
                                     "• Export comparison reports",
                                justify="left")
        message_label.pack(pady=20)
        
        # Botón cerrar
        close_button = tk.Button(main_frame, text="Close", command=dialog.destroy)
        close_button.pack(pady=20)
        
        # Centrar la ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")