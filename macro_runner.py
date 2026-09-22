import time
import threading
from tkinter import messagebox
import pyautogui
import pyperclip
import gui_styles as styles

class MacroRunner:
    def __init__(self, app):
        self.app = app
        self.target_coords = None

    def start_coordinate_pick(self):
        self.app.coords_label.config(text="Get ready! Point your mouse target...", foreground=styles.ALERT_COLOR)
        self.app.update()
        threading.Thread(target=self.capture_mouse_position, daemon=True).start()

    def capture_mouse_position(self):
        time.sleep(3)
        x, y = pyautogui.position()
        self.target_coords = (x, y)
        self.app.coords_label.config(text=f"Target Coordinates Saved: X={x}, Y={y}", foreground=styles.SUCCESS_COLOR)

    def run_auto_paste(self):
        if not self.app.chunks:
            return
        if not self.target_coords:
            messagebox.showerror("Missing Information", "Please map a Window cursor position before running automation.")
            return

        confirm = messagebox.askyesno("Confirm Auto-Run", "This will control your mouse and keyboard. Ready?")
        if confirm:
            threading.Thread(target=self.execute_paste_macro, daemon=True).start()

    def execute_paste_macro(self):
        self.app.autopaste_btn.config(state="disabled")
        try:
            pyautogui.click(self.target_coords[0], self.target_coords[1])
            time.sleep(0.5)

            for index, snippet in enumerate(self.app.chunks):
                pyperclip.copy(snippet)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.25)
                pyautogui.press('enter')
                time.sleep(1.5)

            messagebox.showinfo("Finished", "All codebase blocks automatically transferred!")
        except Exception as e:
            messagebox.showerror("Macro Interrupted", f"An error occurred: {e}")
        finally:
            self.app.autopaste_btn.config(state="normal")
