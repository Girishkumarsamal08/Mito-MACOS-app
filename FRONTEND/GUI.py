import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStyle, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtCore import Qt, QUrl, QSizeF

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

class SiriStyleOverlay(QWidget):
    def __init__(self):
        super().__init__()
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

        self.label = QLabel("Hey Mito", self)
        self.label.setStyleSheet("background: transparent; color: white;")
        self.label.raise_()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(20, 16, self.width() - 90, 40)

        # Transparent video scene
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, 420, 420)
        self.view.setStyleSheet("background: transparent; border:none;")
        self.view.setFrameShape(QGraphicsView.NoFrame)
        self.view.setAttribute(Qt.WA_TranslucentBackground, True)

        self.video_item = QGraphicsVideoItem()
        self.video_item.setSize(QSizeF(420,420))
        self.scene.addItem(self.video_item)

        self.player = QMediaPlayer(self)
        self.player.setVideoOutput(self.video_item)
        self.player.setMuted(True)
        self.player.mediaStatusChanged.connect(self.handle_loop)

        # Default state
        self.set_state("Idle")

        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.view.lower()
        self.label.raise_()
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

        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        self.player.play()

    def handle_loop(self, status):
        from PyQt5.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

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
