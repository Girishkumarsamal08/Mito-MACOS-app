# type: ignore

import os
import sys
from typing import Optional

import cv2
import numpy as np

from PyQt5.QtCore import QObject, QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget


# ============================================================
# PATHS
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
RESOURCES_DIR = os.path.join(PROJECT_ROOT, "Resources")


# ============================================================
# GUI BRIDGE
# ============================================================

class GUIBridge(QObject):
    """
    Thread-safe communication bridge between the backend and GUI.

    Backend threads should NEVER directly manipulate Qt widgets.

    Instead:
        update_state("Thinking")
        update_label("Hmm, wait...")

    and the Qt GUI receives those signals safely.
    """

    state_signal = pyqtSignal(str)
    label_signal = pyqtSignal(str)
    visibility_signal = pyqtSignal(bool)
    quit_signal = pyqtSignal()


# One global bridge used by the application.
gui_bridge = GUIBridge()


# ============================================================
# SIRI-STYLE MITO OVERLAY
# ============================================================

class SiriStyleOverlay(QWidget):
    """
    Floating MITO character window.

    Video states:

        Idle.mp4
        Listening.mp4
        Thinking.mp4
        Speaking.mp4
        Happy.mp4
        Sad.mp4

    The GUI is ONLY responsible for:
        - displaying MITO
        - playing animation videos
        - displaying status text

    Microphone/audio processing belongs to the backend.
    """

    VIDEO_SIZE = 420
    FPS_INTERVAL_MS = 40  # approximately 25 FPS

    def __init__(self) -> None:
        super().__init__()

        self.cap: Optional[cv2.VideoCapture] = None
        self.current_state: str = "Idle"
        self.current_video_path: Optional[str] = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_frame)

        self.init_ui()

    # ========================================================
    # UI INITIALIZATION
    # ========================================================

    def init_ui(self) -> None:
        """
        Create and configure the MITO overlay.
        """

        # ----------------------------------------------------
        # Window icon
        # ----------------------------------------------------

        logo_candidates = [
            os.path.join(RESOURCES_DIR, "logo.png"),
            os.path.join(RESOURCES_DIR, "APP_LOGO.png"),
            os.path.join(RESOURCES_DIR, "Logo.png"),
        ]

        for logo_path in logo_candidates:
            if os.path.exists(logo_path):
                self.setWindowIcon(QIcon(logo_path))
                break

        # ----------------------------------------------------
        # Window configuration
        # ----------------------------------------------------

        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )

        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

        self.setStyleSheet(
            """
            QWidget {
                background: transparent;
                border: none;
            }

            QLabel {
                background: transparent;
                border: none;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            """
        )

        self.resize(self.VIDEO_SIZE, self.VIDEO_SIZE)

        # ----------------------------------------------------
        # Position window at top-right of primary display
        # ----------------------------------------------------

        screen = QApplication.primaryScreen()

        if screen is not None:
            screen_geometry = screen.availableGeometry()

            x = (
                screen_geometry.right()
                - self.width()
                - 30
            )

            y = screen_geometry.top() + 30

            self.move(x, y)

        # ----------------------------------------------------
        # Video label
        # ----------------------------------------------------

        self.video_label = QLabel(self)

        self.video_label.setGeometry(
            0,
            0,
            self.VIDEO_SIZE,
            self.VIDEO_SIZE,
        )

        self.video_label.setAlignment(Qt.AlignCenter)

        self.video_label.setStyleSheet(
            """
            QLabel {
                background: transparent;
                border: none;
            }
            """
        )

        self.video_label.setAttribute(
            Qt.WA_TranslucentBackground,
            True,
        )

        # ----------------------------------------------------
        # Text label
        # ----------------------------------------------------

        self.label = QLabel("Hey Mito", self)

        self.label.setGeometry(
            20,
            16,
            self.width() - 40,
            40,
        )

        self.label.setAlignment(Qt.AlignCenter)

        self.label.setStyleSheet(
            """
            QLabel {
                background: transparent;
                color: white;
                border: none;
                font-size: 20px;
                font-weight: bold;
            }
            """
        )

        self.label.raise_()

        # ----------------------------------------------------
        # GUI bridge connections
        # ----------------------------------------------------

        gui_bridge.state_signal.connect(
            self.set_state
        )

        gui_bridge.label_signal.connect(
            self.update_text
        )

        gui_bridge.visibility_signal.connect(
            self.set_visibility
        )

        gui_bridge.quit_signal.connect(
            self.close_app
        )

        # ----------------------------------------------------
        # Initial state
        # ----------------------------------------------------

        self.set_state("Idle")

        self.show()

    # ========================================================
    # VISIBILITY
    # ========================================================

    def set_visibility(self, visible: bool) -> None:
        """
        Show or hide the MITO overlay.
        """

        if visible:
            self.show()
            self.raise_()
            self.activateWindow()

        else:
            self.hide()

    # ========================================================
    # APPLICATION CLOSE
    # ========================================================

    def close_app(self) -> None:
        """
        Safely stop video playback and close the GUI.
        """

        if self.timer.isActive():
            self.timer.stop()

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        self.current_video_path = None

        self.hide()

        app = QApplication.instance()

        if app is not None:
            app.quit()

    # ========================================================
    # STATE → VIDEO MAPPING
    # ========================================================

    @staticmethod
    def normalize_state(state: str) -> str:
        """
        Convert backend state names into canonical MITO states.

        Supported:

            Idle
            Listening
            Thinking
            Speaking
            Happy
            Sad

        """

        normalized = str(state).strip().lower()

        state_map = {
            "idle": "Idle",
            "sleeping": "Idle",

            "listening": "Listening",

            "thinking": "Thinking",

            "speaking": "Speaking",
            "talking": "Speaking",

            "happy": "Happy",
            "joy": "Happy",

            "sad": "Sad",
            "unhappy": "Sad",
        }

        return state_map.get(
            normalized,
            "Idle",
        )

    # ========================================================
    # VIDEO PATH
    # ========================================================

    def get_video_path(
        self,
        state: str,
    ) -> Optional[str]:
        """
        Find the MP4 associated with a MITO state.

        Expected files:

            Resources/Idle.mp4
            Resources/Listening.mp4
            Resources/Thinking.mp4
            Resources/Speaking.mp4
            Resources/Happy.mp4
            Resources/Sad.mp4
        """

        filename = f"{state}.mp4"

        candidates = [
            os.path.join(
                RESOURCES_DIR,
                filename,
            ),

            os.path.join(
                RESOURCES_DIR,
                filename.lower(),
            ),

            os.path.join(
                RESOURCES_DIR,
                filename.capitalize(),
            ),

            os.path.join(
                PROJECT_ROOT,
                "RESOURCES",
                filename,
            ),
        ]

        for path in candidates:
            if os.path.isfile(path):
                return path

        return None

    # ========================================================
    # CHANGE MITO STATE
    # ========================================================

    def set_state(self, state: str) -> None:
        """
        Change MITO's animation state.
        """

        if not state:
            return

        target_state = self.normalize_state(state)

        # Avoid reopening the exact same video repeatedly.
        if (
            self.current_state == target_state
            and self.cap is not None
            and self.cap.isOpened()
        ):
            return

        video_path = self.get_video_path(
            target_state
        )

        if video_path is None:
            print(
                f"[MITO GUI] Video not found for state: "
                f"{target_state}"
            )

            print(
                f"[MITO GUI] Expected file: "
                f"{os.path.join(RESOURCES_DIR, target_state + '.mp4')}"
            )

            return

        # ----------------------------------------------------
        # Release previous video
        # ----------------------------------------------------

        if self.cap is not None:
            self.cap.release()
            self.cap = None

        # ----------------------------------------------------
        # Open new video
        # ----------------------------------------------------

        new_cap = cv2.VideoCapture(video_path)

        if not new_cap.isOpened():
            print(
                f"[MITO GUI] Failed to open video: "
                f"{video_path}"
            )

            new_cap.release()
            return

        self.cap = new_cap
        self.current_state = target_state
        self.current_video_path = video_path

        # ----------------------------------------------------
        # Start frame timer
        # ----------------------------------------------------

        if not self.timer.isActive():
            self.timer.start(
                self.FPS_INTERVAL_MS
            )

    # ========================================================
    # VIDEO FRAME UPDATE
    # ========================================================

    def update_video_frame(self) -> None:
        """
        Read and display the next video frame.

        The black background is converted into transparency
        so the MITO character appears to float on the desktop.
        """

        if self.cap is None:
            return

        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()

        # ----------------------------------------------------
        # Loop video when it reaches the end
        # ----------------------------------------------------

        if not ret:
            self.cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                0,
            )

            ret, frame = self.cap.read()

        if not ret or frame is None:
            return

        # ----------------------------------------------------
        # OpenCV BGR → RGB
        # ----------------------------------------------------

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB,
        )

        # ----------------------------------------------------
        # Convert dark/black background to alpha
        # ----------------------------------------------------

        rgb_float = (
            rgb.astype(np.float32) / 255.0
        )

        max_rgb = np.max(
            rgb_float,
            axis=2,
        )

        # Pixels near black become transparent.
        # Brighter character pixels remain visible.

        low_threshold = 0.003
        high_threshold = 0.02

        alpha = np.clip(
            (
                max_rgb - low_threshold
            )
            / (
                high_threshold - low_threshold
            ),
            0.0,
            1.0,
        )

        # Smooth alpha transition.
        alpha = (
            alpha
            * alpha
            * (
                3.0
                - 2.0 * alpha
            )
        )

        alpha_channel = (
            alpha * 255.0
        ).astype(np.uint8)

        # ----------------------------------------------------
        # RGB + Alpha
        # ----------------------------------------------------

        rgba = np.dstack(
            (
                rgb,
                alpha_channel,
            )
        )

        rgba = np.ascontiguousarray(
            rgba,
            dtype=np.uint8,
        )

        height, width, channels = (
            rgba.shape
        )

        # ----------------------------------------------------
        # Create QImage
        # ----------------------------------------------------

        qimage = QImage(
            rgba.data,
            width,
            height,
            width * channels,
            QImage.Format_RGBA8888,
        )

        # Make an independent copy so OpenCV memory can
        # safely be reused on the next frame.
        qimage = qimage.copy()

        # ----------------------------------------------------
        # Scale to MITO window
        # ----------------------------------------------------

        pixmap = QPixmap.fromImage(
            qimage
        )

        pixmap = pixmap.scaled(
            self.VIDEO_SIZE,
            self.VIDEO_SIZE,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.video_label.setPixmap(
            pixmap
        )

    # ========================================================
    # TEXT UPDATE
    # ========================================================

    def update_text(self, new_text: str) -> None:
        """
        Update MITO's text label.
        """

        if new_text is None:
            return

        self.label.setText(
            str(new_text)
        )


# ============================================================
# THREAD-SAFE PUBLIC FUNCTIONS
# ============================================================

def update_label(text: str) -> None:
    """
    Update MITO's displayed text.

    Backend usage:

        update_label("Hmm...")

    """
    try:
        from BACKEND.BridgeServer import broadcast_state
        broadcast_state("label", str(text))
    except Exception:
        pass

    gui_bridge.label_signal.emit(
        str(text)
    )


def update_state(state: str) -> None:
    """
    Change MITO animation state.

    Examples:

        update_state("Idle")
        update_state("Listening")
        update_state("Thinking")
        update_state("Speaking")
        update_state("Happy")
        update_state("Sad")
    """
    try:
        from BACKEND.BridgeServer import broadcast_state
        broadcast_state(str(state))
    except Exception:
        pass

    gui_bridge.state_signal.emit(
        str(state)
    )


def set_overlay_visible(
    visible: bool,
) -> None:
    """
    Show/hide MITO.
    """

    gui_bridge.visibility_signal.emit(
        bool(visible)
    )


def quit_overlay() -> None:
    """
    Safely close MITO GUI.
    """

    gui_bridge.quit_signal.emit()


# ============================================================
# STANDALONE TEST MODE
# ============================================================

if __name__ == "__main__":

    app = QApplication.instance()

    if app is None:
        app = QApplication(sys.argv)

    window = SiriStyleOverlay()

    sys.exit(
        app.exec_()
    )