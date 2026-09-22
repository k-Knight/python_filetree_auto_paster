import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import gui_styles as styles
from tree_manager import TreeManager
from macro_runner import MacroRunner
from code_splitter import CodeSplitter

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codebase Splitter & Auto-Paster")
        self.geometry("800x650")

        styles.apply_modern_theme(self)

        self.splitter = CodeSplitter()
        self.target_directory = ""
        self.chunks = []

        self.tree_mgr = TreeManager(self, self.splitter)
        self.macro_runner = MacroRunner(self)

        self.create_widgets()

    def create_widgets(self):
        dir_frame = ttk.LabelFrame(self, text=" 1. Select Codebase Directory ")
        dir_frame.pack(fill="x", padx=15, pady=8)

        self.dir_label = ttk.Label(dir_frame, text="No directory selected", style="Muted.TLabel")
        self.dir_label.pack(side="left", fill="x", expand=True, padx=5)

        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory).pack(side="right")

        tree_frame = ttk.LabelFrame(self, text=" 2. Select Files/Folders to Include ")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=8)

        self.tree = ttk.Treeview(tree_frame, selectmode="none", show="tree")
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill="y", side="right")

        self.tree.bind("<Button-1>", self.tree_mgr.on_tree_click)

        paste_frame = ttk.LabelFrame(self, text=" 3. Target Window Automation (Optional) ")
        paste_frame.pack(fill="x", padx=15, pady=8)

        self.coords_label = ttk.Label(paste_frame, text="Target Cursor Position: Not Set", style="Muted.TLabel")
        self.coords_label.pack(side="left", padx=5)

        ttk.Button(paste_frame, text="Pick Position (3s Delay)", command=self.macro_runner.start_coordinate_pick).pack(side="right")

        control_frame = ttk.Frame(self, padding=5)
        control_frame.pack(fill="x", padx=15, pady=10)

        self.process_btn = ttk.Button(control_frame, text="⚡ Chunk Selected Files", command=self.process_files)
        self.process_btn.pack(side="left", padx=5, expand=True, fill="x")

        self.autopaste_btn = ttk.Button(control_frame, text="🚀 Run Auto-Paste Macro", command=self.macro_runner.run_auto_paste, state="disabled")
        self.autopaste_btn.pack(side="right", padx=5, expand=True, fill="x")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.target_directory = os.path.normpath(directory)
            self.dir_label.config(text=self.target_directory, font=(styles.FONT_FAMILY, 10), foreground=styles.TEXT_COLOR)
            self.tree_mgr.populate_tree()

    def process_files(self):
        if not self.target_directory:
            messagebox.showerror("Error", "Please select a codebase directory first.")
            return

        selected_files = self.tree_mgr.get_all_checked_files()
        if not selected_files:
            messagebox.showwarning("Warning", "No files selected to process.")
            return

        self.chunks = self.splitter.process_selected_files(self.target_directory, selected_files)

        if self.chunks:
            messagebox.showinfo("Success", f"Generated {len(self.chunks)} clipboard snippets successfully!")
            self.autopaste_btn.config(state="normal")
            import pyperclip
            pyperclip.copy(self.chunks[0])
        else:
            messagebox.showwarning("Notice", "No text content found in selected files.")
            self.autopaste_btn.config(state="disabled")
