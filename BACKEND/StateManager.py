# BACKEND/StateManager.py

from threading import Lock

class StateManager:

    def __init__(self):
        self.lock = Lock()

        self.current_state = "idle"

        self.allowed_states = {

            "idle",

            "listening",

            "thinking",

            "speaking",

            "sleep",

            "error"

        }

    def set_state(self, new_state):

        with self.lock:

            if new_state in self.allowed_states:

                self.current_state = new_state

                print(f"[MITO STATE] -> {new_state}")

            else:

                print(f"[MITO ERROR] Invalid state: {new_state}")

    def get_state(self):

        with self.lock:

            return self.current_state


state_manager = StateManager()