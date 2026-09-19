import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyperclip
import pyautogui

from code_splitter import CodeSplitter, DEFAULT_IGNORE_DIRS

class AppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codebase Splitter & Auto-Paster")
        self.geometry("750x600")
        
        self.splitter = CodeSplitter()
        self.target_directory = ""
        self.chunks = []
        self.target_coords = None
        
        self.file_checkboxes = {}
        self.create_widgets()

    def create_widgets(self):
        dir_frame = ttk.LabelFrame(self, text=" 1. Select Codebase Directory ", padding=10)
        dir_frame.pack(fill="x", padx=10, pady=5)
        
        self.dir_label = ttk.Label(dir_frame, text="No directory selected", foreground="gray")
        self.dir_label.pack(side="left", fill="x", expand=True, padx=5)
        
        browse_btn = ttk.Button(dir_frame, text="Browse...", command=self.browse_directory)
        browse_btn.pack(side="right")

        tree_frame = ttk.LabelFrame(self, text=" 2. Select Files/Folders to Include ", padding=10)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, selectmode="none")
        self.tree.heading("#0", text="Project Tree (Check items to include)", anchor="w")
        self.tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(fill="y", side="right")
        
        self.tree.bind("<Button-1>", self.on_tree_click)

        paste_frame = ttk.LabelFrame(self, text=" 3. Target Window Automation (Optional) ", padding=10)
        paste_frame.pack(fill="x", padx=10, pady=5)
        
        self.coords_label = ttk.Label(paste_frame, text="Target Cursor Position: Not Set")
        self.coords_label.pack(side="left", padx=5)
        
        pick_btn = ttk.Button(paste_frame, text="Pick Position (3s Delay)", command=self.start_coordinate_pick)
        pick_btn.pack(side="right")

        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.process_btn = ttk.Button(control_frame, text="⚡ Chunk Selected Files", command=self.process_files)
        self.process_btn.pack(side="left", padx=5)
        
        self.autopaste_btn = ttk.Button(control_frame, text="🚀 Run Auto-Paste Macro", command=self.run_auto_paste, state="disabled")
        self.autopaste_btn.pack(side="right", padx=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.target_directory = os.path.normpath(directory)
            self.dir_label.config(text=self.target_directory, foreground="black")
            self.populate_tree()

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.file_checkboxes.clear()
        
        self.insert_node("", self.target_directory)

    def insert_node(self, parent, path):
        try:
            for entry in os.scandir(path):
                rel_path = os.path.relpath(entry.path, self.target_directory)
                
                if entry.is_dir():
                    if entry.name in DEFAULT_IGNORE_DIRS:
                        continue
                    node = self.tree.insert(parent, "end", text=f"📁 {entry.name}", open=False, values=(rel_path, "unchecked"))
                    self.insert_node(node, entry.path)
                else:
                    _, ext = os.path.splitext(entry.name)
                    if ext.lower() in self.splitter.ignore_extensions:
                        continue
                    self.tree.insert(parent, "end", text=f"⬜ {entry.name}", values=(rel_path, "unchecked"))
        except Exception:
            pass

    def on_tree_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
            
        values = self.tree.item(item_id, "values")
        if not values:
            return
            
        rel_path, status = values[0], values[1]
        new_status = "checked" if status == "unchecked" else "unchecked"
        
        self.set_node_status(item_id, new_status)
        self.update_parent_status(item_id)

    def set_node_status(self, item_id, status):
        """Sets check status of node and matches all child nodes down the hierarchy."""
        display_text = self.tree.item(item_id, "text")
        clean_text = display_text[2:] if display_text[0] in ("⬛", "⬜", "📁") else display_text
        
        if self.tree.get_children(item_id):
            icon = "📁 "
        else:
            icon = "⬛ " if status == "checked" else "⬜ "
            
        rel_path = self.tree.item(item_id, "values")[0]
        self.tree.item(item_id, text=f"{icon}{clean_text}", values=(rel_path, status))
        
        for child in self.tree.get_children(item_id):
            self.set_node_status(child, status)

    def update_parent_status(self, item_id):
        parent_id = self.tree.parent(item_id)
        if not parent_id:
            return
        
        children = self.tree.get_children(parent_id)
        statuses = [self.tree.item(child, "values")[1] for child in children]
        
        if all(s == "checked" for s in statuses):
            new_status = "checked"
        else:
            new_status = "unchecked"
            
        rel_path = self.tree.item(parent_id, "values")[0]
        display_text = self.tree.item(parent_id, "text")[2:]
        self.tree.item(parent_id, text=f"📁 {display_text}", values=(rel_path, new_status))
        self.update_parent_status(parent_id)

    def get_all_checked_files(self):
        checked_files = []
        
        def traverse(item_id):
            values = self.tree.item(item_id, "values")
            if values and values[1] == "checked":
                full_path = os.path.join(self.target_directory, values[0])
                if os.path.isfile(full_path):
                    checked_files.append(values[0])
                    
            for child in self.tree.get_children(item_id):
                traverse(child)
                
        for root_item in self.tree.get_children():
            traverse(root_item)
        return checked_files

    def start_coordinate_pick(self):
        self.coords_label.config(text="Get ready! Point your mouse target...", foreground="red")
        self.update()
        threading.Thread(target=self.capture_mouse_position, daemon=True).start()

    def capture_mouse_position(self):
        time.sleep(3)
        x, y = pyautogui.position()
        self.target_coords = (x, y)
        self.coords_label.config(text=f"Target Coordinates Saved: X={x}, Y={y}", foreground="green")

    def process_files(self):
        if not self.target_directory:
            messagebox.showerror("Error", "Please select a codebase directory first.")
            return
            
        selected_files = self.get_all_checked_files()
        if not selected_files:
            messagebox.showwarning("Warning", "No files selected to process.")
            return
            
        self.chunks = self.splitter.process_selected_files(self.target_directory, selected_files)
        
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
        if not self.target_coords:
            messagebox.showerror("Missing Information", "Please map a Window cursor position before running automation.")
            return

        confirm = messagebox.askyesno("Confirm Auto-Run", "This will control your mouse and keyboard. Ready?")
        if confirm:
            threading.Thread(target=self.execute_paste_macro, daemon=True).start()

    def execute_paste_macro(self):
        self.autopaste_btn.config(state="disabled")
        try:
            pyautogui.click(self.target_coords[0], self.target_coords[1])
            time.sleep(0.5) 
            
            for index, snippet in enumerate(self.chunks):
                pyperclip.copy(snippet)
                pyautogui.hotkey('ctrl', 'v') 
                time.sleep(0.25)
                
                pyautogui.press('enter')
                
                time.sleep(1.0)
                
            messagebox.showinfo("Finished", "All codebase blocks automatically transferred!")
        except Exception as e:
            messagebox.showerror("Macro Interrupted", f"An error occurred: {e}")
        finally:
            self.autopaste_btn.config(state="normal")
