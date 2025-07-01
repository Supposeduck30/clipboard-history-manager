import tkinter as tk
from tkinter import ttk
import pyperclip
import threading
import time
import json
import os

HISTORY_FILE = "clipboard_history.json"

class ClipboardManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipboard Manager")
        self.history = self.load_history()
        self.last_clipboard = ""
        self.max_items = 50

        self.setup_ui()
        self.update_listbox()
        self.monitor_clipboard()

    def setup_ui(self):
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(self.frame, height=20, width=50)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

    def monitor_clipboard(self):
        def loop():
            while True:
                try:
                    current = pyperclip.paste()
                    if current != self.last_clipboard and current.strip():
                        self.last_clipboard = current
                        self.add_to_history(current)
                except:
                    pass
                time.sleep(0.5)
        threading.Thread(target=loop, daemon=True).start()

    def add_to_history(self, text):
        if text in self.history:
            self.history.remove(text)
        self.history.insert(0, text)
        if len(self.history) > self.max_items:
            self.history.pop()
        self.update_listbox()
        self.save_history()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for item in self.history:
            display = item if len(item) < 60 else item[:60] + "..."
            self.listbox.insert(tk.END, display)

    def on_select(self, event):
        if not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        text = self.history[index]
        pyperclip.copy(text)

    def save_history(self):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Error saving history:", e)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception as e:
                print("Error loading history:", e)
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = ClipboardManager(root)
    root.mainloop()
