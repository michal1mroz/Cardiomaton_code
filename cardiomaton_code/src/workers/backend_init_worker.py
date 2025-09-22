from PyQt6.QtCore import QObject, pyqtSignal
from src.controllers.simulation_controller import SimulationController


class BackendInitWorker(QObject):
    finished = pyqtSignal(object)  # return ready SimulationController object
    progress = pyqtSignal(str)     #

    def run(self):
        # Tutaj robimy wszystkie ciężkie operacje inicjalizacji backendu
        self.progress.emit("Loading graph...")
        sim = SimulationController(frame_time=0.05)  # np. tworzenie automatu
        self.progress.emit("Simulation ready")
        self.finished.emit(sim)
