"""
Advanced ML Tab con tabla de selección de features integrada
Versión mejorada que incluye un tab dedicado para seleccionar features antes del entrenamiento
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

class FeatureSelectionWidget:
    """Widget para seleccionar features con tabla interactiva"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_data = None
        self.selected_features = []
        self.target_column = 'vacancies'
        
        # Variables de UI
        self.search_var = tk.StringVar()
        self.show_selected_only_var = tk.BooleanVar()
        self.auto_exclude_var = tk.BooleanVar(value=True)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets de selección de features"""
        # Frame principal
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Información del dataset
        info_frame = ttk.LabelFrame(main_frame, text="Información del Dataset", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.dataset_info_label = ttk.Label(info_frame, text="No dataset cargado", foreground="red")
        self.dataset_info_label.pack(anchor="w")
        
        # Target column selector
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
        
        # Búsqueda
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(search_frame, text="Buscar:").pack(side="left")
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(5, 10))
        search_entry.bind('<KeyRelease>', self.on_search_changed)
        
        ttk.Button(search_frame, text="Limpiar", 
                  command=lambda: self.search_var.set("")).pack(side="left")
        
        # Checkboxes
        checkbox_frame = ttk.Frame(filter_frame)
        checkbox_frame.pack(fill="x")
        
        ttk.Checkbutton(checkbox_frame, text="Solo seleccionadas", 
                       variable=self.show_selected_only_var,
                       command=self.update_table).pack(side="left", padx=(0, 20))
        
        ttk.Checkbutton(checkbox_frame, text="Auto-excluir no numéricas", 
                       variable=self.auto_exclude_var,
                       command=self.apply_auto_exclusions).pack(side="left")
        
        # Tabla de features
        table_frame = ttk.LabelFrame(main_frame, text="Selección de Features", padding="10")
        table_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Container para tabla con scrollbars
        table_container = ttk.Frame(table_frame)
        table_container.pack(fill="both", expand=True)
        
        # Crear Treeview
        columns = ('selected', 'feature', 'dtype', 'non_null', 'unique', 'correlation', 'sample_values')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('selected', text='✓')
        self.tree.heading('feature', text='Feature')
        self.tree.heading('dtype', text='Tipo')
        self.tree.heading('non_null', text='No Nulos')
        self.tree.heading('unique', text='Únicos')
        self.tree.heading('correlation', text='Correlación')
        self.tree.heading('sample_values', text='Valores de Muestra')
        
        # Configurar anchos
        self.tree.column('selected', width=50, anchor='center')
        self.tree.column('feature', width=200, anchor='w')
        self.tree.column('dtype', width=80, anchor='center')
        self.tree.column('non_null', width=80, anchor='center')
        self.tree.column('unique', width=80, anchor='center')
        self.tree.column('correlation', width=100, anchor='center')
        self.tree.column('sample_values', width=250, anchor='w')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table y scrollbars
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind eventos
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        # Controles de selección
        controls_frame = ttk.LabelFrame(main_frame, text="Controles de Selección", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        buttons_frame1 = ttk.Frame(controls_frame)
        buttons_frame1.pack(fill="x", pady=(0, 5))
        
        ttk.Button(buttons_frame1, text="Seleccionar Todo", 
                  command=self.select_all).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame1, text="Deseleccionar Todo", 
                  command=self.deselect_all).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame1, text="Invertir Selección", 
                  command=self.invert_selection).pack(side="left", padx=(0, 20))
        
        ttk.Button(buttons_frame1, text="Solo Numéricas", 
                  command=self.select_numeric_only).pack(side="left", padx=(0, 5))
        ttk.Button(buttons_frame1, text="Alta Correlación (>0.3)", 
                  command=self.select_high_correlation).pack(side="left")
        
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
        """Cargar datos en el widget"""
        self.current_data = data.copy()
        
        # Configurar target combo
        numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
        self.target_combo['values'] = numeric_columns
        
        if self.target_column in numeric_columns:
            self.target_var.set(self.target_column)
        elif numeric_columns:
            self.target_var.set(numeric_columns[-1])
            self.target_column = numeric_columns[-1]
        
        # Inicializar selección con columnas numéricas (excluyendo target)
        self.selected_features = [col for col in numeric_columns if col != self.target_column]
        
        # Actualizar UI
        self.update_dataset_info()
        self.update_table()
        self.update_summary()
    
    def update_dataset_info(self):
        """Actualizar información del dataset"""
        if self.current_data is not None:
            info_text = f"Cargado: {len(self.current_data)} filas × {len(self.current_data.columns)} columnas"
            self.dataset_info_label.config(text=info_text, foreground="green")
        else:
            self.dataset_info_label.config(text="No dataset cargado", foreground="red")
    
    def update_table(self):
        """Actualizar tabla de features"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.current_data is None:
            return
        
        # Calcular correlaciones con target si es posible
        correlations = {}
        if self.target_column and self.target_column in self.current_data.columns:
            try:
                numeric_data = self.current_data.select_dtypes(include=[np.number])
                if self.target_column in numeric_data.columns:
                    corr_series = numeric_data.corr()[self.target_column]
                    correlations = corr_series.to_dict()
            except:
                pass
        
        # Filtrar y mostrar columnas
        search_text = self.search_var.get().lower()
        show_selected_only = self.show_selected_only_var.get()
        
        all_columns = [col for col in self.current_data.columns if col != self.target_column]
        
        for column in all_columns:
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
            
            # Correlación con target
            corr_text = ""
            if column in correlations:
                corr_val = correlations[column]
                if not np.isnan(corr_val):
                    corr_text = f"{corr_val:.3f}"
            
            # Obtener valores de muestra
            sample_values = col_data.dropna().head(3).astype(str).tolist()
            sample_text = ", ".join(sample_values)
            if len(sample_text) > 40:
                sample_text = sample_text[:37] + "..."
            
            # Insertar en tabla
            item_id = self.tree.insert('', 'end', values=(
                selected_mark,
                column,
                dtype,
                f"{non_null}/{len(col_data)}",
                unique_count,
                corr_text,
                sample_text
            ))
            
            # Colorear filas
            if column in self.selected_features:
                self.tree.item(item_id, tags=('selected',))
            else:
                self.tree.item(item_id, tags=('unselected',))
        
        # Configurar colores
        self.tree.tag_configure('selected', background='#ccffcc')
        self.tree.tag_configure('unselected', background='#ffffff')
    
    def update_summary(self):
        """Actualizar resumen de selección"""
        if self.current_data is None:
            return
            
        total = len([col for col in self.current_data.columns if col != self.target_column])
        selected = len(self.selected_features)
        
        self.total_features_label.config(text=str(total))
        self.selected_features_label.config(text=str(selected))
        self.target_summary_label.config(text=self.target_column or "None")
    
    def on_item_double_click(self, event):
        """Manejar doble click en item para toggle selección"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            column_name = self.tree.item(item, 'values')[1]
            self.toggle_feature_selection(column_name)
    
    def on_search_changed(self, event):
        """Manejar cambio en búsqueda"""
        self.update_table()
    
    def on_target_changed(self, event):
        """Manejar cambio de columna target"""
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
    
    def toggle_feature_selection(self, column_name):
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
        """Seleccionar todas las features disponibles"""
        if self.current_data is None:
            return
        self.selected_features = [col for col in self.current_data.columns if col != self.target_column]
        self.update_table()
        self.update_summary()
    
    def deselect_all(self):
        """Deseleccionar todas las features"""
        self.selected_features = []
        self.update_table()
        self.update_summary()
    
    def invert_selection(self):
        """Invertir selección actual"""
        if self.current_data is None:
            return
        available_features = [col for col in self.current_data.columns if col != self.target_column]
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
            messagebox.showwarning("Advertencia", "Necesita dataset y columna target")
            return
        
        try:
            numeric_data = self.current_data.select_dtypes(include=[np.number])
            
            if self.target_column not in numeric_data.columns:
                messagebox.showwarning("Advertencia", "La columna target debe ser numérica")
                return
            
            correlations = numeric_data.corr()[self.target_column].abs()
            high_corr_features = correlations[correlations > 0.3].index.tolist()
            
            # Remover target column
            if self.target_column in high_corr_features:
                high_corr_features.remove(self.target_column)
            
            self.selected_features = high_corr_features
            self.update_table()
            self.update_summary()
            
            messagebox.showinfo("Info", f"Seleccionadas {len(high_corr_features)} features con correlación > 0.3")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error calculando correlaciones: {str(e)}")
    
    def apply_auto_exclusions(self):
        """Aplicar exclusiones automáticas"""
        if not self.auto_exclude_var.get() or self.current_data is None:
            return
        
        # Excluir columnas no numéricas
        numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
        self.selected_features = [col for col in self.selected_features if col in numeric_columns]
        
        self.update_table()
        self.update_summary()
    
    def export_filtered_csv(self):
        """Exportar CSV con solo las features seleccionadas y el target"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "No hay dataset cargado")
            return
        
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        try:
            # Crear dataset filtrado con features seleccionadas + target
            columns_to_export = self.selected_features + [self.target_column]
            filtered_data = self.current_data[columns_to_export].copy()
            
            # Abrir diálogo para guardar
            file_path = filedialog.asksaveasfilename(
                title="Exportar Dataset Filtrado",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if file_path:
                # Guardar CSV
                filtered_data.to_csv(file_path, index=True)
                
                # Crear archivo de metadatos
                metadata_path = file_path.replace('.csv', '_metadata.txt')
                metadata_text = f"""DATASET FILTRADO - METADATOS
===========================
Archivo original: {getattr(self, 'original_file_path', 'Desconocido')}
Fecha de exportación: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

CONFIGURACIÓN:
  Target: {self.target_column}
  Features seleccionadas: {len(self.selected_features)}
  Filas: {len(filtered_data)}
  Columnas totales: {len(filtered_data.columns)}

FEATURES INCLUIDAS:
"""
                for i, feature in enumerate(self.selected_features, 1):
                    metadata_text += f"  {i:2d}. {feature}\n"
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    f.write(metadata_text)
                
                messagebox.showinfo("Éxito", 
                                   f"Dataset filtrado exportado!\n\n"
                                   f"Archivo: {file_path}\n"
                                   f"Features: {len(self.selected_features)}\n"
                                   f"Target: {self.target_column}\n"
                                   f"Filas: {len(filtered_data)}\n\n"
                                   f"Metadatos guardados en: {metadata_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando dataset filtrado:\n{str(e)}")
    
    def get_selected_features(self):
        """Obtener lista de features seleccionadas"""
        return self.selected_features.copy()
    
    def get_target_column(self):
        """Obtener columna target"""
        return self.target_column


class AdvancedMLTabWithFeatureSelection:
    """Advanced ML Tab con selección de features integrada"""
    
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
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets del tab"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Crear notebook para sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        self.create_data_tab()
        self.create_feature_selection_tab()  # Nuevo tab
        self.create_training_tab()
        self.create_results_tab()
        self.create_prediction_tab()
    
    def create_data_tab(self):
        """Tab de carga y exploración de datos"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Datos")
        
        # Sección de carga
        load_frame = ttk.LabelFrame(data_frame, text="Cargar Dataset", padding="10")
        load_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(load_frame, text="Cargar CSV/Excel Original", 
                  command=self.load_dataset).pack(side="left", padx=5)
        
        ttk.Button(load_frame, text="Cargar CSV Filtrado", 
                  command=self.load_filtered_dataset).pack(side="left", padx=5)
        
        # Información del dataset
        info_frame = ttk.LabelFrame(data_frame, text="Información del Dataset", padding="10")
        info_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=20, wrap='word')
        self.info_text.pack(fill="both", expand=True)
    
    def create_feature_selection_tab(self):
        """Tab de selección de features"""
        feature_frame = ttk.Frame(self.notebook)
        self.notebook.add(feature_frame, text="🎯 Features")
        
        # Crear widget de selección de features
        self.feature_selector = FeatureSelectionWidget(feature_frame)
        
        # Botón para aplicar selección
        apply_frame = ttk.Frame(feature_frame)
        apply_frame.pack(fill="x", padx=10, pady=5)
        
        self.apply_features_btn = ttk.Button(apply_frame, text="Aplicar Selección de Features", 
                                           command=self.apply_feature_selection,
                                           state="disabled")
        self.apply_features_btn.pack(side="left", padx=5)
        
        self.feature_status_label = ttk.Label(apply_frame, text="Carga un dataset primero", foreground="red")
        self.feature_status_label.pack(side="left", padx=(20, 0))
    
    def create_training_tab(self):
        """Tab de entrenamiento"""
        train_frame = ttk.Frame(self.notebook)
        self.notebook.add(train_frame, text="🤖 Entrenamiento")
        
        # Panel izquierdo - Controles
        left_panel = ttk.Frame(train_frame)
        left_panel.pack(side="left", fill="y", padx=(10, 5))
        
        # Estado de features
        features_status_frame = ttk.LabelFrame(left_panel, text="Estado de Features", padding="10")
        features_status_frame.pack(fill='x', pady=(0, 10))
        
        self.features_status_label = ttk.Label(features_status_frame, text="No hay features seleccionadas", foreground="red")
        self.features_status_label.pack(anchor="w")
        
        # Parámetros
        params_group = ttk.LabelFrame(left_panel, text="Parámetros Random Forest", padding="10")
        params_group.pack(fill='x', pady=(0, 10))
        
        ttk.Label(params_group, text="N° Estimadores:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Spinbox(params_group, from_=50, to=500, textvariable=self.n_estimators_var, width=10).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Test Size:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.test_size_var, width=10).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(params_group, text="Random State:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(params_group, textvariable=self.random_state_var, width=10).grid(row=2, column=1, padx=5, pady=2)
        
        # Botones
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
        
        # Panel derecho - Resultados
        right_panel = ttk.Frame(train_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10))
        
        results_group = ttk.LabelFrame(right_panel, text="Métricas del Entrenamiento", padding="10")
        results_group.pack(fill='both', expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_group, height=20, wrap='word')
        self.results_text.pack(fill='both', expand=True)
    
    def create_results_tab(self):
        """Tab de resultados con visualizaciones"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📈 Resultados")
        
        # Botones de control
        control_frame = ttk.Frame(results_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="Actualizar Gráficos", 
                  command=self.update_plots).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Guardar Gráficos", 
                  command=self.save_plots).pack(side="left", padx=5)
        
        # Frame para gráficos
        self.plots_frame = ttk.Frame(results_frame)
        self.plots_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Crear figura de matplotlib
        self.fig, self.axes = plt.subplots(2, 3, figsize=(18, 12))
        self.fig.tight_layout(pad=3.0)
        
        # Canvas para mostrar gráficos
        self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def create_prediction_tab(self):
        """Tab de predicción"""
        pred_frame = ttk.Frame(self.notebook)
        self.notebook.add(pred_frame, text="🔮 Predicción")
        
        # Predicción individual
        single_group = ttk.LabelFrame(pred_frame, text="Predicción Individual", padding="10")
        single_group.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(single_group, text="Ingrese valores para las features seleccionadas:").pack(anchor='w')
        
        # Frame para inputs de features
        self.features_frame = ttk.Frame(single_group)
        self.features_frame.pack(fill='x', pady=10)
        
        ttk.Button(single_group, text="Predecir", command=self.predict_single).pack()
        
        # Resultados
        pred_results_group = ttk.LabelFrame(pred_frame, text="Resultados", padding="10")
        pred_results_group.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.prediction_text = scrolledtext.ScrolledText(pred_results_group, height=15, wrap='word')
        self.prediction_text.pack(fill='both', expand=True)
    
    def load_filtered_dataset(self):
        """Cargar dataset filtrado previamente exportado"""
        file_path = filedialog.askopenfilename(
            title="Cargar Dataset Filtrado",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                # Cargar CSV filtrado
                data = pd.read_csv(file_path, index_col=0)
                
                # Detectar automáticamente target y features
                # Asumir que la última columna es el target
                self.target_column = data.columns[-1]
                self.feature_columns = list(data.columns[:-1])
                
                # Cargar dataset
                self.current_data = data.copy()
                
                # Actualizar información
                self.update_dataset_info()
                
                # Actualizar estado de features (ya están aplicadas)
                self.features_status_label.config(
                    text=f"✓ {len(self.feature_columns)} features cargadas, target: {self.target_column}",
                    foreground="green"
                )
                
                # Habilitar entrenamiento directamente
                self.train_btn.config(state="normal")
                
                # Actualizar interfaz de predicción
                self.update_prediction_interface()
                
                # Cambiar al tab de entrenamiento
                self.notebook.select(2)  # Tab de Entrenamiento
                
                # Mostrar detalles en el área de resultados
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
                
                # Notificar al callback
                self.data_loaded_callback(data)
                
                messagebox.showinfo("Éxito", 
                                   f"Dataset filtrado cargado!\n\n"
                                   f"Archivo: {file_path}\n"
                                   f"Features: {len(self.feature_columns)}\n"
                                   f"Target: {self.target_column}\n"
                                   f"Filas: {len(data)}\n\n"
                                   f"El entrenamiento está habilitado.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando dataset filtrado:\n{str(e)}")
    
    def load_dataset(self):
        """Cargar dataset desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Cargar Dataset",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                # Guardar ruta para metadatos
                self.original_file_path = file_path
                
                if file_path.endswith('.xlsx'):
                    data = pd.read_excel(file_path)
                else:
                    data = pd.read_csv(file_path, index_col=0)
                
                self.load_dataset_from_dataframe(data)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando dataset:\n{str(e)}")
    
    def load_dataset_from_dataframe(self, data):
        """Cargar dataset desde DataFrame"""
        try:
            self.current_data = data.copy()
            
            # Cargar datos en el selector de features
            self.feature_selector.load_data(data)
            
            # Actualizar información
            self.update_dataset_info()
            
            # Habilitar botón de aplicar features
            self.apply_features_btn.config(state="normal")
            self.feature_status_label.config(text="Dataset cargado. Selecciona features y aplica.", foreground="orange")
            
            # Notificar al callback
            self.data_loaded_callback(data)
            
            messagebox.showinfo("Éxito", 
                               f"Dataset cargado exitosamente!\n\n"
                               f"Filas: {len(data)}\n"
                               f"Columnas: {len(data.columns)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando dataset:\n{str(e)}")
    
    def update_dataset_info(self):
        """Actualizar información del dataset"""
        if self.current_data is None:
            return
        
        # Identificar columnas numéricas y de texto
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
            stats = self.current_data[col].describe()
            info_lines.append(f"  • {col}: [{stats['min']:.2f}, {stats['max']:.2f}], mean={stats['mean']:.2f}")
        
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
        """Aplicar selección de features para entrenamiento"""
        try:
            self.feature_columns = self.feature_selector.get_selected_features()
            self.target_column = self.feature_selector.get_target_column()
            
            if not self.feature_columns:
                messagebox.showwarning("Advertencia", "No hay features seleccionadas")
                return
            
            if not self.target_column:
                messagebox.showwarning("Advertencia", "No hay columna target seleccionada")
                return
            
            # Actualizar estado en ambos labels
            self.features_status_label.config(
                text=f"✓ {len(self.feature_columns)} features seleccionadas, target: {self.target_column}",
                foreground="green"
            )
            
            self.feature_status_label.config(
                text=f"✓ Features aplicadas: {len(self.feature_columns)} features para entrenamiento",
                foreground="green"
            )
            
            # Habilitar entrenamiento
            self.train_btn.config(state="normal")
            
            # Actualizar interfaz de predicción
            self.update_prediction_interface()
            
            # Cambiar al tab de entrenamiento para mostrar que está listo
            self.notebook.select(2)  # Tab de Entrenamiento
            
            # Mostrar detalles en el área de resultados de entrenamiento
            details_text = f"""FEATURES SELECCIONADAS PARA ENTRENAMIENTO
========================================

Target: {self.target_column}
Features seleccionadas: {len(self.feature_columns)}

LISTA DE FEATURES:
"""
            for i, feature in enumerate(self.feature_columns, 1):
                details_text += f"  {i:2d}. {feature}\n"
            
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Error aplicando selección:\n{str(e)}")
    
    def train_model(self):
        """Entrenar modelo Random Forest"""
        if not self.feature_columns:
            messagebox.showwarning("Advertencia", "Primero selecciona y aplica las features")
            return
        
        try:
            self.train_btn.config(state="disabled")
            
            # Preparar datos
            X = self.current_data[self.feature_columns]
            y = self.current_data[self.target_column]
            
            # Verificar que no hay valores NaN
            if X.isnull().any().any():
                from sklearn.impute import SimpleImputer
                imputer = SimpleImputer(strategy='median')
                X_clean = pd.DataFrame(imputer.fit_transform(X), columns=X.columns, index=X.index)
            else:
                X_clean = X
            
            # División train/test
            from sklearn.model_selection import train_test_split
            X_train, self.X_test, y_train, self.y_test = train_test_split(
                X_clean, y, 
                test_size=self.test_size_var.get(),
                random_state=self.random_state_var.get()
            )
            
            # Crear y entrenar modelo
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            
            self.trained_model = RandomForestRegressor(
                n_estimators=self.n_estimators_var.get(),
                random_state=self.random_state_var.get(),
                n_jobs=-1
            )
            
            self.trained_model.fit(X_train, y_train)
            
            # Evaluar modelo
            train_pred = self.trained_model.predict(X_train)
            self.test_predictions = self.trained_model.predict(self.X_test)
            
            train_mae = mean_absolute_error(y_train, train_pred)
            test_mae = mean_absolute_error(self.y_test, self.test_predictions)
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            test_rmse = np.sqrt(mean_squared_error(self.y_test, self.test_predictions))
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(self.y_test, self.test_predictions)
            
            # Validación cruzada
            from sklearn.model_selection import cross_val_score
            cv_mae = -cross_val_score(self.trained_model, X_clean, y, cv=5, scoring='neg_mean_absolute_error')
            cv_r2 = cross_val_score(self.trained_model, X_clean, y, cv=5, scoring='r2')
            
            # Feature importance
            self.feature_importance = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.trained_model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Mostrar resultados
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
  {'🟢 Excelente' if test_r2 > 0.9 else '🟡 Bueno' if test_r2 > 0.7 else '🔴 Mejorable'} (R² = {test_r2:.3f})
  {'🟢 Bajo error' if test_mae < 5 else '🟡 Error moderado' if test_mae < 10 else '🔴 Error alto'} (MAE = {test_mae:.1f})

FEATURES SELECCIONADAS:
  {', '.join(self.feature_columns[:10])}
  {'...' if len(self.feature_columns) > 10 else ''}
"""
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results_text)
            
            # Habilitar botones
            self.save_btn.config(state="normal")
            
            # Actualizar gráficos
            self.update_plots()
            
            # Cambiar al tab de resultados
            self.notebook.select(3)  # Tab de Resultados
            
            messagebox.showinfo("Entrenamiento Completado", 
                               f"Modelo entrenado exitosamente!\n\n"
                               f"Test R²: {test_r2:.3f}\n"
                               f"Test MAE: {test_mae:.3f}\n"
                               f"Features usadas: {len(self.feature_columns)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error entrenando modelo:\n{str(e)}")
        finally:
            self.train_btn.config(state="normal")
    
    def update_plots(self):
        """Actualizar gráficos de resultados"""
        if self.trained_model is None or self.X_test is None:
            # Limpiar gráficos si no hay modelo
            for ax in self.axes.flat:
                ax.clear()
                ax.text(0.5, 0.5, 'Selecciona features\ny entrena modelo\npara ver gráficos', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12)
                ax.set_xticks([])
                ax.set_yticks([])
            self.canvas.draw()
            return
        
        try:
            # Limpiar gráficos anteriores
            for ax in self.axes.flat:
                ax.clear()
            
            # Calcular residuos normalizados
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
            
            # Métricas
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
            
        except Exception as e:
            print(f"Error actualizando gráficos: {e}")
    
    def save_plots(self):
        """Guardar gráficos como imagen"""
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
        """Actualizar interfaz de predicción con features seleccionadas"""
        # Limpiar frame anterior
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        if not self.feature_columns:
            ttk.Label(self.features_frame, text="No hay features seleccionadas").pack()
            return
        
        # Mostrar features seleccionadas para input
        self.feature_vars = {}
        
        for i, feature in enumerate(self.feature_columns[:10]):  # Limitar a 10 para UI
            row = i // 2
            col = (i % 2) * 3
            
            # Obtener valor promedio para sugerir
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
    
    def predict_single(self):
        """Realizar predicción individual"""
        if self.trained_model is None:
            messagebox.showwarning("Advertencia", "Primero entrena un modelo")
            return
        
        try:
            # Crear vector de features
            feature_vector = []
            input_features = []
            
            for feature in self.feature_columns:
                if feature in self.feature_vars:
                    value = self.feature_vars[feature].get()
                    input_features.append(f"{feature}: {value:.3f}")
                else:
                    # Usar valor promedio para features no mostradas
                    value = self.current_data[feature].mean()
                
                feature_vector.append(value)
            
            # Realizar predicción
            X_pred = np.array(feature_vector).reshape(1, -1)
            prediction = self.trained_model.predict(X_pred)[0]
            
            # Obtener intervalo de confianza
            tree_predictions = [tree.predict(X_pred)[0] for tree in self.trained_model.estimators_]
            pred_std = np.std(tree_predictions)
            
            # Mostrar resultado
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en predicción:\n{str(e)}")
    
    def save_model(self):
        """Guardar modelo entrenado"""
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
                
                # Guardar modelo con metadatos completos
                model_data = {
                    'model': self.trained_model,
                    'feature_columns': self.feature_columns,
                    'target_column': self.target_column,
                    'selected_features': self.feature_selector.get_selected_features(),
                    'training_params': {
                        'n_estimators': self.n_estimators_var.get(),
                        'test_size': self.test_size_var.get(),
                        'random_state': self.random_state_var.get()
                    },
                    'feature_importance': self.feature_importance if hasattr(self, 'feature_importance') else None
                }
                
                joblib.dump(model_data, file_path)
                messagebox.showinfo("Éxito", f"Modelo guardado en:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando modelo:\n{str(e)}")
    
    def load_model(self):
        """Cargar modelo previamente entrenado"""
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
                    
                    # Restaurar configuración de features
                    if 'feature_columns' in model_data:
                        self.feature_columns = model_data['feature_columns']
                    if 'target_column' in model_data:
                        self.target_column = model_data['target_column']
                    
                    # Verificar compatibilidad con dataset actual
                    if self.current_data is not None:
                        missing_features = set(self.feature_columns) - set(self.current_data.columns)
                        if missing_features:
                            messagebox.showwarning("Advertencia", 
                                                 f"El dataset actual no tiene las features:\n{missing_features}")
                        else:
                            # Actualizar selector de features si es posible
                            if hasattr(self, 'feature_selector'):
                                self.feature_selector.selected_features = self.feature_columns
                                self.feature_selector.target_column = self.target_column
                                self.feature_selector.update_table()
                                self.feature_selector.update_summary()
                    
                    # Restaurar parámetros
                    params = model_data.get('training_params', {})
                    self.n_estimators_var.set(params.get('n_estimators', 100))
                    self.test_size_var.set(params.get('test_size', 0.2))
                    self.random_state_var.set(params.get('random_state', 42))
                    
                    # Restaurar feature importance
                    if 'feature_importance' in model_data and model_data['feature_importance'] is not None:
                        self.feature_importance = model_data['feature_importance']
                    
                    # Actualizar estado de UI
                    self.features_status_label.config(
                        text=f"✓ Modelo cargado: {len(self.feature_columns)} features, target: {self.target_column}",
                        foreground="green"
                    )
                    
                    self.save_btn.config(state="normal")
                    self.train_btn.config(state="normal")
                    
                    # Actualizar interfaz de predicción
                    self.update_prediction_interface()
                    
                    messagebox.showinfo("Éxito", f"Modelo cargado desde:\n{file_path}")
                    
                else:
                    # Modelo legacy
                    self.trained_model = model_data
                    messagebox.showinfo("Éxito", "Modelo legacy cargado")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando modelo:\n{str(e)}")
    
    def reset(self):
        """Reset completo del tab"""
        # Reset variables
        self.current_data = None
        self.trained_model = None
        self.feature_columns = []
        self.target_column = 'vacancies'
        self.X_test = None
        self.y_test = None
        self.test_predictions = None
        
        # Reset displays
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "Carga un dataset para comenzar")
        
        self.results_text.delete(1.0, tk.END)
        self.prediction_text.delete(1.0, tk.END)
        
        # Reset feature selector
        if hasattr(self, 'feature_selector'):
            self.feature_selector.current_data = None
            self.feature_selector.selected_features = []
            self.feature_selector.update_table()
            self.feature_selector.update_summary()
        
        # Reset botones
        self.apply_features_btn.config(state="disabled")
        self.train_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        
        # Reset labels
        self.features_status_label.config(text="No hay features seleccionadas", foreground="red")
        self.feature_status_label.config(text="Carga un dataset primero", foreground="red")
        
        # Limpiar interfaz de predicción
        for widget in self.features_frame.winfo_children():
            widget.destroy()
        
        # Limpiar gráficos
        for ax in self.axes.flat:
            ax.clear()
            ax.text(0.5, 0.5, 'Carga un dataset,\nselecciona features\ny entrena un modelo', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
        self.canvas.draw()


# Función de prueba
def test_advanced_ml_with_features():
    """Función de prueba para la clase integrada"""
    import tkinter as tk
    from tkinter import ttk
    
    def data_callback(data):
        print(f"Dataset callback: {data.shape}")
    
    # Crear ventana de prueba
    root = tk.Tk()
    root.title("Advanced ML con Feature Selection - Prueba")
    root.geometry("1600x1000")
    
    # Crear notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Crear instancia del tab integrado
    ml_tab = AdvancedMLTabWithFeatureSelection(notebook, data_callback)
    notebook.add(ml_tab.frame, text="ML con Feature Selection")
    
    # Botón de reset para pruebas
    reset_frame = ttk.Frame(root)
    reset_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Button(reset_frame, text="Reset Tab", command=ml_tab.reset).pack(side="left")
    
    root.mainloop()


# Alias para compatibilidad con app.py existente
AdvancedMLTabWithPlots = AdvancedMLTabWithFeatureSelection

if __name__ == "__main__":
    test_advanced_ml_with_features()