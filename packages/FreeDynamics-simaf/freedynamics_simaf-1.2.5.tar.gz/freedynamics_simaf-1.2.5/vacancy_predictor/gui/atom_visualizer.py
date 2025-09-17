"""
Visualizador 3D para estructuras atómicas de LAMMPS
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import matplotlib.colors as mcolors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)

class AtomVisualizer3D:
    """
    Visualizador 3D especializado para estructuras atómicas
    """
    
    def __init__(self):
        self.fig = None
        self.ax = None
        self.canvas = None
        self.current_data = None
        
        # Colores predefinidos para tipos de átomos
        self.atom_colors = {
            1: '#FF6B6B',  # Rojo
            2: '#4ECDC4',  # Verde azulado
            3: '#45B7D1',  # Azul
            4: '#FFA07A',  # Salmón
            5: '#98D8C8',  # Verde menta
            6: '#FFBE0B',  # Amarillo
            7: '#8B5CF6',  # Púrpura
            8: '#F97316',  # Naranja
            9: '#06D6A0',  # Verde esmeralda
            10: '#F72585', # Rosa fuerte
        }
        
        # Tamaños relativos para tipos de átomos (se pueden ajustar)
        self.atom_sizes = {
            1: 50,   # Pequeño
            2: 75,   # Mediano
            3: 100,  # Grande
            4: 60,
            5: 80,
            6: 70,
            7: 90,
            8: 55,
            9: 85,
            10: 65,
        }
    
    def create_3d_plot(self, parent_frame) -> Tuple[plt.Figure, FigureCanvasTkAgg]:
        """
        Crea el plot 3D en el frame especificado
        
        Args:
            parent_frame: Frame de tkinter donde se agregará el plot
            
        Returns:
            Tuple con la figura y el canvas
        """
        # Crear figura con fondo oscuro para mejor contraste
        self.fig = plt.figure(figsize=(10, 8), facecolor='white')
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Configurar estilo inicial
        self.ax.set_facecolor('white')
        self.ax.grid(True, alpha=0.3)
        
        # Crear canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Agregar toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, parent_frame)
        toolbar.update()
        
        # Mostrar mensaje inicial
        self._show_initial_message()
        
        return self.fig, self.canvas
    
    def _show_initial_message(self):
        """Muestra mensaje inicial en el plot"""
        self.ax.clear()
        self.ax.text(0.5, 0.5, 0.5, 'Carga un archivo .dump para visualizar átomos', 
                    fontsize=14, ha='center', va='center', 
                    transform=self.ax.transAxes)
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.canvas.draw()
    
    def plot_atoms(self, data: pd.DataFrame, metadata: Dict = None, 
                   selected_types: List[int] = None, show_box: bool = True,
                   atom_scale: float = 1.0) -> None:
        """
        Visualiza los átomos en 3D
        
        Args:
            data: DataFrame con datos de átomos
            metadata: Metadatos del archivo dump
            selected_types: Tipos de átomos a mostrar (None = todos)
            show_box: Si mostrar los límites de la caja de simulación
            atom_scale: Factor de escala para el tamaño de los átomos
        """
        if data is None or data.empty:
            self._show_initial_message()
            return
            
        try:
            self.current_data = data
            self.ax.clear()
            
            # Filtrar por tipos seleccionados
            if selected_types:
                plot_data = data[data['type'].isin(selected_types)]
            else:
                plot_data = data
            
            if plot_data.empty:
                self.ax.text(0.5, 0.5, 0.5, 'No hay átomos del tipo seleccionado', 
                           fontsize=12, ha='center', va='center', 
                           transform=self.ax.transAxes)
                self.canvas.draw()
                return
            
            # Extraer coordenadas
            x = plot_data['x'].values
            y = plot_data['y'].values
            z = plot_data['z'].values
            atom_types = plot_data['type'].values
            
            # Crear scatter plot por tipo de átomo
            unique_types = np.unique(atom_types)
            
            for atom_type in unique_types:
                mask = atom_types == atom_type
                x_type = x[mask]
                y_type = y[mask]
                z_type = z[mask]
                
                # Obtener color y tamaño
                color = self.atom_colors.get(atom_type, '#888888')
                size = self.atom_sizes.get(atom_type, 60) * atom_scale
                
                # Plot
                self.ax.scatter(x_type, y_type, z_type, 
                              c=color, s=size, alpha=0.8, 
                              label=f'Tipo {atom_type}', 
                              edgecolors='black', linewidth=0.5)
            
            # Configurar límites y etiquetas
            self._configure_plot_limits(x, y, z, metadata)
            self._configure_plot_appearance(metadata)
            
            # Mostrar caja de simulación
            if show_box and metadata:
                self._draw_simulation_box(metadata)
            
            # Agregar leyenda
            if len(unique_types) <= 10:  # Solo si no hay demasiados tipos
                self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # Actualizar canvas
            self.canvas.draw()
            
            logger.info(f"Visualización actualizada: {len(plot_data)} átomos de {len(unique_types)} tipos")
            
        except Exception as e:
            logger.error(f"Error en visualización: {str(e)}")
            messagebox.showerror("Error", f"Error al visualizar átomos:\n{str(e)}")
    
    def _configure_plot_limits(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, 
                              metadata: Dict = None):
        """Configura los límites del plot"""
        if len(x) == 0:
            return
            
        # Obtener rangos
        x_min, x_max = x.min(), x.max()
        y_min, y_max = y.min(), y.max()
        z_min, z_max = z.min(), z.max()
        
        # Agregar margen
        x_margin = (x_max - x_min) * 0.1
        y_margin = (y_max - y_min) * 0.1
        z_margin = (z_max - z_min) * 0.1
        
        self.ax.set_xlim(x_min - x_margin, x_max + x_margin)
        self.ax.set_ylim(y_min - y_margin, y_max + y_margin)
        self.ax.set_zlim(z_min - z_margin, z_max + z_margin)
    
    def _configure_plot_appearance(self, metadata: Dict = None):
        """Configura la apariencia del plot"""
        self.ax.set_xlabel('X (Å)', fontsize=12)
        self.ax.set_ylabel('Y (Å)', fontsize=12)
        self.ax.set_zlabel('Z (Å)', fontsize=12)
        
        if metadata:
            timestep = metadata.get('timestep', 0)
            num_atoms = metadata.get('num_atoms', 0)
            title = f'Estructura Atómica - Timestep: {timestep}, Átomos: {num_atoms}'
        else:
            title = 'Estructura Atómica'
            
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Hacer el plot más bonito
        self.ax.grid(True, alpha=0.3)
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        
        # Hacer las líneas de la grilla más sutiles
        self.ax.xaxis.pane.set_edgecolor('gray')
        self.ax.yaxis.pane.set_edgecolor('gray')
        self.ax.zaxis.pane.set_edgecolor('gray')
        self.ax.xaxis.pane.set_alpha(0.1)
        self.ax.yaxis.pane.set_alpha(0.1)
        self.ax.zaxis.pane.set_alpha(0.1)
    
    def _draw_simulation_box(self, metadata: Dict):
        """Dibuja los límites de la caja de simulación"""
        if 'box_bounds' not in metadata:
            return
            
        bounds = metadata['box_bounds']
        if len(bounds) < 3:
            return
            
        # Extraer límites
        x_min, x_max = bounds[0]
        y_min, y_max = bounds[1]
        z_min, z_max = bounds[2]
        
        # Definir vértices del cubo
        vertices = [
            [x_min, y_min, z_min], [x_max, y_min, z_min],
            [x_max, y_max, z_min], [x_min, y_max, z_min],
            [x_min, y_min, z_max], [x_max, y_min, z_max],
            [x_max, y_max, z_max], [x_min, y_max, z_max]
        ]
        
        # Definir aristas del cubo
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],  # Cara inferior
            [4, 5], [5, 6], [6, 7], [7, 4],  # Cara superior
            [0, 4], [1, 5], [2, 6], [3, 7]   # Aristas verticales
        ]
        
        # Dibujar aristas
        for edge in edges:
            points = np.array([vertices[edge[0]], vertices[edge[1]]])
            self.ax.plot3D(points[:, 0], points[:, 1], points[:, 2], 
                          'k--', alpha=0.6, linewidth=1)
    
    def update_view(self, elev: float = None, azim: float = None):
        """
        Actualiza el ángulo de vista
        
        Args:
            elev: Ángulo de elevación
            azim: Ángulo azimutal
        """
        if self.ax:
            if elev is not None:
                self.ax.view_init(elev=elev, azim=self.ax.azim)
            if azim is not None:
                self.ax.view_init(elev=self.ax.elev, azim=azim)
            self.canvas.draw()
    
    def save_plot(self, filename: str, dpi: int = 300):
        """
        Guarda el plot actual
        
        Args:
            filename: Nombre del archivo
            dpi: Resolución en puntos por pulgada
        """
        if self.fig:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                           facecolor='white', edgecolor='none')
    
    def reset(self):
        """Resetea el visualizador"""
        self.current_data = None
        if self.ax:
            self._show_initial_message()
    
    def get_atom_statistics(self) -> Dict:
        """Retorna estadísticas de los átomos visualizados"""
        if self.current_data is None or self.current_data.empty:
            return {}
            
        stats = {
            'total_atoms': len(self.current_data),
            'atom_types': self.current_data['type'].unique().tolist(),
            'atoms_by_type': self.current_data['type'].value_counts().to_dict(),
            'coordinate_ranges': {
                'x': (self.current_data['x'].min(), self.current_data['x'].max()),
                'y': (self.current_data['y'].min(), self.current_data['y'].max()),
                'z': (self.current_data['z'].min(), self.current_data['z'].max())
            }
        }
        
        return stats
    
    def set_atom_colors(self, color_mapping: Dict[int, str]):
        """
        Establece colores personalizados para tipos de átomos
        
        Args:
            color_mapping: Diccionario {tipo_atomo: color}
        """
        self.atom_colors.update(color_mapping)
    
    def set_atom_sizes(self, size_mapping: Dict[int, float]):
        """
        Establece tamaños personalizados para tipos de átomos
        
        Args:
            size_mapping: Diccionario {tipo_atomo: tamaño}
        """
        self.atom_sizes.update(size_mapping)