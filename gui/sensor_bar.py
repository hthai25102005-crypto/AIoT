import tkinter as tk


class SensorBar(tk.Frame):
    _bg_color = "#0d1421"
    _bar_bg = "#1a1a2e"
    _bar_fg = "#00e5ff"

    def __init__(self, parent):
        super().__init__(parent, bg=self._bg_color)
        tk.Label(self, text="SENSOR DATA", font=("Arial", 9, "bold"),
                 bg=self._bg_color, fg="#00e5ff").pack(pady=(4, 2))

        self._bars = {}
        self._values = {}
        rows = tk.Frame(self, bg=self._bg_color)
        rows.pack(fill="x", padx=6, pady=(0, 4))
        for label, tag in [("ACC X", "ax"), ("ACC Y", "ay"), ("ACC Z", "az"),
                           ("GYR X", "gx"), ("GYR Y", "gy"), ("GYR Z", "gz")]:
            r = tk.Frame(rows, bg=self._bg_color)
            r.pack(fill="x", pady=1)
            tk.Label(r, text=label, font=("Consolas", 8), width=6, anchor="w",
                     bg=self._bg_color, fg="#888").pack(side="left")
            canvas = tk.Canvas(r, height=8, bg=self._bar_bg, highlightthickness=0)
            canvas.pack(side="left", fill="x", expand=True, padx=(4, 0))
            val_lbl = tk.Label(r, text="0.0", font=("Consolas", 8), width=6, anchor="e",
                               bg=self._bg_color, fg=self._bar_fg)
            val_lbl.pack(side="right")
            self._bars[tag] = canvas
            self._values[tag] = val_lbl

    def update(self, ax, ay, az, gx, gy, gz):
        vals = {"ax": ax, "ay": ay, "az": az, "gx": gx, "gy": gy, "gz": gz}
        for tag, v in vals.items():
            c = self._bars[tag]
            w = c.winfo_width()
            if w < 10:
                continue
            frac = min(abs(v) / 20, 1.0) if tag in ("gx", "gy", "gz") else min(abs(v - 9.8) / 15, 1.0) if tag == "az" else min(abs(v) / 15, 1.0)
            c.delete("all")
            c.create_rectangle(1, 1, int((w - 2) * frac), c.winfo_height() - 2,
                               fill=self._bar_fg, outline="")
            self._values[tag].configure(text=f"{v:.1f}")
