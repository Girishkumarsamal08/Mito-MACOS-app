import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt5.QtGui import QFont, QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

class SiriStyleOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_frame)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                border: none;
            }
            QLabel {
                color: black;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 5px;            
            }
        """)

        self.resize(420, 420)
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(screen_geometry.width() - self.width() - 30, 30)

        self.video_label = QLabel(self)
        self.video_label.setGeometry(0, 0, 420, 420)
        self.video_label.setStyleSheet("background: transparent; border: none;")
        self.video_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.video_label.setAlignment(Qt.AlignCenter)

        self.label = QLabel("Hey Mito", self)
        self.label.setStyleSheet("background: transparent; color: white;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(20, 16, self.width() - 90, 40)
        self.label.raise_()

        # Default state
        self.set_state("Idle")

        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.show()

    def set_state(self, state):
        state_map = {
            "listening": "Thinking",
            "Listening": "Thinking",
        }
        actual_state = state_map.get(state, state)
        video_path = os.path.join(project_root, "Resources", f"{actual_state}.mp4")

        if not os.path.exists(video_path):
            print(f"Video not found: {video_path}")
            return

        if self.cap:
            self.cap.release()

        self.cap = cv2.VideoCapture(video_path)
        if not self.timer.isActive():
            self.timer.start(40)  # ~25 fps

    def update_video_frame(self):
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        if ret:
            img = frame.astype(np.float32) / 255.0
            b, g, r = img[:, :, 0], img[:, :, 1], img[:, :, 2]
            max_rgb = np.maximum(r, np.maximum(g, b))
            val = np.clip((max_rgb - 0.003) / (0.02 - 0.003), 0.0, 1.0)
            alpha = val * val * (3.0 - 2.0 * val)
            rgba = (np.dstack((r, g, b, alpha)) * 255).astype(np.uint8)

            h, w, ch = rgba.shape
            qimg = QImage(rgba.data, w, h, w * ch, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimg).scaled(420, 420, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(pixmap)

    def update_text(self, new_text):
        self.label.setText(new_text)

    
# Function to update the label of the existing overlay window
def update_label(text):
    try:
        from BACKEND.BridgeServer import broadcast_state
        broadcast_state("label", text)
    except Exception:
        pass

    if hasattr(QApplication, "instance") and QApplication.instance():
        for widget in QApplication.instance().allWidgets():
            if isinstance(widget, SiriStyleOverlay):
                widget.update_text(text)
                break

def update_state(state):
    try:
        from BACKEND.BridgeServer import broadcast_state
        broadcast_state(state)
    except Exception:
        pass

    app = QApplication.instance()
    if app:
        for widget in app.allWidgets():
            if isinstance(widget, SiriStyleOverlay):
                widget.set_state(state)
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SiriStyleOverlay()
    sys.exit(app.exec_())
