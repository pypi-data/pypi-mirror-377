


import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Dict
class DataInfoWidget:
    """Widget para mostrar información del dataset"""
    
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Información del Dataset", padding="10")
        self.info_text = scrolledtext.ScrolledText(self.frame, height=20, wrap='word')
        self.info_text.pack(fill="both", expand=True)
    
    def update_info(self, data_info: Dict):
        info_lines = [
            "INFORMACIÓN DEL DATASET",
            "=" * 40,
            f"Filas: {data_info.get('shape', (0, 0))[0]}",
            f"Columnas totales: {data_info.get('shape', (0, 0))[1]}",
            f"Columnas numéricas: {data_info.get('numeric_columns', 0)}",
            f"Columnas de texto: {data_info.get('text_columns', 0)}",
            f"Uso de memoria: {data_info.get('memory_usage', 0) / 1024 / 1024:.2f} MB"
        ]
        
        if data_info.get('file_path'):
            info_lines.append(f"Archivo: {data_info['file_path']}")
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "\n".join(info_lines))
    
    def clear(self):
        self.info_text.delete(1.0, tk.END)
