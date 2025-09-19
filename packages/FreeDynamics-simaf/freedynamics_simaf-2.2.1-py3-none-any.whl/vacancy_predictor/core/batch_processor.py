"""
Procesador batch para archivos LAMMPS dump - VERSIÓN CORREGIDA SIN FUGA DE INFORMACIÓN
Elimina todos los features problemáticos identificados en el análisis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
import gzip
import io

logger = logging.getLogger(__name__)

class BatchDumpProcessor:
    """Procesador batch de archivos LAMMPS dump SIN FUGA de información"""
    
    def __init__(self):
        # Configuración por defecto
        self.atm_total = 16384
        self.energy_min = -4.0
        self.energy_max = -3.0
        self.energy_bins = 10
        
        # Features COMPLETAMENTE PROHIBIDAS para evitar fuga
        self.forbidden_features = [
            # Obvias
            'n_atoms', 'vacancy_fraction', 'vacancy_count', 'atm_total_ref',
            
            # CRÍTICAS identificadas
            'pe_absolute_min',  # FUGA CRÍTICA
            'pe_min',           # Mínimo energía = fuga directa
            'pe_p10',           # Percentiles bajos = fuga
            'pe_p25',           # Percentiles bajos = fuga
            'coord_min',        # Coordinación mínima = fuga
            'coord_p10',        # Percentiles bajos coordinación
            'stress_vm_min',    # Mínimos de stress problemáticos
            'stress_I1_min',    # Mínimos de stress problemáticos
            
            # Cualquier feature que termine en _min
            # (se filtrará dinámicamente)
        ]
        
        self.progress_callback = None
        
    def set_parameters(self, atm_total=16384, energy_min=-4.0, energy_max=-3.0, energy_bins=10):
        """Configurar parámetros del procesador"""
        self.atm_total = atm_total
        self.energy_min = energy_min
        self.energy_max = energy_max
        self.energy_bins = energy_bins
        
    def set_progress_callback(self, callback):
        """Establecer callback para reportar progreso"""
        self.progress_callback = callback
        
    def _report_progress(self, current, total, message=""):
        """Reportar progreso si hay callback"""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def _open_any(self, path: str):
        """Abrir archivo, detectando si está comprimido"""
        p = Path(path)
        if p.suffix == ".gz":
            return io.TextIOWrapper(gzip.open(p, "rb"), encoding="utf-8", newline="")
        return open(p, "r", encoding="utf-8", newline="")
    
    def parse_last_frame_dump(self, path: str) -> Tuple[pd.DataFrame, int]:
        """Lee el ÚLTIMO frame del dump LAMMPS"""
        with self._open_any(path) as f:
            lines = f.read().splitlines()

        idx_atoms = [i for i,l in enumerate(lines) if l.startswith("ITEM: ATOMS ")]
        if not idx_atoms:
            raise RuntimeError(f"No se encontró 'ITEM: ATOMS' en {path}")
        start = idx_atoms[-1]
        header = lines[start].replace("ITEM: ATOMS", "").strip().split()

        nat = None
        for j in range(start-1, -1, -1):
            if lines[j].startswith("ITEM: NUMBER OF ATOMS"):
                nat = int(lines[j+1].strip())
                break
        if nat is None:
            raise RuntimeError(f"No se encontró 'ITEM: NUMBER OF ATOMS' para {path}")

        rows = lines[start+1:start+1+nat]
        K = len(header)
        arr = np.full((len(rows), K), np.nan, dtype=float)
        for r, line in enumerate(rows):
            parts = line.split()
            for c in range(min(K, len(parts))):
                try: 
                    arr[r,c] = float(parts[c])
                except: 
                    arr[r,c] = np.nan
        
        df = pd.DataFrame(arr, columns=header)
        return df, nat
    
    def add_stress_invariants(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega invariantes de stress I1 y von Mises"""
        cols = [f"c_satom[{i}]" for i in range(1,7)]
        if not all(c in df.columns for c in cols):
            return df
        
        sxx, syy, szz, sxy, sxz, syz = (df[c].astype(float) for c in cols)

        I1 = sxx + syy + szz
        mean_normal = I1 / 3.0
        sxx_dev = sxx - mean_normal
        syy_dev = syy - mean_normal
        szz_dev = szz - mean_normal

        # von Mises stress
        vm = np.sqrt(1.5*(sxx_dev**2 + syy_dev**2 + szz_dev**2 + 2*(sxy**2 + sxz**2 + syz**2)))

        df = df.copy()
        df["stress_I1"] = I1
        df["stress_vm"] = vm
        return df
    
    def compute_safe_coordination_features(self, coord_series: pd.Series) -> Dict[str, float]:
        """
        Calcula features de coordinación SEGUROS (sin normalización problemática)
        """
        coord_clean = coord_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        features = {}
        
        if len(coord_clean) == 0:
            # Valores por defecto si no hay datos
            features["coord_mode_ratio"] = 0.0
            features["coord_spread"] = 0.0
            features["coord_asymmetry"] = 0.0
            return features
        
        # 1. SAFE: Ratios internos (no dependen del total de átomos)
        coord_12 = (coord_clean == 12).sum()
        coord_11 = (coord_clean == 11).sum()
        coord_10_or_less = (coord_clean <= 10).sum()
        
        total_present = len(coord_clean)
        
        # Ratios seguros entre diferentes tipos de coordinación
        features["coord_perfect_ratio"] = float(coord_12 / total_present) if total_present > 0 else 0.0
        features["coord_near_perfect_ratio"] = float(coord_11 / total_present) if total_present > 0 else 0.0
        features["coord_defective_ratio"] = float(coord_10_or_less / total_present) if total_present > 0 else 0.0
        
        # 2. SAFE: Estadísticas robustas (solo percentiles medios/altos)
        features["coord_median"] = float(coord_clean.median())
        features["coord_p75"] = float(coord_clean.quantile(0.75))
        features["coord_p90"] = float(coord_clean.quantile(0.90))
        features["coord_max"] = float(coord_clean.max())  # Max es generalmente seguro
        
        # 3. SAFE: Medidas de dispersión relativas
        if len(coord_clean) > 1:
            features["coord_iqr"] = float(coord_clean.quantile(0.75) - coord_clean.quantile(0.25))
            features["coord_cv"] = float(coord_clean.std() / coord_clean.mean()) if coord_clean.mean() > 0 else 0.0
        
        # 4. SAFE: Asimetría interna (sin referencia a totales)
        features["coord_range"] = float(coord_clean.max() - coord_clean.median())
        
        return features
    
    def compute_safe_energy_features(self, pe_series: pd.Series) -> Dict[str, float]:
        """
        Calcula features de energía SEGUROS 
        ELIMINA: pe_min, pe_absolute_min, pe_p10, pe_p25
        """
        pe_clean = pe_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        features = {}
        
        if len(pe_clean) == 0:
            features["pe_median"] = np.nan
            features["pe_p75"] = np.nan
            features["pe_p90"] = np.nan
            features["pe_max"] = np.nan
            features["pe_iqr"] = np.nan
            features["pe_upper_spread"] = np.nan
            return features
        
        # SOLO percentiles medios y altos (NO mínimos)
        features["pe_median"] = float(pe_clean.median())
        features["pe_p75"] = float(pe_clean.quantile(0.75))
        features["pe_p90"] = float(pe_clean.quantile(0.90))
        features["pe_max"] = float(pe_clean.max())  # Max puede ser informativo
        
        # Medidas de dispersión seguras
        if len(pe_clean) > 1:
            features["pe_iqr"] = float(pe_clean.quantile(0.75) - pe_clean.quantile(0.25))
            features["pe_upper_spread"] = float(pe_clean.max() - pe_clean.median())
            
            # Coeficiente de variación (relativo)
            if pe_clean.mean() != 0:
                features["pe_cv"] = float(pe_clean.std() / abs(pe_clean.mean()))
            
        # Histograma MODIFICADO: bins relativos, no absolutos
        self._add_safe_energy_histogram(pe_clean, features)
        
        return features
    
    def _add_safe_energy_histogram(self, pe_clean: pd.Series, features: Dict[str, float]):
        """
        Histograma de energía SEGURO: usa bins relativos a la distribución actual
        NO usa bins absolutos fijos que pueden crear fuga
        """
        if len(pe_clean) == 0:
            return
        
        # Usar quintiles internos en lugar de bins absolutos
        quintiles = pe_clean.quantile([0.2, 0.4, 0.6, 0.8])
        
        total = len(pe_clean)
        
        # Bins relativos basados en la distribución actual
        features["pe_bottom_quintile"] = float((pe_clean <= quintiles[0.2]).sum() / total)
        features["pe_lower_mid_quintile"] = float(
            ((pe_clean > quintiles[0.2]) & (pe_clean <= quintiles[0.4])).sum() / total
        )
        features["pe_mid_quintile"] = float(
            ((pe_clean > quintiles[0.4]) & (pe_clean <= quintiles[0.6])).sum() / total
        )
        features["pe_upper_mid_quintile"] = float(
            ((pe_clean > quintiles[0.6]) & (pe_clean <= quintiles[0.8])).sum() / total
        )
        features["pe_top_quintile"] = float((pe_clean > quintiles[0.8]).sum() / total)
        
    def compute_safe_stress_features(self, stress_props: Dict[str, pd.Series]) -> Dict[str, float]:
        """
        Calcula features de stress SEGUROS
        ELIMINA: stress_*_min, percentiles bajos
        """
        features = {}
        
        for stress_name, stress_series in stress_props.items():
            if stress_name not in ['stress_I1', 'stress_vm', 'sxx', 'syy', 'szz', 'sxy', 'sxz', 'syz']:
                continue
                
            stress_clean = stress_series.replace([np.inf, -np.inf], np.nan).dropna()
            
            if len(stress_clean) == 0:
                continue
            
            prefix = stress_name
            
            # SOLO estadísticas seguras (no mínimos)
            features[f"{prefix}_median"] = float(stress_clean.median())
            features[f"{prefix}_p75"] = float(stress_clean.quantile(0.75))
            features[f"{prefix}_p90"] = float(stress_clean.quantile(0.90))
            features[f"{prefix}_max"] = float(stress_clean.max())
            
            if len(stress_clean) > 1:
                features[f"{prefix}_std"] = float(stress_clean.std())
                features[f"{prefix}_iqr"] = float(
                    stress_clean.quantile(0.75) - stress_clean.quantile(0.25)
                )
        
        return features
    
    def pick_candidate_properties(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """Selecciona propiedades per-átomo candidatas"""
        props: Dict[str, pd.Series] = {}

        # Energía potencial
        for name in ["c_peatom", "pe", "c_pe", "v_pe"]:
            if name in df.columns:
                props["pe"] = df[name].astype(float)
                break

        # Esfuerzos invariantes
        if "stress_I1" in df.columns:  
            props["stress_I1"] = df["stress_I1"].astype(float)
        if "stress_vm" in df.columns:  
            props["stress_vm"] = df["stress_vm"].astype(float)

        # Componentes de stress
        for i, comp in zip(range(1,7), ["sxx","syy","szz","sxy","sxz","syz"]):
            col = f"c_satom[{i}]"
            if col in df.columns: 
                props[comp] = df[col].astype(float)

        # Coordinación
        for name in ["c_coord", "coord", "c_coord1"]:
            if name in df.columns:
                props["coord"] = df[name].astype(float)
                break
        
        for name in ["c_coord2", "coord2", "c_coord_2nd"]:
            if name in df.columns:
                props["coord2"] = df[name].astype(float)
                break

        # Voronoi
        if "c_voro[1]" in df.columns:
            props["voro_vol"] = df["c_voro[1]"].astype(float)

        # Energía cinética
        for name in ["c_keatom", "ke"]:
            if name in df.columns:
                props["ke"] = df[name].astype(float)
                break

        return props
    
    def extract_features_from_dump(self, df: pd.DataFrame, n_atoms: int) -> Dict[str, Any]:
        """
        Extrae features de un DataFrame de átomos SIN FUGA DE INFORMACIÓN
        """
        df = self.add_stress_invariants(df)
        props = self.pick_candidate_properties(df)

        feats: Dict[str, Any] = {}
        
        # 1. Features SEGUROS de coordinación
        if "coord" in props:
            coord_features = self.compute_safe_coordination_features(props["coord"])
            feats.update(coord_features)
        
        if "coord2" in props:
            coord2_features = self.compute_safe_coordination_features(props["coord2"])
            # Añadir prefijo para diferenciar
            coord2_features = {f"coord2_{k}": v for k, v in coord2_features.items()}
            feats.update(coord2_features)
        
        # 2. Features SEGUROS de energía (SIN pe_min, pe_absolute_min, etc.)
        if "pe" in props:
            pe_features = self.compute_safe_energy_features(props["pe"])
            feats.update(pe_features)
        
        # 3. Features SEGUROS de stress
        stress_props = {k: v for k, v in props.items() 
                       if k in ['stress_I1', 'stress_vm', 'sxx', 'syy', 'szz', 'sxy', 'sxz', 'syz']}
        if stress_props:
            stress_features = self.compute_safe_stress_features(stress_props)
            feats.update(stress_features)
        
        # 4. Features seguros de Voronoi
        if "voro_vol" in props:
            voro_features = self.compute_safe_energy_features(props["voro_vol"])
            voro_features = {f"voro_{k}": v for k, v in voro_features.items()}
            feats.update(voro_features)
        
        # 5. Features seguros de energía cinética
        if "ke" in props:
            ke_features = self.compute_safe_energy_features(props["ke"])
            ke_features = {f"ke_{k}": v for k, v in ke_features.items()}
            feats.update(ke_features)
        
        # IMPORTANTE: Vacancies SOLO como metadata, NO como feature
        vacancies = int(self.atm_total - n_atoms)
        feats["vacancies"] = vacancies  # Solo para target externo
        
        return feats
    
    def _filter_forbidden_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filtra features prohibidos, incluyendo filtrado dinámico
        """
        filtered = {}
        
        for feature_name, value in features.items():
            # Filtros específicos
            if feature_name in self.forbidden_features:
                logger.info(f"Eliminando feature prohibido: {feature_name}")
                continue
            
            # Filtros dinámicos
            if feature_name.endswith('_min'):
                logger.info(f"Eliminando feature con _min: {feature_name}")
                continue
            
            if feature_name.endswith('_p10'):
                logger.info(f"Eliminando percentil bajo: {feature_name}")
                continue
                
            if feature_name.endswith('_p25') and any(x in feature_name for x in ['pe_', 'coord_']):
                logger.info(f"Eliminando percentil bajo problemático: {feature_name}")
                continue
            
            # Feature pasa todos los filtros
            filtered[feature_name] = value
        
        return filtered
    
    def find_dump_files(self, directory: str) -> List[str]:
        """Encuentra todos los archivos .dump en un directorio"""
        directory_path = Path(directory)
        dump_files = []
        
        # Buscar archivos .dump
        dump_files.extend(directory_path.glob("*.dump"))
        dump_files.extend(directory_path.glob("*.dump.gz"))
        
        # También buscar patrones comunes
        dump_files.extend(directory_path.glob("dump.*"))
        dump_files.extend(directory_path.glob("dump.*.gz"))
        
        return sorted([str(f) for f in dump_files])
    
    def process_directory(self, directory: str) -> pd.DataFrame:
        """
        Procesa todos los archivos .dump en un directorio
        VERSIÓN CORREGIDA sin data leakage
        """
        dump_files = self.find_dump_files(directory)
        
        if not dump_files:
            raise ValueError(f"No se encontraron archivos .dump en {directory}")
        
        logger.info(f"Encontrados {len(dump_files)} archivos .dump")
        self._report_progress(0, len(dump_files), "Iniciando procesamiento sin fuga...")
        
        rows = []
        errors = []
        
        for i, file_path in enumerate(dump_files, 1):
            try:
                file_name = Path(file_path).name
                self._report_progress(i, len(dump_files), f"Procesando {file_name}")
                
                # Parsear archivo dump
                df, n_atoms = self.parse_last_frame_dump(file_path)
                
                # Extraer features SEGUROS
                features = self.extract_features_from_dump(df, n_atoms)
                
                # Filtrar features prohibidos
                features = self._filter_forbidden_features(features)
                
                features["file"] = file_name
                features["file_path"] = file_path
                
                rows.append(features)
                
                vacancies = int(self.atm_total - n_atoms)
                logger.info(f"Procesado {file_name}: {n_atoms} átomos, {vacancies} vacancies, {len(features)} features seguros")
                
            except Exception as e:
                error_msg = f"Error en {Path(file_path).name}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        if not rows:
            raise RuntimeError("No se pudieron procesar archivos correctamente")
        
        # Crear DataFrame
        dataset = pd.DataFrame(rows).set_index("file").sort_index()
        
        # Reporte final de seguridad
        total_features = len([col for col in dataset.columns if col not in ['file_path', 'vacancies']])
        logger.info(f"Dataset final: {len(dataset)} muestras, {total_features} features SEGUROS")
        
        # Reportar errores si los hubo
        if errors:
            error_summary = f"Se encontraron {len(errors)} errores durante el procesamiento"
            logger.warning(error_summary)
            self._report_progress(len(dump_files), len(dump_files), error_summary)
        else:
            self._report_progress(len(dump_files), len(dump_files), "Procesamiento sin fuga completado")
        
        return dataset
    
    def get_feature_summary(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Genera resumen de features extraídas (versión corregida)"""
        summary = {
            "total_files": len(dataset),
            "total_safe_features": len([col for col in dataset.columns if col not in ['file_path', 'vacancies']]),
            "feature_categories": {},
            "vacancy_stats": {},
            "safety_report": {}
        }
        
        # Categorizar features seguros
        feature_cols = [col for col in dataset.columns if col not in ['file_path', 'vacancies']]
        
        coord_features = [col for col in feature_cols if col.startswith('coord')]
        pe_features = [col for col in feature_cols if col.startswith('pe_')]
        stress_features = [col for col in feature_cols if col.startswith('stress_') or any(x in col for x in ['sxx_', 'syy_', 'szz_', 'sxy_', 'sxz_', 'syz_'])]
        
        summary["feature_categories"] = {
            "coordination_safe": len(coord_features),
            "potential_energy_safe": len(pe_features), 
            "stress_safe": len(stress_features),
            "other_safe": len(feature_cols) - len(coord_features) - len(pe_features) - len(stress_features)
        }
        
        # Verificar que no hay features problemáticos
        forbidden_found = []
        for col in feature_cols:
            if col.endswith('_min') or col.endswith('_p10'):
                forbidden_found.append(col)
        
        summary["safety_report"] = {
            "forbidden_features_found": forbidden_found,
            "is_safe": len(forbidden_found) == 0,
            "eliminated_categories": ["_min statistics", "_p10 percentiles", "absolute minimum values"]
        }
        
        # Estadísticas de vacancies (solo metadata)
        if 'vacancies' in dataset.columns:
            vac_stats = dataset['vacancies'].describe()
            summary["vacancy_stats"] = {
                "min": int(vac_stats['min']),
                "max": int(vac_stats['max']),
                "mean": float(vac_stats['mean']),
                "std": float(vac_stats['std']),
                "note": "Vacancies solo como target, NO como feature"
            }
        
        return summary