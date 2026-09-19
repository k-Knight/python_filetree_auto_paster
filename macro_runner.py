import time
import threading
import pyperclip
import pyautogui
from tkinter import messagebox

class MacroRunner:
    def __init__(self, ui_update_callback):
        self.target_coords = None
        self.ui_update_callback = ui_update_callback

    def start_coordinate_pick(self):
        threading.Thread(target=self._capture_mouse_position, daemon=True).start()

    def _capture_mouse_position(self):
        time.sleep(3)
        x, y = pyautogui.position()
        self.target_coords = (x, y)
        self.ui_update_callback(f"Target Coordinates Saved: X={x}, Y={y}", "#27ae60")

    def run(self, chunks, button_to_toggle):
        confirm = messagebox.askyesno("Confirm Auto-Run", "This will control your mouse and keyboard. Ready?")
        if confirm:
            threading.Thread(target=self._execute, args=(chunks, button_to_toggle), daemon=True).start()

    def _execute(self, chunks, button_to_toggle):
        button_to_toggle.config(state="disabled")
        try:
            pyautogui.click(self.target_coords[0], self.target_coords[1])
            time.sleep(0.5) 
            
            for snippet in chunks:
                pyperclip.copy(snippet)
                pyautogui.hotkey('ctrl', 'v') 
                time.sleep(0.25)
                pyautogui.press('enter')
                time.sleep(1.0)
                
            messagebox.showinfo("Finished", "All codebase blocks automatically transferred!")
        except Exception as e:
            messagebox.showerror("Macro Interrupted", f"An error occurred: {e}")
        finally:
            button_to_toggle.config(state="normal")