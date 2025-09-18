"""
Tab de selección de features con tabla interactiva
Permite activar/desactivar features para el entrenamiento del modelo
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import numpy as np
from typing import Callable, Dict, List, Optional

class FeatureSelectionTab:
    """Tab para selección interactiva de features"""
    
    def __init__(self, parent, feature_update_callback: Callable):
        self.parent = parent
        self.feature_update_callback = feature_update_callback
        
        self.frame = ttk.Frame(parent)
        
        # Estado del tab
        self.current_data = None
        self.all_features = []
        self.selected_features = []
        self.feature_stats = {}
        self.feature_importance = None
        
        # Variables de control
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_features)
        
        self.category_filter_var = tk.StringVar(value="Todas")
        self.importance_filter_var = tk.StringVar(value="Todas")
        
        # Variables de selección masiva
        self.select_all_var = tk.BooleanVar()
        self.select_top_n_var = tk.IntVar(value=20)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del tab"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Panel superior - Controles
        self.create_controls_panel(main_container)
        
        # Panel principal - Tabla de features
        self.create_features_table(main_container)
        
        # Panel inferior - Estadísticas y acciones
        self.create_stats_panel(main_container)
    
    def create_controls_panel(self, parent):
        """Crear panel de controles superiores"""
        controls_frame = ttk.LabelFrame(parent, text="Controles de Selección", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Primera fila - Búsqueda y filtros
        row1 = ttk.Frame(controls_frame)
        row1.pack(fill="x", pady=(0, 5))
        
        # Búsqueda
        ttk.Label(row1, text="Buscar feature:").pack(side="left")
        search_entry = ttk.Entry(row1, textvariable=self.search_var, width=25)
        search_entry.pack(side="left", padx=(5, 15))
        
        # Filtro por categoría
        ttk.Label(row1, text="Categoría:").pack(side="left")
        category_combo = ttk.Combobox(row1, textvariable=self.category_filter_var, 
                                     values=["Todas", "Coordinación", "Energía", "Stress", "Histogramas", "Estadísticas", "Otras"],
                                     state="readonly", width=12)
        category_combo.pack(side="left", padx=(5, 15))
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_features())
        
        # Filtro por importancia
        ttk.Label(row1, text="Importancia:").pack(side="left")
        importance_combo = ttk.Combobox(row1, textvariable=self.importance_filter_var,
                                       values=["Todas", "Alta (>0.05)", "Media (0.01-0.05)", "Baja (<0.01)"],
                                       state="readonly", width=15)
        importance_combo.pack(side="left", padx=(5, 0))
        importance_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_features())
        
        # Segunda fila - Selección masiva
        row2 = ttk.Frame(controls_frame)
        row2.pack(fill="x", pady=(5, 0))
        
        # Seleccionar todos
        select_all_cb = ttk.Checkbutton(row2, text="Seleccionar todas las features visibles", 
                                       variable=self.select_all_var, command=self.toggle_all_features)
        select_all_cb.pack(side="left")
        
        # Seleccionar top N
        ttk.Label(row2, text="Seleccionar top").pack(side="left", padx=(20, 5))
        top_n_spinbox = ttk.Spinbox(row2, from_=5, to=100, textvariable=self.select_top_n_var, width=8)
        top_n_spinbox.pack(side="left")
        ttk.Button(row2, text="por importancia", command=self.select_top_features).pack(side="left", padx=(5, 0))
        
        # Botones de acción
        ttk.Button(row2, text="Invertir selección", command=self.invert_selection).pack(side="right", padx=(5, 0))
        ttk.Button(row2, text="Limpiar selección", command=self.clear_selection).pack(side="right", padx=(5, 0))
    
    def create_features_table(self, parent):
        """Crear tabla principal de features"""
        table_frame = ttk.LabelFrame(parent, text="Features Disponibles", padding="10")
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Frame para la tabla con scrollbars
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill="both", expand=True)
        
        # Definir columnas
        columns = ('selected', 'feature', 'category', 'importance', 'correlation', 'missing_pct', 'min_val', 'max_val', 'mean_val', 'std_val')
        
        self.features_tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        # Configurar headers
        self.features_tree.heading('selected', text='✓')
        self.features_tree.heading('feature', text='Feature')
        self.features_tree.heading('category', text='Categoría')
        self.features_tree.heading('importance', text='Importancia')
        self.features_tree.heading('correlation', text='Correlación')
        self.features_tree.heading('missing_pct', text='% Faltantes')
        self.features_tree.heading('min_val', text='Mín')
        self.features_tree.heading('max_val', text='Máx')
        self.features_tree.heading('mean_val', text='Media')
        self.features_tree.heading('std_val', text='Desv. Est.')
        
        # Configurar anchos de columnas
        self.features_tree.column('selected', width=50, anchor='center')
        self.features_tree.column('feature', width=200, anchor='w')
        self.features_tree.column('category', width=100, anchor='center')
        self.features_tree.column('importance', width=80, anchor='center')
        self.features_tree.column('correlation', width=80, anchor='center')
        self.features_tree.column('missing_pct', width=80, anchor='center')
        self.features_tree.column('min_val', width=80, anchor='center')
        self.features_tree.column('max_val', width=80, anchor='center')
        self.features_tree.column('mean_val', width=80, anchor='center')
        self.features_tree.column('std_val', width=80, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.features_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.features_tree.xview)
        
        self.features_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Event bindings
        self.features_tree.bind('<Double-1>', self.toggle_feature_selection)
        self.features_tree.bind('<Button-1>', self.on_tree_click)
        
        # Packing
        self.features_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Configurar tags para colores
        self.features_tree.tag_configure('selected', background='lightgreen')
        self.features_tree.tag_configure('unselected', background='white')
        self.features_tree.tag_configure('high_importance', foreground='darkgreen', font=('TkDefaultFont', 9, 'bold'))
        self.features_tree.tag_configure('medium_importance', foreground='orange')
        self.features_tree.tag_configure('low_importance', foreground='gray')
    
    def create_stats_panel(self, parent):
        """Crear panel de estadísticas y acciones"""
        stats_frame = ttk.LabelFrame(parent, text="Estadísticas y Acciones", padding="10")
        stats_frame.pack(fill="x")
        
        # Frame izquierdo - Estadísticas
        left_stats = ttk.Frame(stats_frame)
        left_stats.pack(side="left", fill="both", expand=True)
        
        self.stats_text = tk.Text(left_stats, height=6, width=50, wrap='word', font=('Consolas', 9))
        stats_scrollbar = ttk.Scrollbar(left_stats, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side="left", fill="both", expand=True)
        stats_scrollbar.pack(side="right", fill="y")
        
        # Frame derecho - Botones de acción
        right_actions = ttk.Frame(stats_frame)
        right_actions.pack(side="right", fill="y", padx=(10, 0))
        
        ttk.Button(right_actions, text="Aplicar Selección", 
                  command=self.apply_feature_selection, style='Success.TButton').pack(fill='x', pady=2)
        
        ttk.Button(right_actions, text="Guardar Selección", 
                  command=self.save_feature_selection).pack(fill='x', pady=2)
        
        ttk.Button(right_actions, text="Cargar Selección", 
                  command=self.load_feature_selection).pack(fill='x', pady=2)
        
        ttk.Button(right_actions, text="Exportar Features", 
                  command=self.export_selected_features).pack(fill='x', pady=2)
        
        ttk.Button(right_actions, text="Análisis Detallado", 
                  command=self.show_detailed_analysis).pack(fill='x', pady=2)
        
        ttk.Button(right_actions, text="Actualizar Tabla", 
                  command=self.refresh_table).pack(fill='x', pady=2)
    
    def load_dataset(self, data: pd.DataFrame, feature_importance: Optional[pd.DataFrame] = None):
        """Cargar dataset y analizar features"""
        try:
            self.current_data = data.copy()
            self.feature_importance = feature_importance
            
            # Identificar features (excluir target y columnas de texto)
            exclude_cols = ['vacancies', 'filename', 'file_path']
            self.all_features = [col for col in data.columns 
                               if col not in exclude_cols and pd.api.types.is_numeric_dtype(data[col])]
            
            # Inicializar todas las features como seleccionadas
            self.selected_features = self.all_features.copy()
            
            # Calcular estadísticas de features
            self.calculate_feature_stats()
            
            # Actualizar tabla
            self.refresh_table()
            
            # Actualizar estadísticas
            self.update_stats_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando dataset:\n{str(e)}")
    
    def calculate_feature_stats(self):
        """Calcular estadísticas para cada feature"""
        self.feature_stats = {}
        
        target_col = 'vacancies'
        target_data = self.current_data[target_col] if target_col in self.current_data.columns else None
        
        for feature in self.all_features:
            data_col = self.current_data[feature]
            
            # Estadísticas básicas
            stats = {
                'missing_pct': (data_col.isnull().sum() / len(data_col)) * 100,
                'min_val': data_col.min(),
                'max_val': data_col.max(),
                'mean_val': data_col.mean(),
                'std_val': data_col.std(),
                'unique_vals': data_col.nunique(),
                'category': self.categorize_feature(feature)
            }
            
            # Correlación con target si está disponible
            if target_data is not None:
                try:
                    correlation = data_col.corr(target_data)
                    stats['correlation'] = correlation if not pd.isna(correlation) else 0.0
                except:
                    stats['correlation'] = 0.0
            else:
                stats['correlation'] = 0.0
            
            # Importancia si está disponible
            if self.feature_importance is not None:
                importance_row = self.feature_importance[self.feature_importance['feature'] == feature]
                stats['importance'] = importance_row['importance'].iloc[0] if len(importance_row) > 0 else 0.0
            else:
                stats['importance'] = 0.0
            
            self.feature_stats[feature] = stats
    
    def categorize_feature(self, feature_name: str) -> str:
        """Categorizar feature basado en su nombre"""
        feature_lower = feature_name.lower()
        
        if 'coord' in feature_lower:
            return 'Coordinación'
        elif any(word in feature_lower for word in ['energy', 'peatom', 'keatom']):
            return 'Energía'
        elif any(word in feature_lower for word in ['stress', 'satom']):
            return 'Stress'
        elif any(word in feature_lower for word in ['hist', 'bin']):
            return 'Histogramas'
        elif any(word in feature_lower for word in ['mean', 'std', 'min', 'max']):
            return 'Estadísticas'
        elif 'voro' in feature_lower:
            return 'Voronoi'
        else:
            return 'Otras'
    
    def refresh_table(self):
        """Actualizar tabla de features"""
        # Limpiar tabla
        for item in self.features_tree.get_children():
            self.features_tree.delete(item)
        
        # Filtrar features
        filtered_features = self.get_filtered_features()
        
        # Ordenar por importancia si está disponible
        if self.feature_importance is not None:
            filtered_features.sort(key=lambda f: self.feature_stats[f]['importance'], reverse=True)
        
        # Poblar tabla
        for feature in filtered_features:
            stats = self.feature_stats[feature]
            
            # Determinar si está seleccionada
            selected_mark = "✓" if feature in self.selected_features else ""
            
            # Formatear valores
            values = (
                selected_mark,
                feature,
                stats['category'],
                f"{stats['importance']:.4f}" if stats['importance'] > 0 else "N/A",
                f"{stats['correlation']:+.3f}" if stats['correlation'] != 0 else "N/A",
                f"{stats['missing_pct']:.1f}%",
                f"{stats['min_val']:.3f}" if not pd.isna(stats['min_val']) else "N/A",
                f"{stats['max_val']:.3f}" if not pd.isna(stats['max_val']) else "N/A",
                f"{stats['mean_val']:.3f}" if not pd.isna(stats['mean_val']) else "N/A",
                f"{stats['std_val']:.3f}" if not pd.isna(stats['std_val']) else "N/A"
            )
            
            # Determinar tags
            tags = ['selected' if feature in self.selected_features else 'unselected']
            
            # Agregar tag de importancia
            if stats['importance'] > 0.05:
                tags.append('high_importance')
            elif stats['importance'] > 0.01:
                tags.append('medium_importance')
            elif stats['importance'] > 0:
                tags.append('low_importance')
            
            # Insertar fila
            item_id = self.features_tree.insert('', 'end', values=values, tags=tags)
            
            # Guardar referencia feature -> item_id
            self.features_tree.set(item_id, 'feature', feature)
    
    def get_filtered_features(self) -> List[str]:
        """Obtener features filtradas según criterios actuales"""
        filtered = self.all_features.copy()
        
        # Filtro de búsqueda
        search_term = self.search_var.get().lower()
        if search_term:
            filtered = [f for f in filtered if search_term in f.lower()]
        
        # Filtro de categoría
        category_filter = self.category_filter_var.get()
        if category_filter != "Todas":
            filtered = [f for f in filtered if self.feature_stats[f]['category'] == category_filter]
        
        # Filtro de importancia
        importance_filter = self.importance_filter_var.get()
        if importance_filter != "Todas":
            if importance_filter == "Alta (>0.05)":
                filtered = [f for f in filtered if self.feature_stats[f]['importance'] > 0.05]
            elif importance_filter == "Media (0.01-0.05)":
                filtered = [f for f in filtered if 0.01 <= self.feature_stats[f]['importance'] <= 0.05]
            elif importance_filter == "Baja (<0.01)":
                filtered = [f for f in filtered if 0 < self.feature_stats[f]['importance'] < 0.01]
        
        return filtered
    
    def filter_features(self, *args):
        """Callback para filtrar features (llamado por traces de variables)"""
        self.refresh_table()
        self.update_stats_display()
    
    def on_tree_click(self, event):
        """Manejar click en la tabla"""
        region = self.features_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.features_tree.identify_column(event.x, event.y)
            if column == '#1':  # Columna de selección
                self.toggle_feature_selection(event)
    
    def toggle_feature_selection(self, event):
        """Alternar selección de feature"""
        item = self.features_tree.selection()[0] if self.features_tree.selection() else None
        if not item:
            item = self.features_tree.identify_row(event.y)
        
        if item:
            # Obtener nombre de la feature
            feature_name = None
            for child in self.features_tree.get_children():
                if child == item:
                    values = self.features_tree.item(child, 'values')
                    feature_name = values[1]  # Columna 'feature'
                    break
            
            if feature_name and feature_name in self.all_features:
                # Alternar selección
                if feature_name in self.selected_features:
                    self.selected_features.remove(feature_name)
                else:
                    self.selected_features.append(feature_name)
                
                # Actualizar display
                self.refresh_table()
                self.update_stats_display()
    
    def toggle_all_features(self):
        """Alternar selección de todas las features visibles"""
        filtered_features = self.get_filtered_features()
        
        if self.select_all_var.get():
            # Seleccionar todas las visibles
            for feature in filtered_features:
                if feature not in self.selected_features:
                    self.selected_features.append(feature)
        else:
            # Deseleccionar todas las visibles
            for feature in filtered_features:
                if feature in self.selected_features:
                    self.selected_features.remove(feature)
        
        self.refresh_table()
        self.update_stats_display()
    
    def select_top_features(self):
        """Seleccionar top N features por importancia"""
        if self.feature_importance is None:
            messagebox.showwarning("Advertencia", "No hay información de importancia disponible")
            return
        
        top_n = self.select_top_n_var.get()
        
        # Obtener features ordenadas por importancia
        features_by_importance = sorted(self.all_features, 
                                      key=lambda f: self.feature_stats[f]['importance'], 
                                      reverse=True)
        
        # Seleccionar top N
        self.selected_features = features_by_importance[:top_n]
        
        self.refresh_table()
        self.update_stats_display()
        
        messagebox.showinfo("Selección completada", f"Seleccionadas {len(self.selected_features)} features con mayor importancia")
    
    def invert_selection(self):
        """Invertir selección actual"""
        filtered_features = self.get_filtered_features()
        
        new_selection = []
        for feature in self.all_features:
            if feature in filtered_features:
                # Invertir solo las visibles
                if feature not in self.selected_features:
                    new_selection.append(feature)
            elif feature in self.selected_features:
                # Mantener las no visibles que estaban seleccionadas
                new_selection.append(feature)
        
        self.selected_features = new_selection
        self.refresh_table()
        self.update_stats_display()
    
    def clear_selection(self):
        """Limpiar toda la selección"""
        self.selected_features = []
        self.select_all_var.set(False)
        self.refresh_table()
        self.update_stats_display()
    
    def update_stats_display(self):
        """Actualizar display de estadísticas"""
        stats_text = f"""ESTADÍSTICAS DE SELECCIÓN
========================

Features totales: {len(self.all_features)}
Features seleccionadas: {len(self.selected_features)}
Features visibles (filtro): {len(self.get_filtered_features())}

DISTRIBUCIÓN POR CATEGORÍA:
"""
        
        # Contar por categorías
        category_counts = {}
        for feature in self.selected_features:
            category = self.feature_stats[feature]['category']
            category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in sorted(category_counts.items()):
            stats_text += f"  {category}: {count}\n"
        
        if self.feature_importance is not None:
            # Estadísticas de importancia
            selected_importances = [self.feature_stats[f]['importance'] for f in self.selected_features]
            
            if selected_importances:
                stats_text += f"""
IMPORTANCIA DE FEATURES SELECCIONADAS:
  Suma total: {sum(selected_importances):.4f}
  Promedio: {np.mean(selected_importances):.4f}
  Máxima: {max(selected_importances):.4f}
  Mínima: {min(selected_importances):.4f}
"""
        
        # Estadísticas de correlación
        selected_correlations = [abs(self.feature_stats[f]['correlation']) for f in self.selected_features 
                               if self.feature_stats[f]['correlation'] != 0]
        
        if selected_correlations:
            stats_text += f"""
CORRELACIÓN CON TARGET:
  Promedio |correlación|: {np.mean(selected_correlations):.4f}
  Máxima |correlación|: {max(selected_correlations):.4f}
  Features con |corr| > 0.5: {sum(1 for c in selected_correlations if c > 0.5)}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def apply_feature_selection(self):
        """Aplicar selección de features al modelo"""
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        # Notificar al callback
        self.feature_update_callback(self.selected_features.copy())
        
        messagebox.showinfo("Selección aplicada", 
                           f"Se aplicaron {len(self.selected_features)} features al modelo")
    
    def save_feature_selection(self):
        """Guardar selección actual a archivo"""
        from tkinter import filedialog
        import json
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar selección de features",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        
        if file_path:
            try:
                selection_data = {
                    'selected_features': self.selected_features,
                    'total_features': len(self.all_features),
                    'selection_count': len(self.selected_features),
                    'categories': {category: sum(1 for f in self.selected_features 
                                               if self.feature_stats[f]['category'] == category)
                                 for category in set(self.feature_stats[f]['category'] for f in self.selected_features)},
                    'timestamp': pd.Timestamp.now().isoformat()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(selection_data, f, indent=2)
                
                messagebox.showinfo("Guardado exitoso", f"Selección guardada en:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando selección:\n{str(e)}")
    
    def load_feature_selection(self):
        """Cargar selección desde archivo"""
        from tkinter import filedialog
        import json
        
        file_path = filedialog.askopenfilename(
            title="Cargar selección de features",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    selection_data = json.load(f)
                
                loaded_features = selection_data.get('selected_features', [])
                
                # Verificar que las features existan en el dataset actual
                valid_features = [f for f in loaded_features if f in self.all_features]
                invalid_features = [f for f in loaded_features if f not in self.all_features]
                
                self.selected_features = valid_features
                
                self.refresh_table()
                self.update_stats_display()
                
                message = f"Cargadas {len(valid_features)} features válidas"
                if invalid_features:
                    message += f"\n{len(invalid_features)} features no encontradas en el dataset actual"
                
                messagebox.showinfo("Carga completada", message)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando selección:\n{str(e)}")
    
    def export_selected_features(self):
        """Exportar dataset solo con features seleccionadas"""
        if not self.selected_features or self.current_data is None:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas o datos cargados")
            return
        
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar dataset con features seleccionadas",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                # Crear dataset con features seleccionadas + target
                export_columns = self.selected_features.copy()
                if 'vacancies' in self.current_data.columns and 'vacancies' not in export_columns:
                    export_columns.append('vacancies')
                
                export_data = self.current_data[export_columns]
                
                if file_path.endswith('.xlsx'):
                    export_data.to_excel(file_path, index=False)
                else:
                    export_data.to_csv(file_path, index=False)
                
                messagebox.showinfo("Exportación exitosa", 
                                   f"Dataset exportado con {len(self.selected_features)} features:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando dataset:\n{str(e)}")
    
    def show_detailed_analysis(self):
        """Mostrar análisis detallado de features seleccionadas"""
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        # Crear ventana de análisis
        analysis_window = tk.Toplevel(self.frame)
        analysis_window.title("Análisis Detallado de Features")
        analysis_window.geometry("800x600")
        analysis_window.transient(self.frame)
        
        # Texto con análisis
        text_widget = scrolledtext.ScrolledText(analysis_window, wrap="word", padx=20, pady=20)
        text_widget.pack(fill="both", expand=True)
        
        # Generar análisis
        analysis_text = self.generate_detailed_analysis()
        text_widget.insert(1.0, analysis_text)
        text_widget.config(state="disabled")