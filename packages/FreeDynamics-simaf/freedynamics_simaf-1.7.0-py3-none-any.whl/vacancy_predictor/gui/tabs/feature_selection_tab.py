"""
Tab para selección de features (columnas) para entrenamiento ML
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)

class FeatureSelectionTab:
    """Tab para seleccionar features que se usarán en el entrenamiento"""
    
    def __init__(self, parent, feature_selected_callback: Optional[Callable] = None):
        self.parent = parent
        self.feature_selected_callback = feature_selected_callback
        
        # Variables de estado
        self.current_data = None
        self.all_columns = []
        self.selected_features = []
        self.target_column = None
        
        # Variables de UI
        self.search_var = tk.StringVar()
        self.show_selected_only_var = tk.BooleanVar()
        self.auto_exclude_var = tk.BooleanVar(value=True)
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del tab"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Crear secciones
        self.create_header_section(main_container)
        self.create_filter_section(main_container)
        self.create_table_section(main_container)
        self.create_control_section(main_container)
        self.create_summary_section(main_container)
    
    def create_header_section(self, parent):
        """Sección de información del dataset"""
        header_frame = ttk.LabelFrame(parent, text="Dataset Information", padding="10")
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Info del dataset
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(fill="x")
        
        ttk.Label(info_frame, text="Dataset:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.dataset_info_label = ttk.Label(info_frame, text="No dataset loaded", foreground="red")
        self.dataset_info_label.grid(row=0, column=1, sticky="w")
        
        ttk.Label(info_frame, text="Target Column:").grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.target_var = tk.StringVar()
        self.target_combo = ttk.Combobox(info_frame, textvariable=self.target_var, 
                                        state="readonly", width=20)
        self.target_combo.grid(row=1, column=1, sticky="w", pady=(5, 0))
        self.target_combo.bind("<<ComboboxSelected>>", self.on_target_changed)
        
        # Botón para cargar datos
        ttk.Button(info_frame, text="Load from Advanced ML", 
                  command=self.load_from_advanced_ml).grid(row=0, column=2, padx=(20, 0))
    
    def create_filter_section(self, parent):
        """Sección de filtros"""
        filter_frame = ttk.LabelFrame(parent, text="Filters", padding="10")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Búsqueda por texto
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(5, 10))
        search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        ttk.Button(search_frame, text="Clear", 
                  command=lambda: self.search_var.set("")).pack(side="left")
        
        # Checkboxes de filtros
        checkbox_frame = ttk.Frame(filter_frame)
        checkbox_frame.pack(fill="x")
        
        ttk.Checkbutton(checkbox_frame, text="Show selected only", 
                       variable=self.show_selected_only_var,
                       command=self.update_table).pack(side="left", padx=(0, 20))
        
        ttk.Checkbutton(checkbox_frame, text="Auto-exclude non-numeric", 
                       variable=self.auto_exclude_var,
                       command=self.apply_auto_exclusions).pack(side="left")
    
    def create_table_section(self, parent):
        """Sección de tabla con columnas"""
        table_frame = ttk.LabelFrame(parent, text="Feature Selection", padding="10")
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Frame para la tabla con scrollbars
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill="both", expand=True)
        
        # Crear Treeview
        columns = ('selected', 'column', 'dtype', 'non_null', 'unique', 'sample_values')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('selected', text='Selected')
        self.tree.heading('column', text='Column Name')
        self.tree.heading('dtype', text='Data Type')
        self.tree.heading('non_null', text='Non-Null')
        self.tree.heading('unique', text='Unique')
        self.tree.heading('sample_values', text='Sample Values')
        
        # Configurar anchos
        self.tree.column('selected', width=80, anchor='center')
        self.tree.column('column', width=200, anchor='w')
        self.tree.column('dtype', width=100, anchor='center')
        self.tree.column('non_null', width=80, anchor='center')
        self.tree.column('unique', width=80, anchor='center')
        self.tree.column('sample_values', width=300, anchor='w')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind eventos
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-1>', self.on_item_click)
    
    def create_control_section(self, parent):
        """Sección de controles"""
        control_frame = ttk.LabelFrame(parent, text="Selection Controls", padding="10")
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Botones de selección masiva
        button_frame1 = ttk.Frame(control_frame)
        button_frame1.pack(fill="x", pady=(0, 5))
        
        ttk.Button(button_frame1, text="Select All", 
                  command=self.select_all).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame1, text="Deselect All", 
                  command=self.deselect_all).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame1, text="Invert Selection", 
                  command=self.invert_selection).pack(side="left", padx=(0, 20))
        
        # Botones de selección inteligente
        ttk.Button(button_frame1, text="Select Numeric Only", 
                  command=self.select_numeric_only).pack(side="left", padx=(0, 5))
        ttk.Button(button_frame1, text="Select High Correlation", 
                  command=self.select_high_correlation).pack(side="left")
        
        # Botones de aplicación
        button_frame2 = ttk.Frame(control_frame)
        button_frame2.pack(fill="x")
        
        ttk.Button(button_frame2, text="Apply Selection", 
                  command=self.apply_selection, 
                  style="Success.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(button_frame2, text="Reset to Default", 
                  command=self.reset_selection).pack(side="left")
    
    def create_summary_section(self, parent):
        """Sección de resumen"""
        summary_frame = ttk.LabelFrame(parent, text="Selection Summary", padding="10")
        summary_frame.pack(fill="x")
        
        # Labels de resumen
        summary_info = ttk.Frame(summary_frame)
        summary_info.pack(fill="x")
        
        ttk.Label(summary_info, text="Total Features:").grid(row=0, column=0, sticky="w")
        self.total_features_label = ttk.Label(summary_info, text="0")
        self.total_features_label.grid(row=0, column=1, sticky="w", padx=(10, 20))
        
        ttk.Label(summary_info, text="Selected Features:").grid(row=0, column=2, sticky="w")
        self.selected_features_label = ttk.Label(summary_info, text="0", foreground="blue")
        self.selected_features_label.grid(row=0, column=3, sticky="w", padx=(10, 20))
        
        ttk.Label(summary_info, text="Target Column:").grid(row=0, column=4, sticky="w")
        self.target_summary_label = ttk.Label(summary_info, text="None", foreground="green")
        self.target_summary_label.grid(row=0, column=5, sticky="w", padx=(10, 0))
    
    def load_data(self, data: pd.DataFrame, selected_features: List[str] = None):
        """Cargar datos en el tab"""
        try:
            self.current_data = data.copy()
            self.all_columns = list(data.columns)
            
            # Configurar target combo
            self.target_combo['values'] = self.all_columns
            if 'vacancies' in self.all_columns:
                self.target_var.set('vacancies')
                self.target_column = 'vacancies'
            elif self.all_columns:
                self.target_var.set(self.all_columns[-1])
                self.target_column = self.all_columns[-1]
            
            # Inicializar selección
            if selected_features:
                self.selected_features = [col for col in selected_features if col in self.all_columns]
            else:
                self.reset_selection()
            
            # Actualizar UI
            self.update_dataset_info()
            self.update_table()
            self.update_summary()
            
            logger.info(f"Feature selection loaded: {len(data)} rows, {len(data.columns)} columns")
            
        except Exception as e:
            logger.error(f"Error loading data in feature selection: {e}")
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
    
    def load_from_advanced_ml(self):
        """Cargar datos desde Advanced ML tab"""
        try:
            # Intentar obtener datos del tab de Advanced ML
            parent_app = self.get_parent_app()
            if parent_app and hasattr(parent_app, 'advanced_ml_tab'):
                if hasattr(parent_app.advanced_ml_tab, 'current_data') and parent_app.advanced_ml_tab.current_data is not None:
                    self.load_data(parent_app.advanced_ml_tab.current_data)
                    messagebox.showinfo("Success", "Data loaded from Advanced ML tab")
                else:
                    messagebox.showwarning("Warning", "No data found in Advanced ML tab")
            else:
                messagebox.showwarning("Warning", "Cannot access Advanced ML tab")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading from Advanced ML: {str(e)}")
    
    def get_parent_app(self):
        """Obtener referencia a la aplicación principal"""
        # Navegar hacia arriba en la jerarquía de widgets para encontrar la app principal
        widget = self.frame
        while widget:
            if hasattr(widget, 'master') and hasattr(widget.master, 'advanced_ml_tab'):
                return widget.master
            widget = getattr(widget, 'master', None)
        return None
    
    def update_dataset_info(self):
        """Actualizar información del dataset"""
        if self.current_data is not None:
            info_text = f"Loaded: {len(self.current_data)} rows × {len(self.current_data.columns)} columns"
            self.dataset_info_label.config(text=info_text, foreground="green")
        else:
            self.dataset_info_label.config(text="No dataset loaded", foreground="red")
    
    def update_table(self):
        """Actualizar tabla de features"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.current_data is None:
            return
        
        # Filtrar columnas
        search_text = self.search_var.get().lower()
        show_selected_only = self.show_selected_only_var.get()
        
        for column in self.all_columns:
            # Aplicar filtros
            if search_text and search_text not in column.lower():
                continue
            
            if show_selected_only and column not in self.selected_features:
                continue
            
            # Obtener información de la columna
            col_data = self.current_data[column]
            
            # Determinar si está seleccionada
            selected_mark = "✓" if column in self.selected_features else ""
            
            # Obtener estadísticas
            dtype = str(col_data.dtype)
            non_null = col_data.count()
            unique_count = col_data.nunique()
            
            # Obtener valores de muestra
            sample_values = col_data.dropna().head(3).astype(str).tolist()
            sample_text = ", ".join(sample_values)
            if len(sample_text) > 50:
                sample_text = sample_text[:47] + "..."
            
            # Insertar en tabla
            item_id = self.tree.insert('', 'end', values=(
                selected_mark,
                column,
                dtype,
                f"{non_null}/{len(col_data)}",
                unique_count,
                sample_text
            ))
            
            # Colorear filas
            if column == self.target_column:
                self.tree.set(item_id, 'selected', "TARGET")
                self.tree.item(item_id, tags=('target',))
            elif column in self.selected_features:
                self.tree.item(item_id, tags=('selected',))
            else:
                self.tree.item(item_id, tags=('unselected',))
        
        # Configurar colores
        self.tree.tag_configure('target', background='#ffcccc')
        self.tree.tag_configure('selected', background='#ccffcc')
        self.tree.tag_configure('unselected', background='#ffffff')
    
    def update_summary(self):
        """Actualizar resumen de selección"""
        total = len(self.all_columns) - (1 if self.target_column else 0)  # Excluir target
        selected = len(self.selected_features)
        
        self.total_features_label.config(text=str(total))
        self.selected_features_label.config(text=str(selected))
        self.target_summary_label.config(text=self.target_column or "None")
    
    def on_item_double_click(self, event):
        """Manejar doble click en item"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            column_name = self.tree.item(item, 'values')[1]
            if column_name != self.target_column:
                self.toggle_feature_selection(column_name)
    
    def on_item_click(self, event):
        """Manejar click simple en item"""
        pass
    
    def on_search_changed(self, event):
        """Manejar cambio en búsqueda"""
        self.update_table()
    
    def on_target_changed(self, event):
        """Manejar cambio de target column"""
        new_target = self.target_var.get()
        if new_target != self.target_column:
            # Remover target anterior de selected_features si estaba
            if self.target_column in self.selected_features:
                self.selected_features.remove(self.target_column)
            
            # Remover nuevo target de selected_features si está
            if new_target in self.selected_features:
                self.selected_features.remove(new_target)
            
            self.target_column = new_target
            self.update_table()
            self.update_summary()
    
    def toggle_feature_selection(self, column_name: str):
        """Alternar selección de una feature"""
        if column_name == self.target_column:
            return  # No permitir seleccionar target como feature
        
        if column_name in self.selected_features:
            self.selected_features.remove(column_name)
        else:
            self.selected_features.append(column_name)
        
        self.update_table()
        self.update_summary()
    
    def select_all(self):
        """Seleccionar todas las features (excepto target)"""
        self.selected_features = [col for col in self.all_columns if col != self.target_column]
        self.update_table()
        self.update_summary()
    
    def deselect_all(self):
        """Deseleccionar todas las features"""
        self.selected_features = []
        self.update_table()
        self.update_summary()
    
    def invert_selection(self):
        """Invertir selección"""
        available_features = [col for col in self.all_columns if col != self.target_column]
        self.selected_features = [col for col in available_features if col not in self.selected_features]
        self.update_table()
        self.update_summary()
    
    def select_numeric_only(self):
        """Seleccionar solo columnas numéricas"""
        if self.current_data is None:
            return
        
        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
        self.selected_features = [col for col in numeric_columns if col != self.target_column]
        self.update_table()
        self.update_summary()
    
    def select_high_correlation(self):
        """Seleccionar features con alta correlación con target"""
        if self.current_data is None or not self.target_column:
            messagebox.showwarning("Warning", "Need dataset and target column")
            return
        
        try:
            # Calcular correlaciones solo con columnas numéricas
            numeric_data = self.current_data.select_dtypes(include=[np.number])
            
            if self.target_column not in numeric_data.columns:
                messagebox.showwarning("Warning", "Target column must be numeric for correlation analysis")
                return
            
            correlations = numeric_data.corr()[self.target_column].abs()
            high_corr_features = correlations[correlations > 0.1].index.tolist()
            
            # Remover target column
            if self.target_column in high_corr_features:
                high_corr_features.remove(self.target_column)
            
            self.selected_features = high_corr_features
            self.update_table()
            self.update_summary()
            
            messagebox.showinfo("Info", f"Selected {len(high_corr_features)} features with correlation > 0.1")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating correlations: {str(e)}")
    
    def apply_auto_exclusions(self):
        """Aplicar exclusiones automáticas"""
        if not self.auto_exclude_var.get() or self.current_data is None:
            return
        
        # Excluir columnas no numéricas
        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
        self.selected_features = [col for col in self.selected_features if col in numeric_columns]
        
        self.update_table()
        self.update_summary()
    
    def reset_selection(self):
        """Resetear selección a valores por defecto"""
        if self.current_data is None:
            return
        
        # Seleccionar todas las columnas numéricas excepto target
        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
        self.selected_features = [col for col in numeric_columns if col != self.target_column]
        
        self.update_table()
        self.update_summary()
    
    def apply_selection(self):
        """Aplicar selección de features"""
        if not self.selected_features:
            messagebox.showwarning("Warning", "No features selected")
            return
        
        if not self.target_column:
            messagebox.showwarning("Warning", "No target column selected")
            return
        
        try:
            # Notificar callback si existe
            if self.feature_selected_callback:
                selection_info = {
                    'features': self.selected_features.copy(),
                    'target': self.target_column,
                    'data': self.current_data
                }
                self.feature_selected_callback(selection_info)
            
            messagebox.showinfo("Success", 
                               f"Feature selection applied!\n\n"
                               f"Features: {len(self.selected_features)}\n"
                               f"Target: {self.target_column}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error applying selection: {str(e)}")
    
    def get_selected_features(self) -> List[str]:
        """Obtener lista de features seleccionadas"""
        return self.selected_features.copy()
    
    def get_target_column(self) -> Optional[str]:
        """Obtener columna target"""
        return self.target_column
    
    def get_training_data(self) -> tuple:
        """Obtener datos preparados para entrenamiento"""
        if self.current_data is None or not self.selected_features or not self.target_column:
            raise ValueError("Need data, selected features, and target column")
        
        X = self.current_data[self.selected_features]
        y = self.current_data[self.target_column]
        
        return X, y