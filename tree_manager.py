import os
from code_splitter import DEFAULT_IGNORE_DIRS

class TreeManager:
    def __init__(self, app, splitter):
        self.app = app
        self.splitter = splitter

    def populate_tree(self):
        for item in self.app.tree.get_children():
            self.app.tree.delete(item)
        self.insert_node("", self.app.target_directory)

    def insert_node(self, parent, path):
        try:
            entries = sorted(list(os.scandir(path)), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                rel_path = os.path.relpath(entry.path, self.app.target_directory)

                if entry.is_dir():
                    if entry.name in DEFAULT_IGNORE_DIRS:
                        continue
                    node = self.app.tree.insert(parent, "end", text=f"[ ] 📁 {entry.name}", open=False, values=(rel_path, "unchecked"))
                    self.insert_node(node, entry.path)
                else:
                    _, ext = os.path.splitext(entry.name)
                    if ext.lower() in self.splitter.ignore_extensions:
                        continue
                    self.app.tree.insert(parent, "end", text=f"[ ] 📄 {entry.name}", values=(rel_path, "unchecked"))
        except Exception:
            pass

    def on_tree_click(self, event):
        """Triggers checkbox changes on text clicks while preserving folding expansion markers."""
        item_id = self.app.tree.identify_row(event.y)
        if not item_id:
            return

        element = self.app.tree.identify_element(event.x, event.y)
        if element in ("text", "image"):
            values = self.app.tree.item(item_id, "values")
            if not values:
                return

            status = values[1]
            new_status = "checked" if status in ("unchecked", "partial") else "unchecked"

            self.set_node_status(item_id, new_status)
            self.update_parent_status(item_id)

    def set_node_status(self, item_id, status):
        values = self.app.tree.item(item_id, "values")
        if not values:
            return

        rel_path = values[0]
        display_text = self.app.tree.item(item_id, "text")

        clean_text = display_text[6:] if display_text.startswith(("[ ] ", "[X] ", "[-] ")) else display_text
        is_dir = "📁" in display_text or self.app.tree.get_children(item_id)

        if status == "checked":
            prefix = "[X] 📁 " if is_dir else "[X] 📄 "
        elif status == "partial":
            prefix = "[-] 📁 " if is_dir else "[-] 📄 "
        else:
            prefix = "[ ] 📁 " if is_dir else "[ ] 📄 "

        self.app.tree.item(item_id, text=f"{prefix}{clean_text}", values=(rel_path, status))

        for child in self.app.tree.get_children(item_id):
            self.set_node_status(child, status)

    def update_parent_status(self, item_id):
        parent_id = self.app.tree.parent(item_id)
        if not parent_id:
            return

        children = self.app.tree.get_children(parent_id)
        statuses = [self.app.tree.item(child, "values")[1] for child in children]

        if all(s == "checked" for s in statuses):
            new_status = "checked"
        elif all(s == "unchecked" for s in statuses):
            new_status = "unchecked"
        else:
            new_status = "partial"

        rel_path = self.app.tree.item(parent_id, "values")[0]
        display_text = self.app.tree.item(parent_id, "text")
        clean_text = display_text[6:] if display_text.startswith(("[ ] ", "[X] ", "[-] ")) else display_text

        prefix = "[X] 📁 " if new_status == "checked" else ("[-] 📁 " if new_status == "partial" else "[ ] 📁 ")

        self.app.tree.item(parent_id, text=f"{prefix}{clean_text}", values=(rel_path, new_status))
        self.update_parent_status(parent_id)

    def get_all_checked_files(self):
        checked_files = []

        def traverse(item_id):
            values = self.app.tree.item(item_id, "values")
            if values and values[1] == "checked":
                full_path = os.path.join(self.app.target_directory, values[0])
                if os.path.isfile(full_path):
                    checked_files.append(values[0])

            for child in self.app.tree.get_children(item_id):
                traverse(child)

        for root_item in self.app.tree.get_children():
            traverse(root_item)
        return checked_files
