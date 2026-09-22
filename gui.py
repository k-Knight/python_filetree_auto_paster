import os
import customtkinter as ctk
from tkinter import filedialog
import gui_styles as styles
from code_splitter import CodeSplitter
from tree_manager import TreeManager
from macro_runner import MacroRunner

class AppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Code Splitter & Automation Macro")
        self.geometry("980x720")
        self.configure(fg_color=styles.BG_COLOR)

        self.splitter = CodeSplitter()
        self.macro = MacroRunner(self)

        self.target_directory = ""
        self.chunks = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_top_bar()
        self.create_main_content()
        self.create_bottom_bar()

        self.tree_manager = TreeManager(self, self.splitter, self.tree_scroll_frame)

    def create_top_bar(self):
        top_frame = ctk.CTkFrame(self, fg_color=styles.SURFACE_COLOR, height=60, corner_radius=8)
        top_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        top_frame.pack_propagate(False)

        self.dir_label = ctk.CTkLabel(
            top_frame, text="No Directory Selected",
            font=(styles.FONT_FAMILY, 13), text_color=styles.MUTED_TEXT
        )
        self.dir_label.pack(side="left", padx=15, fill="x", expand=True, anchor="w")

        browse_btn = ctk.CTkButton(
            top_frame, text="Browse Folder", font=(styles.FONT_FAMILY, 12, "bold"),
            fg_color=styles.ACCENT_COLOR, hover_color=styles.HOVER_COLOR,
            command=self.browse_folder
        )
        browse_btn.pack(side="right", padx=15)

    def _update_buffer_lbl(self, val):
        self.buffer_val_lbl.configure(text=f"{int(val)} ch")

    def create_main_content(self):
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        content_frame.grid_columnconfigure(0, weight=4)
        content_frame.grid_columnconfigure(1, weight=3)
        content_frame.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(content_frame, fg_color=styles.SURFACE_COLOR, corner_radius=8)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        tree_title = ctk.CTkLabel(
            left_frame, text="Project Workspace Files",
            font=(styles.FONT_FAMILY, 14, "bold"), text_color=styles.BRIGHT_HIGHLIGHT
        )
        tree_title.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self.tree_scroll_frame = ctk.CTkScrollableFrame(
            left_frame, fg_color=styles.BG_COLOR, corner_radius=6
        )
        self.tree_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        control_panel = ctk.CTkFrame(right_frame, fg_color=styles.SURFACE_COLOR, corner_radius=8)
        control_panel.grid(row=0, column=0, sticky="nsew")

        m_title = ctk.CTkLabel(control_panel, text="Automation Configuration", font=(styles.FONT_FAMILY, 14, "bold"), text_color=styles.BRIGHT_HIGHLIGHT)
        m_title.pack(anchor="w", padx=15, pady=10)

        map_btn = ctk.CTkButton(
            control_panel, text="Set Target Area", font=(styles.FONT_FAMILY, 12, "bold"),
            fg_color="#3e3e42", hover_color=styles.HOVER_COLOR,
            command=lambda: self.macro.start_coordinate_pick()
        )
        map_btn.pack(fill="x", padx=15, pady=5)

        self.coords_label = ctk.CTkLabel(
            control_panel, text="No coordinates mapped yet.",
            font=(styles.FONT_FAMILY, 12, "italic"), text_color=styles.MUTED_TEXT
        )
        self.coords_label.pack(anchor="w", padx=15, pady=(0, 15))

        t_title = ctk.CTkLabel(control_panel, text="Macro Delay Settings", font=(styles.FONT_FAMILY, 13, "bold"), text_color=styles.TEXT_COLOR)
        t_title.pack(anchor="w", padx=15, pady=(10, 5))

        paste_label_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        paste_label_frame.pack(fill="x", padx=15)
        ctk.CTkLabel(paste_label_frame, text="Paste Delay:", font=(styles.FONT_FAMILY, 11)).pack(side="left")
        self.paste_val_lbl = ctk.CTkLabel(paste_label_frame, text="0.25s", font=(styles.FONT_FAMILY, 11, "bold"), text_color=styles.BRIGHT_HIGHLIGHT)
        self.paste_val_lbl.pack(side="right")

        self.paste_delay_slider = ctk.CTkSlider(control_panel, from_=0.05, to=1.5, number_of_steps=29, command=self._update_paste_lbl)
        self.paste_delay_slider.set(0.25)
        self.paste_delay_slider.pack(fill="x", padx=15, pady=(2, 10))

        submit_label_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        submit_label_frame.pack(fill="x", padx=15)
        ctk.CTkLabel(submit_label_frame, text="Post-Submit Delay:", font=(styles.FONT_FAMILY, 11)).pack(side="left")
        self.submit_val_lbl = ctk.CTkLabel(submit_label_frame, text="1.50s", font=(styles.FONT_FAMILY, 11, "bold"), text_color=styles.BRIGHT_HIGHLIGHT)
        self.submit_val_lbl.pack(side="right")

        self.submit_delay_slider = ctk.CTkSlider(control_panel, from_=0.5, to=5.0, number_of_steps=45, command=self._update_submit_lbl)
        self.submit_delay_slider.set(1.50)
        self.submit_delay_slider.pack(fill="x", padx=15, pady=(2, 10))

        buffer_label_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
        buffer_label_frame.pack(fill="x", padx=15, pady=(10, 0))
        ctk.CTkLabel(buffer_label_frame, text="Max Chunk Buffer:", font=(styles.FONT_FAMILY, 11)).pack(side="left")
        self.buffer_val_lbl = ctk.CTkLabel(buffer_label_frame, text="8000 ch", font=(styles.FONT_FAMILY, 11, "bold"), text_color=styles.BRIGHT_HIGHLIGHT)
        self.buffer_val_lbl.pack(side="right")

        self.buffer_size_slider = ctk.CTkSlider(control_panel, from_=1000, to=32000, number_of_steps=31, command=self._update_buffer_lbl)
        self.buffer_size_slider.set(8000)
        self.buffer_size_slider.pack(fill="x", padx=15, pady=(2, 10))

        sep = ctk.CTkFrame(control_panel, height=2, fg_color="#333333")
        sep.pack(fill="x", padx=15, pady=15)

        p_title = ctk.CTkLabel(control_panel, text="Processing Status", font=(styles.FONT_FAMILY, 13, "bold"), text_color=styles.TEXT_COLOR)
        p_title.pack(anchor="w", padx=15, pady=(0, 5))

        self.stats_label = ctk.CTkLabel(
            control_panel, text="Selected Files: 0\nGenerated Chunks: 0",
            font=(styles.FONT_FAMILY, 13), justify="left"
        )
        self.stats_label.pack(anchor="w", padx=15, pady=5)

        self.progress_label = ctk.CTkLabel(
            control_panel, text="Macro Idle",
            font=(styles.FONT_FAMILY, 13, "bold"), text_color=styles.MUTED_TEXT, justify="left"
        )
        self.progress_label.pack(anchor="w", padx=15, pady=(5, 10))

    def _update_paste_lbl(self, val):
        self.paste_val_lbl.configure(text=f"{float(val):.2f}s")

    def _update_submit_lbl(self, val):
        self.submit_val_lbl.configure(text=f"{float(val):.2f}s")

    def create_bottom_bar(self):
        bottom_frame = ctk.CTkFrame(self, fg_color=styles.SURFACE_COLOR, height=60, corner_radius=8)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(5, 15))
        bottom_frame.pack_propagate(False)

        process_btn = ctk.CTkButton(
            bottom_frame, text="1. Process Snippets", font=(styles.FONT_FAMILY, 12, "bold"),
            fg_color="#2e7d32", hover_color="#1b5e20",
            command=self.process_selected_code
        )
        process_btn.pack(side="left", padx=15)

        self.autopaste_btn = ctk.CTkButton(
            bottom_frame, text="2. Execute Auto-Paste", font=(styles.FONT_FAMILY, 12, "bold"),
            fg_color=styles.ACCENT_COLOR, hover_color=styles.HOVER_COLOR,
            command=lambda: self.macro.run_auto_paste()
        )
        self.autopaste_btn.pack(side="right", padx=15)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_directory = os.path.normpath(folder)
            self.dir_label.configure(text=self.target_directory, text_color=styles.TEXT_COLOR)
            self.tree_manager.populate_tree()

    def process_selected_code(self):
        selected_files = self.tree_manager.get_all_checked_files()
        if not selected_files:
            self.stats_label.configure(text="Warning: No files selected to parse!", text_color=styles.ALERT_COLOR)
            return

        current_buffer = int(self.buffer_size_slider.get())

        self.chunks = self.splitter.process_selected_files(
            self.target_directory,
            selected_files,
            max_chars_override=current_buffer
        )

        self.stats_label.configure(
            text=f"Selected Files: {len(selected_files)}\nGenerated Chunks: {len(self.chunks)}",
            text_color=styles.SUCCESS_COLOR
        )
