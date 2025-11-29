from typing import Tuple

from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QSize

from src.frontend.frame_rendering.pixmap_renderer import PixmapRenderer
from src.backend.controllers.simulation_controller import SimulationController

class FrameRenderer:

    def __init__(self, controller: SimulationController, image: QImage) -> None:
        self._simulation_controller = controller
        self._pixmap_renderer = PixmapRenderer(image)

    def render_next_frame(self, target_size: QSize, if_charged: bool = False) -> Tuple[int, QPixmap]:
        frame_index = self._simulation_controller.step(if_charged)
        pixmap = self._pixmap_renderer.to_pixmap(target_size)
        return frame_index, pixmap

    def render_frame(self, target_size: QSize, idx: int, if_charged: bool, drop_newer: bool ) -> Tuple[int, QPixmap]:
        frame_index = self._simulation_controller.render_frame(idx, if_charged, drop_newer)
        pixmap = self._pixmap_renderer.to_pixmap(target_size)
        return frame_index, pixmap
