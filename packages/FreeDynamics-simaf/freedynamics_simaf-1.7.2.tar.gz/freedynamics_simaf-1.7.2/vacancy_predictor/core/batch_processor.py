def pick_candidate_properties(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Selecciona propiedades per-átomo candidatas"""
    props: Dict[str, pd.Series] = {}

    # Energía potencial
    for name in ["c_peatom", "pe", "c_pe", "v_pe"]:
        if name in df.columns:
            props["pe"] = df[name].astype(float)  # CORRECCIÓN: astype en lugar de ast
            break

    # Esfuerzos invariantes
    if "stress_I1" in df.columns:  
        props["stress_I1"] = df["stress_I1"].astype(float)  # CORRECCIÓN
    if "stress_vm" in df.columns:  
        props["stress_vm"] = df["stress_vm"].astype(float)  # CORRECCIÓN

    # Componentes de stress
    for i, comp in zip(range(1,7), ["sxx","syy","szz","sxy","sxz","syz"]):
        col = f"c_satom[{i}]"
        if col in df.columns: 
            props[comp] = df[col].astype(float)  # CORRECCIÓN

    # Coordinación
    for name in ["c_coord", "coord", "c_coord1"]:
        if name in df.columns:
            props["coord"] = df[name].astype(float)  # CORRECCIÓN
            break
    
    for name in ["c_coord2", "coord2", "c_coord_2nd"]:
        if name in df.columns:
            props["coord2"] = df[name].astype(float)  # CORRECCIÓN
            break

    # Voronoi
    if "c_voro[1]" in df.columns:
        props["voro_vol"] = df["c_voro[1]"].astype(float)  # CORRECCIÓN

    # Energía cinética
    for name in ["c_keatom", "ke"]:
        if name in df.columns:
            props["ke"] = df[name].astype(float)  # CORRECCIÓN
            break

    return props