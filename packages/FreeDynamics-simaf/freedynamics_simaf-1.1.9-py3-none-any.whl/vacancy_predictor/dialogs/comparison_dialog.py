import tkinter as tk
from tkinter import ttk

class ComparisonDialog:
    def __init__(self, parent, training_data, model_trainer):
        self.parent = parent
        self.training_data = training_data
        self.model_trainer = model_trainer
        self.dialog = None
    
    def show(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Model Comparison")
        self.dialog.geometry("600x400")
        
        # Contenido básico del diálogo
        label = tk.Label(self.dialog, text="Model Comparison Dialog")
        label.pack(pady=20)
        
        close_button = tk.Button(self.dialog, text="Close", command=self.dialog.destroy)
        close_button.pack(pady=10)
        
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
