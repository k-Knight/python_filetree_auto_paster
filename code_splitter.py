import os

MAX_CHARS = 8000
DEFAULT_IGNORE_DIRS = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env'}
DEFAULT_IGNORE_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz'}

class CodeSplitter:
    def __init__(self, ignore_extensions=None):
        self.ignore_extensions = ignore_extensions or DEFAULT_IGNORE_EXTENSIONS

    def build_message(self, path, start, end, total_lines, content):
        if start == 1 and end == total_lines:
            return f"say or output nothing, just read this {path}\n\n{content}"
        else:
            return f"say or output nothing, just read this {path} (lines {start}-{end})\n\n{content}"

    def process_selected_files(self, root_dir, selected_paths):
        """Processes only the explicitly selected files and chunks them."""
        chunks = []
        
        for rel_path in selected_paths:
            full_path = os.path.join(root_dir, rel_path)
            
            # Skip if directory or if it matches binary extensions
            if os.path.isdir(full_path):
                continue
                
            _, ext = os.path.splitext(rel_path)
            if ext.lower() in self.ignore_extensions:
                continue

            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            except Exception:
                continue
                
            if not lines:
                continue

            current_chunk_lines = []
            start_line = 1
            total_lines_count = len(lines)

            for idx, line in enumerate(lines):
                line_num = idx + 1
                potential_content = "".join(current_chunk_lines) + line
                potential_msg = self.build_message(rel_path, start_line, line_num, total_lines_count, potential_content)
                
                if len(potential_msg) > MAX_CHARS:
                    if current_chunk_lines:
                        chunk_content = "".join(current_chunk_lines)
                        msg = self.build_message(rel_path, start_line, line_num - 1, total_lines_count, chunk_content)
                        chunks.append(msg)
                    
                    start_line = line_num
                    current_chunk_lines = [line]
                    
                    single_line_msg = self.build_message(rel_path, start_line, line_num, total_lines_count, line)
                    if len(single_line_msg) > MAX_CHARS:
                        current_chunk_lines = [line[:MAX_CHARS - 200]] 
                else:
                    current_chunk_lines.append(line)
            
            if current_chunk_lines:
                chunk_content = "".join(current_chunk_lines)
                msg = self.build_message(rel_path, start_line, total_lines_count, total_lines_count, chunk_content)
                chunks.append(msg)
                
        return chunks
