"""
Procesador batch para archivos LAMMPS dump - Integración con GUI
Versión corregida SIN FUGA de información
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
    """Procesador batch de archivos LAMMPS dump para extracción de features SIN FUGA"""
    
    def __init__(self):
        # Configuración por defecto
        self.atm_total = 16384
        self.energy_min = -4.0
        self.energy_max = -3.0
        self.energy_bins = 10
        
        # Features prohibidas que causan fuga de información
        self.forbidden_features = [
            'n_atoms',
            'vacancy_fraction', 
            'vacancy_count',
            'atm_total_ref' # Ahora también prohibimos vacancies como feature
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

        # CORRECCIÓN: Usar ** para potencia en lugar de ^
        vm = np.sqrt(1.5*(sxx_dev**2 + syy_dev**2 + szz_dev**2 + 2*(sxy**2 + sxz**2 + syz**2)))

        df = df.copy()
        df["stress_I1"] = I1
        df["stress_vm"] = vm
        return df
    
    def compute_coordination_histogram(self, coord_series: pd.Series) -> Dict[str, float]:
        """Calcula histograma de coordinación"""
        coord_clean = coord_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        hist_features = {}
        if len(coord_clean) == 0:
            hist_features["coord_bin_4_5"] = 0.0
            hist_features["coord_bin_6_7"] = 0.0
            hist_features["coord_bin_8_9"] = 0.0
            hist_features["coord_bin_10_11"] = 0.0
            hist_features["coord_bin_12"] = 0.0
            hist_features["coord_below_8"] = 0.0
            hist_features["coord_perfect_12"] = 0.0
            return hist_features
        
        total = len(coord_clean)
        
        hist_features["coord_bin_4_5"] = float(((coord_clean >= 4) & (coord_clean <= 5)).sum() / total)
        hist_features["coord_bin_6_7"] = float(((coord_clean >= 6) & (coord_clean <= 7)).sum() / total)
        hist_features["coord_bin_8_9"] = float(((coord_clean >= 8) & (coord_clean <= 9)).sum() / total)
        hist_features["coord_bin_10_11"] = float(((coord_clean >= 10) & (coord_clean <= 11)).sum() / total)
        hist_features["coord_bin_12"] = float((coord_clean >= 12).sum() / total)
        
        hist_features["coord_below_8"] = float((coord_clean < 8).sum() / total)
        hist_features["coord_perfect_12"] = float((coord_clean == 12).sum() / total)
        
        return hist_features
    
    def compute_energy_histogram(self, pe_series: pd.Series) -> Dict[str, float]:
        """Calcula histograma de energía"""
        pe_clean = pe_series.replace([np.inf, -np.inf], np.nan).dropna()
        
        hist_features = {}
        
        if len(pe_clean) == 0:
            for i in range(self.energy_bins):
                hist_features[f"pe_bin_{i}"] = 0.0
            hist_features["pe_below_min"] = 0.0
            hist_features["pe_above_max"] = 0.0
            return hist_features
        
        total = len(pe_clean)
        bin_edges = np.linspace(self.energy_min, self.energy_max, self.energy_bins + 1)
        hist, _ = np.histogram(pe_clean, bins=bin_edges)
        
        for i in range(self.energy_bins):
            hist_features[f"pe_bin_{i}"] = float(hist[i] / total)
        
        hist_features["pe_below_min"] = float((pe_clean < self.energy_min).sum() / total)
        hist_features["pe_above_max"] = float((pe_clean > self.energy_max).sum() / total)
        
        return hist_features
    
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
    
    def agg_stats(self, x: pd.Series, prefix: str) -> Dict[str, float]:
        """Calcula estadísticos agregados robustos"""
        x = pd.to_numeric(x, errors="coerce").replace([np.inf,-np.inf], np.nan).dropna()
        if x.empty:
            return {f"{prefix}_{k}": np.nan for k in
                    ["min","p10","p25","median","p75","p90","max","mean","std","skew","kurt"]}
        q = x.quantile([0.10,0.25,0.50,0.75,0.90])
        return {
            f"{prefix}_min":   float(x.min()),
            f"{prefix}_p10":   float(q.loc[0.10]),
            f"{prefix}_p25":   float(q.loc[0.25]),
            f"{prefix}_median":float(q.loc[0.50]),
            f"{prefix}_p75":   float(q.loc[0.75]),
            f"{prefix}_p90":   float(q.loc[0.90]),
            f"{prefix}_max":   float(x.max()),
            f"{prefix}_mean":  float(x.mean()),
            f"{prefix}_std":   float(x.std(ddof=1)) if len(x)>1 else 0.0,
            f"{prefix}_skew":  float(x.skew()) if len(x)>2 else 0.0,
            f"{prefix}_kurt":  float(x.kurt()) if len(x)>3 else 0.0,
        }
    
    def extra_bulk_indicators(self, props: Dict[str, pd.Series]) -> Dict[str, float]:
        """Indicadores adicionales de defectos en bulk"""
        out = {}
        
        if "coord" in props:
            c = props["coord"].dropna()
            out["frac_coord_le_11"] = float((c <= 11).mean()) if len(c) else np.nan
            out["frac_coord_le_10"] = float((c <= 10).mean()) if len(c) else np.nan
            out["frac_coord_le_9"] = float((c <= 9).mean()) if len(c) else np.nan
        
        if "coord2" in props:
            c2 = props["coord2"].dropna()
            if len(c2):
                out["frac_coord2_le_5"] = float((c2 <= 5).mean())
                out["frac_coord2_le_4"] = float((c2 <= 4).mean())
                out["frac_coord2_le_3"] = float((c2 <= 3).mean())
        
        if "stress_vm" in props:
            vm = props["stress_vm"].dropna()
            if len(vm):
                thr = vm.quantile(0.95)
                out["frac_vm_top5"] = float((vm >= thr).mean())
        
        if "pe" in props:
            pe = props["pe"].dropna()
            if len(pe):
                thr = pe.quantile(0.95)
                out["frac_pe_top5"] = float((pe >= thr).mean())
        
        return out
    
    def extract_features_from_dump(self, df: pd.DataFrame, n_atoms: int) -> Dict[str, Any]:
        """
        Extrae features de un DataFrame de átomos SIN incluir información de vacancias
        que pueda causar fuga de información
        
        IMPORTANTE: Todas las estadísticas se calculan sobre los átomos presentes,
        NO sobre el total configurado por el usuario
        """
        df = self.add_stress_invariants(df)
        props = self.pick_candidate_properties(df)

        feats: Dict[str, Any] = {}
        
        # Agregados estadísticos por propiedad (solo sobre átomos presentes)
        for pname, series in props.items():
            feats.update(self.agg_stats(series, pname))

        # Indicadores de defectos (solo sobre átomos presentes)
        feats.update(self.extra_bulk_indicators(props))

        # Histograma de coordinación (solo sobre átomos presentes)
        if "coord" in props:
            coord_hist = self.compute_coordination_histogram(props["coord"])
            feats.update(coord_hist)
        
        # Histograma de energía (solo sobre átomos presentes)
        if "pe" in props:
            pe_hist = self.compute_energy_histogram(props["pe"])
            feats.update(pe_hist)

        # Energía mínima absoluta (solo sobre átomos presentes)
        if "pe" in props:
            pe_clean = props["pe"].replace([np.inf, -np.inf], np.nan).dropna()
            if len(pe_clean):
                feats["pe_absolute_min"] = float(pe_clean.min())
        
        # IMPORTANTE: NO incluimos vacancies en las features
        # El target se calculará externamente si es necesario
        # vacancies = int(self.atm_total - n_atoms)  # ¡NO INCLUIR!
        
        return feats
    
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
        Procesa todos los archivos .dump en un directorio y retorna DataFrame con features
        SIN incluir información de vacancias
        """
        dump_files = self.find_dump_files(directory)
        
        if not dump_files:
            raise ValueError(f"No se encontraron archivos .dump en {directory}")
        
        logger.info(f"Encontrados {len(dump_files)} archivos .dump")
        self._report_progress(0, len(dump_files), "Iniciando procesamiento...")
        
        rows = []
        errors = []
        
        for i, file_path in enumerate(dump_files, 1):
            try:
                file_name = Path(file_path).name
                self._report_progress(i, len(dump_files), f"Procesando {file_name}")
                
                # Parsear archivo dump
                df, n_atoms = self.parse_last_frame_dump(file_path)
                
                # Extraer features (SIN información de vacancias)
                features = self.extract_features_from_dump(df, n_atoms)
                features["file"] = file_name
                features["file_path"] = file_path
                
                # Calcular vacancias solo como metadata, no como feature
                vacancies = int(self.atm_total - n_atoms)
                features["vacancies"] = vacancies  # Solo para uso externo como target
                
                rows.append(features)
                
                logger.info(f"Procesado {file_name}: {n_atoms} átomos presentes, {vacancies} vacancias")
                
            except Exception as e:
                error_msg = f"Error en {Path(file_path).name}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        if not rows:
            raise RuntimeError("No se pudieron procesar archivos correctamente")
        
        # Crear DataFrame
        dataset = pd.DataFrame(rows).set_index("file").sort_index()
        
        # ELIMINAR features prohibidas para evitar fuga
        for forbidden in self.forbidden_features:
            if forbidden in dataset.columns:
                dataset = dataset.drop(columns=[forbidden])
                logger.info(f"Eliminada feature prohibida: {forbidden}")
        
        # Reportar errores si los hubo
        if errors:
            error_summary = f"Se encontraron {len(errors)} errores durante el procesamiento"
            logger.warning(error_summary)
            self._report_progress(len(dump_files), len(dump_files), error_summary)
        else:
            self._report_progress(len(dump_files), len(dump_files), "Procesamiento completado")
        
        return dataset
    
    def get_feature_summary(self, dataset: pd.DataFrame) -> Dict[str, Any]:
        """Genera resumen de features extraídas"""
        summary = {
            "total_files": len(dataset),
            "total_features": len([col for col in dataset.columns if col not in ['file_path']]),
            "feature_categories": {},
            "vacancy_stats": {}
        }
        
        # Categorizar features (excluyendo metadata)
        feature_cols = [col for col in dataset.columns if col not in ['file_path']]
        
        coord_features = [col for col in feature_cols if col.startswith('coord')]
        pe_features = [col for col in feature_cols if col.startswith('pe')]
        stress_features = [col for col in feature_cols if col.startswith('stress') or any(x in col for x in ['sxx', 'syy', 'szz', 'sxy', 'sxz', 'syz'])]
        
        summary["feature_categories"] = {
            "coordination": len(coord_features),
            "potential_energy": len(pe_features), 
            "stress": len(stress_features),
            "other": len(feature_cols) - len(coord_features) - len(pe_features) - len(stress_features)
        }
        
        # Estadísticas de vacancias si existe la columna (solo para información)
        if 'vacancies' in dataset.columns:
            vac_stats = dataset['vacancies'].describe()
            summary["vacancy_stats"] = {
                "min": int(vac_stats['min']),
                "max": int(vac_stats['max']),
                "mean": float(vac_stats['mean']),
                "std": float(vac_stats['std'])
            }
        
        return summary