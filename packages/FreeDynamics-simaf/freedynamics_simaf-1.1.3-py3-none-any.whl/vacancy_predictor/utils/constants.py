"""
Constants and configuration values for the Vacancy Predictor package
"""

import os
from pathlib import Path

# Package information
PACKAGE_NAME = "vacancy-predictor"
PACKAGE_VERSION = "1.0.0"

# File formats
SUPPORTED_DATA_FORMATS = {
    '.csv': 'Comma Separated Values',
    '.xlsx': 'Excel Workbook',
    '.xls': 'Excel 97-2003 Workbook', 
    '.json': 'JSON Data',
    '.jsonl': 'JSON Lines',
    '.pkl': 'Python Pickle',
    '.dump': 'Data Dump File'
}

# Default paths
DEFAULT_OUTPUT_DIR = Path.home() / "vacancy_predictor_output"
DEFAULT_MODELS_DIR = DEFAULT_OUTPUT_DIR / "models"
DEFAULT_DATA_DIR = DEFAULT_OUTPUT_DIR / "data"
DEFAULT_REPORTS_DIR = DEFAULT_OUTPUT_DIR / "reports"

# Ensure directories exist
for directory in [DEFAULT_OUTPUT_DIR, DEFAULT_MODELS_DIR, DEFAULT_DATA_DIR, DEFAULT_REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ML Algorithm configurations
REGRESSION_ALGORITHMS = {
    'linear_regression': {
        'name': 'Linear Regression',
        'description': 'Simple linear relationship modeling',
        'pros': ['Fast', 'Interpretable', 'No hyperparameters'],
        'cons': ['Assumes linear relationship', 'Sensitive to outliers']
    },
    'ridge': {
        'name': 'Ridge Regression',
        'description': 'Linear regression with L2 regularization',
        'pros': ['Handles multicollinearity', 'Prevents overfitting'],
        'cons': ['Still assumes linearity', 'Requires tuning alpha']
    },
    'lasso': {
        'name': 'Lasso Regression', 
        'description': 'Linear regression with L1 regularization',
        'pros': ['Feature selection', 'Sparse solutions'],
        'cons': ['Can be unstable', 'Requires tuning alpha']
    },
    'random_forest': {
        'name': 'Random Forest Regressor',
        'description': 'Ensemble of decision trees',
        'pros': ['Handles non-linearity', 'Feature importance', 'Robust'],
        'cons': ['Less interpretable', 'Can overfit with small datasets']
    },
    'gradient_boosting': {
        'name': 'Gradient Boosting Regressor',
        'description': 'Sequential ensemble method',
        'pros': ['High accuracy', 'Handles different data types'],
        'cons': ['Prone to overfitting', 'Requires tuning']
    },
    'decision_tree': {
        'name': 'Decision Tree Regressor',
        'description': 'Tree-based model with splits',
        'pros': ['Highly interpretable', 'Handles non-linearity'],
        'cons': ['Prone to overfitting', 'Unstable']
    },
    'svr': {
        'name': 'Support Vector Regression',
        'description': 'SVM for regression tasks',
        'pros': ['Effective in high dimensions', 'Memory efficient'],
        'cons': ['Slow on large datasets', 'Requires feature scaling']
    }
}

CLASSIFICATION_ALGORITHMS = {
    'logistic_regression': {
        'name': 'Logistic Regression',
        'description': 'Linear model for classification',
        'pros': ['Fast', 'Interpretable', 'Probabilistic output'],
        'cons': ['Assumes linear decision boundary', 'Sensitive to outliers']
    },
    'random_forest': {
        'name': 'Random Forest Classifier',
        'description': 'Ensemble of decision trees',
        'pros': ['Handles non-linearity', 'Feature importance', 'Robust'],
        'cons': ['Less interpretable', 'Can overfit with small datasets']
    },
    'gradient_boosting': {
        'name': 'Gradient Boosting Classifier',
        'description': 'Sequential ensemble method',
        'pros': ['High accuracy', 'Handles different data types'],
        'cons': ['Prone to overfitting', 'Requires tuning']
    },
    'decision_tree': {
        'name': 'Decision Tree Classifier',
        'description': 'Tree-based model with splits',
        'pros': ['Highly interpretable', 'Handles non-linearity'],
        'cons': ['Prone to overfitting', 'Unstable']
    },
    'svc': {
        'name': 'Support Vector Classifier',
        'description': 'SVM for classification tasks',
        'pros': ['Effective in high dimensions', 'Versatile kernels'],
        'cons': ['Slow on large datasets', 'Requires feature scaling']
    },
    'naive_bayes': {
        'name': 'Naive Bayes',
        'description': 'Probabilistic classifier based on Bayes theorem',
        'pros': ['Fast', 'Works with small datasets', 'Handles multi-class'],
        'cons': ['Assumes feature independence', 'Can be oversimplified']
    }
}

# Default hyperparameter grids for tuning
DEFAULT_PARAM_GRIDS = {
    'random_forest': {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    },
    'gradient_boosting': {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'subsample': [0.8, 0.9, 1.0]
    },
    'ridge': {
        'alpha': [0.1, 1.0, 10.0, 100.0]
    },
    'lasso': {
        'alpha': [0.1, 1.0, 10.0, 100.0]
    },
    'svc': {
        'C': [0.1, 1, 10, 100],
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto', 0.1, 1]
    },
    'svr': {
        'C': [0.1, 1, 10, 100], 
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto', 0.1, 1],
        'epsilon': [0.01, 0.1, 0.2]
    }
}

# GUI Configuration
GUI_CONFIG = {
    'window_size': (1200, 800),
    'min_window_size': (800, 600),
    'default_font': ('Arial', 10),
    'header_font': ('Arial', 12, 'bold'),
    'mono_font': ('Courier New', 9),
    'colors': {
        'primary': '#2E86AB',
        'secondary': '#A23B72', 
        'success': '#28A745',
        'warning': '#FFC107',
        'danger': '#DC3545',
        'light': '#F8F9FA',
        'dark': '#343A40'
    }
}

# Data validation thresholds
VALIDATION_THRESHOLDS = {
    'max_missing_percent': 50,  # Warn if column has >50% missing
    'max_memory_mb': 500,       # Warn if dataset >500MB
    'min_samples_per_class': 5, # Minimum samples per class for classification
    'max_categories': 50,       # Maximum unique categories for categorical
    'outlier_threshold': 0.05   # Flag if >5% outliers
}

# Export formats
EXPORT_FORMATS = {
    'csv': {
        'extension': '.csv',
        'description': 'Comma Separated Values',
        'method': 'to_csv'
    },
    'excel': {
        'extension': '.xlsx', 
        'description': 'Excel Workbook',
        'method': 'to_excel'
    },
    'json': {
        'extension': '.json',
        'description': 'JSON Format',
        'method': 'to_json'
    },
    'parquet': {
        'extension': '.parquet',
        'description': 'Parquet Format', 
        'method': 'to_parquet'
    }
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'vacancy_predictor.log',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'vacancy_predictor': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# URLs and links
DOCUMENTATION_URL = "https://vacancy-predictor.readthedocs.io"
GITHUB_URL = "https://github.com/tuusuario/vacancy-predictor"
PYPI_URL = "https://pypi.org/project/vacancy-predictor"
SUPPORT_EMAIL = "support@vacancy-predictor.com"

# Error messages
ERROR_MESSAGES = {
    'no_data': "No data loaded. Please load a dataset first.",
    'no_features': "No features selected. Please select features for training.",
    'no_target': "No target selected. Please select a target variable.",
    'no_model': "No model trained. Please train a model first.",
    'invalid_file': "Invalid file format. Supported formats: {formats}",
    'file_not_found': "File not found: {filepath}",
    'insufficient_data': "Insufficient data for training. Need at least {min_samples} samples.",
    'invalid_target': "Invalid target variable. Target must have at least 2 unique values."
}