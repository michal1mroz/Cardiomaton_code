import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt

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

    def render_next_frame(self, target_size) -> QPixmap:
        """
        Renders the next simulation frame and converts it to a QPixmap.

        Args:
            target_size : QSize

        Returns:
            QPixmap: A pixmap representation of the simulation frame, scaled to the given target size.
        """
        data = self.ctrl.step()
        rgba = self.cmap(self.norm(data))
        rgb  = (rgba[:, :, :3] * 255).astype(np.uint8)

        h, w, _ = rgb.shape
        bytes_per_line = 3 * w
        img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(img)
        return pix.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio)
