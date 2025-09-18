"""
application_config.py
Configuración centralizada para la aplicación Vacancy Predictor
"""

from pathlib import Path
import os

class ApplicationConfig:
    """Configuración centralizada de la aplicación"""
    
    # Información de la aplicación
    APP_NAME = "Vacancy Predictor"
    APP_TITLE = "ML Suite v4.0 Enhanced"
    VERSION = "4.0.0"
    
    # Configuración de ventana
    WINDOW_GEOMETRY = "1600x1000"
    MIN_WINDOW_SIZE = (1200, 800)
    
    # Directorios
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_DIR = BASE_DIR / "config"
    LOGS_DIR = BASE_DIR / "logs"
    EXPORTS_DIR = BASE_DIR / "exports"
    TEMP_DIR = BASE_DIR / "temp"
    
    # Archivos
    LOG_FILE = LOGS_DIR / "vacancy_predictor.log"
    CONFIG_FILE = CONFIG_DIR / "app_config.json"
    
    # Configuración de logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Estilos TTK
    TTK_STYLES = {
        'Title.TLabel': {'font': ('Arial', 12, 'bold')},
        'Success.TButton': {'foreground': 'green'},
        'Action.TButton': {'foreground': 'blue'},
        'Processing.TButton': {'foreground': 'orange'},
        'Advanced.TButton': {'foreground': 'purple'},
        'Feature.TButton': {'foreground': 'darkblue'},
        'Header.TLabel': {'font': ('Arial', 14, 'bold'), 'foreground': 'navy'},
        'Enhanced.TLabel': {'font': ('Arial', 10, 'bold'), 'foreground': 'darkgreen'},
        'Warning.TLabel': {'foreground': 'red'},
        'Info.TLabel': {'foreground': 'blue'}
    }
    
    # Configuración de datos
    SUPPORTED_FILE_FORMATS = {
        'csv': {'extensions': ['.csv'], 'description': 'CSV files'},
        'excel': {'extensions': ['.xlsx', '.xls'], 'description': 'Excel files'},
        'dump': {'extensions': ['.dump', '.dump.gz'], 'description': 'LAMMPS dump files'},
        'json': {'extensions': ['.json'], 'description': 'JSON files'},
        'joblib': {'extensions': ['.joblib', '.pkl'], 'description': 'Model files'}
    }
    
    # Configuración de ML
    ML_CONFIG = {
        'default_n_estimators': 100,
        'default_test_size': 0.2,
        'default_random_state': 42,
        'default_cv_folds': 5,
        'max_features_display': 20,
        'feature_importance_threshold': 0.001,
        'correlation_threshold': 0.05
    }
    
    # Configuración de feature selection
    FEATURE_SELECTION = {
        'min_features': 5,
        'max_features': 200,
        'default_top_n': 20,
        'categories': [
            'Coordinación', 'Energía', 'Stress', 
            'Histogramas', 'Estadísticas', 'Voronoi', 'Otras'
        ],
        'importance_levels': {
            'high': 0.05,
            'medium': 0.01,
            'low': 0.001
        }
    }
    
    # Configuración de exportación
    EXPORT_CONFIG = {
        'default_export_dir': 'vacancy_predictor_exports',
        'include_metadata': True,
        'compress_large_files': True,
        'max_file_size_mb': 100
    }
    
    # Configuración de interfaz
    UI_CONFIG = {
        'notebook_tabs': [
            {'name': 'batch', 'title': '📄 Batch Processing'},
            {'name': 'enhanced_ml', 'title': '🧠 Enhanced ML'}
        ],
        'status_bar_sections': [
            {'name': 'main', 'width': -1},
            {'name': 'features', 'width': 200},
            {'name': 'memory', 'width': 150},
            {'name': 'datasets', 'width': 120}
        ],
        'dialog_sizes': {
            'statistics': '800x600',
            'analysis': '900x700',
            'user_guide': '900x700',
            'about': '600x500'
        }
    }
    
    # Mensajes de la aplicación
    MESSAGES = {
        'welcome': "Vacancy Predictor v4.0 Enhanced Ready - Advanced Feature Selection Available",
        'data_loaded': "Dataset cargado: {samples} muestras, {features} features",
        'model_trained': "Modelo entrenado exitosamente - R²: {r2:.3f}, MAE: {mae:.3f}",
        'features_selected': "Features seleccionadas: {count} de {total}",
        'export_complete': "Exportación completada: {files} archivos en {directory}",
        'reset_complete': "Nuevo proyecto creado - Enhanced ML ready"
    }
    
    # Atajos de teclado
    KEYBOARD_SHORTCUTS = {
        '<Control-n>': 'Nuevo proyecto',
        '<Control-i>': 'Importar dataset',
        '<Control-e>': 'Exportar datos',
        '<Control-f>': 'Selección de features',
        '<Control-s>': 'Guardar proyecto',
        '<Control-q>': 'Salir',
        '<F1>': 'Guía del usuario',
        '<F2>': 'Estadísticas de datos',
        '<F3>': 'Uso de memoria',
        '<F4>': 'Análisis de features'
    }
    
    @classmethod
    def create_directories(cls):
        """Crear directorios necesarios"""
        directories = [cls.CONFIG_DIR, cls.LOGS_DIR, cls.EXPORTS_DIR, cls.TEMP_DIR]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_file_types_for_dialog(cls, category=None):
        """Obtener tipos de archivo para diálogos"""
        if category and category in cls.SUPPORTED_FILE_FORMATS:
            format_info = cls.SUPPORTED_FILE_FORMATS[category]
            return [(format_info['description'], ' '.join(f'*{ext}' for ext in format_info['extensions']))]
        
        # Todos los formatos
        all_types = []
        for format_info in cls.SUPPORTED_FILE_FORMATS.values():
            all_types.append((format_info['description'], ' '.join(f'*{ext}' for ext in format_info['extensions'])))
        
        return all_types
    
    @classmethod
    def is_supported_file(cls, file_path):
        """Verificar si un archivo es soportado"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        for format_info in cls.SUPPORTED_FILE_FORMATS.values():
            if extension in format_info['extensions']:
                return True
        
        return False
    
    @classmethod
    def get_file_category(cls, file_path):
        """Obtener categoría de archivo"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        for category, format_info in cls.SUPPORTED_FILE_FORMATS.items():
            if extension in format_info['extensions']:
                return category
        
        return 'unknown'


class FeatureCategories:
    """Categorización automática de features"""
    
    CATEGORY_PATTERNS = {
        'Coordinación': ['coord', 'coordination', 'neighbors'],
        'Energía': ['energy', 'peatom', 'keatom', 'potential'],
        'Stress': ['stress', 'satom', 'pressure', 'strain'],
        'Histogramas': ['hist', 'bin', 'distribution'],
        'Estadísticas': ['mean', 'std', 'min', 'max', 'avg', 'median'],
        'Voronoi': ['voro', 'voronoi', 'volume'],
        'Geometría': ['x', 'y', 'z', 'position', 'distance'],
        'Temporal': ['time', 'step', 'frame'],
        'Identificadores': ['id', 'type', 'tag', 'label']
    }
    
    @classmethod
    def categorize_feature(cls, feature_name):
        """Categorizar una feature basado en su nombre"""
        feature_lower = feature_name.lower()
        
        for category, patterns in cls.CATEGORY_PATTERNS.items():
            if any(pattern in feature_lower for pattern in patterns):
                return category
        
        return 'Otras'
    
    @classmethod
    def get_category_color(cls, category):
        """Obtener color asociado a una categoría"""
        colors = {
            'Coordinación': '#1f77b4',    # Azul
            'Energía': '#ff7f0e',         # Naranja
            'Stress': '#2ca02c',          # Verde
            'Histogramas': '#d62728',     # Rojo
            'Estadísticas': '#9467bd',    # Púrpura
            'Voronoi': '#8c564b',         # Marrón
            'Geometría': '#e377c2',       # Rosa
            'Temporal': '#7f7f7f',        # Gris
            'Identificadores': '#bcbd22', # Oliva
            'Otras': '#17becf'            # Cian
        }
        
        return colors.get(category, '#000000')


class ValidationRules:
    """Reglas de validación para datos y configuraciones"""
    
    # Validación de datasets
    MIN_SAMPLES = 10
    MAX_SAMPLES = 1000000
    MIN_FEATURES = 1
    MAX_FEATURES = 10000
    MAX_MISSING_PERCENTAGE = 50.0
    
    # Validación de modelos
    MIN_N_ESTIMATORS = 10
    MAX_N_ESTIMATORS = 1000
    MIN_TEST_SIZE = 0.1
    MAX_TEST_SIZE = 0.5
    
    # Validación de feature selection
    MIN_SELECTED_FEATURES = 2
    MIN_FEATURE_IMPORTANCE = 0.0001
    MIN_CORRELATION = 0.001
    
    @classmethod
    def validate_dataset(cls, data):
        """Validar dataset"""
        errors = []
        warnings = []
        
        # Validar tamaño
        if len(data) < cls.MIN_SAMPLES:
            errors.append(f"Dataset muy pequeño: {len(data)} < {cls.MIN_SAMPLES} muestras")
        elif len(data) > cls.MAX_SAMPLES:
            warnings.append(f"Dataset muy grande: {len(data)} > {cls.MAX_SAMPLES} muestras")
        
        # Validar features
        if len(data.columns) < cls.MIN_FEATURES:
            errors.append(f"Muy pocas features: {len(data.columns)} < {cls.MIN_FEATURES}")
        elif len(data.columns) > cls.MAX_FEATURES:
            warnings.append(f"Muchas features: {len(data.columns)} > {cls.MAX_FEATURES}")
        
        # Validar valores faltantes
        missing_pct = (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
        if missing_pct > cls.MAX_MISSING_PERCENTAGE:
            errors.append(f"Demasiados valores faltantes: {missing_pct:.1f}% > {cls.MAX_MISSING_PERCENTAGE}%")
        
        return {'errors': errors, 'warnings': warnings, 'valid': len(errors) == 0}
    
    @classmethod
    def validate_ml_params(cls, params):
        """Validar parámetros de ML"""
        errors = []
        
        # N estimators
        n_est = params.get('n_estimators', 100)
        if not (cls.MIN_N_ESTIMATORS <= n_est <= cls.MAX_N_ESTIMATORS):
            errors.append(f"n_estimators debe estar entre {cls.MIN_N_ESTIMATORS} y {cls.MAX_N_ESTIMATORS}")
        
        # Test size
        test_size = params.get('test_size', 0.2)
        if not (cls.MIN_TEST_SIZE <= test_size <= cls.MAX_TEST_SIZE):
            errors.append(f"test_size debe estar entre {cls.MIN_TEST_SIZE} y {cls.MAX_TEST_SIZE}")
        
        return {'errors': errors, 'valid': len(errors) == 0}
    
    @classmethod
    def validate_feature_selection(cls, selected_features, total_features):
        """Validar selección de features"""
        errors = []
        warnings = []
        
        if len(selected_features) < cls.MIN_SELECTED_FEATURES:
            errors.append(f"Muy pocas features seleccionadas: {len(selected_features)} < {cls.MIN_SELECTED_FEATURES}")
        
        reduction_pct = (1 - len(selected_features) / total_features) * 100
        if reduction_pct > 90:
            warnings.append(f"Reducción muy alta: {reduction_pct:.1f}% de features eliminadas")
        elif reduction_pct < 10:
            warnings.append(f"Reducción muy baja: {reduction_pct:.1f}% de features eliminadas")
        
        return {'errors': errors, 'warnings': warnings, 'valid': len(errors) == 0}


# Configuración por defecto que se puede sobreescribir
DEFAULT_CONFIG = {
    'model': ApplicationConfig.ML_CONFIG,
    'feature_selection': ApplicationConfig.FEATURE_SELECTION,
    'export': ApplicationConfig.EXPORT_CONFIG,
    'ui': ApplicationConfig.UI_CONFIG
}