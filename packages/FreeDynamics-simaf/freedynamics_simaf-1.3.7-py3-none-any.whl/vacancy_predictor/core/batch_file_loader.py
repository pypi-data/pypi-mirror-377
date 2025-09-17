# vacancy_predictor/core/batch_file_loader.py
"""
Batch file loader for processing multiple dump files from a directory
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import pickle
from datetime import datetime

logger = logging.getLogger(__name__)

class BatchFileLoader:
    """
    Handle batch loading and processing of multiple dump files
    """
    
    def __init__(self):
        self.loaded_files = {}
        self.file_metadata = {}
        self.combined_data = None
        self.processing_stats = {}
        self.supported_extensions = {'.csv', '.xlsx', '.xls', '.json', '.pkl', '.txt', '.tsv'}
    
    def scan_directory(self, directory_path: str) -> Dict[str, List[str]]:
        """
        Scan directory for supported files
        
        Args:
            directory_path: Path to directory to scan
            
        Returns:
            Dictionary with file types as keys and file paths as values
        """
        try:
            directory = Path(directory_path)
            if not directory.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            files_by_type = {}
            all_files = []
            
            # Scan directory recursively
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    extension = file_path.suffix.lower()
                    if extension in self.supported_extensions:
                        file_type = self._get_file_type(extension)
                        
                        if file_type not in files_by_type:
                            files_by_type[file_type] = []
                        
                        files_by_type[file_type].append(str(file_path))
                        all_files.append(str(file_path))
            
            # Store metadata
            self.file_metadata['scan_directory'] = directory_path
            self.file_metadata['scan_time'] = datetime.now().isoformat()
            self.file_metadata['total_files'] = len(all_files)
            self.file_metadata['files_by_type'] = files_by_type
            
            logger.info(f"Scanned directory: {directory_path}")
            logger.info(f"Found {len(all_files)} supported files")
            
            return files_by_type
            
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
            raise
    
    def _get_file_type(self, extension: str) -> str:
        """Get file type category from extension"""
        type_mapping = {
            '.csv': 'CSV',
            '.tsv': 'CSV',
            '.txt': 'CSV',
            '.xlsx': 'Excel',
            '.xls': 'Excel',
            '.json': 'JSON',
            '.pkl': 'Pickle'
        }
        return type_mapping.get(extension, 'Unknown')
    
    def load_single_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Load a single file and return DataFrame with metadata
        
        Args:
            file_path: Path to file to load
            
        Returns:
            Tuple of (DataFrame, metadata_dict)
        """
        try:
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            
            # File metadata
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'extension': extension,
                'load_time': None,
                'load_success': False,
                'error_message': None,
                'rows': 0,
                'columns': 0
            }
            
            start_time = datetime.now()
            
            # Load based on file type
            if extension in ['.csv', '.txt', '.tsv']:
                data = self._load_csv_file(file_path)
            elif extension in ['.xlsx', '.xls']:
                data = self._load_excel_file(file_path)
            elif extension == '.json':
                data = self._load_json_file(file_path)
            elif extension == '.pkl':
                data = self._load_pickle_file(file_path)
            else:
                raise ValueError(f"Unsupported file type: {extension}")
            
            # Update metadata
            load_time = (datetime.now() - start_time).total_seconds()
            metadata.update({
                'load_time': load_time,
                'load_success': True,
                'rows': len(data),
                'columns': len(data.columns),
                'memory_usage': data.memory_usage(deep=True).sum()
            })
            
            logger.info(f"Loaded {file_path.name}: {len(data)} rows, {len(data.columns)} columns")
            
            return data, metadata
            
        except Exception as e:
            metadata['error_message'] = str(e)
            logger.error(f"Error loading {file_path}: {e}")
            return pd.DataFrame(), metadata
    
    def _load_csv_file(self, file_path: Path) -> pd.DataFrame:
        """Load CSV file with automatic delimiter detection"""
        # Try common delimiters
        delimiters = [',', ';', '\t', '|']
        
        for delimiter in delimiters:
            try:
                data = pd.read_csv(file_path, delimiter=delimiter, nrows=5)
                if len(data.columns) > 1:  # More than one column suggests correct delimiter
                    return pd.read_csv(file_path, delimiter=delimiter)
            except:
                continue
        
        # Default fallback
        return pd.read_csv(file_path)
    
    def _load_excel_file(self, file_path: Path) -> pd.DataFrame:
        """Load Excel file"""
        # Try to load first sheet
        return pd.read_excel(file_path)
    
    def _load_json_file(self, file_path: Path) -> pd.DataFrame:
        """Load JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to DataFrame
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # If it's a dictionary, try to convert to DataFrame
            return pd.DataFrame([data])
        else:
            raise ValueError("JSON format not supported for DataFrame conversion")
    
    def _load_pickle_file(self, file_path: Path) -> pd.DataFrame:
        """Load pickle file"""
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        if isinstance(data, pd.DataFrame):
            return data
        else:
            raise ValueError("Pickle file does not contain a DataFrame")
    
    def load_batch(self, file_paths: List[str], max_workers: int = 4) -> Dict[str, Dict[str, Any]]:
        """
        Load multiple files in parallel
        
        Args:
            file_paths: List of file paths to load
            max_workers: Maximum number of parallel workers
            
        Returns:
            Dictionary with results for each file
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.load_single_file, file_path): file_path 
                for file_path in file_paths
            }
            
            # Collect results
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    data, metadata = future.result()
                    
                    # Store results
                    file_key = Path(file_path).stem
                    results[file_key] = {
                        'data': data,
                        'metadata': metadata
                    }
                    
                    # Store in loaded_files if successful
                    if metadata['load_success']:
                        self.loaded_files[file_key] = data
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results[Path(file_path).stem] = {
                        'data': pd.DataFrame(),
                        'metadata': {
                            'file_path': file_path,
                            'load_success': False,
                            'error_message': str(e)
                        }
                    }
        
        # Update processing stats
        self.processing_stats = self._calculate_processing_stats(results)
        
        return results
    
    def _calculate_processing_stats(self, results: Dict) -> Dict[str, Any]:
        """Calculate processing statistics"""
        total_files = len(results)
        successful_files = sum(1 for r in results.values() if r['metadata']['load_success'])
        failed_files = total_files - successful_files
        
        total_rows = sum(r['metadata'].get('rows', 0) for r in results.values())
        total_columns = max(r['metadata'].get('columns', 0) for r in results.values()) if results else 0
        total_memory = sum(r['metadata'].get('memory_usage', 0) for r in results.values())
        
        return {
            'total_files': total_files,
            'successful_files': successful_files,
            'failed_files': failed_files,
            'success_rate': (successful_files / total_files * 100) if total_files > 0 else 0,
            'total_rows': total_rows,
            'total_columns': total_columns,
            'total_memory_mb': total_memory / (1024 * 1024),
            'processing_time': datetime.now().isoformat()
        }
    
    def combine_dataframes(self, 
                          strategy: str = 'concat', 
                          ignore_index: bool = True,
                          add_source_column: bool = True) -> pd.DataFrame:
        """
        Combine loaded DataFrames into a single DataFrame
        
        Args:
            strategy: How to combine ('concat', 'union', 'intersection')
            ignore_index: Whether to reset index
            add_source_column: Whether to add a column indicating source file
            
        Returns:
            Combined DataFrame
        """
        if not self.loaded_files:
            raise ValueError("No files loaded")
        
        dataframes = []
        
        for file_key, df in self.loaded_files.items():
            if df.empty:
                continue
                
            # Add source column if requested
            if add_source_column:
                df = df.copy()
                df['_source_file'] = file_key
            
            dataframes.append(df)
        
        if not dataframes:
            return pd.DataFrame()
        
        # Combine based on strategy
        if strategy == 'concat':
            # Simple concatenation
            self.combined_data = pd.concat(dataframes, ignore_index=ignore_index, sort=False)
        
        elif strategy == 'union':
            # Union of columns (all columns from all DataFrames)
            self.combined_data = pd.concat(dataframes, ignore_index=ignore_index, sort=False)
        
        elif strategy == 'intersection':
            # Only common columns
            if len(dataframes) > 1:
                common_columns = set(dataframes[0].columns)
                for df in dataframes[1:]:
                    common_columns = common_columns.intersection(set(df.columns))
                
                # Filter DataFrames to common columns
                filtered_dfs = [df[list(common_columns)] for df in dataframes]
                self.combined_data = pd.concat(filtered_dfs, ignore_index=ignore_index)
            else:
                self.combined_data = dataframes[0]
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        logger.info(f"Combined {len(dataframes)} DataFrames into single DataFrame with {len(self.combined_data)} rows")
        
        return self.combined_data
    
    def get_summary_report(self) -> Dict[str, Any]:
        """Get summary report of batch loading operation"""
        report = {
            'file_metadata': self.file_metadata,
            'processing_stats': self.processing_stats,
            'loaded_files_summary': {},
            'combined_data_info': None
        }
        
        # Individual file summaries
        for file_key, df in self.loaded_files.items():
            report['loaded_files_summary'][file_key] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'null_counts': df.isnull().sum().to_dict(),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
            }
        
        # Combined data info
        if self.combined_data is not None:
            report['combined_data_info'] = {
                'shape': self.combined_data.shape,
                'columns': list(self.combined_data.columns),
                'memory_usage_mb': self.combined_data.memory_usage(deep=True).sum() / (1024 * 1024),
                'duplicate_rows': self.combined_data.duplicated().sum()
            }
        
        return report
    
    def export_summary(self, output_path: str) -> None:
        """Export summary report to JSON file"""
        report = self.get_summary_report()
        
        # Convert non-serializable objects to strings
        def convert_for_json(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif hasattr(obj, 'dtype'):
                return str(obj)
            return obj
        
        # Clean report for JSON serialization
        import json
        clean_report = json.loads(json.dumps(report, default=convert_for_json))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(clean_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary report exported to: {output_path}")
    
    def filter_files_by_pattern(self, pattern: str) -> Dict[str, pd.DataFrame]:
        """
        Filter loaded files by filename pattern
        
        Args:
            pattern: Regex pattern to match filenames
            
        Returns:
            Dictionary of matching files
        """
        import re
        
        filtered_files = {}
        regex = re.compile(pattern, re.IGNORECASE)
        
        for file_key, df in self.loaded_files.items():
            if regex.search(file_key):
                filtered_files[file_key] = df
        
        return filtered_files
    
    def get_column_analysis(self) -> Dict[str, Any]:
        """
        Analyze columns across all loaded files
        
        Returns:
            Analysis of column consistency across files
        """
        if not self.loaded_files:
            return {}
        
        all_columns = set()
        file_columns = {}
        
        # Collect all columns
        for file_key, df in self.loaded_files.items():
            file_columns[file_key] = set(df.columns)
            all_columns.update(df.columns)
        
        # Find common and unique columns
        common_columns = set.intersection(*file_columns.values()) if file_columns else set()
        
        column_analysis = {
            'total_unique_columns': len(all_columns),
            'common_columns': list(common_columns),
            'common_columns_count': len(common_columns),
            'all_columns': list(all_columns),
            'file_specific_columns': {},
            'column_frequency': {}
        }
        
        # Column frequency
        for column in all_columns:
            count = sum(1 for cols in file_columns.values() if column in cols)
            column_analysis['column_frequency'][column] = count
        
        # File-specific columns
        for file_key, cols in file_columns.items():
            unique_to_file = cols - common_columns
            if unique_to_file:
                column_analysis['file_specific_columns'][file_key] = list(unique_to_file)
        
        return column_analysis
    
    def clear_loaded_data(self):
        """Clear all loaded data to free memory"""
        self.loaded_files.clear()
        self.combined_data = None
        self.processing_stats = {}
        logger.info("Cleared all loaded data")