import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyperclip

from code_splitter import CodeSplitter
from gui_styles import apply_theme
from tree_manager import TreeManager
from macro_runner import MacroRunner

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codebase Splitter & Auto-Paster")
        self.geometry("800x650")
        
        apply_theme(self)
        
        self.splitter = CodeSplitter()
        self.chunks = []
        
        self.create_widgets()
        self.tree_manager = TreeManager(self.tree, self.splitter)
        self.macro_runner = MacroRunner(self.update_coord_label)

    def create_widgets(self):
        # 1. Target Directory Section
        dir_frame = ttk.LabelFrame(self, text=" 1. Select Codebase Directory ")
        dir_frame.pack(fill="x", padx=15, pady=8)
        
        self.dir_label = ttk.Label(dir_frame, text="No directory selected", foreground="#7f8c8d", wraplength=600)
        self.dir_label.pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Button(dir_frame, text="Browse...", command=self.browse_directory).pack(side="right")

        # 2. Project Tree Section
        tree_frame = ttk.LabelFrame(self, text=" 2. Select Files/Folders to Include ")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=8)

        self.tree = ttk.Treeview(tree_frame, selectmode="none", show="tree")
        self.tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill="y", side="right")
        
        self.tree.bind("<Button-1>", self.on_tree_click)

        # 3. Macro Automation Section
        paste_frame = ttk.LabelFrame(self, text=" 3. Target Window Automation (Optional) ")
        paste_frame.pack(fill="x", padx=15, pady=8)
        
        self.coords_label = ttk.Label(paste_frame, text="Target Cursor Position: Not Set", font=("Segoe UI", 9, "italic"))
        self.coords_label.pack(side="left", padx=5)
        
        ttk.Button(paste_frame, text="Pick Position (3s Delay)", command=self.start_coordinate_pick).pack(side="right")

        # 4. Global Action Controls
        control_frame = ttk.Frame(self, padding=5)
        control_frame.pack(fill="x", padx=15, pady=10)
        
        self.process_btn = ttk.Button(control_frame, text="⚡ Chunk Selected Files", command=self.process_files)
        self.process_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        self.autopaste_btn = ttk.Button(control_frame, text="🚀 Run Auto-Paste Macro", command=self.run_auto_paste, state="disabled")
        self.autopaste_btn.pack(side="right", padx=5, expand=True, fill="x")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_label.config(text=os.path.normpath(directory), foreground="#2c3e50")
            self.tree_manager.populate(directory)

    def on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        element = self.tree.identify_element(event.x, event.y)
        self.tree_manager.handle_click(item_id, element)

    def update_coord_label(self, text, color):
        self.coords_label.config(text=text, foreground=color)

    def start_coordinate_pick(self):
        self.coords_label.config(text="Get ready! Point your mouse target...", foreground="#e74c3c")
        self.update()
        self.macro_runner.start_coordinate_pick()

    def process_files(self):
        if not self.tree_manager.target_directory:
            messagebox.showerror("Error", "Please select a codebase directory first.")
            return
            
        selected_files = self.tree_manager.get_checked_files()
        if not selected_files:
            messagebox.showwarning("Warning", "No files selected to process.")
            return
            
        self.chunks = self.splitter.process_selected_files(self.tree_manager.target_directory, selected_files)
        
        if self.chunks:
            messagebox.showinfo("Success", f"Generated {len(self.chunks)} clipboard snippets successfully!")
            self.autopaste_btn.config(state="normal")
            pyperclip.copy(self.chunks[0])
        else:
            messagebox.showwarning("Notice", "No text content found in selected files.")
            self.autopaste_btn.config(state="disabled")

    def run_auto_paste(self):
        if not self.chunks:
            return
        if not self.macro_runner.target_coords:
            messagebox.showerror("Missing Information", "Please map a Window cursor position before running automation.")
            return
        self.macro_runner.run(self.chunks, self.autopaste_btn)