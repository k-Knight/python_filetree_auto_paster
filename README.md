# Code Splitter & Automation Macro

A lightweight Windows desktop app designed to slice large source code files into context-safe chunks and auto-type them into external AI windows. It reads your project structure, lets you select target files via a custom file tree, and uses background macros to systematically paste and submit codeblocks.

## Features

- **Auto-Setup**: Automatically checks for and installs missing dependencies (`customtkinter`, `pyautogui`, `pyperclip`, `pillow`) on its first launch.
- **Visual File Tree**: Select entire folders or specific files with recursive, partial-state checkboxes.
- **Dynamic Buffer Slider**: Adjust maximum chunk limits on the fly (from 1,000 to 32,000 characters) to match your AI's context limit.
- **Threaded Macro Runner**: Safe automated input execution with adjustable paste and post-submit delays so your UI never freezes.

## How to Run

Just double-click `main.pyw` or fire it up from PowerShell/CMD:

```powershell
python main.pyw
```

## How to Use It

1. **Select a Project**: Click **Browse Folder** and choose your codebase directory.
2. **Map the Target**: Click **Set Target Area**, then quickly hover your mouse over the text box where you want to paste the code (you have 3 seconds before it saves the coordinates).
3. **Configure Limits**: Check the boxes for the files you want to send and adjust the **Max Chunk Buffer** slider.
4. **Process & Run**: Click **1. Process Snippets** to generate the blocks, then hit **2. Execute Auto-Paste** to start the unattended transfer macro.
