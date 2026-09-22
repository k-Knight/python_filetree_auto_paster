import tkinter as tk
from tkinter import ttk

BG_COLOR = "#1e1e1e"
SURFACE_COLOR = "#252526"
TEXT_COLOR = "#d4d4d4"
ACCENT_COLOR = "#007acc"
HOVER_COLOR = "#3c3c3c"
MUTED_TEXT = "#808080"
SUCCESS_COLOR = "#4ec9b0"
ALERT_COLOR = "#f44336"

FONT_FAMILY = "Segoe UI"

def apply_modern_theme(root):
    """Configures a clean, modern dark UI styling scheme using ttk."""
    style = ttk.Style(root)
    style.theme_use("clam")

    root.configure(bg=BG_COLOR)
    style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR, font=(FONT_FAMILY, 10))

    style.configure("TLabelframe", background=BG_COLOR, bordercolor="#333333", borderwidth=1, relief="solid")
    style.configure("TLabelframe.Label", background=BG_COLOR, foreground=ACCENT_COLOR, font=(FONT_FAMILY, 10, "bold"))

    style.configure("Treeview",
                    background=SURFACE_COLOR,
                    fieldbackground=SURFACE_COLOR,
                    foreground=TEXT_COLOR,
                    rowheight=26,
                    borderwidth=0,
                    font=(FONT_FAMILY, 10))
    style.map("Treeview", background=[("selected", ACCENT_COLOR)], foreground=[("selected", "#ffffff")])

    style.configure("TButton",
                    background=SURFACE_COLOR,
                    foreground=TEXT_COLOR,
                    bordercolor="#3e3e42",
                    borderwidth=1,
                    relief="flat",
                    padding=(10, 5),
                    font=(FONT_FAMILY, 9, "bold"))

    style.map("TButton",
              background=[("active", HOVER_COLOR), ("disabled", BG_COLOR)],
              foreground=[("disabled", MUTED_TEXT)],
              bordercolor=[("disabled", "#2d2d30")])

    style.configure("Muted.TLabel", font=(FONT_FAMILY, 9, "italic"), foreground=MUTED_TEXT)
    style.configure("Main.TLabel", font=(FONT_FAMILY, 10), foreground=TEXT_COLOR)
