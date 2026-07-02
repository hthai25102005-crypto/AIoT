import tkinter as tk

VN = {"STANDING": "DUNG", "SITTING": "NGOI", "LYING": "NAM", "UNKNOWN": "KHONG RO"}


class StatusPanel(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#0d1421")
        tk.Label(self, text="SYSTEM STATUS", font=("Arial", 11, "bold"),
                 bg="#0d1421", fg="#7c4dff").pack(pady=(6, 2))

        self.posture_lbl = tk.Label(self, text="--", font=("Arial", 20, "bold"),
                                    bg="#0d1421", fg="#e0e0ff")
        self.posture_lbl.pack(pady=(2, 0))

        self.score_lbl = tk.Label(self, text="0", font=("Arial", 28, "bold"),
                                  bg="#0d1421", fg="#888")
        self.score_lbl.pack()

        self.alert_lbl = tk.Label(self, text="BINH THUONG", font=("Arial", 14, "bold"),
                                  bg="#0d1421", fg="#00e676")
        self.alert_lbl.pack(pady=(0, 6))

    def update(self, posture, score, fall):
        self.posture_lbl.configure(text=VN.get(posture, posture))
        self.score_lbl.configure(text=f"{score:.0f}")
        c = "#ff1744" if score >= 65 else ("#ffab00" if score >= 40 else "#00e676")
        self.score_lbl.configure(fg=c)
        self.alert_lbl.configure(text="TE NGA" if fall else "BINH THUONG",
                                 fg="#ff1744" if fall else "#00e676")
