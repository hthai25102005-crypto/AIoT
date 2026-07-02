import tkinter as tk


class LogPanel(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#0d1421")
        tk.Label(self, text="EVENT LOG", font=("Arial", 9, "bold"),
                 bg="#0d1421", fg="#ff1744").pack(pady=(4, 2))

        self.listbox = tk.Listbox(self, bg="#0a0f1a", fg="#ccc",
                                  selectbackground="#333", relief="flat",
                                  font=("Consolas", 9), borderwidth=1,
                                  highlightbackground="#1a2a4a")
        self.listbox.pack(fill="both", expand=True, padx=4, pady=(0, 4))

    def add_event(self, text):
        fg = "#ccc"
        if "TE NGA" in text.upper() or "FALL" in text.upper():
            fg = "#ff1744"
        elif any(w in text.lower() for w in ("warn", "caution", "skip")):
            fg = "#ffab00"
        self.listbox.insert(0, f"  {text}")
        self.listbox.itemconfigure(0, fg=fg)
        if self.listbox.size() > 100:
            self.listbox.delete(100)
