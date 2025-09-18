"""
File handling utilities for various formats
"""

import os
import json
import pickle
import csv
import gzip
import zipfile
import shutil
from pathlib import Path
from typing import Any, Dict, List, Union, Optional
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """
    Handles file operations for various formats
    """
    
    def __init__(self):
        self.supported_formats = {
            '.csv', '.json', '.jsonl', '.pkl', '.dump', 
            '.xlsx', '.xls', '.txt'
        }
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get basic information about a file
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stat = file_path.stat()
        
        return {
            'name': file_path.name,
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / 1024**2,
            'extension': file_path.suffix.lower(),
            'absolute_path': str(file_path.absolute()),
            'is_supported': file_path.suffix.lower() in self.supported_formats
        }
    
    def validate_file_format(self, file_path: Union[str, Path]) -> bool:
        """
        Check if file format is supported
        """
        file_path = Path(file_path)
        return file_path.suffix.lower() in self.supported_formats
    
    def create_backup(self, file_path: Union[str, Path]) -> Path:
        """
        Create a backup of the file
        """
        file_path = Path(file_path)
        backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
        
        # Create backup
        shutil.copy2(file_path, backup_path)
        
        logger.info(f"Backup created: {backup_path}")
        return backup_path
    
    def safe_write_json(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Safely write JSON data to file
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temporary file first
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Move temporary file to final location
            temp_path.replace(file_path)
            logger.info(f"JSON data written to: {file_path}")
            
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def safe_write_pickle(self, data: Any, file_path: Union[str, Path]) -> None:
        """
        Safely write pickle data to file
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temporary file first
        temp_path = file_path.with_suffix('.tmp')
        
        try:
            with open(temp_path, 'wb') as f:
                pickle.dump(data, f)
            
            # Move temporary file to final location
            temp_path.replace(file_path)
            logger.info(f"Pickle data written to: {file_path}")
            
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    def estimate_csv_size(self, file_path: Union[str, Path], 
                         sample_rows: int = 1000) -> Dict[str, Any]:
        """
        Estimate CSV file characteristics by sampling
        """
        file_path = Path(file_path)
        
        # Read sample rows
        import pandas as pd
        sample_df = pd.read_csv(file_path, nrows=sample_rows)
        
        # Estimate total rows
        file_size = file_path.stat().st_size
        sample_size = len(sample_df.to_csv(index=False).encode('utf-8'))
        estimated_rows = int((file_size / sample_size) * sample_rows)
        
        return {
            'estimated_rows': estimated_rows,
            'sample_rows': len(sample_df),
            'columns': len(sample_df.columns),
            'column_names': list(sample_df.columns),
            'memory_estimate_mb': (estimated_rows / sample_rows) * (sample_df.memory_usage(deep=True).sum() / 1024**2)
        }
    
    def chunk_csv_reader(self, file_path: Union[str, Path], 
                        chunk_size: int = 10000):
        """
        Generator for reading CSV in chunks
        """
        import pandas as pd
        
        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            yield chunk
    
    def convert_dump_to_csv(self, dump_path: Union[str, Path], 
                           csv_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Convert dump file to CSV format
        """
        dump_path = Path(dump_path)
        csv_path = Path(csv_path)
        
        # Load dump file
        try:
            with open(dump_path, 'rb') as f:
                data = pickle.load(f)
        except:
            # Try alternative loading methods
            try:
                with open(dump_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    data = json.loads(content)
            except:
                raise ValueError(f"Unable to load dump file: {dump_path}")
        
        # Convert to DataFrame
        import pandas as pd
        
        if isinstance(data, pd.DataFrame):
            df = data
        elif isinstance(data, dict):
            df = pd.DataFrame(data)
        elif isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame({'data': data})
        else:
            df = pd.DataFrame(data)
        
        # Save as CSV
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        
        conversion_info = {
            'original_file': str(dump_path),
            'converted_file': str(csv_path),
            'rows': len(df),
            'columns': len(df.columns),
            'original_size_mb': dump_path.stat().st_size / 1024**2,
            'converted_size_mb': csv_path.stat().st_size / 1024**2
        }
        
        logger.info(f"Converted {dump_path} to {csv_path}")
        return conversion_info
    
    def validate_file_integrity(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate file integrity and readability
        """
        file_path = Path(file_path)
        
        result = {
            'is_valid': False,
            'file_type': None,
            'error': None,
            'warnings': []
        }
        
        if not file_path.exists():
            result['error'] = f"File does not exist: {file_path}"
            return result
        
        extension = file_path.suffix.lower()
        
        try:
            if extension == '.csv':
                import pandas as pd
                # Try to read first few rows
                pd.read_csv(file_path, nrows=5)
                result['file_type'] = 'CSV'
                result['is_valid'] = True
                
            elif extension in ['.xlsx', '.xls']:
                import pandas as pd
                pd.read_excel(file_path, nrows=5)
                result['file_type'] = 'Excel'
                result['is_valid'] = True
                
            elif extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                result['file_type'] = 'JSON'
                result['is_valid'] = True
                
            elif extension == '.jsonl':
                with open(file_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if i >= 5:  # Check first 5 lines
                            break
                        json.loads(line.strip())
                result['file_type'] = 'JSON Lines'
                result['is_valid'] = True
                
            elif extension in ['.pkl', '.dump']:
                with open(file_path, 'rb') as f:
                    pickle.load(f)
                result['file_type'] = 'Pickle/Dump'
                result['is_valid'] = True
                
            else:
                result['error'] = f"Unsupported file type: {extension}"
                
        except Exception as e:
            result['error'] = f"File validation failed: {str(e)}"
        
        return result
    
    def clean_temp_files(self, directory: Union[str, Path], 
                        pattern: str = "*.tmp") -> int:
        """
        Clean temporary files in a directory
        """
        directory = Path(directory)
        
        if not directory.exists():
            return 0
        
        temp_files = list(directory.glob(pattern))
        removed_count = 0
        
        for temp_file in temp_files:
            try:
                temp_file.unlink()
                removed_count += 1
                logger.debug(f"Removed temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_file}: {str(e)}")
        
        return removed_count
    
    def compress_file(self, input_path: Union[str, Path], 
                     output_path: Optional[Union[str, Path]] = None,
                     compression_type: str = 'gzip') -> Path:
        """
        Compress a file using specified compression
        """
        input_path = Path(input_path)
        
        if output_path is None:
            if compression_type == 'gzip':
                output_path = input_path.with_suffix(input_path.suffix + '.gz')
            elif compression_type == 'zip':
                output_path = input_path.with_suffix('.zip')
            else:
                raise ValueError(f"Unsupported compression type: {compression_type}")
        else:
            output_path = Path(output_path)
        
        if compression_type == 'gzip':
            with open(input_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
        elif compression_type == 'zip':
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(input_path, input_path.name)
        else:
            raise ValueError(f"Unsupported compression type: {compression_type}")
        
        logger.info(f"Compressed {input_path} to {output_path}")
        return output_path
    
    def decompress_file(self, input_path: Union[str, Path], 
                       output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Decompress a compressed file
        """
        input_path = Path(input_path)
        
        if output_path is None:
            if input_path.suffix == '.gz':
                output_path = input_path.with_suffix('')
            elif input_path.suffix == '.zip':
                output_path = input_path.parent / input_path.stem
            else:
                raise ValueError(f"Unknown compression format: {input_path.suffix}")
        else:
            output_path = Path(output_path)
        
        if input_path.suffix == '.gz':
            with gzip.open(input_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    
        elif input_path.suffix == '.zip':
            with zipfile.ZipFile(input_path, 'r') as zipf:
                zipf.extractall(output_path.parent)
                # Assume single file in zip
                extracted_files = zipf.namelist()
                if len(extracted_files) == 1:
                    extracted_path = output_path.parent / extracted_files[0]
                    if extracted_path != output_path:
                        extracted_path.rename(output_path)
        else:
            raise ValueError(f"Unsupported compression format: {input_path.suffix}")
        
        logger.info(f"Decompressed {input_path} to {output_path}")
        return output_path
    
    def batch_convert_files(self, input_directory: Union[str, Path],
                           output_directory: Union[str, Path],
                           input_format: str = 'dump',
                           output_format: str = 'csv') -> Dict[str, Any]:
        """
        Batch convert files from one format to another
        """
        input_dir = Path(input_directory)
        output_dir = Path(output_directory)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find files to convert
        if input_format == 'dump':
            pattern = '*.dump'
        elif input_format == 'pkl':
            pattern = '*.pkl'
        else:
            pattern = f'*.{input_format}'
        
        input_files = list(input_dir.glob(pattern))
        
        results = {
            'total_files': len(input_files),
            'converted_files': 0,
            'failed_files': 0,
            'errors': []
        }
        
        for input_file in input_files:
            try:
                if output_format == 'csv':
                    output_file = output_dir / f"{input_file.stem}.csv"
                    self.convert_dump_to_csv(input_file, output_file)
                else:
                    # Add other conversion types as needed
                    raise ValueError(f"Conversion to {output_format} not implemented")
                
                results['converted_files'] += 1
                logger.info(f"Converted: {input_file.name}")
                
            except Exception as e:
                results['failed_files'] += 1
                error_msg = f"Failed to convert {input_file.name}: {str(e)}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
        
        return results
    
    def read_file_sample(self, file_path: Union[str, Path], 
                        lines: int = 10) -> Dict[str, Any]:
        """
        Read a sample of lines from a file for preview
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        sample_data = {
            'file_type': extension,
            'sample_lines': [],
            'total_size_mb': file_path.stat().st_size / 1024**2
        }
        
        try:
            if extension == '.csv':
                import pandas as pd
                df_sample = pd.read_csv(file_path, nrows=lines)
                sample_data['sample_lines'] = df_sample.to_dict('records')
                sample_data['columns'] = list(df_sample.columns)
                
            elif extension in ['.xlsx', '.xls']:
                import pandas as pd
                df_sample = pd.read_excel(file_path, nrows=lines)
                sample_data['sample_lines'] = df_sample.to_dict('records')
                sample_data['columns'] = list(df_sample.columns)
                
            elif extension == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        sample_data['sample_lines'] = data[:lines]
                    else:
                        sample_data['sample_lines'] = [data]
                        
            elif extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    sample_data['sample_lines'] = [f.readline().strip() for _ in range(lines)]
                    
            else:
                sample_data['sample_lines'] = ["Binary file - cannot preview"]
                
        except Exception as e:
            sample_data['error'] = str(e)
            sample_data['sample_lines'] = [f"Error reading file: {str(e)}"]
        
        return sample_data
    
    def get_directory_summary(self, directory: Union[str, Path]) -> Dict[str, Any]:
        """
        Get summary information about files in a directory
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        summary = {
            'total_files': 0,
            'total_size_mb': 0,
            'file_types': {},
            'largest_files': []
        }
        
        all_files = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                extension = file_path.suffix.lower() or 'no_extension'
                
                summary['total_files'] += 1
                summary['total_size_mb'] += file_size / 1024**2
                
                if extension not in summary['file_types']:
                    summary['file_types'][extension] = {'count': 0, 'size_mb': 0}
                
                summary['file_types'][extension]['count'] += 1
                summary['file_types'][extension]['size_mb'] += file_size / 1024**2
                
                all_files.append({
                    'path': str(file_path),
                    'size_mb': file_size / 1024**2
                })
        
        # Get top 10 largest files
        all_files.sort(key=lambda x: x['size_mb'], reverse=True)
        summary['largest_files'] = all_files[:10]
        
        return summary