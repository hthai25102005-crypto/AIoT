import tkinter as tk
from tkinter import Label
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import threading
import time

class CameraPanel(tk.Frame):

    BORDER_COLOR = "#1a2a4a"
    BG_COLOR = "#0a0f1a"

    def __init__(self, parent):

        super().__init__(parent, bg=self.BORDER_COLOR)

        self.inner = tk.Frame(
            self,
            bg=self.BG_COLOR
        )
        self.inner.pack(fill="both", expand=True, padx=2, pady=2)

        self.label = tk.Label(
            self.inner,
            text="[ CAMERA OFFLINE ]",
            bg=self.BG_COLOR,
            fg="#ff4444",
            font=("Arial", 14, "bold")
        )
        self.label.pack(fill="both", expand=True)

        self.fps_lbl = tk.Label(
            self.inner,
            text="",
            bg=self.BG_COLOR,
            fg="#00e676",
            font=("Consolas", 10, "bold"),
            anchor="se"
        )

        self.fps_lbl.place(
            relx=1,
            rely=1,
            x=-8,
            y=-8,
            anchor="se"
        )

        self.photo = None

        # Kích thước hiển thị cố định
        self.display_width = 640
        self.display_height = 480

    def update_frame(self, frame, fps=0):

        if frame is None:
            return

        if frame.size == 0:
            return

        # Resize
        frame = cv2.resize(
            frame,
            (self.display_width, self.display_height),
            interpolation=cv2.INTER_LINEAR
        )

        # BGR -> RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # OpenCV -> PIL
        image = Image.fromarray(frame)

        # PIL -> Tkinter
        self.photo = ImageTk.PhotoImage(image=image)

        # Update image
        self.label.configure(
            image=self.photo,
            text=""
        )

        # Giữ reference
        self.label.image = self.photo

        # FPS
        self.fps_lbl.configure(
            text=f"{fps:.1f} FPS"
        )