import tkinter as tk
from tkinter import ttk

def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    
    style.configure(".", font=("Segoe UI", 10))
    style.configure("Treeview", rowheight=24, font=("Segoe UI", 10))
    style.configure("TLabelframe", padding=10)
    style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), foreground="#2c3e50")
    style.configure("TButton", padding=5, font=("Segoe UI", 9, "bold"))