


import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
class ModelVisualizationWidget:
    """Widget para visualizaciones del modelo"""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        
        # Control frame
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="Actualizar Gráficos", 
                  command=self.update_plots).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Guardar Gráficos", 
                  command=self.save_plots).pack(side="left", padx=5)
        
        # Plots frame
        self.plots_frame = ttk.Frame(self.frame)
        self.plots_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.fig, self.axes = plt.subplots(2, 3, figsize=(18, 12))
        self.fig.tight_layout(pad=3.0)
        
        self.canvas = FigureCanvasTkAgg(self.fig, self.plots_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Data for plotting
        self.training_results = None
        self.feature_importance = None
    
    def on_model_changed(self, model: Any, feature_importance: pd.DataFrame = None):
        self.feature_importance = feature_importance
        # Los resultados de entrenamiento se actualizarán por separado
    
    def update_training_results(self, results: Dict):
        self.training_results = results
        self.update_plots()
    
    def update_plots(self):
        if self.training_results is None:
            self.clear_plots()
            return
        
        try:
            for ax in self.axes.flat:
                ax.clear()
            
            results = self.training_results
            y_test = results['y_test']
            test_predictions = results['test_predictions']
            
            # 1. Predicciones vs Valores Reales
            ax1 = self.axes[0, 0]
            ax1.scatter(y_test, test_predictions, alpha=0.6, color='red', s=50)
            
            min_val = min(y_test.min(), test_predictions.min())
            max_val = max(y_test.max(), test_predictions.max())
            ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Predicción perfecta')
            
            ax1.set_xlabel('Valores Reales')
            ax1.set_ylabel('Predicciones')
            ax1.set_title('Predicciones vs Valores Reales')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Métricas en el gráfico
            ax1.text(0.05, 0.95, f'R² = {results["test_r2"]:.3f}\nMAE = {results["test_mae"]:.3f}', 
                    transform=ax1.transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                    verticalalignment='top')
            
            # 2. Residuos
            ax2 = self.axes[0, 1]
            residuals = y_test - test_predictions
            ax2.scatter(test_predictions, residuals, alpha=0.6, color='blue', s=50)
            ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
            ax2.set_xlabel('Predicciones')
            ax2.set_ylabel('Residuos')
            ax2.set_title('Análisis de Residuos')
            ax2.grid(True, alpha=0.3)
            
            # 3. Feature Importance
            if self.feature_importance is not None:
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
            ax4.hist(residuals, bins=20, alpha=0.7, color='green', edgecolor='black')
            ax4.axvline(x=0, color='red', linestyle='--', linewidth=2)
            ax4.set_xlabel('Residuos')
            ax4.set_ylabel('Frecuencia')
            ax4.set_title('Distribución de Residuos')
            ax4.grid(True, alpha=0.3)
            
            # 5. Errores por Muestra
            ax5 = self.axes[1, 1]
            abs_errors = np.abs(residuals)
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

MAE: {results['test_mae']:.4f}
RMSE: {results['test_rmse']:.4f}
R²: {results['test_r2']:.4f}

Muestras: {results['test_samples']}
Error máximo: {np.max(abs_errors):.2f}
Error promedio: {np.mean(abs_errors):.2f}

CV R²: {results['cv_r2_mean']:.3f} ± {results['cv_r2_std']:.3f}
CV MAE: {results['cv_mae_mean']:.3f} ± {results['cv_mae_std']:.3f}"""
            
            ax6.text(0.1, 0.9, metrics_text, transform=ax6.transAxes, fontsize=10,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                    verticalalignment='top', fontfamily='monospace')
            
            self.fig.tight_layout(pad=2.0)
            self.canvas.draw()
            
        except Exception as e:
            print(f"[ERROR] Error actualizando gráficos: {e}")
    
    def clear_plots(self):
        for ax in self.axes.flat:
            ax.clear()
            ax.text(0.5, 0.5, 'Entrena un modelo\npara ver gráficos', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
        self.canvas.draw()
    
    def save_plots(self):
        if self.training_results is None:
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
