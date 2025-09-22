from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

class SimulationWorker(QObject):
    frame_ready = pyqtSignal(int, dict) # frame number, frame data
    request_next_frame = pyqtSignal()

    def __init__(self, sim):
        super().__init__()
        self.sim = sim
        self.request_next_frame.connect(self.do_step)

    @pyqtSlot()
    def do_step(self):
        frame, data = self.sim.step()
        self.sim.recorder.record((frame, data))
        self.frame_ready.emit(frame, data)
