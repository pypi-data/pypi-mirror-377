"""
Tab especializado para carga y visualización de archivos LAMMPS dump
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Callable
import logging
from vacancy_predictor.utils.atom_visualizer import AtomVisualizer3D

logger = logging.getLogger(__name__)

class LAMMPSTab:
    """Tab especializado para carga y visualización de archivos LAMMPS dump"""
    
    def __init__(self, parent, data_loaded_callback: Callable):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        
        # Componentes especializados
        self.lammps_parser = LAMMPSTab()
        self.visualizer = AtomVisualizer3D()
        
        self.frame = ttk.Frame(parent)
        
        # Variables
        self.file_path_var = tk.StringVar()
        self.current_data = None
        self.current_metadata = None
        
        # Variables para controles de visualización
        self.show_box_var = tk.BooleanVar(value=True)
        self.atom_scale_var = tk.DoubleVar(value=1.0)
        self.selected_atom_types = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the LAMMPS tab"""
        main_container = ttk.Frame(self.frame, padding="10")
        main_container.pack(fill="both", expand=True)
        
        # Crear estructura con paneles
        self.create_left_panel(main_container)
        self.create_right_panel(main_container)
    
    def create_left_panel(self, parent):
        """Crear panel izquierdo con controles"""
        left_panel = ttk.Frame(parent)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        
        # Sección de carga de archivos
        self.create_file_section(left_panel)
        
        # Sección de información
        self.create_info_section(left_panel)
        
        # Sección de controles de visualización
        self.create_visualization_controls(left_panel)
    
    def create_right_panel(self, parent):
        """Crear panel derecho con visualización"""
        right_panel = ttk.Frame(parent)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Frame para la visualización 3D
        viz_frame = ttk.LabelFrame(right_panel, text="Visualización 3D", padding="10")
        viz_frame.pack(fill="both", expand=True)
        
        # Crear el visualizador 3D
        self.visualizer.create_3d_plot(viz_frame)
    
    def create_file_section(self, parent):
        """Create file loading section"""
        file_frame = ttk.LabelFrame(parent, text="Cargar Archivo LAMMPS", padding="10")
        file_frame.pack(fill="x", pady=(0, 10))
        
        path_frame = ttk.Frame(file_frame)
        path_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(path_frame, text="Archivo:").pack(anchor="w")
        
        file_entry = ttk.Entry(path_frame, textvariable=self.file_path_var, 
                              state="readonly", width=40)
        file_entry.pack(fill="x", pady=(5, 0))
        
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Seleccionar .dump", 
                  command=self.browse_file).pack(side="left")
        
        ttk.Button(btn_frame, text="Cargar Datos", 
                  command=self.load_data).pack(side="left", padx=(10, 0))
        
        info_label = ttk.Label(file_frame, 
                              text="Solo archivos LAMMPS .dump", 
                              font=("Arial", 8), foreground="gray")
        info_label.pack(anchor="w", pady=(5, 0))
    
    def create_info_section(self, parent):
        """Create data information section"""
        info_frame = ttk.LabelFrame(parent, text="Información del Sistema", padding="10")
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.info_text = tk.Text(info_frame, height=8, wrap="word", 
                               state="disabled", font=("Courier", 9))
        self.info_text.pack(fill="x")
    
    def create_visualization_controls(self, parent):
        """Crear controles de visualización"""
        controls_frame = ttk.LabelFrame(parent, text="Controles de Visualización", padding="10")
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Checkbox para mostrar caja de simulación
        ttk.Checkbutton(controls_frame, text="Mostrar límites de caja", 
                       variable=self.show_box_var,
                       command=self.update_visualization).pack(anchor="w")
        
        # Control de escala de átomos
        scale_frame = ttk.Frame(controls_frame)
        scale_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(scale_frame, text="Escala de átomos:").pack(anchor="w")
        
        scale_control = ttk.Scale(scale_frame, from_=0.1, to=3.0, 
                                 variable=self.atom_scale_var,
                                 orient="horizontal",
                                 command=self.on_scale_change)
        scale_control.pack(fill="x", pady=(5, 0))
        
        self.scale_label = ttk.Label(scale_frame, text="1.0x")
        self.scale_label.pack(anchor="w")
        
        # Frame para selección de tipos de átomos
        types_frame = ttk.Frame(controls_frame)
        types_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(types_frame, text="Tipos de átomos:").pack(anchor="w")
        
        # Listbox para tipos de átomos
        self.types_listbox = tk.Listbox(types_frame, selectmode="multiple", height=4)
        self.types_listbox.pack(fill="x", pady=(5, 0))
        self.types_listbox.bind('<<ListboxSelect>>', self.on_atom_type_select)
        
        # Botones para selección
        types_btn_frame = ttk.Frame(types_frame)
        types_btn_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Button(types_btn_frame, text="Todos", 
                  command=self.select_all_atom_types).pack(side="left")
        ttk.Button(types_btn_frame, text="Ninguno", 
                  command=self.clear_atom_types).pack(side="left", padx=(5, 0))
        
        # Botón para actualizar visualización
        ttk.Button(controls_frame, text="Actualizar Vista", 
                  command=self.update_visualization).pack(fill="x", pady=(10, 0))
        
        # Botón para exportar
        ttk.Button(controls_frame, text="Exportar CSV", 
                  command=self.export_current_frame).pack(fill="x", pady=(5, 0))
    
    def browse_file(self):
        """Abrir diálogo para seleccionar archivo"""
        file_types = [
            ("LAMMPS dump files", "*.dump"),
            ("All files", "*.*")
        ]
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo LAMMPS dump", 
            filetypes=file_types
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def load_data(self):
        """Cargar datos desde archivo LAMMPS dump"""
        file_path = self.file_path_var.get()
        
        if not file_path:
            messagebox.showwarning("Advertencia", "Por favor selecciona un archivo primero")
            return
        
        if not Path(file_path).exists():
            messagebox.showerror("Error", "Archivo no encontrado")
            return
        
        # Verificar extensión
        if not file_path.lower().endswith('.dump'):
            messagebox.showerror("Error", "Solo se pueden cargar archivos .dump de LAMMPS")
            return
        
        try:
            # Mostrar cursor de espera
            self.frame.config(cursor="wait")
            self.frame.update()
            
            # Cargar datos usando el parser LAMMPS
            self.current_data = self.lammps_parser.parse_dump_file(file_path)
            self.current_metadata = self.lammps_parser.metadata
            
            # Actualizar displays
            self.update_atom_types_list()
            self.refresh_data_info()
            self.update_visualization()
            
            # Notificar al callback principal
            self.data_loaded_callback(self.current_data)
            
            # Mostrar mensaje de éxito
            summary = self.lammps_parser.get_summary()
            message = (f"Datos cargados exitosamente!\n\n"
                      f"Timestep: {summary.get('timestep', 'N/A')}\n"
                      f"Átomos: {summary.get('num_atoms', 0)}\n"
                      f"Tipos de átomos: {summary.get('num_atom_types', 0)}\n"
                      f"Timesteps totales: {summary.get('total_timesteps', 1)}")
            
            messagebox.showinfo("Éxito", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo:\n{str(e)}")
            logger.error(f"Error loading LAMMPS data: {str(e)}")
        finally:
            # Restaurar cursor normal
            self.frame.config(cursor="")
    
    def update_atom_types_list(self):
        """Actualizar lista de tipos de átomos"""
        if self.current_data is None:
            return
            
        atom_types = self.lammps_parser.get_atom_types()
        
        # Limpiar listbox
        self.types_listbox.delete(0, tk.END)
        
        # Agregar tipos
        for atom_type in atom_types:
            count = len(self.current_data[self.current_data['type'] == atom_type])
            self.types_listbox.insert(tk.END, f"Tipo {atom_type} ({count} átomos)")
        
        # Seleccionar todos por defecto
        self.select_all_atom_types()
    
    def on_scale_change(self, value):
        """Callback para cambio de escala"""
        scale_value = float(value)
        self.scale_label.config(text=f"{scale_value:.1f}x")
        # Actualizar visualización en tiempo real
        self.update_visualization()
    
    def on_atom_type_select(self, event):
        """Callback para selección de tipos de átomos"""
        selected_indices = self.types_listbox.curselection()
        atom_types = self.lammps_parser.get_atom_types()
        
        if selected_indices:
            self.selected_atom_types = [atom_types[i] for i in selected_indices]
        else:
            self.selected_atom_types = []
        
        # Actualizar visualización
        self.update_visualization()
    
    def select_all_atom_types(self):
        """Seleccionar todos los tipos de átomos"""
        self.types_listbox.selection_set(0, tk.END)
        self.selected_atom_types = self.lammps_parser.get_atom_types()
        self.update_visualization()
    
    def clear_atom_types(self):
        """Deseleccionar todos los tipos de átomos"""
        self.types_listbox.selection_clear(0, tk.END)
        self.selected_atom_types = []
        self.update_visualization()
    
    def update_visualization(self):
        """Actualizar la visualización 3D"""
        if self.current_data is None:
            return
            
        try:
            self.visualizer.plot_atoms(
                data=self.current_data,
                metadata=self.current_metadata,
                selected_types=self.selected_atom_types if self.selected_atom_types else None,
                show_box=self.show_box_var.get(),
                atom_scale=self.atom_scale_var.get()
            )
        except Exception as e:
            logger.error(f"Error updating visualization: {str(e)}")
            messagebox.showerror("Error", f"Error al actualizar visualización:\n{str(e)}")
    
    def refresh_data_info(self):
        """Actualizar información del sistema"""
        if self.current_data is None:
            info_text = "No hay datos cargados"
        else:
            summary = self.lammps_parser.get_summary()
            box_dims = summary.get('box_dimensions', {})
            coord_ranges = summary.get('coordinate_ranges', {})
            
            info_lines = [
                f"INFORMACIÓN DEL SISTEMA LAMMPS",
                f"=" * 35,
                f"Timestep actual: {summary.get('timestep', 'N/A')}",
                f"Total timesteps: {summary.get('total_timesteps', 1)}",
                f"Número de átomos: {summary.get('num_atoms', 0)}",
                f"Tipos de átomos: {summary.get('num_atom_types', 0)}",
                "",
                f"DIMENSIONES DE LA CAJA:",
                f"X: {box_dims.get('x', (0, 0))[0]:.3f} - {box_dims.get('x', (0, 0))[1]:.3f}",
                f"Y: {box_dims.get('y', (0, 0))[0]:.3f} - {box_dims.get('y', (0, 0))[1]:.3f}",
                f"Z: {box_dims.get('z', (0, 0))[0]:.3f} - {box_dims.get('z', (0, 0))[1]:.3f}",
                "",
                f"RANGO DE COORDENADAS:",
                f"X: {coord_ranges.get('x', (0, 0))[0]:.3f} - {coord_ranges.get('x', (0, 0))[1]:.3f}",
                f"Y: {coord_ranges.get('y', (0, 0))[0]:.3f} - {coord_ranges.get('y', (0, 0))[1]:.3f}",
                f"Z: {coord_ranges.get('z', (0, 0))[0]:.3f} - {coord_ranges.get('z', (0, 0))[1]:.3f}",
            ]
            
            info_text = "\n".join(info_lines)
        
        # Actualizar widget de texto
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state="disabled")
    
    def export_current_frame(self):
        """Exportar frame actual como CSV"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "No hay datos para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar como CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.current_data.to_csv(file_path, index=False)
                messagebox.showinfo("Éxito", f"Datos exportados a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")
    
    def save_visualization(self):
        """Guardar visualización actual"""
        if self.current_data is None:
            messagebox.showwarning("Advertencia", "No hay visualización para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar visualización",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.visualizer.save_plot(file_path)
                messagebox.showinfo("Éxito", f"Visualización guardada en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
    
    def reset(self):
        """Reset del tab"""
        self.file_path_var.set("")
        self.current_data = None
        self.current_metadata = None
        self.selected_atom_types = []
        
        # Limpiar displays
        self.types_listbox.delete(0, tk.END)
        
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "No hay datos cargados")
        self.info_text.config(state="disabled")
        
        # Reset visualizador
        self.visualizer.reset()
        
        # Reset controles
        self.show_box_var.set(True)
        self.atom_scale_var.set(1.0)
        self.scale_label.config(text="1.0x")