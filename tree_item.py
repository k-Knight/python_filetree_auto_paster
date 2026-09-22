import os
from code_splitter import DEFAULT_IGNORE_DIRS

class TreeItem:
    def __init__(self, name, rel_path, is_dir, depth, parent=None):
        self.name = name
        self.rel_path = rel_path
        self.is_dir = is_dir
        self.depth = depth
        self.parent = parent
        self.is_expanded = False
        self.is_checked = False
        self.children = []
        self.has_scanned = False

        self.y_min = 0
        self.y_max = 0

    @staticmethod
    def scan_level(root_path, current_dir, target_list, depth, parent_node, ignore_extensions):
        """Scans a target sub-directory level and populates structural items."""
        try:
            full_path = os.path.join(root_path, current_dir) if current_dir else root_path
            entries = sorted(list(os.scandir(full_path)), key=lambda e: (not e.is_dir(), e.name.lower()))

            for entry in entries:
                rel_path = os.path.relpath(entry.path, root_path)
                if entry.is_dir():
                    if entry.name in DEFAULT_IGNORE_DIRS:
                        continue
                    item = TreeItem(entry.name, rel_path, is_dir=True, depth=depth, parent=parent_node)
                    target_list.append(item)
                else:
                    _, ext = os.path.splitext(entry.name)
                    if ext.lower() in ignore_extensions:
                        continue
                    item = TreeItem(entry.name, rel_path, is_dir=False, depth=depth, parent=parent_node)
                    target_list.append(item)
        except Exception:
            pass
