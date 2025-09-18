"""
data_manager.py
Gestión centralizada de datos para Vacancy Predictor
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging
import sys
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from .application_config import ApplicationConfig, ValidationRules

logger = logging.getLogger(__name__)

class DataManager:
    """
    Gestor centralizado de datos de la aplicación
    Maneja carga, validación, transformación y exportación de datos
    """
    
    def __init__(self):
        """Inicializar gestor de datos"""
        self.datasets = {}
        self.metadata = {}
        self.config = ApplicationConfig()
        
        # Estadísticas globales
        self.global_stats = {
            'total_samples': 0,
            'total_features': 0,
            'total_memory_mb': 0,
            'datasets_loaded': 0
        }
        
        logger.info("DataManager initialized")
    
    # =============================================================================
    # MÉTODOS DE CARGA DE DATOS
    # =============================================================================
    
    def load_dataset_from_file(self, file_path: str) -> pd.DataFrame:
        """
        Cargar dataset desde archivo
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            DataFrame con los datos cargados
            
        Raises:
            ValueError: Si el formato no es soportado
            FileNotFoundError: Si el archivo no existe
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        if not self.config.is_supported_file(file_path):
            raise ValueError(f"Formato de archivo no soportado: {file_path.suffix}")
        
        try:
            # Determinar método de carga según extensión
            if file_path.suffix.lower() == '.csv':
                data = self._load_csv(file_path)
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                data = self._load_excel(file_path)
            else:
                raise ValueError(f"Formato no implementado: {file_path.suffix}")
            
            # Validar datos cargados
            validation_result = self._validate_dataset(data)
            
            # Generar metadata
            metadata = self._generate_metadata(data, file_path, validation_result)
            
            # Almacenar dataset
            dataset_id = self._generate_dataset_id(file_path)
            self.add_dataset(data, dataset_id, metadata)
            
            logger.info(f"Dataset cargado exitosamente: {file_path.name} ({len(data)} filas, {len(data.columns)} columnas)")
            
            return data
            
        except Exception as e:
            logger.error(f"Error cargando dataset {file_path}: {e}")
            raise
    
    def _load_csv(self, file_path: Path) -> pd.DataFrame:
        """Cargar archivo CSV con configuración optimizada"""
        try:
            # Intentar con índice en primera columna
            data = pd.read_csv(file_path, index_col=0)
        except:
            # Si falla, cargar sin índice
            data = pd.read_csv(file_path)
        
        return data
    
    def _load_excel(self, file_path: Path) -> pd.DataFrame:
        """Cargar archivo Excel"""
        return pd.read_excel(file_path)
    
    def add_dataset(self, data: pd.DataFrame, dataset_id: str, metadata: Optional[Dict] = None):
        """
        Agregar dataset al manager
        
        Args:
            data: DataFrame con los datos
            dataset_id: Identificador único del dataset
            metadata: Metadatos opcionales
        """
        # Validar dataset
        validation_result = self._validate_dataset(data)
        if not validation_result['valid']:
            logger.warning(f"Dataset {dataset_id} tiene errores de validación: {validation_result['errors']}")
        
        # Generar metadata si no se proporciona
        if metadata is None:
            metadata = self._generate_metadata(data, dataset_id, validation_result)
        
        # Almacenar dataset y metadata
        self.datasets[dataset_id] = data.copy()
        self.metadata[dataset_id] = metadata
        
        # Actualizar estadísticas globales
        self._update_global_stats()
        
        logger.info(f"Dataset agregado: {dataset_id} ({len(data)} filas, {len(data.columns)} columnas)")
    
    # =============================================================================
    # MÉTODOS DE VALIDACIÓN Y METADATA
    # =============================================================================
    
    def _validate_dataset(self, data: pd.DataFrame) -> Dict:
        """Validar dataset usando reglas de validación"""
        return ValidationRules.validate_dataset(data)
    
    def _generate_metadata(self, data: pd.DataFrame, source: str, validation_result: Dict) -> Dict:
        """Generar metadata para un dataset"""
        metadata = {
            'source': str(source),
            'created_at': datetime.now().isoformat(),
            'shape': data.shape,
            'columns': list(data.columns),
            'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
            'memory_usage_mb': data.memory_usage(deep=True).sum() / (1024 * 1024),
            'validation': validation_result
        }
        
        # Estadísticas descriptivas para columnas numéricas
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            metadata['numeric_stats'] = {
                col: {
                    'mean': float(data[col].mean()),
                    'std': float(data[col].std()),
                    'min': float(data[col].min()),
                    'max': float(data[col].max()),
                    'missing_count': int(data[col].isnull().sum()),
                    'missing_pct': float((data[col].isnull().sum() / len(data)) * 100)
                }
                for col in numeric_cols
            }
        
        # Información de columnas de texto
        text_cols = data.select_dtypes(include=['object']).columns
        if len(text_cols) > 0:
            metadata['text_stats'] = {
                col: {
                    'unique_count': int(data[col].nunique()),
                    'missing_count': int(data[col].isnull().sum()),
                    'most_common': str(data[col].mode().iloc[0]) if len(data[col].mode()) > 0 else None
                }
                for col in text_cols
            }
        
        return metadata
    
    def _generate_dataset_id(self, source) -> str:
        """Generar ID único para dataset"""
        base_name = Path(source).stem if isinstance(source, (str, Path)) else str(source)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}"
    
    def _update_global_stats(self):
        """Actualizar estadísticas globales"""
        self.global_stats = {
            'total_samples': sum(len(data) for data in self.datasets.values()),
            'total_features': sum(len(data.columns) for data in self.datasets.values()),
            'total_memory_mb': sum(self.metadata[k]['memory_usage_mb'] for k in self.metadata.keys()),
            'datasets_loaded': len(self.datasets)
        }
    
    # =============================================================================
    # MÉTODOS DE CONSULTA Y ESTADÍSTICAS
    # =============================================================================
    
    def get_dataset(self, dataset_id: str) -> Optional[pd.DataFrame]:
        """Obtener dataset por ID"""
        return self.datasets.get(dataset_id)
    
    def get_dataset_metadata(self, dataset_id: str) -> Optional[Dict]:
        """Obtener metadata de dataset"""
        return self.metadata.get(dataset_id)
    
    def list_datasets(self) -> List[str]:
        """Listar IDs de todos los datasets"""
        return list(self.datasets.keys())
    
    def get_datasets_info(self) -> Dict:
        """Obtener información resumida de todos los datasets"""
        info = {}
        for dataset_id in self.datasets.keys():
            data = self.datasets[dataset_id]
            metadata = self.metadata[dataset_id]
            
            info[dataset_id] = {
                'shape': data.shape,
                'memory_mb': metadata['memory_usage_mb'],
                'created_at': metadata['created_at'],
                'source': metadata['source'],
                'valid': metadata['validation']['valid']
            }
        
        return info
    
    def get_comprehensive_statistics(self) -> Dict:
        """Obtener estadísticas comprehensivas de todos los datasets"""
        stats = {
            'global': self.global_stats.copy(),
            'datasets': {}
        }
        
        for dataset_id, data in self.datasets.items():
            metadata = self.metadata[dataset_id]
            
            # Estadísticas por dataset
            dataset_stats = {
                'basic_info': {
                    'rows': len(data),
                    'columns': len(data.columns),
                    'memory_mb': metadata['memory_usage_mb'],
                    'missing_values_pct': (data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100
                },
                'column_types': dict(data.dtypes.value_counts()),
                'validation': metadata['validation']
            }
            
            # Target column info si existe
            if 'vacancies' in data.columns:
                target_stats = data['vacancies'].describe()
                dataset_stats['target_stats'] = {
                    'mean': float(target_stats['mean']),
                    'std': float(target_stats['std']),
                    'min': float(target_stats['min']),
                    'max': float(target_stats['max']),
                    'range': float(target_stats['max'] - target_stats['min'])
                }
            
            stats['datasets'][dataset_id] = dataset_stats
        
        return stats
    
    def get_memory_usage(self) -> Dict:
        """Obtener información detallada de uso de memoria"""
        memory_info = {
            'total_datasets_mb': self.global_stats['total_memory_mb'],
            'datasets': {}
        }
        
        for dataset_id, data in self.datasets.items():
            memory_info['datasets'][dataset_id] = {
                'memory_mb': self.metadata[dataset_id]['memory_usage_mb'],
                'samples': len(data),
                'features': len(data.columns),
                'mb_per_sample': self.metadata[dataset_id]['memory_usage_mb'] / len(data) if len(data) > 0 else 0
            }
        
        # Información del proceso si psutil está disponible
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info['process'] = {
                'rss_mb': process.memory_info().rss / (1024 * 1024),
                'vms_mb': process.memory_info().vms / (1024 * 1024),
                'percent': process.memory_percent()
            }
        except ImportError:
            memory_info['process'] = {'status': 'psutil not available'}
        
        return memory_info
    
    # =============================================================================
    # MÉTODOS DE ANÁLISIS DE FEATURES
    # =============================================================================
    
    def analyze_features(self, dataset_id: str) -> Dict:
        """Analizar features de un dataset específico"""
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset {dataset_id} no encontrado")
        
        data = self.datasets[dataset_id]
        
        # Identificar tipos de features
        numeric_features = data.select_dtypes(include=[np.number]).columns.tolist()
        text_features = data.select_dtypes(include=['object']).columns.tolist()
        
        # Excluir columnas especiales
        exclude_cols = ['vacancies', 'filename', 'file_path']
        feature_columns = [col for col in numeric_features if col not in exclude_cols]
        
        analysis = {
            'total_features': len(data.columns),
            'numeric_features': len(numeric_features),
            'text_features': len(text_features),
            'usable_features': len(feature_columns),
            'feature_columns': feature_columns,
            'excluded_columns': [col for col in data.columns if col not in feature_columns],
            'feature_categories': {},
            'quality_metrics': {}
        }
        
        # Categorización automática de features
        from .application_config import FeatureCategories
        
        for feature in feature_columns:
            category = FeatureCategories.categorize_feature(feature)
            if category not in analysis['feature_categories']:
                analysis['feature_categories'][category] = []
            analysis['feature_categories'][category].append(feature)
        
        # Métricas de calidad por feature
        target_col = 'vacancies' if 'vacancies' in data.columns else None
        
        for feature in feature_columns:
            feature_data = data[feature]
            
            quality_metrics = {
                'missing_pct': (feature_data.isnull().sum() / len(data)) * 100,
                'unique_values': feature_data.nunique(),
                'zero_values_pct': (feature_data == 0).sum() / len(data) * 100 if feature_data.dtype in [np.number] else 0,
                'std_dev': float(feature_data.std()) if feature_data.dtype in [np.number] else None,
                'range': float(feature_data.max() - feature_data.min()) if feature_data.dtype in [np.number] else None
            }
            
            # Correlación con target si está disponible
            if target_col and feature != target_col:
                try:
                    correlation = feature_data.corr(data[target_col])
                    quality_metrics['correlation'] = float(correlation) if not pd.isna(correlation) else 0.0
                except:
                    quality_metrics['correlation'] = 0.0
            
            analysis['quality_metrics'][feature] = quality_metrics
        
        return analysis
    
    # =============================================================================
    # MÉTODOS DE EXPORTACIÓN
    # =============================================================================
    
    def export_dataset(self, dataset_id: str, output_path: str, format: str = 'csv') -> bool:
        """
        Exportar dataset específico
        
        Args:
            dataset_id: ID del dataset a exportar
            output_path: Ruta de salida
            format: Formato de exportación ('csv', 'excel')
            
        Returns:
            True si la exportación fue exitosa
        """
        if dataset_id not in self.datasets:
            raise ValueError(f"Dataset {dataset_id} no encontrado")
        
        data = self.datasets[dataset_id]
        output_path = Path(output_path)
        
        try:
            if format.lower() == 'csv':
                data.to_csv(output_path)
            elif format.lower() in ['excel', 'xlsx']:
                data.to_excel(output_path, index=False)
            else:
                raise ValueError(f"Formato no soportado: {format}")
            
            logger.info(f"Dataset {dataset_id} exportado a {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando dataset {dataset_id}: {e}")
            raise
    
    def export_all_data(self, base_directory: str, additional_data: Optional[Dict] = None) -> Dict:
        """
        Exportar todos los datos y metadatos
        
        Args:
            base_directory: Directorio base para la exportación
            additional_data: Datos adicionales de la aplicación
            
        Returns:
            Información sobre la exportación realizada
        """
        export_dir = Path(base_directory) / f"vacancy_predictor_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        export_info = {
            'directory': str(export_dir),
            'timestamp': datetime.now().isoformat(),
            'files_count': 0,
            'datasets_exported': 0,
            'errors': []
        }
        
        try:
            # Exportar datasets
            for dataset_id, data in self.datasets.items():
                try:
                    dataset_file = export_dir / f"{dataset_id}.csv"
                    data.to_csv(dataset_file)
                    exported_files.append(dataset_file.name)
                    export_info['datasets_exported'] += 1
                except Exception as e:
                    export_info['errors'].append(f"Error exportando {dataset_id}: {e}")
            
            # Exportar metadata
            metadata_file = export_dir / "datasets_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2, default=str)
            exported_files.append(metadata_file.name)
            
            # Exportar estadísticas globales
            stats_file = export_dir / "global_statistics.json"
            with open(stats_file, 'w') as f:
                json.dump(self.get_comprehensive_statistics(), f, indent=2, default=str)
            exported_files.append(stats_file.name)
            
            # Exportar datos adicionales si se proporcionan
            if additional_data:
                for key, value in additional_data.items():
                    try:
                        additional_file = export_dir / f"{key}.json"
                        with open(additional_file, 'w') as f:
                            json.dump(value, f, indent=2, default=str)
                        exported_files.append(additional_file.name)
                    except Exception as e:
                        export_info['errors'].append(f"Error exportando {key}: {e}")
            
            # Crear reporte de exportación
            report_lines = [
                "VACANCY PREDICTOR - EXPORT REPORT",
                "=" * 40,
                f"Export Date: {export_info['timestamp']}",
                f"Export Directory: {export_dir}",
                f"Datasets Exported: {export_info['datasets_exported']}",
                f"Total Files: {len(exported_files)}",
                "",
                "EXPORTED FILES:",
                "-" * 20
            ]
            
            for file in exported_files:
                report_lines.append(f"✓ {file}")
            
            if export_info['errors']:
                report_lines.extend([
                    "",
                    "ERRORS:",
                    "-" * 10
                ])
                for error in export_info['errors']:
                    report_lines.append(f"✗ {error}")
            
            # Guardar reporte
            report_file = export_dir / "export_report.txt"
            with open(report_file, 'w') as f:
                f.write("\n".join(report_lines))
            exported_files.append(report_file.name)
            
            export_info['files_count'] = len(exported_files)
            export_info['exported_files'] = exported_files
            
            logger.info(f"Exportación completa: {len(exported_files)} archivos en {export_dir}")
            
        except Exception as e:
            logger.error(f"Error durante exportación: {e}")
            export_info['errors'].append(f"Error general: {e}")
            raise
        
        return export_info
    
    # =============================================================================
    # MÉTODOS DE LIMPIEZA Y RESET
    # =============================================================================
    
    def remove_dataset(self, dataset_id: str) -> bool:
        """Eliminar dataset específico"""
        if dataset_id in self.datasets:
            del self.datasets[dataset_id]
            del self.metadata[dataset_id]
            self._update_global_stats()
            logger.info(f"Dataset {dataset_id} eliminado")
            return True
        return False
    
    def cleanup(self):
        """Limpieza de recursos antes del cierre"""
        logger.info("Cleaning up DataManager resources")
        # Aquí se pueden agregar operaciones de limpieza específicas
        pass
    
    def reset(self):
        """Reset completo del gestor de datos"""
        self.datasets.clear()
        self.metadata.clear()
        self.global_stats = {
            'total_samples': 0,
            'total_features': 0,
            'total_memory_mb': 0,
            'datasets_loaded': 0
        }
        logger.info("DataManager reset completed")
    
    # =============================================================================
    # MÉTODOS AUXILIARES
    # =============================================================================
    
    def get_feature_suggestions(self, dataset_id: str, min_importance: float = 0.01) -> List[str]:
        """Obtener sugerencias de features basadas en análisis"""
        analysis = self.analyze_features(dataset_id)
        
        # Filtrar features por calidad
        suggested_features = []
        
        for feature, metrics in analysis['quality_metrics'].items():
            # Criterios de selección
            if (metrics['missing_pct'] < 20 and  # Menos del 20% de valores faltantes
                metrics.get('correlation', 0) != 0 and  # Tiene correlación calculada
                abs(metrics.get('correlation', 0)) > 0.05):  # Correlación mínima
                suggested_features.append(feature)
        
        return suggested_features
    
    def compare_datasets(self, dataset_id1: str, dataset_id2: str) -> Dict:
        """Comparar dos datasets"""
        if dataset_id1 not in self.datasets or dataset_id2 not in self.datasets:
            raise ValueError("Uno o ambos datasets no encontrados")
        
        data1 = self.datasets[dataset_id1]
        data2 = self.datasets[dataset_id2]
        
        comparison = {
            'dataset1': {
                'id': dataset_id1,
                'shape': data1.shape,
                'columns': set(data1.columns)
            },
            'dataset2': {
                'id': dataset_id2,
                'shape': data2.shape,
                'columns': set(data2.columns)
            },
            'comparison': {
                'common_columns': list(set(data1.columns) & set(data2.columns)),
                'unique_to_1': list(set(data1.columns) - set(data2.columns)),
                'unique_to_2': list(set(data2.columns) - set(data1.columns)),
                'shape_difference': (data1.shape[0] - data2.shape[0], data1.shape[1] - data2.shape[1])
            }
        }
        
        return comparison