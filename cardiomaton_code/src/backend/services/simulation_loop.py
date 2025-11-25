from PyQt6.QtCore import QTimer, QObject, pyqtSignal

from src.backend.controllers.simulation_controller import SimulationController

class SimulationRunner(QObject):
    frame_tick = pyqtSignal()

    def __init__(self, base_frame_time: float):
        super().__init__()
        self.base_frame_time = base_frame_time
        self.current_frame_time = base_frame_time
        self.running = False

        self._timer = QTimer()
        self._timer.timeout.connect(self.frame_tick.emit)
        QTimer.singleShot(0, self.frame_tick.emit)

    def set_speed_level(self, speed_text: str, sim_controller: SimulationController):
        try:
            speed_int = int(speed_text[0])
            multiplier = 2 ** (speed_int - 1)
            self.current_frame_time = self.base_frame_time / multiplier
            sim_controller.frame_time = self.current_frame_time

            if self.running:
                self._timer.start(int(self.current_frame_time * 1000))
        except (ValueError, IndexError):
            pass

    def toggle(self):
        self.running = not self.running
        if self.running:
            self._timer.start(int(self.current_frame_time * 1000))
        else:
            self._timer.stop()
        return self.running

    def stop(self):
        self.running = False
        self._timer.stop()