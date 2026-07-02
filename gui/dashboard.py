import tkinter as tk
import time

from gui.camera_panel import CameraPanel
from gui.status_panel import StatusPanel
from gui.sensor_bar import SensorBar
from gui.graph_panel import GraphPanel
from gui.log_panel import LogPanel


class Dashboard:

    def __init__(self, root):
        self.root = root
        self.root.title("AIoT FALL DETECTION PRO UI")
        self.root.geometry("1500x850")
        self.root.configure(bg="#080d18")

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=6)
        root.grid_columnconfigure(1, weight=4)

        # === LEFT COLUMN ===
        self.left = tk.Frame(root, bg="#080d18")
        self.left.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.left.grid_rowconfigure(0, weight=1)
        self.left.grid_columnconfigure(0, weight=1)

        self.camera = CameraPanel(self.left)
        self.camera.grid(row=0, column=0, sticky="nsew", pady=(0, 4))

        # Info bar below camera
        self.info_bar = tk.Frame(self.left, bg="#0d1421")
        self.info_bar.grid(row=1, column=0, sticky="ew", pady=(0, 0))
        self._fps_lbl = tk.Label(self.info_bar, text="FPS: --", font=("Consolas", 10, "bold"),
                                 bg="#0d1421", fg="#00e676")
        self._fps_lbl.pack(side="left", padx=10, pady=4)
        self._mag_lbl = tk.Label(self.info_bar, text="MAG: --", font=("Consolas", 10, "bold"),
                                 bg="#0d1421", fg="#ffab00")
        self._mag_lbl.pack(side="left", padx=10, pady=4)
        self._fall_count_lbl = tk.Label(self.info_bar, text="FALLS: 0", font=("Consolas", 10, "bold"),
                                        bg="#0d1421", fg="#ff1744")
        self._fall_count_lbl.pack(side="right", padx=10, pady=4)

        # === RIGHT COLUMN ===
        self.right = tk.Frame(root, bg="#080d18")
        self.right.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)
        self.right.grid_rowconfigure(0, weight=2)
        self.right.grid_rowconfigure(1, weight=1)
        self.right.grid_rowconfigure(2, weight=2)
        self.right.grid_rowconfigure(3, weight=3)
        self.right.grid_columnconfigure(0, weight=1)

        self.status = StatusPanel(self.right)
        self.status.grid(row=0, column=0, sticky="nsew", pady=2)

        self.sensor = SensorBar(self.right)
        self.sensor.grid(row=1, column=0, sticky="nsew", pady=2)

        self.graph = GraphPanel(self.right)
        self.graph.grid(row=2, column=0, sticky="nsew", pady=2)

        self.log = LogPanel(self.right)
        self.log.grid(row=3, column=0, sticky="nsew", pady=2)

        self._start = time.time()
        self._fall_count = 0

    def update_camera(self, frame):
        fps = self._current_fps if hasattr(self, "_current_fps") else 0
        self.camera.update_frame(frame, fps)

    def update_status(self, fall):
        if fall and hasattr(self, "_last_fall") and not self._last_fall:
            self._fall_count += 1
        self._last_fall = fall
        self._fall_count_lbl.configure(text=f"FALLS: {self._fall_count}")

    def update_info(self, posture, score, mag, fps, ax=0, ay=0, az=0, gx=0, gy=0, gz=0):
        self._current_fps = fps
        self._fps_lbl.configure(text=f"FPS: {fps:.0f}")
        self._mag_lbl.configure(text=f"MAG: {mag:.2f}")
        self.status.update(posture, score, self._falling)
        self.sensor.update(ax, ay, az, gx, gy, gz)
        self.graph.update(score)

    @property
    def _falling(self):
        return getattr(self, "_last_fall", False)
