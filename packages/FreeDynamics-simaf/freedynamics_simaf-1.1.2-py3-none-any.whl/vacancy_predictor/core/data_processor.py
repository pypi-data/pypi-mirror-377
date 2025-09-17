"""
Data processing module for handling various file formats including .dump files
"""

import pandas as pd
import numpy as np
import pickle
import json
import csv
import os
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import logging
from ..utils.validators import DataValidator
from ..utils.file_handlers import FileHandler

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles data loading, preprocessing, and feature selection
    """
    
    def __init__(self):
        self.data = None
        self.original_data = None
        self.features = None
        self.target = None
        self.target_column = None
        self.file_handler = FileHandler()
        self.validator = DataValidator()
        
    def load_data(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load data from various file formats including .dump files
        
        Args:
            file_path: Path to the data file
            
        Returns:
            pd.DataFrame: Loaded data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            extension = file_path.suffix.lower()
            
            if extension == '.dump':
                self.data = self._load_dump_file(file_path)
            elif extension == '.csv':
                self.data = pd.read_csv(file_path)
            elif extension in ['.json', '.jsonl']:
                self.data = self._load_json_file(file_path)
            elif extension in ['.xlsx', '.xls']:
                self.data = pd.read_excel(file_path)
            elif extension == '.pkl':
                with open(file_path, 'rb') as f:
                    self.data = pickle.load(f)
                if not isinstance(self.data, pd.DataFrame):
                    self.data = pd.DataFrame(self.data)
            else:
                raise ValueError(f"Unsupported file format: {extension}")
                
            # Store original data for reference
            self.original_data = self.data.copy()
            
            # Basic validation
            self.validator.validate_dataframe(self.data)
            
            logger.info(f"Successfully loaded data with shape: {self.data.shape}")
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            raise
    
    def _load_dump_file(self, file_path: Path) -> pd.DataFrame:
        """
        Load data from .dump files (assumes pickle format)
        """
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                
            # Handle different dump formats
            if isinstance(data, pd.DataFrame):
                return data
            elif isinstance(data, dict):
                return pd.DataFrame(data)
            elif isinstance(data, list):
                # Try to convert list to DataFrame
                if len(data) > 0 and isinstance(data[0], dict):
                    return pd.DataFrame(data)
                else:
                    # Create DataFrame with single column
                    return pd.DataFrame({'data': data})
            else:
                # Try to convert to DataFrame
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error loading dump file: {str(e)}")
            # Try alternative approaches
            try:
                # Try reading as text and parsing
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Try JSON parsing
                    data = json.loads(content)
                    return pd.DataFrame(data)
            except:
                raise ValueError(f"Unable to parse dump file: {file_path}")
    
    def _load_json_file(self, file_path: Path) -> pd.DataFrame:
        """Load JSON or JSONL files"""
        if file_path.suffix.lower() == '.jsonl':
            # Handle JSON Lines format
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data.append(json.loads(line.strip()))
            return pd.DataFrame(data)
        else:
            # Handle regular JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return pd.DataFrame(data)
    
    def export_to_csv(self, output_path: Union[str, Path]) -> None:
        """
        Export current data to CSV format
        """
        if self.data is None:
            raise ValueError("No data loaded to export")
            
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.data.to_csv(output_path, index=False)
        logger.info(f"Data exported to: {output_path}")
    
    def get_column_info(self) -> Dict[str, Dict]:
        """
        Get detailed information about columns
        """
        if self.data is None:
            return {}
            
        info = {}
        for col in self.data.columns:
            info[col] = {
                'dtype': str(self.data[col].dtype),
                'null_count': self.data[col].isnull().sum(),
                'unique_count': self.data[col].nunique(),
                'sample_values': self.data[col].dropna().head(5).tolist()
            }
            
            if self.data[col].dtype in ['int64', 'float64']:
                info[col].update({
                    'min': self.data[col].min(),
                    'max': self.data[col].max(),
                    'mean': self.data[col].mean(),
                    'std': self.data[col].std()
                })
                
        return info
    
    def select_features(self, feature_columns: List[str]) -> None:
        """
        Select feature columns for training
        """
        if self.data is None:
            raise ValueError("No data loaded")
            
        missing_cols = [col for col in feature_columns if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"Columns not found: {missing_cols}")
            
        self.features = self.data[feature_columns].copy()
        logger.info(f"Selected {len(feature_columns)} features")
    
    def set_target(self, target_column: str) -> None:
        """
        Set target column for prediction
        """
        if self.data is None:
            raise ValueError("No data loaded")
            
        if target_column not in self.data.columns:
            raise ValueError(f"Target column '{target_column}' not found")
            
        self.target = self.data[target_column].copy()
        self.target_column = target_column
        logger.info(f"Set target column: {target_column}")
    
    def preprocess_data(self, 
                       handle_missing: str = 'drop',
                       encode_categorical: bool = True,
                       scale_numeric: bool = False) -> None:
        """
        Preprocess the data
        
        Args:
            handle_missing: How to handle missing values ('drop', 'fill_mean', 'fill_median', 'fill_mode')
            encode_categorical: Whether to encode categorical variables
            scale_numeric: Whether to scale numeric variables
        """
        if self.features is None or self.target is None:
            raise ValueError("Features and target must be selected first")
        
        # Handle missing values
        if handle_missing == 'drop':
            # Drop rows with any missing values
            mask = ~(self.features.isnull().any(axis=1) | self.target.isnull())
            self.features = self.features[mask]
            self.target = self.target[mask]
        elif handle_missing == 'fill_mean':
            self.features = self.features.fillna(self.features.mean())
        elif handle_missing == 'fill_median':
            self.features = self.features.fillna(self.features.median())
        elif handle_missing == 'fill_mode':
            self.features = self.features.fillna(self.features.mode().iloc[0])
            
        # Encode categorical variables
        if encode_categorical:
            categorical_columns = self.features.select_dtypes(include=['object']).columns
            for col in categorical_columns:
                self.features[col] = pd.Categorical(self.features[col]).codes
                
        # Scale numeric variables
        if scale_numeric:
            from sklearn.preprocessing import StandardScaler
            numeric_columns = self.features.select_dtypes(include=[np.number]).columns
            scaler = StandardScaler()
            self.features[numeric_columns] = scaler.fit_transform(self.features[numeric_columns])
            
        logger.info("Data preprocessing completed")
    
    def get_training_data(self) -> tuple:
        """
        Get features and target for training
        
        Returns:
            tuple: (features, target)
        """
        if self.features is None or self.target is None:
            raise ValueError("Features and target must be selected first")
            
        return self.features, self.target
    
    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the data
        """
        if self.data is None:
            return {}
            
        return {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'memory_usage': self.data.memory_usage(deep=True).sum(),
            'numeric_columns': list(self.data.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(self.data.select_dtypes(include=['object']).columns)
        }