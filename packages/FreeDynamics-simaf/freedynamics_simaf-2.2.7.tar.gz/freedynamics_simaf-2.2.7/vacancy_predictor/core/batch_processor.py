"""
Procesador batch mejorado para archivos LAMMPS dump
Versión con mitigación adicional de fuga de información
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Set
import logging
import gzip
import io
import hashlib
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class FeatureMode(Enum):
    """Modos de extracción de features"""
    CONSERVATIVE = "conservative"  # Mínima fuga posible
    STANDARD = "standard"          # Balance entre información y fuga
    FULL = "full"                  # Todas las features (mayor riesgo)

@dataclass
class ProcessingConfig:
    """Configuración centralizada del procesador"""
    atm_total: int = 16384
    energy_min: float = -4.0
    energy_max: float = -3.0
    energy_bins: int = 10
    feature_mode: FeatureMode = FeatureMode.STANDARD
    add_noise: bool = False
    noise_level: float = 0.01
    validate_features: bool = True
    
class BatchDumpProcessor:
    """Procesador batch de archivos LAMMPS dump con mitigación de fuga"""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        
        # Features con diferentes niveles de riesgo de fuga
        self.high_risk_features = {
            'n_atoms', 'vacancy_fraction', 'vacancy_count',
            'coord_below_8', 'coord_perfect_12', 'coord_bin_4_5',
            'frac_coord_le_9', 'frac_coord_le_10', 'frac_coord_le_11'
        }
        
        self.medium_risk_features = {
            'coord_bin_6_7', 'coord_bin_8_9', 'coord_bin_10_11',
            'frac_vm_top5', 'frac_pe_top5', 
            'coord2_le_3', 'coord2_le_4', 'coord2_le_5'
        }
        
        self.low_risk_features = {
            'pe_mean', 'pe_std', 'pe_median',
            'stress_vm_mean', 'stress_vm_std',
            'stress_I1_mean', 'stress_I1_std'
        }
        
        self.progress_callback = None
        self._feature_correlations = {}
        
    def set_parameters(self, **kwargs):
        """Actualizar parámetros de configuración"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def set_feature_mode(self, mode: FeatureMode):
        """Establecer el modo de extracción de features"""
        self.config.feature_mode = mode
        logger.info(f"Modo de features establecido: {mode.value}")
        
    def get_allowed_features(self) -> Set[str]:
        """Obtener conjunto de features permitidas según el modo"""
        if self.config.feature_mode == FeatureMode.CONSERVATIVE:
            # Solo features de bajo riesgo
            return self.low_risk_features
        elif self.config.feature_mode == FeatureMode.STANDARD:
            # Features de bajo y medio riesgo
            return self.low_risk_features | self.medium_risk_features
        else:  # FULL
            # Todas las features excepto las explícitamente prohibidas
            return None  # Significa usar todas
    
    def _add_gaussian_noise(self, value: float, scale: float = None) -> float:
        """Agregar ruido gaussiano a un valor"""
        if not self.config.add_noise:
            return value
        scale = scale or self.config.noise_level
        return value + np.random.normal(0, scale * abs(value))
    
    def _open_any(self, path: str):
        """Abrir archivo, detectando si está comprimido"""
        p = Path(path)
        if p.suffix == ".gz":
            return io.TextIOWrapper(gzip.open(p, "rb"), encoding="utf-8", newline="")
        return open(p, "r", encoding="utf-8", newline="")
    
    def parse_last_frame_dump(self, path: str) -> Tuple[pd.DataFrame, int, Dict[str, Any]]:
        """
        Lee el ÚLTIMO frame del dump LAMMPS con metadata adicional
        Parser adaptativo que maneja múltiples formatos
        
        Returns:
            df: DataFrame con datos de átomos
            n_atoms: Número de átomos
            metadata: Información adicional del frame
        """
        with self._open_any(path) as f:
            lines = f.read().splitlines()

        # Buscar secciones ATOMS (frames)
        idx_atoms = [i for i, l in enumerate(lines) if l.startswith("ITEM: ATOMS")]
        if not idx_atoms:
            # Intentar buscar sin espacio después de ATOMS
            idx_atoms = [i for i, l in enumerate(lines) if l.startswith("ITEM: ATOMS")]
            if not idx_atoms:
                raise RuntimeError(f"No se encontró 'ITEM: ATOMS' en {path}")
        
        start = idx_atoms[-1]
        header = lines[start].replace("ITEM: ATOMS", "").strip().split()
        
        # Extraer metadata adicional
        metadata = {}
        nat = None
        timestep = None
        box_bounds = []
        
        # Buscar NUMBER OF ATOMS para este frame (búsqueda más flexible)
        for j in range(start-1, max(0, start-50), -1):
            if lines[j].startswith("ITEM: NUMBER OF ATOMS"):
                if j+1 < len(lines):
                    try:
                        nat = int(lines[j+1].strip())
                        break
                    except ValueError:
                        continue
            elif lines[j].startswith("ITEM: TIMESTEP"):
                if j+1 < len(lines):
                    try:
                        timestep = int(lines[j+1].strip())
                        metadata['timestep'] = timestep
                    except ValueError:
                        pass
            elif lines[j].startswith("ITEM: BOX BOUNDS"):
                # Leer las siguientes 3 líneas para los bounds
                for k in range(1, 4):
                    if j+k < len(lines):
                        bounds = lines[j+k].split()
                        if len(bounds) >= 2:
                            try:
                                box_bounds.append([float(bounds[0]), float(bounds[1])])
                            except ValueError:
                                pass
                if len(box_bounds) == 3:
                    metadata['box_volume'] = np.prod([b[1]-b[0] for b in box_bounds])
                    metadata['box_bounds'] = box_bounds
        
        # Si no encontramos NUMBER OF ATOMS, contar líneas hasta el siguiente ITEM
        if nat is None:
            logger.warning(f"No se encontró 'ITEM: NUMBER OF ATOMS' en {path}, contando líneas...")
            next_item_idx = None
            for j in range(start + 1, len(lines)):
                if lines[j].startswith("ITEM:") or j == len(lines) - 1:
                    next_item_idx = j if lines[j].startswith("ITEM:") else j + 1
                    break
            
            if next_item_idx is None:
                next_item_idx = len(lines)
            
            # Contar líneas de datos (ignorando vacías)
            data_lines = []
            for j in range(start + 1, next_item_idx):
                if lines[j].strip():  # Solo contar líneas no vacías
                    data_lines.append(lines[j])
            
            nat = len(data_lines)
            metadata['atoms_counted'] = True
            logger.info(f"Contados {nat} átomos en {Path(path).name}")
        
        if nat <= 0:
            raise RuntimeError(f"Número inválido de átomos ({nat}) en {path}")

        
        # Parsear datos de átomos
        rows = lines[start+1:start+1+nat]
        K = len(header)
        arr = np.full((len(rows), K), np.nan, dtype=float)
        
        valid_row_count = 0
        for line in rows:
            if line.strip():  # Solo procesar líneas no vacías
                parts = line.split()
                for c in range(min(K, len(parts))):
                    try: 
                        arr[valid_row_count, c] = float(parts[c])
                    except ValueError: 
                        arr[valid_row_count, c] = np.nan
                valid_row_count += 1
        
        # Ajustar el array al número real de filas válidas
        if valid_row_count < len(rows):
            arr = arr[:valid_row_count]
            nat = valid_row_count
        
        df = pd.DataFrame(arr, columns=header)
        return df, nat, metadata
    
    def add_stress_invariants(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega invariantes de stress I1, I2, I3 y von Mises"""
        cols = [f"c_satom[{i}]" for i in range(1,7)]
        if not all(c in df.columns for c in cols):
            return df
        
        sxx, syy, szz, sxy, sxz, syz = (df[c].astype(float) for c in cols)

        # Primer invariante (traza)
        I1 = sxx + syy + szz
        
        # Segundo invariante
        I2 = sxx*syy + syy*szz + szz*sxx - sxy**2 - sxz**2 - syz**2
        
        # Tercer invariante (determinante)
        I3 = (sxx * (syy*szz - syz**2) - 
              sxy * (sxy*szz - syz*sxz) + 
              sxz * (sxy*syz - syy*sxz))
        
        # Von Mises stress
        mean_normal = I1 / 3.0
        sxx_dev = sxx - mean_normal
        syy_dev = syy - mean_normal
        szz_dev = szz - mean_normal
        vm = np.sqrt(1.5*(sxx_dev**2 + syy_dev**2 + szz_dev**2 + 
                          2*(sxy**2 + sxz**2 + syz**2)))
        
        df = df.copy()
        df["stress_I1"] = I1
        df["stress_I2"] = I2
        df["stress_I3"] = I3
        df["stress_vm"] = vm
        
        # Stress hidrostático
        df["stress_hydro"] = -I1 / 3.0
        
        return df
    
    def compute_safe_coordination_features(self, coord_series: pd.Series) -> Dict[str, float]:
        """
        Calcula features de coordinación con menor riesgo de fuga
        """
        coord_clean = coord_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        features = {}
        if len(coord_clean) == 0:
            return {
                "coord_mean": np.nan,
                "coord_std": np.nan,
                "coord_entropy": np.nan
            }
        
        # Features estadísticas básicas (menor correlación con vacancias)
        features["coord_mean"] = float(coord_clean.mean())
        features["coord_std"] = float(coord_clean.std())
        
        # Entropía de la distribución (información sin revelar conteos directos)
        hist, _ = np.histogram(coord_clean, bins=range(0, 15))
        hist_norm = hist / hist.sum() if hist.sum() > 0 else hist
        entropy = -np.sum(hist_norm * np.log(hist_norm + 1e-10))
        features["coord_entropy"] = float(entropy)
        
        # Agregar ruido si está configurado
        if self.config.add_noise:
            for key in features:
                features[key] = self._add_gaussian_noise(features[key])
        
        # Solo agregar features de bins si el modo lo permite
        allowed = self.get_allowed_features()
        if allowed is None or "coord_bin_10_11" in allowed:
            # Bins más seguros (menos correlacionados con vacancias)
            features["coord_bin_10_11"] = float(((coord_clean >= 10) & (coord_clean <= 11)).sum() / len(coord_clean))
            features["coord_bin_12"] = float((coord_clean >= 12).sum() / len(coord_clean))
        
        return features
    
    def compute_robust_energy_features(self, pe_series: pd.Series) -> Dict[str, float]:
        """
        Calcula features de energía robustas
        """
        pe_clean = pe_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        features = {}
        
        if len(pe_clean) == 0:
            return {
                "pe_iqr": np.nan,
                "pe_mad": np.nan,
                "pe_entropy": np.nan
            }
        
        # Medidas robustas de dispersión
        q25, q75 = pe_clean.quantile([0.25, 0.75])
        features["pe_iqr"] = float(q75 - q25)  # Rango intercuartil
        
        # Desviación absoluta mediana (MAD)
        median = pe_clean.median()
        mad = (pe_clean - median).abs().median()
        features["pe_mad"] = float(mad)
        
        # Entropía del histograma de energía
        hist, _ = np.histogram(pe_clean, bins=self.config.energy_bins)
        hist_norm = hist / hist.sum() if hist.sum() > 0 else hist
        entropy = -np.sum(hist_norm * np.log(hist_norm + 1e-10))
        features["pe_entropy"] = float(entropy)
        
        # Momentos estandarizados (menos sensibles a outliers)
        if len(pe_clean) > 3:
            features["pe_skew_robust"] = float(((pe_clean - median) / mad).skew()) if mad > 0 else 0.0
            features["pe_kurt_robust"] = float(((pe_clean - median) / mad).kurt()) if mad > 0 else 0.0
        
        return features
    
    def compute_spatial_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calcula features espaciales que no revelan directamente vacancias
        """
        features = {}
        
        if all(col in df.columns for col in ['x', 'y', 'z']):
            # Centro de masa
            com_x = df['x'].mean()
            com_y = df['y'].mean()
            com_z = df['z'].mean()
            
            # Giro (gyration radius)
            r_squared = (df['x'] - com_x)**2 + (df['y'] - com_y)**2 + (df['z'] - com_z)**2
            features["gyration_radius"] = float(np.sqrt(r_squared.mean()))
            
            # Dispersión espacial
            features["spatial_std_x"] = float(df['x'].std())
            features["spatial_std_y"] = float(df['y'].std())
            features["spatial_std_z"] = float(df['z'].std())
        
        return features
    
    def extract_features_from_dump(self, df: pd.DataFrame, n_atoms: int, 
                                  metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extrae features con control de fuga de información
        IMPORTANTE: 'vacancies' se incluye como columna pero NO como feature
        """
        df = self.add_stress_invariants(df)
        
        feats: Dict[str, Any] = {}
        allowed_features = self.get_allowed_features()
        
        # 1. Features básicas de energía (bajo riesgo)
        if "c_peatom" in df.columns or "pe" in df.columns:
            pe_col = "c_peatom" if "c_peatom" in df.columns else "pe"
            pe_series = df[pe_col].astype(float)
            
            # Estadísticos robustos
            robust_energy = self.compute_robust_energy_features(pe_series)
            feats.update(robust_energy)
            
            # Solo agregar estadísticos básicos si el modo lo permite
            if allowed_features is None or "pe_mean" in allowed_features:
                pe_clean = pe_series.replace([np.inf, -np.inf], np.nan).dropna()
                if len(pe_clean) > 0:
                    feats["pe_mean"] = float(pe_clean.mean())
                    feats["pe_std"] = float(pe_clean.std())
                    feats["pe_median"] = float(pe_clean.median())
        
        # 2. Features de stress (riesgo medio-bajo)
        stress_cols = ["stress_I1", "stress_I2", "stress_I3", "stress_vm", "stress_hydro"]
        for col in stress_cols:
            if col in df.columns:
                series = df[col].astype(float)
                series_clean = series.replace([np.inf, -np.inf], np.nan).dropna()
                if len(series_clean) > 0:
                    # Solo estadísticos básicos
                    feats[f"{col}_mean"] = float(series_clean.mean())
                    feats[f"{col}_std"] = float(series_clean.std())
                    
                    # Agregar cuartiles solo si el modo lo permite
                    if allowed_features is None or f"{col}_q75" in allowed_features:
                        q25, q75 = series_clean.quantile([0.25, 0.75])
                        feats[f"{col}_q25"] = float(q25)
                        feats[f"{col}_q75"] = float(q75)
        
        # 3. Features de coordinación (con control estricto)
        if "c_coord" in df.columns or "coord" in df.columns:
            coord_col = "c_coord" if "c_coord" in df.columns else "coord"
            coord_series = df[coord_col].astype(float)
            
            if self.config.feature_mode == FeatureMode.CONSERVATIVE:
                # Solo features muy seguras
                coord_features = self.compute_safe_coordination_features(coord_series)
                feats.update({k: v for k, v in coord_features.items() 
                             if k in ["coord_mean", "coord_std", "coord_entropy"]})
            else:
                # Más features pero con precaución
                coord_features = self.compute_safe_coordination_features(coord_series)
                feats.update(coord_features)
        
        # 4. Features espaciales (bajo riesgo)
        spatial_features = self.compute_spatial_features(df)
        feats.update(spatial_features)
        
        # 5. Features de volumen de Voronoi (si está disponible)
        if "c_voro[1]" in df.columns:
            voro_series = df["c_voro[1]"].astype(float)
            voro_clean = voro_series.replace([np.inf, -np.inf], np.nan).dropna()
            if len(voro_clean) > 0:
                feats["voro_vol_mean"] = float(voro_clean.mean())
                feats["voro_vol_std"] = float(voro_clean.std())
                feats["voro_vol_cv"] = float(voro_clean.std() / voro_clean.mean()) if voro_clean.mean() != 0 else 0.0
        
        # 6. Agregar metadata del sistema (si está disponible)
        if metadata:
            if 'box_volume' in metadata and self.config.feature_mode != FeatureMode.CONSERVATIVE:
                # Densidad efectiva (puede ser útil pero con cuidado)
                effective_density = n_atoms / metadata['box_volume']
                feats["effective_density"] = float(effective_density)
                
                # Agregar ruido a la densidad si está configurado
                if self.config.add_noise:
                    feats["effective_density"] = self._add_gaussian_noise(feats["effective_density"])
        
        # 7. Hash del archivo para tracking (no es una feature para ML)
        feats["file_hash"] = self._compute_file_hash(df)
        
        # 8. IMPORTANTE: Calcular vacancies como columna TARGET (no como feature)
        # Esta columna DEBE estar presente para que la GUI funcione
        vacancies = int(self.config.atm_total - n_atoms)
        feats["vacancies"] = vacancies  # COLUMNA TARGET - será excluida de features
        
        # Metadata adicional (con prefijo _ para distinguir)
        feats["_n_atoms_metadata"] = n_atoms
        
        return feats
    
    def _compute_file_hash(self, df: pd.DataFrame) -> str:
        """Calcula un hash único para el contenido del frame"""
        # Usar solo las primeras filas para el hash (más rápido)
        sample = df.head(100).to_string()
        return hashlib.md5(sample.encode()).hexdigest()[:8]
    
    def validate_features(self, features: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida que las features no contengan información prohibida
        
        Returns:
            is_valid: True si las features son válidas
            warnings: Lista de advertencias
        """
        warnings = []
        is_valid = True
        
        # Verificar que no haya features prohibidas
        forbidden_found = []
        for key in features.keys():
            if any(forbidden in key.lower() for forbidden in ['vacancy', 'n_atoms', 'atom_count']):
                if not key.startswith('_'):  # Los metadatos con _ están permitidos
                    forbidden_found.append(key)
                    is_valid = False
        
        if forbidden_found:
            warnings.append(f"Features prohibidas encontradas: {forbidden_found}")
        
        # Verificar correlaciones sospechosas (si tenemos historial)
        if self._feature_correlations:
            high_corr = []
            for feat, corr in self._feature_correlations.items():
                if abs(corr) > 0.95:  # Correlación muy alta con vacancias
                    high_corr.append(f"{feat} (r={corr:.3f})")
                    warnings.append(f"Feature '{feat}' tiene alta correlación con vacancias: {corr:.3f}")
        
        # Verificar valores anómalos
        for key, value in features.items():
            if isinstance(value, (int, float)) and not key.startswith('_'):
                if np.isnan(value) or np.isinf(value):
                    warnings.append(f"Feature '{key}' contiene NaN o Inf")
        
        return is_valid, warnings
    
    def process_directory(self, directory: str, 
                         validate: bool = True,
                         save_intermediate: bool = False) -> pd.DataFrame:
        """
        Procesa todos los archivos .dump en un directorio con validación
        IMPORTANTE: Mantiene 'vacancies' como columna para el target
        """
        dump_files = self.find_dump_files(directory)
        
        if not dump_files:
            raise ValueError(f"No se encontraron archivos .dump en {directory}")
        
        logger.info(f"Encontrados {len(dump_files)} archivos .dump")
        logger.info(f"Modo de features: {self.config.feature_mode.value}")
        
        self._report_progress(0, len(dump_files), "Iniciando procesamiento...")
        
        rows = []
        errors = []
        validation_warnings = []
        
        for i, file_path in enumerate(dump_files, 1):
            try:
                file_name = Path(file_path).name
                self._report_progress(i, len(dump_files), f"Procesando {file_name}")
                
                # Parsear archivo dump con metadata
                df, n_atoms, metadata = self.parse_last_frame_dump(file_path)
                
                # Extraer features con control de fuga
                features = self.extract_features_from_dump(df, n_atoms, metadata)
                features["file"] = file_name
                features["file_path"] = file_path
                
                # Validar features si está habilitado
                if validate and self.config.validate_features:
                    is_valid, warnings = self.validate_features(features)
                    if warnings:
                        validation_warnings.extend([(file_name, w) for w in warnings])
                    if not is_valid:
                        logger.warning(f"Features inválidas en {file_name}")
                
                rows.append(features)
                
                # Log con información limitada para evitar revelar vacancias en logs
                logger.info(f"Procesado {file_name}: {n_atoms} átomos presentes")
                
            except Exception as e:
                error_msg = f"Error en {Path(file_path).name}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        if not rows:
            raise RuntimeError("No se pudieron procesar archivos correctamente")
        
        # Crear DataFrame
        dataset = pd.DataFrame(rows).set_index("file").sort_index()
        
        # IMPORTANTE: Identificar columnas pero NO eliminar 'vacancies'
        metadata_cols = [col for col in dataset.columns if col.startswith('_')]
        auxiliary_cols = ['file_path', 'file_hash']
        
        # 'vacancies' es el TARGET, no es una feature pero DEBE mantenerse en el dataset
        target_col = 'vacancies'
        
        # Features son todas las demás columnas (excluyendo metadata, auxiliares y target)
        feature_cols = [col for col in dataset.columns 
                       if col not in metadata_cols + auxiliary_cols + [target_col]]
        
        # Eliminar features de alto riesgo según el modo (pero NO el target)
        if self.config.feature_mode == FeatureMode.CONSERVATIVE:
            cols_to_drop = []
            for col in feature_cols:  # Solo verificar features, no el target
                if any(risk in col for risk in ['coord_bin', 'coord_le', 'frac_', 'top5']):
                    cols_to_drop.append(col)
            if cols_to_drop:
                dataset = dataset.drop(columns=cols_to_drop)
                logger.info(f"Eliminadas {len(cols_to_drop)} features de alto riesgo")
        
        # Verificar que 'vacancies' sigue presente
        if target_col not in dataset.columns:
            logger.error(f"ERROR: La columna '{target_col}' no está presente en el dataset")
            # Recalcular si es necesario
            if '_n_atoms_metadata' in dataset.columns:
                dataset[target_col] = self.config.atm_total - dataset['_n_atoms_metadata']
                logger.info(f"Columna '{target_col}' recalculada desde metadata")
        
        # Guardar resultados intermedios si está habilitado
        if save_intermediate:
            intermediate_path = Path(directory) / "features_intermediate.csv"
            dataset.to_csv(intermediate_path)
            logger.info(f"Resultados intermedios guardados en {intermediate_path}")
        
        # Reportar resumen
        if errors:
            logger.warning(f"Se encontraron {len(errors)} errores durante el procesamiento")
        
        if validation_warnings:
            logger.warning(f"Se encontraron {len(validation_warnings)} advertencias de validación")
            for file, warning in validation_warnings[:5]:  # Mostrar solo las primeras 5
                logger.warning(f"  {file}: {warning}")
        
        # Actualizar el conteo de features (excluyendo el target)
        actual_feature_cols = [col for col in dataset.columns 
                              if col not in metadata_cols + auxiliary_cols + [target_col]]
        
        self._report_progress(len(dump_files), len(dump_files), 
                            f"Procesamiento completado: {len(actual_feature_cols)} features + target '{target_col}'")
        
        logger.info(f"Dataset final: {len(dataset)} muestras, {len(actual_feature_cols)} features, target: '{target_col}'")
        
        return dataset
    
    def find_dump_files(self, directory: str) -> List[str]:
        """Encuentra todos los archivos .dump en un directorio"""
        directory_path = Path(directory)
        dump_files = []
        
        # Buscar archivos .dump con varios patrones
        patterns = ["*.dump", "*.dump.gz", "dump.*", "dump.*.gz", "*.lammpstrj", "*.lammpstrj.gz"]
        
        for pattern in patterns:
            dump_files.extend(directory_path.glob(pattern))
        
        # Eliminar duplicados y ordenar
        dump_files = list(set(dump_files))
        
        return sorted([str(f) for f in dump_files])
    
    def _report_progress(self, current: int, total: int, message: str = ""):
        """Reportar progreso si hay callback"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def set_progress_callback(self, callback):
        """Establecer callback para reportar progreso"""
        self.progress_callback = callback
    
    def analyze_feature_importance(self, dataset: pd.DataFrame, 
                                  target_col: str = '_vacancies_metadata') -> pd.DataFrame:
        """
        Analiza la importancia de las features y su correlación con el target
        Útil para identificar posibles fugas
        """
        if target_col not in dataset.columns:
            logger.warning(f"Columna target '{target_col}' no encontrada")
            return pd.DataFrame()
        
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash']]
        
        correlations = []
        for col in feature_cols:
            if dataset[col].dtype in [np.float64, np.int64]:
                corr = dataset[col].corr(dataset[target_col])
                correlations.append({
                    'feature': col,
                    'correlation': corr,
                    'abs_correlation': abs(corr),
                    'risk_level': 'high' if abs(corr) > 0.7 else 'medium' if abs(corr) > 0.4 else 'low'
                })
        
        importance_df = pd.DataFrame(correlations).sort_values('abs_correlation', ascending=False)
        
        # Almacenar para validación futura
        self._feature_correlations = {row['feature']: row['correlation'] 
                                     for _, row in importance_df.iterrows()}
        
        return importance_df
    
    def get_feature_summary(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Genera resumen detallado de features extraídas"""
        # Separar columnas por tipo
        metadata_cols = [col for col in dataset.columns if col.startswith('_')]
        feature_cols = [col for col in dataset.columns 
                       if not col.startswith('_') and col not in ['file_path', 'file_hash']]
        
        summary = {
            "total_files": len(dataset),
            "total_features": len(feature_cols),
            "feature_mode": self.config.feature_mode.value,
            "feature_categories": {},
            "data_quality": {},
            "configuration": {
                "atm_total": self.config.atm_total,
                "add_noise": self.config.add_noise,
                "noise_level": self.config.noise_level if self.config.add_noise else None
            }
        }
        
        # Categorizar features
        categories = {
            "energy": [],
            "stress": [],
            "coordination": [],
            "spatial": [],
            "voronoi": [],
            "other": []
        }
        
        for col in feature_cols:
            if 'pe_' in col or 'energy' in col.lower():
                categories["energy"].append(col)
            elif 'stress' in col or any(x in col for x in ['sxx', 'syy', 'szz', 'sxy', 'sxz', 'syz']):
                categories["stress"].append(col)
            elif 'coord' in col:
                categories["coordination"].append(col)
            elif any(x in col for x in ['spatial', 'gyration', 'com_']):
                categories["spatial"].append(col)
            elif 'voro' in col:
                categories["voronoi"].append(col)
            else:
                categories["other"].append(col)
        
        summary["feature_categories"] = {k: len(v) for k, v in categories.items()}
        summary["feature_list_by_category"] = categories
        
        # Análisis de calidad de datos
        null_counts = dataset[feature_cols].isnull().sum()
        inf_counts = dataset[feature_cols].apply(lambda x: np.isinf(x).sum())
        
        summary["data_quality"] = {
            "features_with_nulls": int((null_counts > 0).sum()),
            "features_with_inf": int((inf_counts > 0).sum()),
            "total_null_values": int(null_counts.sum()),
            "completeness_ratio": float(1 - null_counts.sum() / (len(dataset) * len(feature_cols)))
        }
        
        # Estadísticas de vacancias (solo si existe en metadata)
        if '_vacancies_metadata' in dataset.columns:
            vac_stats = dataset['_vacancies_metadata'].describe()
            summary["vacancy_distribution"] = {
                "min": int(vac_stats['min']),
                "max": int(vac_stats['max']),
                "mean": float(vac_stats['mean']),
                "std": float(vac_stats['std']),
                "median": float(dataset['_vacancies_metadata'].median())
            }
        
        return summary


# Funciones auxiliares para análisis post-procesamiento

def detect_data_leakage(dataset: pd.DataFrame, target_col: str = '_vacancies_metadata',
                        threshold: float = 0.9) -> List[str]:
    """
    Detecta posibles fugas de información basándose en correlaciones
    
    Args:
        dataset: DataFrame con features
        target_col: Columna objetivo
        threshold: Umbral de correlación para considerar fuga
    
    Returns:
        Lista de features sospechosas
    """
    if target_col not in dataset.columns:
        return []
    
    suspicious_features = []
    feature_cols = [col for col in dataset.columns 
                   if not col.startswith('_') and col not in ['file_path', 'file_hash']]
    
    for col in feature_cols:
        if dataset[col].dtype in [np.float64, np.int64]:
            corr = abs(dataset[col].corr(dataset[target_col]))
            if corr > threshold:
                suspicious_features.append((col, corr))
    
    # Ordenar por correlación
    suspicious_features.sort(key=lambda x: x[1], reverse=True)
    
    if suspicious_features:
        logger.warning(f"Detectadas {len(suspicious_features)} features con alta correlación al target:")
        for feat, corr in suspicious_features[:5]:
            logger.warning(f"  - {feat}: {corr:.3f}")
    
    return [feat for feat, _ in suspicious_features]


def create_train_test_split(dataset: pd.DataFrame, 
                           test_size: float = 0.2,
                           random_state: int = 42,
                           stratify_on: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Crea división train/test con opciones de estratificación
    
    Args:
        dataset: DataFrame completo
        test_size: Proporción del conjunto de test
        random_state: Semilla para reproducibilidad
        stratify_on: Columna para estratificar (e.g., '_vacancies_metadata')
    
    Returns:
        train_df, test_df
    """
    from sklearn.model_selection import train_test_split
    
    if stratify_on and stratify_on in dataset.columns:
        # Crear bins para estratificación si es continua
        stratify_values = pd.qcut(dataset[stratify_on], q=5, labels=False, duplicates='drop')
    else:
        stratify_values = None
    
    train_idx, test_idx = train_test_split(
        dataset.index,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_values
    )
    
    train_df = dataset.loc[train_idx].copy()
    test_df = dataset.loc[test_idx].copy()
    
    logger.info(f"División creada: {len(train_df)} train, {len(test_df)} test")
    
    return train_df, test_df


def prepare_ml_dataset(dataset: pd.DataFrame,
                      target_col: str = 'vacancies',  # Cambiado de '_vacancies_metadata'
                      remove_suspicious: bool = True,
                      correlation_threshold: float = 0.9) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepara dataset para machine learning
    IMPORTANTE: 'vacancies' es el target, NO una feature
    
    Args:
        dataset: DataFrame con features
        target_col: Columna objetivo (default: 'vacancies')
        remove_suspicious: Si eliminar features sospechosas
        correlation_threshold: Umbral para considerar feature sospechosa
    
    Returns:
        X (features), y (target)
    """
    # Copiar dataset
    df = dataset.copy()
    
    # Extraer target
    if target_col not in df.columns:
        # Intentar con el nombre de metadata si no encuentra el principal
        if '_vacancies_metadata' in df.columns:
            logger.warning(f"Usando '_vacancies_metadata' como target en lugar de '{target_col}'")
            target_col = '_vacancies_metadata'
        else:
            raise ValueError(f"Target column '{target_col}' not found in dataset")
    
    y = df[target_col].copy()
    
    # Seleccionar solo features (excluir metadata, columnas auxiliares Y el target)
    exclude_cols = [target_col, 'file_path', 'file_hash']
    exclude_cols.extend([col for col in df.columns if col.startswith('_')])
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols].copy()
    
    logger.info(f"Preparando dataset con {len(feature_cols)} features, target: '{target_col}'")
    
    # Eliminar features sospechosas si está habilitado
    if remove_suspicious:
        # Usar el target correcto para detección de fuga
        suspicious = detect_data_leakage(dataset, target_col, correlation_threshold)
        if suspicious:
            logger.info(f"Eliminando {len(suspicious)} features sospechosas de alta correlación con '{target_col}'")
            X = X.drop(columns=suspicious, errors='ignore')
    
    # Imputar valores faltantes
    from sklearn.impute import SimpleImputer
    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(
        imputer.fit_transform(X),
        columns=X.columns,
        index=X.index
    )
    
    logger.info(f"Dataset preparado: {X_imputed.shape[0]} muestras, {X_imputed.shape[1]} features, target: {y.name}")
    
    return X_imputed, y


# Ejemplo de uso con diferentes modos
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Procesador batch LAMMPS con control de fuga")
    parser.add_argument("directory", help="Directorio con archivos .dump")
    parser.add_argument("--mode", choices=['conservative', 'standard', 'full'],
                       default='standard', help="Modo de extracción de features")
    parser.add_argument("--add-noise", action='store_true',
                       help="Agregar ruido gaussiano a las features")
    parser.add_argument("--noise-level", type=float, default=0.01,
                       help="Nivel de ruido (fracción del valor)")
    parser.add_argument("--output", help="Archivo CSV de salida")
    parser.add_argument("--analyze", action='store_true',
                       help="Realizar análisis de fuga de información")
    
    args = parser.parse_args()
    
    # Configurar procesador
    config = ProcessingConfig(
        feature_mode=FeatureMode[args.mode.upper()],
        add_noise=args.add_noise,
        noise_level=args.noise_level,
        validate_features=True
    )
    
    processor = BatchDumpProcessor(config)
    
    # Procesar directorio
    print(f"Procesando directorio: {args.directory}")
    print(f"Modo: {config.feature_mode.value}")
    
    dataset = processor.process_directory(args.directory, validate=True)
    
    # Análisis de fuga si está habilitado
    if args.analyze:
        print("\n=== Análisis de Fuga de Información ===")
        importance_df = processor.analyze_feature_importance(dataset)
        
        if not importance_df.empty:
            print("\nTop 10 features más correlacionadas con vacancias:")
            print(importance_df.head(10).to_string())
            
            high_risk = importance_df[importance_df['risk_level'] == 'high']
            if not high_risk.empty:
                print(f"\n⚠️ ADVERTENCIA: {len(high_risk)} features de alto riesgo detectadas")
                print(high_risk[['feature', 'correlation']].to_string())
    
    # Resumen
    summary = processor.get_feature_summary(dataset)
    print("\n=== Resumen del Procesamiento ===")
    print(f"Total archivos: {summary['total_files']}")
    print(f"Total features: {summary['total_features']}")
    print(f"Modo: {summary['feature_mode']}")
    print(f"Categorías de features:")
    for cat, count in summary['feature_categories'].items():
        print(f"  - {cat}: {count}")
    print(f"Calidad de datos: {summary['data_quality']['completeness_ratio']:.1%} completo")
    
    # Guardar resultados
    if args.output:
        # Separar features de metadata antes de guardar
        feature_cols = [col for col in dataset.columns if not col.startswith('_')]
        dataset[feature_cols].to_csv(args.output)
        print(f"\nFeatures guardadas en: {args.output}")
        
        # Guardar metadata separadamente
        metadata_file = args.output.replace('.csv', '_metadata.csv')
        metadata_cols = [col for col in dataset.columns if col.startswith('_')]
        if metadata_cols:
            dataset[metadata_cols].to_csv(metadata_file)
            print(f"Metadata guardada en: {metadata_file}")