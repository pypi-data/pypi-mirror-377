#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced ML Tab con selección de features - VERSIÓN COMPLETA Y COMPACTA
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json


class FeatureSelectionWidget:
    def __init__(self, parent):
        self.parent = parent
        self.current_data = None
        self.selected_features = []
        self.target_column = 'vacancies'
        self.feature_stats = {}
        
        self.search_var = tk.StringVar()
        self.show_selected_only_var = tk.BooleanVar()
        self.auto_exclude_var = tk.BooleanVar(value=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.parent)
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
        self.target_var = tk.StringVar(value=self.target_column)
        self.target_combo = ttk.Combobox(target_frame, textvariable=self.target_var, 
                                        state="readonly", width=20)
        self.target_combo.pack(side="left", padx=(5, 0))
        self.target_combo.bind("<<ComboboxSelected>>", self.on_target_changed)
        
        # Filtros
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros", padding="10")
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
                       command=self.update_table).pack(side="left", padx=(0, 20))
        
        # Tabla de features
        table_frame = ttk.LabelFrame(main_frame, text="Selección de Features", padding="10")
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill="both", expand=True)
        
        columns = ('selected', 'feature', 'category', 'dtype', 'correlation', 'sample_values')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        self.tree.heading('selected', text='✓')
        self.tree.heading('feature', text='Feature')
        self.tree.heading('category', text='Categoría')
        self.tree.heading('dtype', text='Tipo')
        self.tree.heading('correlation', text='Correlación')
        self.tree.heading('sample_values', text='Valores de Muestra')
        
        self.tree.column('selected', width=50, anchor='center')
        self.tree.column('feature', width=200, anchor='w')
        self.tree.column('category', width=100, anchor='center')
        self.tree.column('dtype', width=80, anchor='center')
        self.tree.column('correlation', width=100, anchor='center')
        self.tree.column('sample_values', width=250, anchor='w')
        
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        # Controles
        controls_frame = ttk.LabelFrame(main_frame, text="Controles de Selección", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        buttons_frame1 = ttk.Frame(controls_frame)
        buttons_frame1.pack(fill="x", pady=(0, 5))
        
        ttk.Button(buttons_frame1, text="Seleccionar Todo", 
                  command=self.select_all).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame1, text="Deseleccionar Todo", 
                  command=self.deselect_all).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame1, text="Exportar CSV Filtrado", 
                  command=self.export_filtered_csv).pack(side="left", padx=(0, 20))
        
        ttk.Button(buttons_frame1, text="Solo Numéricas", 
                  command=self.select_numeric_only).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame1, text="Alta Correlación (>0.3)", 
                  command=self.select_high_correlation).pack(side="left")
        
        # Segunda fila de botones - Configuración
        buttons_frame2 = ttk.Frame(controls_frame)
        buttons_frame2.pack(fill="x", pady=(5, 0))
        
        ttk.Button(buttons_frame2, text="Guardar Configuración", 
                  command=self.save_feature_config).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame2, text="Cargar Configuración", 
                  command=self.load_feature_config).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame2, text="Configuración por Defecto", 
                  command=self.load_default_config).pack(side="left", padx=(0, 20))
        
        # Resumen
        summary_frame = ttk.LabelFrame(main_frame, text="Resumen de Selección", padding="10")
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
        
        return main_frame
    
    def load_data(self, data):
        try:
            self.current_data = data.copy()
            
            numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
            self.target_combo['values'] = numeric_columns
            
            if self.target_column in numeric_columns:
                self.target_var.set(self.target_column)
            elif numeric_columns:
                self.target_var.set(numeric_columns[-1])
                self.target_column = numeric_columns[-1]
            
            self.calculate_feature_stats()
            self.selected_features = [col for col in numeric_columns if col != self.target_column]
            
            self.update_dataset_info()
            self.update_table()
            self.update_summary()
            
            print(f"[DEBUG] Features cargadas: {len(self.selected_features)} seleccionadas")
            
        except Exception as e:
            print(f"[ERROR] Error cargando datos: {e}")
            messagebox.showerror("Error", f"Error cargando datos: {str(e)}")
    
    def calculate_feature_stats(self):
        self.feature_stats = {}
        target_data = self.current_data[self.target_column] if self.target_column in self.current_data.columns else None
        
        for col in self.current_data.columns:
            if col == self.target_column:
                continue
                
            col_data = self.current_data[col]
            category = self.categorize_feature(col)
            
            stats = {
                'category': category,
                'dtype': str(col_data.dtype),
                'sample_values': col_data.dropna().head(3).astype(str).tolist()
            }
            
            if target_data is not None and pd.api.types.is_numeric_dtype(col_data):
                try:
                    correlation = col_data.corr(target_data)
                    stats['correlation'] = correlation if not pd.isna(correlation) else 0.0
                except:
                    stats['correlation'] = 0.0
            else:
                stats['correlation'] = 0.0
            
            self.feature_stats[col] = stats
    
    def categorize_feature(self, feature_name):
        feature_lower = feature_name.lower()
        
        if 'coord' in feature_lower:
            return 'Coordinación'
        elif any(word in feature_lower for word in ['energy', 'pe_', 'peatom']):
            return 'Energía'
        elif any(word in feature_lower for word in ['stress', 'vm', 'satom']):
            return 'Stress'
        elif any(word in feature_lower for word in ['hist', 'bin']):
            return 'Histogramas'
        elif 'voro' in feature_lower:
            return 'Voronoi'
        elif any(word in feature_lower for word in ['mean', 'std', 'min', 'max', 'p10', 'p25', 'p75', 'p90']):
            return 'Estadísticas'
        else:
            return 'Otras'
    
    def update_dataset_info(self):
        if self.current_data is not None:
            info_text = f"Cargado: {len(self.current_data)} filas × {len(self.current_data.columns)} columnas"
            self.dataset_info_label.config(text=info_text, foreground="green")
        else:
            self.dataset_info_label.config(text="No dataset cargado", foreground="red")
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.current_data is None:
            return
        
        search_text = self.search_var.get().lower()
        show_selected_only = self.show_selected_only_var.get()
        
        all_columns = [col for col in self.current_data.columns if col != self.target_column]
        
        for column in all_columns:
            if search_text and search_text not in column.lower():
                continue
            
            if show_selected_only and column not in self.selected_features:
                continue
            
            stats = self.feature_stats.get(column, {})
            selected_mark = "✓" if column in self.selected_features else ""
            
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
            
            if column in self.selected_features:
                self.tree.item(item_id, tags=('selected',))
            else:
                self.tree.item(item_id, tags=('unselected',))
        
        self.tree.tag_configure('selected', background='#ccffcc')
        self.tree.tag_configure('unselected', background='#ffffff')
    
    def update_summary(self):
        if self.current_data is None:
            return
            
        total = len([col for col in self.current_data.columns if col != self.target_column])
        selected = len(self.selected_features)
        
        self.total_features_label.config(text=str(total))
        self.selected_features_label.config(text=str(selected))
        self.target_summary_label.config(text=self.target_column or "None")
    
    def on_item_double_click(self, event):
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            column_name = self.tree.item(item, 'values')[1]
            self.toggle_feature_selection(column_name)
    
    def on_search_changed(self, event):
        self.update_table()
    
    def on_target_changed(self, event):
        new_target = self.target_var.get()
        if new_target != self.target_column:
            if self.target_column in self.selected_features:
                self.selected_features.remove(self.target_column)
            
            if new_target in self.selected_features:
                self.selected_features.remove(new_target)
            
            self.target_column = new_target
            self.calculate_feature_stats()
            self.update_table()
            self.update_summary()
            
            print(f"[DEBUG] Target cambiado a: {self.target_column}")
    
    def toggle_feature_selection(self, column_name):
        if column_name == self.target_column:
            return
        
        if column_name in self.selected_features:
            self.selected_features.remove(column_name)
            print(f"[DEBUG] Feature deseleccionada: {column_name}")
        else:
            self.selected_features.append(column_name)
            print(f"[DEBUG] Feature seleccionada: {column_name}")
        
        self.update_table()
        self.update_summary()
    
    def select_all(self):
        if self.current_data is None:
            return
        self.selected_features = [col for col in self.current_data.columns if col != self.target_column]
        self.update_table()
        self.update_summary()
        print(f"[DEBUG] Todas las features seleccionadas: {len(self.selected_features)}")
    
    def deselect_all(self):
        self.selected_features = []
        self.update_table()
        self.update_summary()
        print("[DEBUG] Todas las features deseleccionadas")
    
    def select_numeric_only(self):
        if self.current_data is None:
            return
        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
        self.selected_features = [col for col in numeric_columns if col != self.target_column]
        self.update_table()
        self.update_summary()
        print(f"[DEBUG] Features numéricas seleccionadas: {len(self.selected_features)}")
    
    def select_high_correlation(self):
        if self.current_data is None or not self.target_column:
            messagebox.showwarning("Advertencia", "Necesita dataset y columna target")
            return
        
        try:
            high_corr_features = []
            for feature, stats in self.feature_stats.items():
                if abs(stats.get('correlation', 0)) > 0.3:
                    high_corr_features.append(feature)
            
            self.selected_features = high_corr_features
            self.update_table()
            self.update_summary()
            
            messagebox.showinfo("Info", f"Seleccionadas {len(high_corr_features)} features con correlación > 0.3")
            print(f"[DEBUG] Features alta correlación seleccionadas: {len(high_corr_features)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error calculando correlaciones: {str(e)}")
    
    def save_feature_config(self):
        """Guardar configuración de features seleccionadas"""
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar Configuración de Features",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                config = {
                    'selected_features': self.selected_features,
                    'target_column': self.target_column,
                    'total_features': len([col for col in self.current_data.columns if col != self.target_column]),
                    'feature_categories': {},
                    'feature_correlations': {},
                    'metadata': {
                        'timestamp': pd.Timestamp.now().isoformat(),
                        'dataset_shape': self.current_data.shape if self.current_data is not None else None,
                        'description': f"Configuración con {len(self.selected_features)} features seleccionadas"
                    }
                }
                
                # Agregar información detallada de las features
                for feature in self.selected_features:
                    if feature in self.feature_stats:
                        stats = self.feature_stats[feature]
                        config['feature_categories'][feature] = stats.get('category', 'N/A')
                        config['feature_correlations'][feature] = stats.get('correlation', 0.0)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Éxito", 
                                   f"Configuración guardada!\n\n"
                                   f"Archivo: {file_path}\n"
                                   f"Features: {len(self.selected_features)}\n"
                                   f"Target: {self.target_column}")
                
                print(f"[DEBUG] Configuración guardada: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando configuración:\n{str(e)}")
    
    def load_feature_config(self):
        """Cargar configuración de features desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Cargar Configuración de Features",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if 'selected_features' not in config:
                    messagebox.showerror("Error", "Archivo de configuración inválido")
                    return
                
                # Verificar qué features existen en el dataset actual
                loaded_features = config['selected_features']
                if self.current_data is not None:
                    available_features = [col for col in self.current_data.columns if col != self.target_column]
                    valid_features = [f for f in loaded_features if f in available_features]
                    missing_features = [f for f in loaded_features if f not in available_features]
                    
                    self.selected_features = valid_features
                    
                    # Actualizar target si está disponible
                    if 'target_column' in config and config['target_column'] in self.current_data.columns:
                        old_target = self.target_column
                        self.target_column = config['target_column']
                        self.target_var.set(self.target_column)
                        
                        # Recalcular estadísticas si cambió el target
                        if old_target != self.target_column:
                            self.calculate_feature_stats()
                    
                    self.update_table()
                    self.update_summary()
                    
                    message = f"Configuración cargada!\n\n"
                    message += f"Features válidas: {len(valid_features)}\n"
                    if missing_features:
                        message += f"Features no encontradas: {len(missing_features)}\n"
                    message += f"Target: {self.target_column}"
                    
                    messagebox.showinfo("Éxito", message)
                    
                    if missing_features:
                        print(f"[WARNING] Features no encontradas: {missing_features}")
                    
                else:
                    messagebox.showwarning("Advertencia", "Carga primero un dataset")
                
                print(f"[DEBUG] Configuración cargada: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando configuración:\n{str(e)}")
    
    def load_default_config(self):
        """Cargar configuración por defecto basada en categorías importantes"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "Carga primero un dataset")
            return
        
        # Seleccionar features importantes por defecto
        default_features = []
        
        for col in self.current_data.columns:
            if col == self.target_column:
                continue
            
            if col in self.feature_stats:
                category = self.feature_stats[col].get('category', '')
                correlation = abs(self.feature_stats[col].get('correlation', 0))
                
                # Incluir features con alta correlación o categorías importantes
                if (correlation > 0.1 or 
                    category in ['Coordinación', 'Energía', 'Estadísticas'] or
                    any(word in col.lower() for word in ['mean', 'std', 'coord', 'energy'])):
                    default_features.append(col)
        
        # Si no hay suficientes, agregar features numéricas
        if len(default_features) < 20:
            numeric_cols = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
            for col in numeric_cols:
                if col != self.target_column and col not in default_features:
                    default_features.append(col)
                    if len(default_features) >= 30:  # Límite razonable
                        break
        
        self.selected_features = default_features
        self.update_table()
        self.update_summary()
        
        messagebox.showinfo("Configuración por Defecto", 
                           f"Cargadas {len(default_features)} features por defecto\n\n"
                           f"Criterios: alta correlación, categorías importantes")
        
        print(f"[DEBUG] Configuración por defecto cargada: {len(default_features)} features")
    
    def export_filtered_csv(self):
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "No hay dataset cargado")
            return
        
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        try:
            columns_to_export = self.selected_features + [self.target_column]
            filtered_data = self.current_data[columns_to_export].copy()
            
            file_path = filedialog.asksaveasfilename(
                title="Exportar Dataset Filtrado",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if file_path:
                filtered_data.to_csv(file_path, index=True)
                
                metadata_path = file_path.replace('.csv', '_metadata.txt')
                metadata_text = f"""DATASET FILTRADO - METADATOS
===========================
Fecha de exportación: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

CONFIGURACIÓN:
  Target: {self.target_column}
  Features seleccionadas: {len(self.selected_features)}
  Filas: {len(filtered_data)}
  Columnas totales: {len(filtered_data.columns)}

FEATURES INCLUIDAS:
"""
                for i, feature in enumerate(self.selected_features, 1):
                    category = self.feature_stats.get(feature, {}).get('category', 'N/A')
                    correlation = self.feature_stats.get(feature, {}).get('correlation', 0)
                    metadata_text += f"  {i:2d}. {feature} ({category}, corr: {correlation:.3f})\n"
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    f.write(metadata_text)
                
                messagebox.showinfo("Éxito", 
                                   f"Dataset filtrado exportado!\n\n"
                                   f"Archivo: {file_path}\n"
                                   f"Features: {len(self.selected_features)}\n"
                                   f"Target: {self.target_column}\n"
                                   f"Filas: {len(filtered_data)}\n\n"
                                   f"Metadatos: {metadata_path}")
                
                print(f"[DEBUG] CSV exportado: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando dataset filtrado:\n{str(e)}")
    
    def get_selected_features(self):
        print(f"[DEBUG] get_selected_features() llamado: {len(self.selected_features)} features")
        return self.selected_features.copy()
    
    def get_target_column(self):
        print(f"[DEBUG] get_target_column() llamado: {self.target_column}")
        return self.target_column
    
    def get_feature_config(self):
        """Obtener configuración completa de features"""
        return {
            'selected_features': self.selected_features.copy(),
            'target_column': self.target_column,
            'feature_stats': self.feature_stats.copy(),
            'total_available': len([col for col in self.current_data.columns if col != self.target_column]) if self.current_data is not None else 0
        }


class AdvancedMLTabWithFeatureSelection:
    def __init__(self, parent, data_loaded_callback):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        
        self.frame = ttk.Frame(parent)
        
        # Variables de entrenamiento
        self.n_estimators_var = tk.IntVar(value=100)
        self.test_size_var = tk.DoubleVar(value=0.2)
        self.random_state_var = tk.IntVar(value=42)
        
        # Estado actual
        self.current_data = None
        self.trained_model = None
        self.feature_columns = []
        self.target_column = 'vacancies'
        self.X_test = None
        self.y_test = None
        self.test_predictions = None
        self.original_file_path = None
        self.feature_importance = None
        
        self.create_widgets()
    
    def create_widgets(self):
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        self.create_data_tab()
        self.create_feature_selection_tab()
        self.create_training_tab()
        self.create_results_tab()
        self.create_prediction_tab()
    
    def create_data_tab(self):
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Datos")
        
        load_frame = ttk.LabelFrame(data_frame, text="Cargar Dataset", padding="10")
        load_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(load_frame, text="Cargar CSV/Excel Original", 
                  command=self.load_dataset).pack(side="left", padx=5)
        
        ttk.Button(load_frame, text="Cargar CSV Filtrado", 
                  command=self.load_filtered_dataset).pack(side="left", padx=5)
        
        info_frame = ttk.LabelFrame(data_frame, text="Información del Dataset", padding="10")
        info_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=20, wrap='word')
        self.info_text.pack(fill="both", expand=True)
    
    def create_feature_selection_tab(self):
        feature_frame = ttk.Frame(self.notebook)
        self.notebook.add(feature_frame, text="🎯 Features")
        
        self.feature_selector = FeatureSelectionWidget(feature_frame)
        
        apply_frame = ttk.Frame(feature_frame)
        apply_frame.pack(fill="x", padx=10, pady=5)
        
        self.apply_features_btn = ttk.Button(apply_frame, text="Aplicar Selección de Features", 
                                           command=self.apply_feature_selection,
                                           state="disabled")
        self.apply_features_btn.pack(side="left", padx=5)
        
        self.feature_status_label = ttk.Label(apply_frame, text="Carga un dataset primero", foreground="red")
        self.feature_status_label.pack(side="left", padx=(20, 0))
    
    def create_training_tab(self):
        train_frame = ttk.Frame(self.notebook)
        self.notebook.add(train_frame, text="🤖 Entrenamiento")
        
        left_panel = ttk.Frame(train_frame)
        left_panel.pack(side="left", fill="y", padx=(10, 5))
        
        features_status_frame = ttk.LabelFrame(left_panel, text="Estado de Features", padding="10")
        features_status_frame.pack(fill='x', pady=(0, 10))
        
        self.features_status_label = ttk.Label(features_status_frame, text="No hay features seleccionadas", foreground="red")
        self.features_status_label.pack(anchor="w")
        
        params_group = ttk.LabelFrame(left_panel, text="Parámetros Random Forest", padding="10")
        params_group.pack(fill='x', pady=(0, 10))
        
        ttk.Label(params_group, text="N° Estimadores:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Spinbox(params_group, from_=50, to=500, textvariable=self.n_estimators_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Test Size:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.test_size_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Random State:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.random_state_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        buttons_group = ttk.LabelFrame(left_panel, text="Acciones", padding="10")
        buttons_group.pack(fill='x', pady=(0, 10))
        
        self.train_btn = ttk.Button(buttons_group, text="Entrenar Modelo", 
                                   command=self.train_model, state="disabled")
        self.train_btn.pack(fill='x', pady=2)
        
        self.save_btn = ttk.Button(buttons_group, text="Guardar Modelo", 
                                  command=self.save_model, state="disabled")
        self.save_btn.pack(fill='x', pady=2)
        
        ttk.Button(buttons_group, text="Cargar Modelo", 
                  command=self.load_model).pack(fill='x', pady=2)
        
        right_panel = ttk.Frame(train_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10))
        
        results_group = ttk.LabelFrame(right_panel, text="Métricas del Entrenamiento", padding="10")
        results_group.pack(fill='both', expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_group, height=20, wrap='word')
        self.results_text.pack(fill='both', expand=True)
    
    def create_results_tab(self):
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📈 Resultados")
        
        control_frame = ttk.Frame(results_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="Actualizar Gráficos", 
                  command=self.update_plots).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Guardar Gráficos", 
                  command=self.save_plots).pack(side="left", padx=5)
        
        self.plots_frame = ttk.Frame(results_frame)
        self.plots_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.fig, self.axes = plt.subplots(2, 3, figsize=(18, 12))
        self.fig.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_prediction_tab(self):
        pred_frame = ttk.Frame(self.notebook)
        self.notebook.add(pred_frame, text="🔮 Predicción")
        
        single_group = ttk.LabelFrame(pred_frame, text="Predicción Individual", padding="10")
        single_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(single_group, text="Ingrese valores para las features seleccionadas:").pack(anchor='w')
        
        self.features_frame = ttk.Frame(single_group)
        self.features_frame.pack(fill='x', pady=10)
        
        ttk.Button(single_group, text="Predecir", command=self.predict_single).pack()
        
        pred_results_group = ttk.LabelFrame(pred_frame, text="Resultados", padding="10")
        pred_results_group.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.prediction_text = scrolledtext.ScrolledText(pred_results_group, height=15, wrap='word')
        self.prediction_text.pack(fill='both', expand=True)
    
    def load_dataset(self):
        file_path = filedialog.askopenfilename(
            title="Cargar Dataset",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                self.original_file_path = file_path
                
                if file_path.endswith('.xlsx'):
                    data = pd.read_excel(file_path)
                else:
                    data = pd.read_csv(file_path, index_col=0)
                
                self.load_dataset_from_dataframe(data)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando dataset:\n{str(e)}")
    
    def load_filtered_dataset(self):
        file_path = filedialog.askopenfilename(
            title="Cargar Dataset Filtrado",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                data = pd.read_csv(file_path, index_col=0)
                
                self.target_column = data.columns[-1]
                self.feature_columns = list(data.columns[:-1])
                
                self.current_data = data.copy()
                self.update_dataset_info()
                
                self.features_status_label.config(
                    text=f"✓ {len(self.feature_columns)} features cargadas, target: {self.target_column}",
                    foreground="green"
                )
                
                self.train_btn.config(state="normal")
                self.update_prediction_interface()
                self.notebook.select(2)
                
                details_text = f"""DATASET FILTRADO CARGADO
========================

Archivo: {file_path}
Target: {self.target_column}
Features: {len(self.feature_columns)}

FEATURES DISPONIBLES:
"""
                for i, feature in enumerate(self.feature_columns, 1):
                    details_text += f"  {i:2d}. {feature}\n"
                
                details_text += f"""

ESTADO: ✓ LISTO PARA ENTRENAR
Dataset filtrado cargado correctamente.
El modelo usará {len(self.feature_columns)} features para predecir {self.target_column}.
"""
                
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(1.0, details_text)
                
                self.data_loaded_callback(data)
                
                messagebox.showinfo("Éxito", 
                                   f"Dataset filtrado cargado!\n\n"
                                   f"Archivo: {file_path}\n"
                                   f"Features: {len(self.feature_columns)}\n"
                                   f"Target: {self.target_column}\n"
                                   f"Filas: {len(data)}\n\n"
                                   f"El entrenamiento está habilitado.")
                
                print(f"[DEBUG] Dataset filtrado cargado: {len(self.feature_columns)} features")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando dataset filtrado:\n{str(e)}")
    
    def load_dataset_from_dataframe(self, data):
        try:
            self.current_data = data.copy()
            
            self.feature_selector.load_data(data)
            self.update_dataset_info()
            
            self.apply_features_btn.config(state="normal")
            self.feature_status_label.config(text="Dataset cargado. Selecciona features y aplica.", foreground="orange")
            
            self.data_loaded_callback(data)
            self.notebook.select(1)
            
            messagebox.showinfo("Éxito", 
                               f"Dataset cargado exitosamente!\n\n"
                               f"Filas: {len(data)}\n"
                               f"Columnas: {len(data.columns)}\n\n"
                               f"Ahora selecciona las features en el tab 'Features'")
            
            print(f"[DEBUG] Dataset cargado desde dataframe: {data.shape}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando dataset:\n{str(e)}")
    
    def update_dataset_info(self):
        if self.current_data is None:
            return
        
        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
        text_columns = self.current_data.select_dtypes(include=['object']).columns.tolist()
        
        info_lines = [
            "INFORMACIÓN DEL DATASET",
            "=" * 40,
            f"Filas: {len(self.current_data)}",
            f"Columnas totales: {len(self.current_data.columns)}",
            f"Columnas numéricas: {len(numeric_columns)}",
            f"Columnas de texto: {len(text_columns)}",
            "",
            "COLUMNAS NUMÉRICAS:",
            "-" * 20
        ]
        
        for col in numeric_columns[:15]:
            try:
                stats = self.current_data[col].describe()
                info_lines.append(f"  • {col}: [{stats['min']:.2f}, {stats['max']:.2f}], mean={stats['mean']:.2f}")
            except:
                info_lines.append(f"  • {col}: [datos numéricos]")
        
        if len(numeric_columns) > 15:
            info_lines.append(f"  ... y {len(numeric_columns) - 15} más")
        
        if text_columns:
            info_lines.extend([
                "",
                "COLUMNAS DE TEXTO:",
                "-" * 20
            ])
            for col in text_columns:
                info_lines.append(f"  • {col}")
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "\n".join(info_lines))
    
    def apply_feature_selection(self):
        try:
            print("[DEBUG] apply_feature_selection() llamado")
            
            self.feature_columns = self.feature_selector.get_selected_features()
            self.target_column = self.feature_selector.get_target_column()
            
            print(f"[DEBUG] Features obtenidas: {len(self.feature_columns)}")
            print(f"[DEBUG] Target obtenido: {self.target_column}")
            
            if not self.feature_columns:
                messagebox.showwarning("Advertencia", "No hay features seleccionadas")
                return
            
            if not self.target_column:
                messagebox.showwarning("Advertencia", "No hay columna target seleccionada")
                return
            
            self.features_status_label.config(
                text=f"✓ {len(self.feature_columns)} features seleccionadas, target: {self.target_column}",
                foreground="green"
            )
            
            self.feature_status_label.config(
                text=f"✓ Features aplicadas: {len(self.feature_columns)} features para entrenamiento",
                foreground="green"
            )
            
            self.train_btn.config(state="normal")
            self.update_prediction_interface()
            self.notebook.select(2)
            
            details_text = f"""FEATURES SELECCIONADAS PARA ENTRENAMIENTO
========================================

Target: {self.target_column}
Features seleccionadas: {len(self.feature_columns)}

LISTA DE FEATURES:
"""
            for i, feature in enumerate(self.feature_columns, 1):
                category = "N/A"
                if hasattr(self.feature_selector, 'feature_stats') and feature in self.feature_selector.feature_stats:
                    category = self.feature_selector.feature_stats[feature].get('category', 'N/A')
                details_text += f"  {i:2d}. {feature} ({category})\n"
            
            details_text += f"""

ESTADO: ✓ LISTO PARA ENTRENAR
El modelo usará estas {len(self.feature_columns)} features para predecir {self.target_column}.
Presiona 'Entrenar Modelo' para comenzar.
"""
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, details_text)
            
            messagebox.showinfo("Éxito", 
                               f"Selección aplicada correctamente!\n\n"
                               f"Features: {len(self.feature_columns)}\n"
                               f"Target: {self.target_column}\n\n"
                               f"El botón 'Entrenar Modelo' está ahora habilitado.")
            
            print(f"[DEBUG] Selección aplicada exitosamente")
            
        except Exception as e:
            print(f"[ERROR] Error aplicando selección: {e}")
            messagebox.showerror("Error", f"Error aplicando selección:\n{str(e)}")
    
    def train_model(self):
        if not self.feature_columns:
            messagebox.showwarning("Advertencia", "Primero selecciona y aplica las features")
            return
        
        try:
            self.train_btn.config(state="disabled")
            
            print(f"[DEBUG] Iniciando entrenamiento con {len(self.feature_columns)} features")
            
            X = self.current_data[self.feature_columns]
            y = self.current_data[self.target_column]
            
            print(f"[DEBUG] X shape: {X.shape}, y shape: {y.shape}")
            
            if X.isnull().any().any():
                from sklearn.impute import SimpleImputer
                imputer = SimpleImputer(strategy='median')
                X_clean = pd.DataFrame(imputer.fit_transform(X), columns=X.columns, index=X.index)
                print("[DEBUG] Valores NaN imputados")
            else:
                X_clean = X
            
            from sklearn.model_selection import train_test_split
            X_train, self.X_test, y_train, self.y_test = train_test_split(
                X_clean, y, 
                test_size=self.test_size_var.get(),
                random_state=self.random_state_var.get()
            )
            
            print(f"[DEBUG] Train shape: {X_train.shape}, Test shape: {self.X_test.shape}")
            
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            
            self.trained_model = RandomForestRegressor(
                n_estimators=self.n_estimators_var.get(),
                random_state=self.random_state_var.get(),
                n_jobs=-1
            )
            
            print("[DEBUG] Entrenando modelo...")
            self.trained_model.fit(X_train, y_train)
            
            train_pred = self.trained_model.predict(X_train)
            self.test_predictions = self.trained_model.predict(self.X_test)
            
            train_mae = mean_absolute_error(y_train, train_pred)
            test_mae = mean_absolute_error(self.y_test, self.test_predictions)
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            test_rmse = np.sqrt(mean_squared_error(self.y_test, self.test_predictions))
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(self.y_test, self.test_predictions)
            
            print(f"[DEBUG] Métricas calculadas - Test R²: {test_r2:.3f}, Test MAE: {test_mae:.3f}")
            
            from sklearn.model_selection import cross_val_score
            cv_mae = -cross_val_score(self.trained_model, X_clean, y, cv=5, scoring='neg_mean_absolute_error')
            cv_r2 = cross_val_score(self.trained_model, X_clean, y, cv=5, scoring='r2')
            
            self.feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.trained_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            results_text = f"""RESULTADOS DEL ENTRENAMIENTO
===========================

CONFIGURACIÓN:
  Random Forest con {self.n_estimators_var.get()} estimadores
  Test size: {self.test_size_var.get():.1%}
  Features utilizadas: {len(self.feature_columns)}
  Target: {self.target_column}
  Muestras de entrenamiento: {len(X_train)}
  Muestras de prueba: {len(self.X_test)}

MÉTRICAS DE RENDIMIENTO:
  Train MAE:  {train_mae:.3f}
  Test MAE:   {test_mae:.3f}
  Train RMSE: {train_rmse:.3f}
  Test RMSE:  {test_rmse:.3f}
  Train R²:   {train_r2:.3f}
  Test R²:    {test_r2:.3f}

VALIDACIÓN CRUZADA (5-fold):
  CV MAE:  {cv_mae.mean():.3f} ± {cv_mae.std():.3f}
  CV R²:   {cv_r2.mean():.3f} ± {cv_r2.std():.3f}

TOP 15 FEATURES MÁS IMPORTANTES:
"""
            
            for i, row in self.feature_importance.head(15).iterrows():
                results_text += f"  {row['feature'][:40]:40s}: {row['importance']:.4f}\n"
            
            results_text += f"""

INTERPRETACIÓN:
  {'Excelente' if test_r2 > 0.9 else 'Bueno' if test_r2 > 0.7 else 'Mejorable'} (R² = {test_r2:.3f})
  {'Bajo error' if test_mae < 5 else 'Error moderado' if test_mae < 10 else 'Error alto'} (MAE = {test_mae:.1f})

FEATURES SELECCIONADAS:
  {', '.join(self.feature_columns[:10])}
  {'...' if len(self.feature_columns) > 10 else ''}
"""
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results_text)
            
            self.save_btn.config(state="normal")
            self.update_plots()
            self.notebook.select(3)
            
            messagebox.showinfo("Entrenamiento Completado", 
                               f"Modelo entrenado exitosamente!\n\n"
                               f"Test R²: {test_r2:.3f}\n"
                               f"Test MAE: {test_mae:.3f}\n"
                               f"Features usadas: {len(self.feature_columns)}")
            
            print("[DEBUG] Entrenamiento completado exitosamente")
            
        except Exception as e:
            print(f"[ERROR] Error entrenando modelo: {e}")
            messagebox.showerror("Error", f"Error entrenando modelo:\n{str(e)}")
        finally:
            self.train_btn.config(state="normal")
    
    def update_plots(self):
        if self.trained_model is None or self.X_test is None:
            for ax in self.axes.flat:
                ax.clear()
                ax.text(0.5, 0.5, 'Selecciona features\ny entrena modelo\npara ver gráficos', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
            self.canvas.draw()
            return
        
        try:
            for ax in self.axes.flat:
                ax.clear()
            
            y_test_safe = self.y_test.copy()
            y_test_safe[y_test_safe == 0] = 1e-10
            normalized_residuals = 1 - (self.test_predictions / y_test_safe)
            
            # 1. Predicciones vs Valores Reales
            ax1 = self.axes[0, 0]
            ax1.scatter(self.y_test, self.test_predictions, alpha=0.6, color='red', s=50)
            
            min_val = min(self.y_test.min(), self.test_predictions.min())
            max_val = max(self.y_test.max(), self.test_predictions.max())
            ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Predicción perfecta')
            
            ax1.set_xlabel('Valores Reales')
            ax1.set_ylabel('Predicciones')
            ax1.set_title('Predicciones vs Valores Reales')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
            r2 = r2_score(self.y_test, self.test_predictions)
            mae = mean_absolute_error(self.y_test, self.test_predictions)
            rmse = np.sqrt(mean_squared_error(self.y_test, self.test_predictions))
            
            ax1.text(0.05, 0.95, f'R² = {r2:.3f}\nMAE = {mae:.3f}\nRMSE = {rmse:.3f}', 
                    transform=ax1.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                    verticalalignment='top')
            
            # 2. Residuos Normalizados
            ax2 = self.axes[0, 1]
            ax2.scatter(self.test_predictions, normalized_residuals, alpha=0.6, color='blue', s=50)
            ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
            ax2.set_xlabel('Predicciones')
            ax2.set_ylabel('Residuos Normalizados')
            ax2.set_title('Residuos Normalizados')
            ax2.grid(True, alpha=0.3)
            
            # 3. Feature Importance
            ax3 = self.axes[0, 2]
            top_features = self.feature_importance.head(10)
            y_pos = np.arange(len(top_features))
            ax3.barh(y_pos, top_features['importance'], color='steelblue', alpha=0.8)
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels([f[:20] for f in top_features['feature']], fontsize=8)
            ax3.set_xlabel('Importancia')
            ax3.set_title('Top 10 Features')
            ax3.invert_yaxis()
            
            # 4. Distribución de Residuos
            ax4 = self.axes[1, 0]
            ax4.hist(normalized_residuals, bins=20, alpha=0.7, color='green', edgecolor='black')
            ax4.axvline(x=0, color='red', linestyle='--', linewidth=2)
            ax4.set_xlabel('Residuos Normalizados')
            ax4.set_ylabel('Frecuencia')
            ax4.set_title('Distribución de Residuos')
            ax4.grid(True, alpha=0.3)
            
            # 5. Errores por Muestra
            ax5 = self.axes[1, 1]
            abs_errors = np.abs(self.y_test - self.test_predictions)
            indices = range(len(abs_errors))
            ax5.bar(indices, abs_errors, alpha=0.7, color='orange')
            ax5.set_xlabel('Índice de Muestra')
            ax5.set_ylabel('Error Absoluto')
            ax5.set_title('Errores por Muestra')
            ax5.grid(True, alpha=0.3)
            
            # 6. Métricas Resumidas
            ax6 = self.axes[1, 2]
            ax6.axis('off')
            
            metrics_text = f"""Métricas del Modelo

Features seleccionadas: {len(self.feature_columns)}
Target: {self.target_column}

MAE: {mae:.4f}
RMSE: {rmse:.4f}
R²: {r2:.4f}

Muestras: {len(self.y_test)}
Error máximo: {np.max(abs_errors):.2f}
Error promedio: {np.mean(abs_errors):.2f}

Top feature:
{self.feature_importance.iloc[0]['feature'][:20]}
(imp: {self.feature_importance.iloc[0]['importance']:.3f})"""
            
            ax6.text(0.1, 0.9, metrics_text, transform=ax6.transAxes, fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                    verticalalignment='top', fontfamily='monospace')
            
            self.fig.tight_layout(pad=2.0)
            self.canvas.draw()
            
            print("[DEBUG] Gráficos actualizados")
            
        except Exception as e:
            print(f"[ERROR] Error actualizando gráficos: {e}")
    
    def save_plots(self):
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "No hay gráficos para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar Gráficos",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")]
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráficos guardados en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando gráficos:\n{str(e)}")
    
    def update_prediction_interface(self):
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        if not self.feature_columns:
            ttk.Label(self.features_frame, text="No hay features seleccionadas").pack()
            return
        
        self.feature_vars = {}
        
        for i, feature in enumerate(self.feature_columns[:10]):
            row = i // 2
            col = (i % 2) * 3
            
            if self.current_data is not None:
                avg_value = self.current_data[feature].mean()
                label_text = f"{feature} (promedio: {avg_value:.2f}):"
            else:
                avg_value = 0.0
                label_text = f"{feature}:"
            
            ttk.Label(self.features_frame, text=label_text).grid(row=row, column=col, sticky='w', padx=5, pady=2)
            
            var = tk.DoubleVar(value=avg_value)
            self.feature_vars[feature] = var
            
            entry = ttk.Entry(self.features_frame, textvariable=var, width=15)
            entry.grid(row=row, column=col+1, padx=5, pady=2)
        
        if len(self.feature_columns) > 10:
            ttk.Label(self.features_frame, 
                     text=f"... y {len(self.feature_columns) - 10} features más (usando valores promedio)").grid(
                         row=(len(self.feature_columns[:10]) // 2) + 1, column=0, columnspan=6, pady=10)
        
        print(f"[DEBUG] Interfaz de predicción actualizada con {len(self.feature_columns)} features")
    
    def predict_single(self):
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "Primero entrena un modelo")
            return
        
        try:
            feature_vector = []
            input_features = []
            
            for feature in self.feature_columns:
                if hasattr(self, 'feature_vars') and feature in self.feature_vars:
                    value = self.feature_vars[feature].get()
                    input_features.append(f"{feature}: {value:.3f}")
                else:
                    value = self.current_data[feature].mean()
                
                feature_vector.append(value)
            
            X_pred = np.array(feature_vector).reshape(1, -1)
            prediction = self.trained_model.predict(X_pred)[0]
            
            tree_predictions = [tree.predict(X_pred)[0] for tree in self.trained_model.estimators_]
            pred_std = np.std(tree_predictions)
            
            result_text = f"""PREDICCIÓN INDIVIDUAL
====================

CONFIGURACIÓN:
  Features seleccionadas: {len(self.feature_columns)}
  Target: {self.target_column}

VALORES DE ENTRADA (features principales):
"""
            
            for input_feat in input_features:
                result_text += f"  • {input_feat}\n"
            
            result_text += f"""

RESULTADO:
  {self.target_column} predichas: {prediction:.2f}
  Rango estimado: {prediction - 1.96*pred_std:.2f} - {prediction + 1.96*pred_std:.2f}
  Incertidumbre: ± {1.96*pred_std:.2f}

INTERPRETACIÓN:
  El modelo predice {prediction:.0f} {self.target_column} con una 
  incertidumbre de ±{1.96*pred_std:.1f} (95% confianza).
  
  Basado en {len(self.feature_columns)} features seleccionadas.
"""
            
            self.prediction_text.delete(1.0, tk.END)
            self.prediction_text.insert(1.0, result_text)
            
            print(f"[DEBUG] Predicción realizada: {prediction:.2f}")
            
        except Exception as e:
            print(f"[ERROR] Error en predicción: {e}")
            messagebox.showerror("Error", f"Error en predicción:\n{str(e)}")
    
    def save_model(self):
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "No hay modelo entrenado")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar Modelo",
            defaultextension=".joblib",
            filetypes=[("Joblib files", "*.joblib")]
        )
        
        if file_path:
            try:
                import joblib
                
                model_data = {
                    'model': self.trained_model,
                    'feature_columns': self.feature_columns,
                    'target_column': self.target_column,
                    'selected_features': self.feature_selector.get_selected_features() if hasattr(self, 'feature_selector') else self.feature_columns,
                    'training_params': {
                        'n_estimators': self.n_estimators_var.get(),
                        'test_size': self.test_size_var.get(),
                        'random_state': self.random_state_var.get()
                    },
                    'feature_importance': self.feature_importance if hasattr(self, 'feature_importance') else None,
                    'feature_stats': self.feature_selector.feature_stats if hasattr(self.feature_selector, 'feature_stats') else None,
                    'feature_config': self.feature_selector.get_feature_config() if hasattr(self.feature_selector, 'get_feature_config') else None
                }
                
                joblib.dump(model_data, file_path)
                messagebox.showinfo("Éxito", f"Modelo guardado en:\n{file_path}")
                print(f"[DEBUG] Modelo guardado: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando modelo:\n{str(e)}")
    
    def load_model(self):
        file_path = filedialog.askopenfilename(
            title="Cargar Modelo",
            filetypes=[("Joblib files", "*.joblib")]
        )
        
        if file_path:
            try:
                import joblib
                
                model_data = joblib.load(file_path)
                
                if isinstance(model_data, dict):
                    self.trained_model = model_data['model']
                    
                    if 'feature_columns' in model_data:
                        self.feature_columns = model_data['feature_columns']
                    if 'target_column' in model_data:
                        self.target_column = model_data['target_column']
                    
                    if self.current_data is not None:
                        missing_features = set(self.feature_columns) - set(self.current_data.columns)
                        if missing_features:
                            messagebox.showwarning("Advertencia", 
                                                 f"El dataset actual no tiene las features:\n{missing_features}")
                        else:
                            if hasattr(self, 'feature_selector'):
                                self.feature_selector.selected_features = self.feature_columns
                                self.feature_selector.target_column = self.target_column
                                self.feature_selector.update_table()
                                self.feature_selector.update_summary()
                    
                    params = model_data.get('training_params', {})
                    self.n_estimators_var.set(params.get('n_estimators', 100))
                    self.test_size_var.set(params.get('test_size', 0.2))
                    self.random_state_var.set(params.get('random_state', 42))
                    
                    if 'feature_importance' in model_data and model_data['feature_importance'] is not None:
                        self.feature_importance = model_data['feature_importance']
                    
                    self.features_status_label.config(
                        text=f"✓ Modelo cargado: {len(self.feature_columns)} features, target: {self.target_column}",
                        foreground="green"
                    )
                    
                    self.save_btn.config(state="normal")
                    self.train_btn.config(state="normal")
                    
                    self.update_prediction_interface()
                    
                    messagebox.showinfo("Éxito", f"Modelo cargado desde:\n{file_path}")
                    print(f"[DEBUG] Modelo cargado: {file_path}")
                    
                else:
                    self.trained_model = model_data
                    messagebox.showinfo("Éxito", "Modelo legacy cargado")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando modelo:\n{str(e)}")
    
    def reset(self):
        """Resetear completamente el estado del tab"""
        print("[DEBUG] Reset iniciado")
        
        self.current_data = None
        self.trained_model = None
        self.feature_columns = []
        self.target_column = 'vacancies'
        self.X_test = None
        self.y_test = None
        self.test_predictions = None
        self.original_file_path = None
        self.feature_importance = None
        
        # Resetear feature selector
        if hasattr(self, 'feature_selector'):
            self.feature_selector.current_data = None
            self.feature_selector.selected_features = []
            self.feature_selector.target_column = 'vacancies'
            self.feature_selector.feature_stats = {}
        
        # Resetear interfaz
        self.features_status_label.config(text="No hay features seleccionadas", foreground="red")
        self.feature_status_label.config(text="Carga un dataset primero", foreground="red")
        
        self.train_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.apply_features_btn.config(state="disabled")
        
        # Limpiar textos
        self.info_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.prediction_text.delete(1.0, tk.END)
        
        # Limpiar gráficos
        for ax in self.axes.flat:
            ax.clear()
            ax.text(0.5, 0.5, 'No hay datos\npara mostrar', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
        self.canvas.draw()
        
        # Limpiar interfaz de predicción
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        print("[DEBUG] Reset completado")
    
    def get_frame(self):
        """Obtener el frame principal para ser agregado a un notebook"""
        return self.frame
    
    def get_current_config(self):
        """Obtener configuración actual completa"""
        config = {
            'has_data': self.current_data is not None,
            'has_model': self.trained_model is not None,
            'feature_columns': self.feature_columns.copy(),
            'target_column': self.target_column,
            'training_params': {
                'n_estimators': self.n_estimators_var.get(),
                'test_size': self.test_size_var.get(),
                'random_state': self.random_state_var.get()
            }
        }
        
        if hasattr(self, 'feature_selector'):
            config['feature_config'] = self.feature_selector.get_feature_config()
        
        return config


# Función principal para testing
def main():
    """Función principal para testing del tab"""
    root = tk.Tk()
    root.title("Advanced ML Tab - Test")
    root.geometry("1400x900")
    
    def dummy_callback(data):
        print(f"[CALLBACK] Data loaded: {data.shape}")
    
    # Crear el tab
    ml_tab = AdvancedMLTabWithFeatureSelection(root, dummy_callback)
    ml_tab.get_frame().pack(fill="both", expand=True)
    
    # Datos de prueba
    def load_test_data():
        # Crear datos sintéticos para testing
        np.random.seed(42)
        n_samples = 1000
        
        data = pd.DataFrame({
            'coord_mean': np.random.normal(8, 1, n_samples),
            'coord_std': np.random.normal(2, 0.5, n_samples),
            'energy_mean': np.random.normal(-3, 0.5, n_samples),
            'energy_std': np.random.normal(0.5, 0.1, n_samples),
            'stress_vm_mean': np.random.normal(0.1, 0.02, n_samples),
            'voro_vol_mean': np.random.normal(15, 2, n_samples),
            'hist_coord_4_6': np.random.randint(0, 50, n_samples),
            'hist_coord_6_8': np.random.randint(50, 200, n_samples),
            'hist_coord_8_10': np.random.randint(200, 400, n_samples),
            'hist_energy_bin_1': np.random.randint(0, 100, n_samples),
            'hist_energy_bin_2': np.random.randint(100, 300, n_samples),
        })
        
        # Crear target con algo de correlación
        data['vacancies'] = (
            data['coord_mean'] * -2 + 
            data['energy_mean'] * 5 + 
            data['stress_vm_mean'] * 10 + 
            np.random.normal(0, 2, n_samples) + 30
        ).astype(int).clip(0, 100)
        
        ml_tab.load_dataset_from_dataframe(data)
    
    # Agregar botón de test
    test_frame = ttk.Frame(root)
    test_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Button(test_frame, text="Cargar Datos de Prueba", 
              command=load_test_data).pack(side="left", padx=5)
    
    ttk.Button(test_frame, text="Reset", 
              command=ml_tab.reset).pack(side="left", padx=5)
    
    root.mainloop()


if __name__ == "__main__":
    main()