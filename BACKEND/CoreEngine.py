# BACKEND/CoreEngine.py

from BACKEND.StateManager import state_manager

class CoreEngine:

    def __init__(self):

        print("[MITO] Core Engine Booting...")

    def startup(self):

        print("[MITO] Starting systems...")

        state_manager.set_state("idle")

        print("[MITO] Systems online.")

    def listening(self):

        state_manager.set_state("listening")

    def thinking(self):

        state_manager.set_state("thinking")

    def speaking(self):

        state_manager.set_state("speaking")

    def idle(self):

        state_manager.set_state("idle")

    def error(self):

        state_manager.set_state("error")


core_engine = CoreEngine()