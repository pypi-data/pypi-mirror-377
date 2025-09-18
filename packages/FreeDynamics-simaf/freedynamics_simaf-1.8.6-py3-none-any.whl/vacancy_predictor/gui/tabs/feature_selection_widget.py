


import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
from .feature_selector import FeatureSelector

from .configuration_manager import ConfigurationManager
class FeatureSelectionWidget:
    """Widget para selección de features"""
    
    def __init__(self, parent, feature_selector: FeatureSelector):
        self.feature_selector = feature_selector
        self.current_data = None
        
        # Variables de UI
        self.search_var = tk.StringVar()
        self.show_selected_only_var = tk.BooleanVar()
        
        self.create_widgets(parent)
        
        # Observer pattern
        self.feature_selector.add_observer(self)
    
    def create_widgets(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Info del dataset
        info_frame = ttk.LabelFrame(main_frame, text="Información del Dataset", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.dataset_info_label = ttk.Label(info_frame, text="No dataset cargado", foreground="red")
        self.dataset_info_label.pack(anchor="w")
        
        # Target selector
        target_frame = ttk.Frame(info_frame)
        target_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Label(target_frame, text="Columna Target:").pack(side="left")
        self.target_var = tk.StringVar(value=self.feature_selector.target_column)
        self.target_combo = ttk.Combobox(target_frame, textvariable=self.target_var, 
                                        state="readonly", width=20)
        self.target_combo.pack(side="left", padx=(5, 0))
        self.target_combo.bind("<<ComboboxSelected>>", self.on_target_changed)
        
        # Filtros
        self.create_filters(main_frame)
        
        # Tabla
        self.create_table(main_frame)
        
        # Controles
        self.create_controls(main_frame)
        
        # Resumen
        self.create_summary(main_frame)
    
    def create_filters(self, parent):
        filter_frame = ttk.LabelFrame(parent, text="Filtros", padding="10")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(search_frame, text="Buscar:").pack(side="left")
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(5, 10))
        search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        ttk.Button(search_frame, text="Limpiar", 
                  command=lambda: self.search_var.set("")).pack(side="left")
        
        checkbox_frame = ttk.Frame(filter_frame)
        checkbox_frame.pack(fill="x")
        
        ttk.Checkbutton(checkbox_frame, text="Solo seleccionadas", 
                       variable=self.show_selected_only_var,
                       command=self.update_table).pack(side="left")
    
    def create_table(self, parent):
        table_frame = ttk.LabelFrame(parent, text="Selección de Features", padding="10")
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill="both", expand=True)
        
        columns = ('selected', 'feature', 'category', 'dtype', 'correlation', 'sample_values')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        # Headers
        self.tree.heading('selected', text='✓')
        self.tree.heading('feature', text='Feature')
        self.tree.heading('category', text='Categoría')
        self.tree.heading('dtype', text='Tipo')
        self.tree.heading('correlation', text='Correlación')
        self.tree.heading('sample_values', text='Valores de Muestra')
        
        # Column widths
        self.tree.column('selected', width=50, anchor='center')
        self.tree.column('feature', width=200, anchor='w')
        self.tree.column('category', width=100, anchor='center')
        self.tree.column('dtype', width=80, anchor='center')
        self.tree.column('correlation', width=100, anchor='center')
        self.tree.column('sample_values', width=250, anchor='w')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Events
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        # Tags
        self.tree.tag_configure('selected', background='#ccffcc')
        self.tree.tag_configure('unselected', background='#ffffff')
    
    def create_controls(self, parent):
        controls_frame = ttk.LabelFrame(parent, text="Controles de Selección", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Primera fila
        buttons_frame1 = ttk.Frame(controls_frame)
        buttons_frame1.pack(fill="x", pady=(0, 5))
        
        ttk.Button(buttons_frame1, text="Seleccionar Todo", 
                  command=self.select_all).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame1, text="Deseleccionar Todo", 
                  command=self.select_none).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame1, text="Solo Numéricas", 
                  command=self.select_numeric_only).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame1, text="Alta Correlación (>0.3)", 
                  command=self.select_high_correlation).pack(side="left")
        
        # Segunda fila - Configuración
        buttons_frame2 = ttk.Frame(controls_frame)
        buttons_frame2.pack(fill="x", pady=(5, 0))
        
        ttk.Button(buttons_frame2, text="Guardar Configuración", 
                  command=self.save_config).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame2, text="Cargar Configuración", 
                  command=self.load_config).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame2, text="Exportar CSV Filtrado", 
                  command=self.export_csv).pack(side="left", padx=(0, 5))
    
    def create_summary(self, parent):
        summary_frame = ttk.LabelFrame(parent, text="Resumen de Selección", padding="10")
        summary_frame.pack(fill="x")
        
        summary_info = ttk.Frame(summary_frame)
        summary_info.pack(fill="x")
        
        ttk.Label(summary_info, text="Total Features:").grid(row=0, column=0, sticky="w")
        self.total_features_label = ttk.Label(summary_info, text="0")
        self.total_features_label.grid(row=0, column=1, sticky="w", padx=(10, 20))
        
        ttk.Label(summary_info, text="Seleccionadas:").grid(row=0, column=2, sticky="w")
        self.selected_features_label = ttk.Label(summary_info, text="0", foreground="blue")
        self.selected_features_label.grid(row=0, column=3, sticky="w", padx=(10, 20))
        
        ttk.Label(summary_info, text="Target:").grid(row=0, column=4, sticky="w")
        self.target_summary_label = ttk.Label(summary_info, text="vacancies", foreground="green")
        self.target_summary_label.grid(row=0, column=5, sticky="w", padx=(10, 0))
    
    # Event handlers
    def on_data_changed(self, data: pd.DataFrame):
        self.current_data = data
        
        # Actualizar target combo
        numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        self.target_combo['values'] = numeric_columns
        
        # Actualizar feature selector
        self.feature_selector.update_data(data)
        
        # Actualizar UI
        self.update_dataset_info()
        self.update_table()
        self.update_summary()
    
    def on_features_changed(self, features: List[str], target: str):
        self.target_var.set(target)
        self.update_table()
        self.update_summary()
    
    def on_target_changed(self, event):
        new_target = self.target_var.get()
        self.feature_selector.set_target(new_target)
        
        if self.current_data is not None:
            self.feature_selector.update_data(self.current_data)
            self.update_table()
            self.update_summary()
    
    def on_search_changed(self, event):
        self.update_table()
    
    def on_item_double_click(self, event):
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            column_name = self.tree.item(item, 'values')[1]
            self.feature_selector.toggle_feature(column_name)
    
    # UI update methods
    def update_dataset_info(self):
        if self.current_data is not None:
            info_text = f"Cargado: {len(self.current_data)} filas × {len(self.current_data.columns)} columnas"
            self.dataset_info_label.config(text=info_text, foreground="green")
        else:
            self.dataset_info_label.config(text="No dataset cargado", foreground="red")
    
    def update_table(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.current_data is None:
            return
        
        search_text = self.search_var.get().lower()
        show_selected_only = self.show_selected_only_var.get()
        
        all_columns = [col for col in self.current_data.columns if col != self.feature_selector.target_column]
        
        for column in all_columns:
            if search_text and search_text not in column.lower():
                continue
            
            if show_selected_only and column not in self.feature_selector.selected_features:
                continue
            
            stats = self.feature_selector.feature_stats.get(column, {})
            selected_mark = "✓" if column in self.feature_selector.selected_features else ""
            
            sample_values = stats.get('sample_values', [])
            sample_text = ", ".join(sample_values)
            if len(sample_text) > 40:
                sample_text = sample_text[:37] + "..."
            
            item_id = self.tree.insert('', 'end', values=(
                selected_mark,
                column,
                stats.get('category', 'N/A'),
                stats.get('dtype', 'N/A'),
                f"{stats.get('correlation', 0):.3f}" if stats.get('correlation', 0) != 0 else "N/A",
                sample_text
            ))
            
            if column in self.feature_selector.selected_features:
                self.tree.item(item_id, tags=('selected',))
            else:
                self.tree.item(item_id, tags=('unselected',))
    
    def update_summary(self):
        if self.current_data is None:
            return
            
        total = len([col for col in self.current_data.columns if col != self.feature_selector.target_column])
        selected = len(self.feature_selector.selected_features)
        
        self.total_features_label.config(text=str(total))
        self.selected_features_label.config(text=str(selected))
        self.target_summary_label.config(text=self.feature_selector.target_column or "None")
    
    # Action methods
    def select_all(self):
        if self.current_data is None:
            return
        available_features = [col for col in self.current_data.columns if col != self.feature_selector.target_column]
        self.feature_selector.select_all(available_features)
    
    def select_none(self):
        self.feature_selector.select_none()
    
    def select_numeric_only(self):
        if self.current_data is None:
            return
        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
        available_features = [col for col in numeric_columns if col != self.feature_selector.target_column]
        self.feature_selector.select_all(available_features)
    
    def select_high_correlation(self):
        self.feature_selector.select_by_correlation(0.3)
        messagebox.showinfo("Info", f"Seleccionadas features con correlación > 0.3")
    
    def save_config(self):
        if not self.feature_selector.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar Configuración de Features",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            config = self.feature_selector.get_config()
            if ConfigurationManager.save_feature_config(config, file_path):
                messagebox.showinfo("Éxito", f"Configuración guardada en:\n{file_path}")
            else:
                messagebox.showerror("Error", "Error guardando configuración")
    
    def load_config(self):
        file_path = filedialog.askopenfilename(
            title="Cargar Configuración de Features",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            config = ConfigurationManager.load_feature_config(file_path)
            if config and self.current_data is not None:
                available_features = list(self.current_data.columns)
                self.feature_selector.load_config(config, available_features)
                messagebox.showinfo("Éxito", "Configuración cargada correctamente")
            else:
                messagebox.showerror("Error", "Error cargando configuración")
    
    def export_csv(self):
        if self.current_data is None or not self.feature_selector.selected_features:
            messagebox.showwarning("Advertencia", "No hay datos o features seleccionadas")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar Dataset Filtrado",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                columns_to_export = self.feature_selector.selected_features + [self.feature_selector.target_column]
                filtered_data = self.current_data[columns_to_export].copy()
                filtered_data.to_csv(file_path, index=True)
                messagebox.showinfo("Éxito", f"Dataset exportado a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando: {str(e)}")
