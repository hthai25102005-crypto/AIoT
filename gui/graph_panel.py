import tkinter as tk
from collections import deque


class GraphPanel(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#0d1421")
        tk.Label(self, text="FALL SCORE TREND", font=("Arial", 9, "bold"),
                 bg="#0d1421", fg="#ffab00").pack(pady=(4, 2))
        self.values = deque(maxlen=60)

        canvas_frame = tk.Frame(self, bg="#0a0f1a")
        canvas_frame.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self.canvas = tk.Canvas(canvas_frame, bg="#0a0f1a", highlightthickness=1,
                                highlightbackground="#1a2a4a")
        self.canvas.pack(fill="both", expand=True)

        self._labels = []
        for i in range(0, 100, 20):
            l = tk.Label(canvas_frame, text=f"{i}%", font=("Consolas", 7),
                         bg="#0a0f1a", fg="#333")
            l.place(relx=0.02, rely=1 - i / 100, anchor="sw")
            self._labels.append(l)

    def update(self, value):
        self.values.append(value)
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 20 or h < 20 or len(self.values) < 2:
            return

        # grid lines
        for pct in (20, 40, 60, 80):
            y = h - h * pct / 100
            self.canvas.create_line(0, y, w, y, fill="#151d30", width=1)

        # line
        n = len(self.values)
        step = w / 60
        pts = [(i * step, h - v * h / 100) for i, v in enumerate(self.values)]
        for i in range(n - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            clr = "#ff1744" if self.values[i + 1] >= 65 else (
                "#ffab00" if self.values[i + 1] >= 40 else "#00e676")
            self.canvas.create_line(x1, y1, x2, y2, fill=clr, width=2,
                                    capstyle="round")
