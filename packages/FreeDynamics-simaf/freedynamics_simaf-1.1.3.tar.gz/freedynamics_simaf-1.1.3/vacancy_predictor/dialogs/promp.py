#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interfaz grÃ¡fica para seleccionar features antes del entrenamiento
Compatible con vacancy_pipeline.py y otros pipelines de ML
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Set

class FeatureSelectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Selector de Features para ML")
        self.root.geometry("1200x700")
        
        # Variables
        self.dataset_path = None
        self.df = None
        self.selected_features = set()
        self.feature_vars = {}
        self.target_column = None
        
        # Configurar estilo
        self.setup_style()
        
        # Crear interfaz
        self.create_widgets()
        
    def setup_style(self):
        """Configurar estilos visuales"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        self.colors = {
            'coord': '#4CAF50',      # Verde para coordinaciÃ³n
            'pe': '#2196F3',          # Azul para energÃ­a
            'stress': '#FF9800',      # Naranja para stress
            'voro': '#9C27B0',        # PÃºrpura para Voronoi
            'vacancy': '#F44336',     # Rojo para vacancias
            'other': '#607D8B'        # Gris para otros
        }
        
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar peso de filas y columnas
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # ========== SecciÃ³n superior: Carga de archivo ==========
        load_frame = ttk.LabelFrame(main_frame, text="Cargar Dataset", padding="10")
        load_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(load_frame, text="ðŸ“ Seleccionar archivo CSV", 
                  command=self.load_dataset).grid(row=0, column=0, padx=5)
        
        self.file_label = ttk.Label(load_frame, text="No se ha cargado ningÃºn archivo")
        self.file_label.grid(row=0, column=1, padx=10)
        
        # Info del dataset
        self.info_label = ttk.Label(load_frame, text="")
        self.info_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # ========== SecciÃ³n izquierda: CategorÃ­as ==========
        cat_frame = ttk.LabelFrame(main_frame, text="CategorÃ­as", padding="10")
        cat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Botones de categorÃ­as
        self.category_buttons = {}
        categories = [
            ("CoordinaciÃ³n", 'coord'),
            ("EnergÃ­a", 'pe'),
            ("Stress", 'stress'),
            ("Voronoi", 'voro'),
            ("Vacancias", 'vacancy'),
            ("Otros", 'other')
        ]
        
        for i, (label, key) in enumerate(categories):
            btn = ttk.Button(cat_frame, text=f"{label} (0)", 
                           command=lambda k=key: self.toggle_category(k))
            btn.grid(row=i, column=0, pady=2, sticky=(tk.W, tk.E))
            self.category_buttons[key] = btn
        
        # Botones de selecciÃ³n rÃ¡pida
        ttk.Separator(cat_frame, orient='horizontal').grid(row=len(categories), 
                                                          column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(cat_frame, text="âœ“ Seleccionar todo", 
                  command=self.select_all).grid(row=len(categories)+1, column=0, pady=2, 
                                               sticky=(tk.W, tk.E))
        ttk.Button(cat_frame, text="âœ— Deseleccionar todo", 
                  command=self.deselect_all).grid(row=len(categories)+2, column=0, pady=2, 
                                                 sticky=(tk.W, tk.E))
        
        # ========== SecciÃ³n central: Lista de features ==========
        feature_frame = ttk.LabelFrame(main_frame, text="Features disponibles", padding="10")
        feature_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        feature_frame.columnconfigure(0, weight=1)
        feature_frame.rowconfigure(0, weight=1)
        
        # Frame con scroll para checkboxes
        canvas = tk.Canvas(feature_frame, bg='white')
        scrollbar_y = ttk.Scrollbar(feature_frame, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(feature_frame, orient="horizontal", command=canvas.xview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # ========== SecciÃ³n derecha: EstadÃ­sticas ==========
        stats_frame = ttk.LabelFrame(main_frame, text="EstadÃ­sticas y Vista Previa", padding="10")
        stats_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Target selector
        ttk.Label(stats_frame, text="Columna Target:").grid(row=0, column=0, sticky=tk.W)
        self.target_combo = ttk.Combobox(stats_frame, state="readonly", width=25)
        self.target_combo.grid(row=0, column=1, padx=5, pady=5)
        self.target_combo.bind('<<ComboboxSelected>>', self.on_target_change)
        
        # EstadÃ­sticas
        self.stats_text = tk.Text(stats_frame, width=40, height=15, wrap=tk.WORD)
        self.stats_text.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scroll para estadÃ­sticas
        stats_scroll = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        stats_scroll.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        # ========== SecciÃ³n inferior: Acciones ==========
        action_frame = ttk.Frame(main_frame, padding="10")
        action_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Contador de features seleccionadas
        self.counter_label = ttk.Label(action_frame, text="Features seleccionadas: 0/0", 
                                      font=('Arial', 11, 'bold'))
        self.counter_label.grid(row=0, column=0, padx=10)
        
        # Botones de acciÃ³n
        ttk.Button(action_frame, text="ðŸ’¾ Guardar dataset filtrado", 
                  command=self.save_filtered_dataset).grid(row=0, column=1, padx=5)
        
        ttk.Button(action_frame, text="ðŸ“Š Entrenar modelo", 
                  command=self.train_model).grid(row=0, column=2, padx=5)
        
        ttk.Button(action_frame, text="ðŸ“‹ Exportar configuraciÃ³n", 
                  command=self.export_config).grid(row=0, column=3, padx=5)
        
        ttk.Button(action_frame, text="ðŸ“¥ Importar configuraciÃ³n", 
                  command=self.import_config).grid(row=0, column=4, padx=5)
        
    def load_dataset(self):
        """Cargar archivo CSV"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.df = pd.read_csv(filename, index_col=0)
                self.dataset_path = filename
                
                # Actualizar info
                self.file_label.config(text=f"ðŸ“„ {Path(filename).name}")
                self.info_label.config(text=f"Filas: {len(self.df)} | Columnas: {len(self.df.columns)}")
                
                # Detectar columna target
                self.detect_target_column()
                
                # Mostrar features
                self.display_features()
                
                # Actualizar estadÃ­sticas
                self.update_statistics()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo:\n{str(e)}")
    
    def detect_target_column(self):
        """Detectar automÃ¡ticamente la columna target"""
        possible_targets = ['vacancies', 'n_vac', 'target', 'y', 'label']
        
        target_columns = [col for col in self.df.columns if col.lower() in possible_targets]
        
        # Actualizar combobox
        self.target_combo['values'] = list(self.df.columns)
        
        if target_columns:
            self.target_column = target_columns[0]
            self.target_combo.set(self.target_column)
        elif 'vacancies' in self.df.columns:
            self.target_column = 'vacancies'
            self.target_combo.set(self.target_column)
    
    def on_target_change(self, event):
        """Manejar cambio de columna target"""
        self.target_column = self.target_combo.get()
        self.display_features()
        self.update_statistics()
    
    def categorize_feature(self, feature_name: str) -> str:
        """Categorizar una feature basÃ¡ndose en su nombre"""
        feature_lower = feature_name.lower()
        
        if 'coord' in feature_lower:
            return 'coord'
        elif 'pe' in feature_lower or 'energy' in feature_lower:
            return 'pe'
        elif 'stress' in feature_lower or 'vm' in feature_lower or 'pressure' in feature_lower:
            return 'stress'
        elif 'voro' in feature_lower:
            return 'voro'
        elif 'vacan' in feature_lower or 'vac' in feature_lower:
            return 'vacancy'
        else:
            return 'other'
    
    def display_features(self):
        """Mostrar todas las features con checkboxes"""
        if self.df is None:
            return
        
        # Limpiar frame anterior
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.feature_vars = {}
        self.selected_features = set()
        
        # Obtener features (excluyendo target)
        features = [col for col in self.df.columns if col != self.target_column]
        
        # Agrupar por categorÃ­a
        categories = {}
        for feat in features:
            cat = self.categorize_feature(feat)
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(feat)
        
        # Mostrar por categorÃ­as
        row = 0
        for cat in ['coord', 'pe', 'stress', 'voro', 'vacancy', 'other']:
            if cat not in categories or not categories[cat]:
                continue
            
            # Header de categorÃ­a
            header = ttk.Label(self.scrollable_frame, 
                             text=f"â”â”â” {cat.upper()} â”â”â”",
                             font=('Arial', 10, 'bold'))
            header.grid(row=row, column=0, columnspan=3, pady=(10, 5), sticky=tk.W)
            row += 1
            
            # Features de la categorÃ­a
            for i, feat in enumerate(sorted(categories[cat])):
                var = tk.BooleanVar(value=True)
                self.feature_vars[feat] = var
                self.selected_features.add(feat)
                
                # Checkbox
                cb = ttk.Checkbutton(self.scrollable_frame, text=feat, variable=var,
                                    command=self.update_selection)
                cb.grid(row=row + i//3, column=i%3, sticky=tk.W, padx=5, pady=2)
            
            row += (len(categories[cat]) + 2) // 3 + 1
        
        # Actualizar contadores de categorÃ­as
        self.update_category_counts()
        self.update_selection()
    
    def update_category_counts(self):
        """Actualizar contadores en botones de categorÃ­as"""
        if not self.feature_vars:
            return
        
        counts = {cat: 0 for cat in self.colors.keys()}
        
        for feat, var in self.feature_vars.items():
            if var.get():
                cat = self.categorize_feature(feat)
                counts[cat] = counts.get(cat, 0) + 1
        
        for cat, btn in self.category_buttons.items():
            total = sum(1 for f in self.feature_vars.keys() 
                       if self.categorize_feature(f) == cat)
            selected = counts.get(cat, 0)
            
            label = cat.capitalize()
            if cat == 'pe':
                label = "EnergÃ­a"
            elif cat == 'coord':
                label = "CoordinaciÃ³n"
            elif cat == 'voro':
                label = "Voronoi"
            elif cat == 'vacancy':
                label = "Vacancias"
            elif cat == 'other':
                label = "Otros"
            
            btn.config(text=f"{label} ({selected}/{total})")
    
    def toggle_category(self, category):
        """Activar/desactivar todas las features de una categorÃ­a"""
        if not self.feature_vars:
            return
        
        # Verificar si todas estÃ¡n seleccionadas
        cat_features = [f for f in self.feature_vars.keys() 
                       if self.categorize_feature(f) == category]
        
        all_selected = all(self.feature_vars[f].get() for f in cat_features)
        
        # Toggle
        new_value = not all_selected
        for feat in cat_features:
            self.feature_vars[feat].set(new_value)
        
        self.update_selection()
    
    def select_all(self):
        """Seleccionar todas las features"""
        for var in self.feature_vars.values():
            var.set(True)
        self.update_selection()
    
    def deselect_all(self):
        """Deseleccionar todas las features"""
        for var in self.feature_vars.values():
            var.set(False)
        self.update_selection()
    
    def update_selection(self):
        """Actualizar lista de features seleccionadas"""
        self.selected_features = {feat for feat, var in self.feature_vars.items() if var.get()}
        
        # Actualizar contador
        total = len(self.feature_vars)
        selected = len(self.selected_features)
        self.counter_label.config(text=f"Features seleccionadas: {selected}/{total}")
        
        # Actualizar contadores de categorÃ­as
        self.update_category_counts()
        
        # Actualizar estadÃ­sticas
        self.update_statistics()
    
    def update_statistics(self):
        """Actualizar panel de estadÃ­sticas"""
        self.stats_text.delete(1.0, tk.END)
        
        if self.df is None or not self.selected_features:
            self.stats_text.insert(tk.END, "No hay features seleccionadas")
            return
        
        stats_info = []
        stats_info.append("=" * 35)
        stats_info.append("RESUMEN DE FEATURES SELECCIONADAS")
        stats_info.append("=" * 35)
        stats_info.append(f"\nTotal seleccionadas: {len(self.selected_features)}")
        
        if self.target_column:
            stats_info.append(f"Target: {self.target_column}")
            
            # EstadÃ­sticas del target
            if self.target_column in self.df.columns:
                target_data = self.df[self.target_column]
                stats_info.append(f"\nEstadÃ­sticas del target:")
                stats_info.append(f"  Min: {target_data.min():.2f}")
                stats_info.append(f"  Max: {target_data.max():.2f}")
                stats_info.append(f"  Media: {target_data.mean():.2f}")
                stats_info.append(f"  Std: {target_data.std():.2f}")
        
        # Features por categorÃ­a
        stats_info.append("\nFeatures por categorÃ­a:")
        for cat in ['coord', 'pe', 'stress', 'voro', 'vacancy', 'other']:
            count = sum(1 for f in self.selected_features if self.categorize_feature(f) == cat)
            if count > 0:
                stats_info.append(f"  {cat}: {count}")
        
        # Features con mÃ¡s varianza
        if len(self.selected_features) > 0:
            stats_info.append("\nTop 10 features (por varianza):")
            variances = {}
            for feat in self.selected_features:
                if feat in self.df.columns:
                    variances[feat] = self.df[feat].var()
            
            sorted_vars = sorted(variances.items(), key=lambda x: x[1], reverse=True)[:10]
            for feat, var in sorted_vars:
                stats_info.append(f"  {feat[:25]}: {var:.4f}")
        
        self.stats_text.insert(tk.END, "\n".join(stats_info))
    
    def save_filtered_dataset(self):
        """Guardar dataset con solo las features seleccionadas"""
        if self.df is None or not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Incluir target si existe
                columns = list(self.selected_features)
                if self.target_column and self.target_column in self.df.columns:
                    columns.append(self.target_column)
                
                filtered_df = self.df[columns]
                filtered_df.to_csv(filename)
                
                messagebox.showinfo("Ã‰xito", f"Dataset guardado con {len(columns)} columnas")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
    
    def export_config(self):
        """Exportar configuraciÃ³n de features seleccionadas"""
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            config = {
                'selected_features': list(self.selected_features),
                'target_column': self.target_column,
                'total_features': len(self.feature_vars),
                'dataset_info': {
                    'rows': len(self.df) if self.df is not None else 0,
                    'original_file': str(self.dataset_path) if self.dataset_path else None
                }
            }
            
            with open(filename, 'w') as f:
                json.dump(config, f, indent=4)
            
            messagebox.showinfo("Ã‰xito", "ConfiguraciÃ³n exportada")
    
    def import_config(self):
        """Importar configuraciÃ³n de features"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                if 'selected_features' in config:
                    # Deseleccionar todo primero
                    for var in self.feature_vars.values():
                        var.set(False)
                    
                    # Seleccionar las del config
                    for feat in config['selected_features']:
                        if feat in self.feature_vars:
                            self.feature_vars[feat].set(True)
                    
                    # Actualizar target si existe
                    if 'target_column' in config and config['target_column']:
                        self.target_column = config['target_column']
                        if self.target_column in self.df.columns:
                            self.target_combo.set(self.target_column)
                    
                    self.update_selection()
                    messagebox.showinfo("Ã‰xito", "ConfiguraciÃ³n importada")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al importar:\n{str(e)}")
    
    def train_model(self):
        """Entrenar modelo con features seleccionadas"""
        if self.df is None or not self.selected_features:
            messagebox.showwarning("Advertencia", "No hay features seleccionadas")
            return
        
        if not self.target_column or self.target_column not in self.df.columns:
            messagebox.showwarning("Advertencia", "No se ha seleccionado columna target")
            return
        
        # AquÃ­ puedes llamar a tu funciÃ³n de entrenamiento
        # Por ejemplo:
        result = messagebox.askyesno(
            "Entrenar modelo",
            f"Â¿Entrenar modelo con {len(self.selected_features)} features?\n\n"
            f"Target: {self.target_column}\n"
            f"Muestras: {len(self.df)}"
        )
        
        if result:
            # Guardar configuraciÃ³n temporal
            config_file = "temp_train_config.json"
            config = {
                'selected_features': list(self.selected_features),
                'target_column': self.target_column,
                'dataset_path': str(self.dataset_path)
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f)
            
            messagebox.showinfo(
                "ConfiguraciÃ³n lista",
                f"ConfiguraciÃ³n guardada en {config_file}\n\n"
                "Puedes usar esta configuraciÃ³n para entrenar tu modelo:\n"
                "python train_model.py --config temp_train_config.json"
            )


def main():
    """FunciÃ³n principal"""
    root = tk.Tk()
    app = FeatureSelectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()