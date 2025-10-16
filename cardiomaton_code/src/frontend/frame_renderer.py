from typing import Dict, Tuple
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
    def __init__(self, controller: SimulationController):
        """
        Initialize the FrameRenderer.

        Args:
            controller : The simulation controller that provides the next simulation frame as a NumPy array.
        """
        self.ctrl = controller
        self.cmap = ListedColormap(['white', '#f4f8ff', 'yellow', 'red', 'blue', 'green', 'black'])
        self.norm = BoundaryNorm(np.arange(-0.5, 7.5, 1), self.cmap.N)
        self.last_data = None
        self.current_data = None

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
        frame, data = self.ctrl.step()
        self.last_data = data
        self.ctrl.recorder.record((frame, data))

        return frame, self.render_frame(target_size, self.last_data, if_charged)

    def render_frame(self, target_size, data: Dict[Tuple[int, int], CellDict], show_charge=False) -> QImage:
        self.current_data = data
        shape = self.ctrl.shape

        if show_charge:
            return self._render_charge(data, shape, target_size)
        else:
            return self._render_state(data, shape, target_size)

    def _render_charge(self, data: Dict[Tuple[int, int], CellDict], shape: Tuple[int, int], target_size: QSize) -> QPixmap:
        rgba = np.zeros((shape[0], shape[1], 4), dtype=np.uint8)

        hsv_img = np.zeros((shape[0], shape[1], 3), dtype=np.uint8)
        for (x, y), cell in data.items():
            hsv_img[x, y] = self._cell_to_hsv(cell)

        rgb_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
        rgba[:, :, :3] = rgb_img
        rgba[:, :, 3] = 0
        for (x, y), cell in data.items():
            rgba[x, y, 3] = 255

        return self._to_pixmap(rgba, target_size)

    def _render_state(self, data: Dict[Tuple[int, int], CellDict], shape: Tuple[int, int], target_size: QSize) -> QPixmap:
        rgba = np.zeros((shape[0], shape[1], 4), dtype=np.uint8)

        val = np.ones(shape, dtype=np.uint8) * 255
        for (x, y), cell in data.items():
            val[x, y] = cell["state_value"]

        rgb = (self.cmap(self.norm(val))[:, :, :3] * 255).astype(np.uint8)

        rgba[:, :, :3] = rgb
        rgba[:, :, 3] = 0
        for (x, y), cell in data.items():
            rgba[x, y, 3] = 255

        return self._to_pixmap(rgba, target_size)

    def _to_pixmap(self, img_array: np.ndarray, target_size: QSize) -> QPixmap:
        h, w, _ = img_array.shape
        bytes_per_line = 4 * w
        qimage = QImage(img_array.data, w, h, bytes_per_line, QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimage).scaled(target_size, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)

    def _cell_to_hsv(self, cell: CellDict) -> Tuple[int, int, int]:
        # Got to think of a better way to get the gray color
        if not cell["auto_polarization"] and cell["state_name"] == "Polarization":
            return 108, 11, 255
        # Naive linear cast from range -90...30 to 30...0
        h = max(-cell["charge"] * 0.25 + 7.5, 0)
        return int(h), 255,255
