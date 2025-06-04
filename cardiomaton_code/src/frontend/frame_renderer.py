from typing import Tuple
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import cv2

from src.frontend.simulation_controller import SimulationController


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
        self.cmap = ListedColormap(['white', 'gray', 'yellow', 'red', 'blue', 'green', 'black'])
        self.norm = BoundaryNorm(np.arange(-0.5, 7.5, 1), self.cmap.N)
        self.last_data = None

    def render_next_frame(self, target_size) -> QPixmap:
        """
        Renders the next simulation frame and converts it to a QPixmap.

        Args:
            target_size : QSize

        Returns:
            QPixmap: A pixmap representation of the simulation frame, scaled to the given target size.
        """
        data = self.ctrl.step()
        self.last_data = data

        val = np.array([[cell["state_value"] if cell is not None else 0 for cell in row] for row in data])
        rgba = self.cmap(self.norm(val))
        rgb  = (rgba[:, :, :3] * 255).astype(np.uint8)

        h, w, _ = rgb.shape
        bytes_per_line = 3 * w
        img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(img)
        return pix.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio)
    
    def _cell_to_hsv(self, cell) -> Tuple[int, int, int]:
        # Got to think of a better way to get the gray color
        if not cell["auto_polarization"] and cell["state_name"] == "Polarization":
            return (0,0,124)
        # Naive linear cast from range -90...30 to 30...0
        h = max(-cell["charge"] * 0.25 + 7.5, 0)
        return int(h), 255,255

    def render_next_frame_charge(self, target_size) -> QPixmap: 
        """
        Method to create the next simulation frame scaled to the given size. Uses charge as a base for the cell color.

        Args:
            target_size (QSize): Target size of the rendered image.

        Returns:
            QPixmap: generated automaton frame
        """
        data = self.ctrl.step()
        self.last_data = data

        im_array = cv2.cvtColor(np.array([[self._cell_to_hsv(cell) if cell is not None else (0,0,255) for cell in row] for row in data], dtype=np.uint8), cv2.COLOR_HSV2RGB)
        h, w, _ = im_array.shape
        bytes_per_line = 3 * w
        qimage = QImage(im_array.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(qimage).scaled(
            target_size,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
        )