import sys
import os
import cv2  # type: ignore
import numpy as np  # type: ignore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton  # type: ignore
from PyQt5.QtGui import QFont, QIcon, QPixmap, QImage  # type: ignore
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject  # type: ignore

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

class GUIBridge(QObject):
    state_signal = pyqtSignal(str)
    label_signal = pyqtSignal(str)
    visibility_signal = pyqtSignal(bool)
    quit_signal = pyqtSignal()

gui_bridge = GUIBridge()

class SiriStyleOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_frame)
        self.init_ui()

    def init_ui(self):
        logo_path = os.path.join(project_root, "Resources", "logo.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(project_root, "Resources", "APP_LOGO.png")
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

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

        # Connect signals for thread safety
        gui_bridge.state_signal.connect(self.set_state)
        gui_bridge.label_signal.connect(self.update_text)
        gui_bridge.visibility_signal.connect(self.set_visibility)
        gui_bridge.quit_signal.connect(self.close_app)

        # Default state
        self.set_state("Idle")

        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.show()

    def set_visibility(self, visible):
        if visible:
            self.show()
            self.raise_()
            self.activateWindow()
        else:
            self.hide()

    def close_app(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.cap:
            self.cap.release()
        self.hide()
        QApplication.quit()

    def set_state(self, state):
        if not state:
            return
        
        clean_state = str(state).strip()
        state_map = {
            "listening": "Idle",
            "Listening": "Idle",
            "thinking": "Thinking",
            "Thinking": "Thinking",
            "speaking": "Speaking",
            "Speaking": "Speaking",
            "idle": "Idle",
            "Idle": "Idle",
            "sleeping": "Idle",
            "Sleeping": "Idle",
            "happy": "Happy",
            "Happy": "Happy",
            "sad": "Sad",
            "Sad": "Sad",
        }
        target_name = state_map.get(clean_state, clean_state)
        if target_name in ["listening", "Listening"]:
            target_name = "Idle"

        candidates = [
            os.path.join(project_root, "Resources", f"{target_name}.mp4"),
            os.path.join(project_root, "Resources", f"{target_name.lower()}.mp4"),
            os.path.join(project_root, "Resources", f"{target_name.capitalize()}.mp4"),
            os.path.join(project_root, "RESOURCES", f"{target_name}.mp4"),
        ]

        video_path = None
        for cand in candidates:
            if os.path.exists(cand):
                video_path = cand
                break

        if not video_path:
            print(f"[GUI Video Error] Video not found for state: {state}")
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


# Thread-safe helper functions
def update_label(text):
    try:
        from BACKEND.BridgeServer import broadcast_state
        broadcast_state("label", text)
    except Exception:
        pass
    gui_bridge.label_signal.emit(text)

def update_state(state):
    try:
        from BACKEND.BridgeServer import broadcast_state
        broadcast_state(state)
    except Exception:
        pass
    gui_bridge.state_signal.emit(state)

def set_overlay_visible(visible: bool):
    gui_bridge.visibility_signal.emit(visible)

def quit_overlay():
    gui_bridge.quit_signal.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SiriStyleOverlay()
    sys.exit(app.exec_())
