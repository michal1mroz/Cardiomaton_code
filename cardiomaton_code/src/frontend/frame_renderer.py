import time
from typing import Dict, Optional, Tuple
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QSize
import cv2

from src.models.cell import CellDict
from src.controllers.simulation_controller import SimulationController


class FrameRenderer:
    """
    Handles conversion of simulation data into visual frames.
    """
    def __init__(self, controller: SimulationController, image: QImage):
        """
        Initialize the FrameRenderer.

        Args:
            controller : The simulation controller that provides the next simulation frame as a NumPy array.
        """
        self.ctrl = controller

        self.last_data = None
        self.current_data = None
        self.image = image
        
    def render_next_frame(self, target_size, if_charged: bool = False) -> Tuple[int, QPixmap]:
        """
        Renders the next simulation frame and converts it to a QPixmap.
        Sends the data to the recorder for playback.

        Args:
            target_size : QSize
            if_charged : true if returned QPixmap stores VOLTAGE, false if returned QPixmap stores cell states
        Returns:
            Tuple[int, QPixmap]: A pixmap representation of the simulation frame, scaled to the given target size and
                int value of the frame counter
        """
        frame, data = self.ctrl.step(if_charged)
        self.current_data = data
        self.ctrl.recorder.record((frame, data))
        return frame, self._to_pixmap(target_size)

    def render_frame(self, target_size: QSize, idx: int, if_charged: bool, drop_newer: bool) -> Tuple[int, QPixmap]:
        frame = self.ctrl.render_frame(idx, if_charged, drop_newer)
        return frame, self._to_pixmap(target_size)

    def _to_pixmap(self, target_size: QSize) -> QPixmap:
        return QPixmap.fromImage(self.image).scaled(target_size, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
    
    def get_cell_data(self, position: Tuple[int, int]) -> Optional[Dict]:
        return self.ctrl.get_cell_data(position)
