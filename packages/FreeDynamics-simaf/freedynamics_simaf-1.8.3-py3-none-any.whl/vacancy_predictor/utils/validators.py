"""
Data validation utilities
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Validates data quality and consistency
    """
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive DataFrame validation
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dict with validation results
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        # Basic checks
        if df.empty:
            results['errors'].append("DataFrame is empty")
            results['is_valid'] = False
            return results
        
        # Check for completely empty columns
        empty_cols = df.columns[df.isnull().all()].tolist()
        if empty_cols:
            results['warnings'].append(f"Completely empty columns: {empty_cols}")
        
        # Check for duplicate columns
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            results['warnings'].append(f"Duplicate column names: {duplicate_cols}")
        
        # Check for excessive missing data
        missing_pct = (df.isnull().sum() / len(df)) * 100
        high_missing = missing_pct[missing_pct > 50].index.tolist()
        if high_missing:
            results['warnings'].append(f"Columns with >50% missing data: {high_missing}")
        
        # Check for constant columns
        constant_cols = []
        for col in df.columns:
            if df[col].nunique() <= 1:
                constant_cols.append(col)
        if constant_cols:
            results['warnings'].append(f"Constant columns (no variation): {constant_cols}")
        
        # Memory usage check
        memory_mb = df.memory_usage(deep=True).sum() / 1024**2
        if memory_mb > 500:  # 500MB threshold
            results['warnings'].append(f"Large dataset: {memory_mb:.1f}MB")
        
        # Store info
        results['info'] = {
            'shape': df.shape,
            'memory_usage_mb': memory_mb,
            'missing_data_pct': missing_pct.to_dict(),
            'dtypes': df.dtypes.value_counts().to_dict()
        }
        
        self.validation_results = results
        return results
    
    def validate_features_target(self, features: pd.DataFrame, 
                                target: pd.Series) -> Dict[str, Any]:
        """
        Validate features and target for ML training
        """
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check alignment
        if len(features) != len(target):
            results['errors'].append("Features and target have different lengths")
            results['is_valid'] = False
        
        # Check for missing values in target
        if target.isnull().any():
            results['errors'].append("Target contains missing values")
            results['is_valid'] = False
        
        # Check for infinite values
        if np.isinf(features.select_dtypes(include=[np.number])).any().any():
            results['warnings'].append("Features contain infinite values")
        
        # Check feature variation
        low_variance_features = []
        for col in features.select_dtypes(include=[np.number]).columns:
            if features[col].var() < 1e-6:
                low_variance_features.append(col)
        
        if low_variance_features:
            results['warnings'].append(f"Low variance features: {low_variance_features}")
        
        return results
    
    def suggest_preprocessing(self, df: pd.DataFrame) -> List[str]:
        """
        Suggest preprocessing steps based on data analysis
        """
        suggestions = []
        
        # Missing data suggestions
        missing_pct = (df.isnull().sum() / len(df)) * 100
        if missing_pct.max() > 0:
            suggestions.append("Handle missing values (imputation or removal)")
        
        # Categorical encoding suggestions
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            suggestions.append("Encode categorical variables")
        
        # Scaling suggestions
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            ranges = df[numeric_cols].max() - df[numeric_cols].min()
            if ranges.max() / ranges.min() > 100:  # Large scale differences
                suggestions.append("Consider feature scaling/normalization")
        
        # Outlier detection suggestions
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > len(df) * 0.05:  # More than 5% outliers
                suggestions.append(f"Review outliers in column '{col}'")
                break
        
        return suggestions