import sys
import subprocess
import tkinter as tk
from tkinter import ttk
import site

REQUIRED_PACKAGES = ["customtkinter", "pyautogui", "pyperclip", "pillow"]

def install_dependencies():
    missing = []
    for pkg in REQUIRED_PACKAGES:
        import_name = "PIL" if pkg == "pillow" else pkg
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)

    if not missing:
        return

    root = tk.Tk()
    root.title("Setup")
    root.geometry("350x120")
    root.resizable(False, False)

    label = ttk.Label(root, text="Installing required dependencies...", font=("Segoe UI", 11))
    label.pack(pady=15)

    progress = ttk.Progressbar(root, mode="indeterminate", length=280)
    progress.pack(pady=5)
    progress.start(10)

    def run_installation():
        for pkg in missing:
            label.config(text=f"Installing {pkg}...")
            root.update()
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            except Exception as e:
                print(f"Failed to install {pkg}: {e}")

        importlib_reload = sys.modules.get('importlib')
        if importlib_reload:
            importlib_reload.invalidate_caches()

        for path in site.getusersitepackages():
            if path not in sys.path:
                sys.path.append(path)

        root.destroy()

    root.after(100, run_installation)
    root.mainloop()

install_dependencies()

from gui import AppGUI

def main():
    app = AppGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
