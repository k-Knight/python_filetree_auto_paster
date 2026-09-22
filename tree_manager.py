import customtkinter as ctk
import gui_styles as styles
from tree_item import TreeItem
from PIL import Image, ImageTk, ImageDraw

class TreeManager:
    def __init__(self, app, splitter, container_frame):
        self.app = app
        self.splitter = splitter
        self.container = container_frame

        self.canvas = ctk.CTkCanvas(self.container, bg=styles.BG_COLOR, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.root_items = []
        self.visible_flattened_items = []
        self.row_height = 28

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def populate_tree(self):
        self.root_items.clear()
        if not self.app.target_directory:
            self._redraw_canvas()
            return

        TreeItem.scan_level(
            self.app.target_directory, "", self.root_items,
            depth=0, parent_node=None, ignore_extensions=self.splitter.ignore_extensions
        )
        self.refresh_tree_layout()

    def refresh_tree_layout(self):
        self.visible_flattened_items.clear()

        def build_flat_list(item_list):
            for item in item_list:
                self.visible_flattened_items.append(item)
                if item.is_dir and item.is_expanded:
                    if not item.has_scanned:
                        TreeItem.scan_level(
                            self.app.target_directory, item.rel_path, item.children,
                            depth=item.depth + 1, parent_node=item, ignore_extensions=self.splitter.ignore_extensions
                        )
                        item.has_scanned = True
                    build_flat_list(item.children)

        build_flat_list(self.root_items)
        self._redraw_canvas()

    def draw_vector_rounded_rect(self, x1, y1, x2, y2, radius=4, fill_color="", outline_color="", width=1):
        """Generates a perfectly anti-aliased rounded shape using Pillow memory buffers."""

        w = int(x2 - x1)
        h = int(y1 - y1)
        w = int(w) if w > 0 else 16
        h = int(y2 - y1) if (y2 - y1) > 0 else 16

        scale = 4
        sw, sh = w * scale, h * scale
        sradius = radius * scale
        swidth = width * scale

        img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        box = [0, 0, sw - 1, sh - 1]

        s_fill = fill_color if fill_color else None
        s_out = outline_color if outline_color else None

        draw.rounded_rectangle(
            box,
            radius=sradius,
            fill=s_fill,
            outline=s_out,
            width=swidth if s_out else 0
        )

        img = img.resize((w, h), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(img)

        if not hasattr(self, '_img_cache'):
            self._img_cache = []
        self._img_cache.append(tk_img)

        self.canvas.create_image(x1, y1, image=tk_img, anchor="nw")

    def _draw_tree_guides(self, item, indent, mid_y, y_pos):
        if item.depth <= 0:
            return
        line_x_start = (item.depth - 1) * 22 + 11
        line_x_end = indent + 6

        self.canvas.create_line(line_x_start, mid_y, line_x_end, mid_y, fill="#3a3a3a", width=1, dash=(2, 2))

        parent_y = 0
        if hasattr(item, 'parent') and item.parent in self.visible_flattened_items:
            parent_idx = self.visible_flattened_items.index(item.parent)
            parent_y = (parent_idx * self.row_height) + 20
        else:
            parent_y = max(0, mid_y - self.row_height)

        self.canvas.create_line(line_x_start, parent_y, line_x_start, mid_y, fill="#3a3a3a", width=1, dash=(2, 2))

    def _redraw_canvas(self):
        """Clears the view, resets the image buffer cache, and renders the modern workspace tree."""
        self.canvas.delete("all")
        if hasattr(self, '_img_cache'):
            self._img_cache.clear()
        else:
            self._img_cache = []

        total_items = len(self.visible_flattened_items)
        needed_height = total_items * self.row_height

        self.canvas.configure(height=max(needed_height, 400))
        self.canvas.config(scrollregion=(0, 0, 600, needed_height))

        for idx, item in enumerate(self.visible_flattened_items):
            y_pos = idx * self.row_height
            item.y_min, item.y_max = y_pos, y_pos + self.row_height
            indent, mid_y = item.depth * 22, y_pos + 14

            self._draw_tree_guides(item, indent, mid_y, y_pos)

            if item.is_dir:
                arrow = "▼" if item.is_expanded else "▶"
                self.canvas.create_text(
                    indent + 11, mid_y, text=arrow,
                    fill=styles.MUTED_TEXT, font=(styles.FONT_FAMILY, 9, "bold"),
                    anchor="center"
                )

            self.draw_vector_rounded_rect(
                x1=indent + 24, y1=y_pos + 6, x2=indent + 40, y2=y_pos + 22,
                radius=4, fill_color=styles.SURFACE_COLOR, outline_color="#555555", width=2
            )

            if item.is_checked:
                self.draw_vector_rounded_rect(
                    x1=indent + 27, y1=y_pos + 9, x2=indent + 37, y2=y_pos + 19,
                    radius=2, fill_color=styles.BRIGHT_HIGHLIGHT, outline_color="", width=0
                )
            elif getattr(item, 'is_partial', False):
                self.draw_vector_rounded_rect(
                    x1=indent + 28, y1=y_pos + 13, x2=indent + 36, y2=y_pos + 15,
                    radius=1, fill_color=styles.BRIGHT_HIGHLIGHT, outline_color="", width=0
                )

            text_x = indent + 48
            icon = "📁 " if item.is_dir else "📄 "
            full_label = f"{icon} {item.name}"
            color = styles.BRIGHT_HIGHLIGHT if item.is_dir else styles.TEXT_COLOR
            weight = "bold" if item.is_dir else "normal"

            self.canvas.create_text(
                text_x, mid_y, text=full_label,
                fill=color, font=(styles.FONT_FAMILY, 11, weight),
                anchor="w"
            )

    def on_canvas_click(self, event):
        canvas_y = self.canvas.canvasy(event.y)
        canvas_x = event.x

        target_item = next((item for item in self.visible_flattened_items if item.y_min <= canvas_y <= item.y_max), None)
        if not target_item:
            return

        indent = target_item.depth * 22

        if target_item.is_dir and canvas_x < (indent + 20):
            target_item.is_expanded = not target_item.is_expanded
            self.refresh_tree_layout()
        else:
            if getattr(target_item, 'is_partial', False) or target_item.is_checked:
                new_state = False
            else:
                new_state = True

            target_item.is_checked = new_state
            target_item.is_partial = False

            if target_item.is_dir:
                self._cascade_check_downwards(target_item, new_state)

            self._update_parent_states_upwards()
            self._redraw_canvas()

    def _cascade_check_downwards(self, item, state):
        item.is_checked = state
        item.is_partial = False
        if item.is_dir:
            if not item.has_scanned:
                TreeItem.scan_level(self.app.target_directory, item.rel_path, item.children, item.depth + 1, parent_node=item, ignore_extensions=self.splitter.ignore_extensions)
                item.has_scanned = True
            for child in item.children:
                self._cascade_check_downwards(child, state)

    def _update_parent_states_upwards(self):
        """Walks from the deepest structural children elements upwards to assign partial folder markers."""
        all_items = []
        def collect(item_list):
            for item in item_list:
                all_items.append(item)
                if item.children:
                    collect(item.children)
        collect(self.root_items)

        sorted_items = sorted(all_items, key=lambda x: x.depth, reverse=True)

        for item in sorted_items:
            if not item.is_dir or not item.children:
                continue

            child_checked = [c.is_checked for c in item.children]
            child_partial = [getattr(c, 'is_partial', False) for c in item.children]

            if all(child_checked):
                item.is_checked = True
                item.is_partial = False
            elif not any(child_checked) and not any(child_partial):
                item.is_checked = False
                item.is_partial = False
            else:
                item.is_checked = False
                item.is_partial = True

    def _cascade_check(self, item, state):
        item.is_checked = state
        if item.is_dir:
            if not item.has_scanned:
                TreeItem.scan_level(self.app.target_directory, item.rel_path, item.children, item.depth + 1, parent_node=item, ignore_extensions=self.splitter.ignore_extensions)
                item.has_scanned = True
            for child in item.children:
                self._cascade_check(child, state)

    def get_all_checked_files(self):
        checked_files = []
        def collect(item_list):
            for item in item_list:
                if not item.is_dir and item.is_checked:
                    checked_files.append(item.rel_path)
                if item.children:
                    collect(item.children)
        collect(self.root_items)
        return checked_files
