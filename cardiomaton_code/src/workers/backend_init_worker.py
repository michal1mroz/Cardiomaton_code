from PyQt6.QtCore import QObject, pyqtSignal
from src.controllers.simulation_controller import SimulationController


class BackendInitWorker(QObject):
    finished = pyqtSignal(object)
    progress = pyqtSignal(str)

    def run(self):
        self.progress.emit("Loading graph...")
        sim = SimulationController(frame_time=0.05)
        self.progress.emit("Simulation ready")
        self.finished.emit(sim)
