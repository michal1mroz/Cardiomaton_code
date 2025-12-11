from PyQt6.QtCore import QObject, QThread, pyqtSignal


class BackendInitWorker(QObject):
    finished = pyqtSignal(object, object, object)  # sim, renderer, image

    def __init__(self, base_frame_time):
        super().__init__()
        self.base_frame_time = base_frame_time

    def run(self):
        from PyQt6.QtGui import QImage
        from src.backend.controllers.simulation_controller import SimulationController
        from src.frontend.frame_rendering.frame_renderer import FrameRenderer

        size = (292, 400)

        image = QImage(size[1], size[0], QImage.Format.Format_RGBA8888)
        sim = SimulationController(frame_time=self.base_frame_time, image=image)
        renderer = FrameRenderer(sim, image)

        self.finished.emit(sim, renderer, image)
