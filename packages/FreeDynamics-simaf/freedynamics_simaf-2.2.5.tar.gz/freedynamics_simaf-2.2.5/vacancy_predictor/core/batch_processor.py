"""
Parser mejorado para archivos LAMMPS dump con diagnóstico y manejo de múltiples formatos
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
import logging
import gzip
import io
import re

logger = logging.getLogger(__name__)

class BatchDumpProcessor:
    """Parser flexible para diferentes formatos de LAMMPS dump"""
    
    def __init__(self):
        self.last_error_details = None
        self.format_stats = {}
        
    def diagnose_dump_format(self, path: str, max_lines: int = 1000) -> Dict[str, Any]:
        """
        Diagnostica el formato del archivo dump
        """
        diagnosis = {
            "file": Path(path).name,
            "format_type": "unknown",
            "has_timestep": False,
            "has_number_atoms": False,
            "has_box_bounds": False,
            "has_atoms_section": False,
            "atom_header": None,
            "num_frames": 0,
            "sample_lines": [],
            "error": None
        }
        
        try:
            with self._open_any(path) as f:
                lines = []
                for i, line in enumerate(f):
                    lines.append(line.strip())
                    if i >= max_lines:
                        break
            
            # Buscar patrones clave
            timestep_indices = []
            number_atoms_indices = []
            atoms_indices = []
            
            for i, line in enumerate(lines):
                if line.startswith("ITEM: TIMESTEP"):
                    timestep_indices.append(i)
                    diagnosis["has_timestep"] = True
                elif line.startswith("ITEM: NUMBER OF ATOMS"):
                    number_atoms_indices.append(i)
                    diagnosis["has_number_atoms"] = True
                elif line.startswith("ITEM: ATOMS"):
                    atoms_indices.append(i)
                    diagnosis["has_atoms_section"] = True
                    diagnosis["atom_header"] = line.replace("ITEM: ATOMS", "").strip()
                elif line.startswith("ITEM: BOX BOUNDS"):
                    diagnosis["has_box_bounds"] = True
            
            diagnosis["num_frames"] = len(timestep_indices)
            
            # Determinar tipo de formato
            if diagnosis["has_number_atoms"] and diagnosis["has_atoms_section"]:
                diagnosis["format_type"] = "standard"
            elif diagnosis["has_atoms_section"] and not diagnosis["has_number_atoms"]:
                diagnosis["format_type"] = "compact"  # Sin línea NUMBER OF ATOMS
            elif not diagnosis["has_atoms_section"]:
                diagnosis["format_type"] = "custom"  # Formato personalizado
            
            # Guardar líneas de muestra
            diagnosis["sample_lines"] = lines[:50]
            
            # Si es formato compacto, intentar contar átomos
            if diagnosis["format_type"] == "compact" and atoms_indices:
                # Contar líneas entre ITEM: ATOMS y el siguiente ITEM
                first_atoms_idx = atoms_indices[0]
                next_item_idx = None
                for i in range(first_atoms_idx + 1, len(lines)):
                    if lines[i].startswith("ITEM:"):
                        next_item_idx = i
                        break
                if next_item_idx:
                    diagnosis["estimated_atoms"] = next_item_idx - first_atoms_idx - 1
            
        except Exception as e:
            diagnosis["error"] = str(e)
        
        return diagnosis
    
    def _open_any(self, path: str):
        """Abrir archivo, detectando si está comprimido"""
        p = Path(path)
        if p.suffix == ".gz":
            return io.TextIOWrapper(gzip.open(p, "rb"), encoding="utf-8", newline="")
        return open(p, "r", encoding="utf-8", newline="")
    
    def parse_last_frame_adaptive(self, path: str) -> Tuple[pd.DataFrame, int, Dict[str, Any]]:
        """
        Parser adaptativo que maneja múltiples formatos de LAMMPS dump
        """
        # Primero diagnosticar el formato
        diagnosis = self.diagnose_dump_format(path, max_lines=5000)
        
        with self._open_any(path) as f:
            lines = f.read().splitlines()
        
        metadata = {"format": diagnosis["format_type"]}
        
        # Buscar secciones ATOMS (frames)
        atoms_indices = [i for i, l in enumerate(lines) if l.startswith("ITEM: ATOMS")]
        
        if not atoms_indices:
            # Intentar formato alternativo sin "ITEM: ATOMS"
            # Buscar patrones numéricos después de TIMESTEP
            return self._parse_custom_format(lines, path)
        
        # Usar el último frame
        last_atoms_idx = atoms_indices[-1]
        header_line = lines[last_atoms_idx]
        header = header_line.replace("ITEM: ATOMS", "").strip().split()
        
        # Buscar NUMBER OF ATOMS para este frame
        n_atoms = None
        
        # Método 1: Buscar "ITEM: NUMBER OF ATOMS" antes del frame
        for j in range(last_atoms_idx - 1, max(0, last_atoms_idx - 20), -1):
            if lines[j].startswith("ITEM: NUMBER OF ATOMS"):
                if j + 1 < len(lines):
                    try:
                        n_atoms = int(lines[j + 1].strip())
                        break
                    except ValueError:
                        continue
        
        # Método 2: Si no hay NUMBER OF ATOMS, contar hasta el siguiente ITEM
        if n_atoms is None:
            next_item_idx = None
            for j in range(last_atoms_idx + 1, len(lines)):
                if lines[j].startswith("ITEM:") or lines[j].strip() == "":
                    next_item_idx = j
                    break
            
            if next_item_idx is None:
                next_item_idx = len(lines)
            
            n_atoms = next_item_idx - last_atoms_idx - 1
            metadata["atoms_counted"] = True
        
        # Validar n_atoms
        if n_atoms <= 0:
            raise RuntimeError(f"Número inválido de átomos: {n_atoms}")
        
        # Parsear datos de átomos
        data_lines = lines[last_atoms_idx + 1 : last_atoms_idx + 1 + n_atoms]
        
        # Crear array para los datos
        n_cols = len(header)
        data_array = np.full((n_atoms, n_cols), np.nan, dtype=float)
        
        for i, line in enumerate(data_lines):
            if line.strip():  # Ignorar líneas vacías
                parts = line.split()
                for j in range(min(n_cols, len(parts))):
                    try:
                        data_array[i, j] = float(parts[j])
                    except ValueError:
                        data_array[i, j] = np.nan
        
        # Crear DataFrame
        df = pd.DataFrame(data_array, columns=header)
        
        # Extraer metadata adicional
        for j in range(last_atoms_idx - 1, max(0, last_atoms_idx - 50), -1):
            if lines[j].startswith("ITEM: TIMESTEP"):
                if j + 1 < len(lines):
                    try:
                        metadata["timestep"] = int(lines[j + 1].strip())
                    except ValueError:
                        pass
            elif lines[j].startswith("ITEM: BOX BOUNDS"):
                box_bounds = []
                for k in range(1, 4):
                    if j + k < len(lines):
                        bounds = lines[j + k].split()
                        if len(bounds) >= 2:
                            box_bounds.append([float(bounds[0]), float(bounds[1])])
                if len(box_bounds) == 3:
                    metadata["box_volume"] = np.prod([b[1] - b[0] for b in box_bounds])
        
        return df, n_atoms, metadata
    
    def _parse_custom_format(self, lines: List[str], path: str) -> Tuple[pd.DataFrame, int, Dict[str, Any]]:
        """
        Parser para formatos personalizados de LAMMPS
        """
        # Buscar patrones de datos numéricos
        data_start = None
        data_end = None
        
        # Detectar bloques de datos numéricos
        for i, line in enumerate(lines):
            parts = line.split()
            if len(parts) >= 3:  # Mínimo esperado para datos de átomos
                try:
                    # Intentar convertir los primeros valores a float
                    _ = [float(p) for p in parts[:3]]
                    if data_start is None:
                        data_start = i
                except ValueError:
                    if data_start is not None and data_end is None:
                        data_end = i
                        break
        
        if data_start is None:
            raise RuntimeError(f"No se encontraron datos numéricos en {path}")
        
        if data_end is None:
            data_end = len(lines)
        
        # Parsear datos
        data_lines = lines[data_start:data_end]
        n_atoms = len(data_lines)
        
        # Determinar número de columnas
        first_line_parts = data_lines[0].split()
        n_cols = len(first_line_parts)
        
        # Crear nombres de columnas genéricos
        header = [f"col_{i}" for i in range(n_cols)]
        
        # Intentar identificar columnas comunes
        if n_cols >= 3:
            header[0] = "id"
            if n_cols >= 6:
                header[3] = "x"
                header[4] = "y" 
                header[5] = "z"
        
        # Crear array de datos
        data_array = np.full((n_atoms, n_cols), np.nan, dtype=float)
        
        for i, line in enumerate(data_lines):
            parts = line.split()
            for j in range(min(n_cols, len(parts))):
                try:
                    data_array[i, j] = float(parts[j])
                except ValueError:
                    data_array[i, j] = np.nan
        
        df = pd.DataFrame(data_array, columns=header)
        metadata = {"format": "custom", "warning": "Formato no estándar detectado"}
        
        return df, n_atoms, metadata
    
    def validate_parsed_data(self, df: pd.DataFrame, n_atoms: int) -> Dict[str, Any]:
        """
        Valida los datos parseados
        """
        validation = {
            "is_valid": True,
            "warnings": [],
            "stats": {}
        }
        
        # Verificar tamaño
        if len(df) != n_atoms:
            validation["warnings"].append(f"Discrepancia: DataFrame tiene {len(df)} filas, esperadas {n_atoms}")
            validation["is_valid"] = False
        
        # Verificar columnas críticas
        expected_cols = ["x", "y", "z"]
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            validation["warnings"].append(f"Columnas faltantes: {missing_cols}")
        
        # Estadísticas de NaN
        nan_counts = df.isnull().sum()
        if nan_counts.any():
            validation["warnings"].append(f"Valores NaN detectados: {nan_counts[nan_counts > 0].to_dict()}")
        
        # Estadísticas básicas
        validation["stats"] = {
            "n_rows": len(df),
            "n_cols": len(df.columns),
            "columns": list(df.columns),
            "dtypes": {col: str(df[col].dtype) for col in df.columns}
        }
        
        return validation


class ImprovedBatchProcessor:
    """Procesador batch mejorado con parser flexible"""
    
    def __init__(self, config=None):
        self.parser = BatchDumpProcessor()
        self.config = config or {}
        self.atm_total = self.config.get('atm_total', 16384)
        self.progress_callback = None
        self.diagnostics = []
        
    def set_progress_callback(self, callback):
        """Establecer callback para reportar progreso"""
        self.progress_callback = callback
    
    def _report_progress(self, current, total, message=""):
        """Reportar progreso si hay callback"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def diagnose_directory(self, directory: str) -> pd.DataFrame:
        """
        Diagnostica todos los archivos dump en un directorio
        """
        dump_files = self.find_dump_files(directory)
        diagnostics = []
        
        for file_path in dump_files:
            diag = self.parser.diagnose_dump_format(file_path)
            diag["file_path"] = file_path
            diagnostics.append(diag)
        
        df_diag = pd.DataFrame(diagnostics)
        
        # Resumen
        print("\n=== DIAGNÓSTICO DE ARCHIVOS DUMP ===")
        print(f"Total archivos: {len(df_diag)}")
        print(f"Formatos detectados: {df_diag['format_type'].value_counts().to_dict()}")
        print(f"Con NUMBER OF ATOMS: {df_diag['has_number_atoms'].sum()}")
        print(f"Con ATOMS section: {df_diag['has_atoms_section'].sum()}")
        print(f"Con errores: {df_diag['error'].notna().sum()}")
        
        return df_diag
    
    def find_dump_files(self, directory: str) -> List[str]:
        """Encuentra todos los archivos dump"""
        directory_path = Path(directory)
        dump_files = []
        
        patterns = ["*.dump", "*.dump.gz", "dump.*", "dump.*.gz", 
                   "*.lammpstrj", "*.lammpstrj.gz", "*.lammps"]
        
        for pattern in patterns:
            dump_files.extend(directory_path.glob(pattern))
        
        return sorted(list(set([str(f) for f in dump_files])))
    
    def process_directory_adaptive(self, directory: str) -> pd.DataFrame:
        """
        Procesa directorio con parser adaptativo
        """
        dump_files = self.find_dump_files(directory)
        
        if not dump_files:
            raise ValueError(f"No se encontraron archivos dump en {directory}")
        
        print(f"Encontrados {len(dump_files)} archivos")
        
        rows = []
        errors = []
        format_counts = {}
        
        for i, file_path in enumerate(dump_files, 1):
            file_name = Path(file_path).name
            self._report_progress(i, len(dump_files), f"Procesando {file_name}")
            
            try:
                # Parsear con método adaptativo
                df, n_atoms, metadata = self.parser.parse_last_frame_adaptive(file_path)
                
                # Validar datos
                validation = self.parser.validate_parsed_data(df, n_atoms)
                
                if not validation["is_valid"]:
                    logger.warning(f"Validación fallida para {file_name}: {validation['warnings']}")
                
                # Contar formato
                fmt = metadata.get("format", "unknown")
                format_counts[fmt] = format_counts.get(fmt, 0) + 1
                
                # Extraer features básicas
                features = self.extract_basic_features(df, n_atoms)
                features["file"] = file_name
                features["file_path"] = file_path
                features["format_type"] = fmt
                features["n_atoms"] = n_atoms
                features["vacancies"] = self.atm_total - n_atoms
                
                rows.append(features)
                
                logger.info(f"Procesado {file_name}: {n_atoms} átomos, formato: {fmt}")
                
            except Exception as e:
                error_msg = f"Error en {file_name}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
                
                # Intentar diagnóstico
                try:
                    diag = self.parser.diagnose_dump_format(file_path)
                    logger.info(f"Diagnóstico de {file_name}: {diag}")
                except:
                    pass
        
        # Resumen
        print(f"\n=== RESUMEN DE PROCESAMIENTO ===")
        print(f"Archivos procesados: {len(rows)}/{len(dump_files)}")
        print(f"Errores: {len(errors)}")
        print(f"Formatos encontrados: {format_counts}")
        
        if errors:
            print(f"\nPrimeros 5 errores:")
            for err in errors[:5]:
                print(f"  - {err}")
        
        if not rows:
            raise RuntimeError("No se pudieron procesar archivos")
        
        return pd.DataFrame(rows)
    
    def extract_basic_features(self, df: pd.DataFrame, n_atoms: int) -> Dict[str, Any]:
        """
        Extrae features básicas del DataFrame
        """
        features = {}
        
        # Identificar columnas disponibles
        available_cols = set(df.columns)
        
        # Energía potencial (buscar variantes)
        pe_col = None
        for col in ["c_peatom", "pe", "c_pe", "PotEng", "v_pe"]:
            if col in available_cols:
                pe_col = col
                break
        
        if pe_col:
            pe_series = pd.to_numeric(df[pe_col], errors='coerce')
            pe_clean = pe_series.dropna()
            if len(pe_clean) > 0:
                features["pe_mean"] = float(pe_clean.mean())
                features["pe_std"] = float(pe_clean.std())
                features["pe_min"] = float(pe_clean.min())
                features["pe_max"] = float(pe_clean.max())
        
        # Coordenadas espaciales
        if all(col in available_cols for col in ["x", "y", "z"]):
            features["spatial_std_x"] = float(df["x"].std())
            features["spatial_std_y"] = float(df["y"].std())
            features["spatial_std_z"] = float(df["z"].std())
        
        # Coordinación
        coord_col = None
        for col in ["c_coord", "coord", "c_coord1"]:
            if col in available_cols:
                coord_col = col
                break
        
        if coord_col:
            coord_series = pd.to_numeric(df[coord_col], errors='coerce')
            coord_clean = coord_series.dropna()
            if len(coord_clean) > 0:
                features["coord_mean"] = float(coord_clean.mean())
                features["coord_std"] = float(coord_clean.std())
        
        # Stress (si está disponible)
        stress_cols = [f"c_satom[{i}]" for i in range(1, 7)]
        if all(col in available_cols for col in stress_cols):
            for i, col in enumerate(stress_cols, 1):
                stress = pd.to_numeric(df[col], errors='coerce').dropna()
                if len(stress) > 0:
                    features[f"stress_{i}_mean"] = float(stress.mean())
        
        return features


# Función de prueba rápida
def test_parser(file_path: str):
    """
    Prueba el parser con un archivo específico
    """
    parser = BatchDumpProcessor()
    
    print(f"\n=== DIAGNÓSTICO DE {Path(file_path).name} ===")
    diagnosis = parser.diagnose_dump_format(file_path)
    
    for key, value in diagnosis.items():
        if key != "sample_lines":
            print(f"{key}: {value}")
    
    if diagnosis["sample_lines"]:
        print("\nPrimeras 10 líneas del archivo:")
        for line in diagnosis["sample_lines"][:10]:
            print(f"  {line}")
    
    try:
        df, n_atoms, metadata = parser.parse_last_frame_adaptive(file_path)
        print(f"\n✓ Parseado exitoso: {n_atoms} átomos, {len(df.columns)} columnas")
        print(f"Columnas: {list(df.columns)}")
        print(f"Metadata: {metadata}")
    except Exception as e:
        print(f"\n✗ Error al parsear: {e}")
    
    return diagnosis


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if Path(sys.argv[1]).is_file():
            # Probar un archivo específico
            test_parser(sys.argv[1])
        elif Path(sys.argv[1]).is_dir():
            # Procesar directorio
            processor = ImprovedBatchProcessor()
            
            # Primero diagnosticar
            print("Realizando diagnóstico...")
            diag_df = processor.diagnose_directory(sys.argv[1])
            
            # Luego procesar
            print("\nProcesando archivos...")
            dataset = processor.process_directory_adaptive(sys.argv[1])
            
            print(f"\nDataset final: {dataset.shape}")
            print(dataset.head())
    else:
        print("Uso: python script.py <archivo_dump o directorio>")