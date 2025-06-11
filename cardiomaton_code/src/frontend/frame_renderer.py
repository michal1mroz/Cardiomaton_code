from typing import Dict, Tuple
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
import cv2

from src.models.cell import CellDict
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
        self.current_data = None

    def render_next_frame(self, target_size, if_charged = False) -> Tuple[int, QPixmap]:
        """
        Renders the next simulation frame and converts it to a QPixmap.
        Sends the data to the recorder for playback.


        Args:
            target_size : QSize

        Returns:
            Tuple[int, QPixmap]: A pixmap representation of the simulation frame, scaled to the given target size and
                int value of the frame counter
        """
        frame, data = self.ctrl.step()
        self.last_data = data
        self.ctrl.recorder.record((frame, data))

        return frame, self.render_frame(target_size, self.last_data, if_charged)

    def render_frame(self, target_size, data: Dict[Tuple[int, int], CellDict], if_charged = False) -> QImage:
        self.current_data = data
        #val = np.array([[cell["state_value"] if cell is not None else 0 for cell in row] for row in data])
        size = self.ctrl.automaton.shape
        if if_charged:
            hsv_img = np.zeros((size[0], size[1], 3), dtype=np.uint8)
            for position, cell in data.items():
                x, y = position
                hsv_img[x, y] = self._cell_to_hsv(cell)
            im_rgb = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)

            h, w, _ = im_rgb.shape
            bytes_per_line = 3 * w
            qimage = QImage(im_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            return QPixmap.fromImage(qimage).scaled(
                target_size,
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
            )
        else:
            val = np.ones((size[0], size[1]), dtype=np.uint8) * 255
            for position, cell in data.items():
                x, y = position
                # val[x,y] = cell["state_value"]
                val[x, y] = cell.get("state_value", cell.get("s", 0)) + (0 if "s" in cell else 0)
            rgba = self.cmap(self.norm(val))
            rgb = (rgba[:, :, :3] * 255).astype(np.uint8)

            h, w, _ = rgb.shape
            bytes_per_line = 3 * w
            img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pix = QPixmap.fromImage(img)
            scaled = pix.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio)

            return scaled
    
    # def _cell_to_hsv(self, cell: CellDict) -> Tuple[int, int, int]:
    #     # Got to think of a better way to get the gray color
    #     if not cell["auto_polarization"] and cell["state_name"] == "Polarization":
    #         return (0,0,124)
    #     # Naive linear cast from range -90...30 to 30...0
    #     h = max(-cell["charge"] * 0.25 + 7.5, 0)
    #     return int(h), 255,255
    def _cell_to_hsv(self, cell: CellDict) -> Tuple[int, int, int]:
        """
        Converts cell data to HSV color space for visualization.
        Supports both full and compact formats.
        """
        compact_format = "p" in cell and "auto_polarization" not in cell

        if compact_format:
            auto_pol = cell["p"]
            state = cell["s"]
            charge = cell["c"]
        else:
            auto_pol = cell["auto_polarization"]
            state_name = cell["state_name"].lower()
            state = 1 if "polarization" in state_name else 0  # heuristic
            charge = cell["charge"]

        # Szary kolor dla niepolaryzujących w stanie polaryzacji
        if not auto_pol and state == 1:
            return (0, 0, 124)

        # Rzutowanie napięcia (-90..30 mV) na odcień (30..0)
        h = max(-charge * 0.25 + 7.5, 0)
        return int(h), 255, 255


    def render_next_frame_charge(self, target_size) -> Tuple[int, QPixmap]: 
        """
        Method to create the next simulation frame scaled to the given size. Uses charge as a base for the cell color.

        Args:
            target_size (QSize): Target size of the rendered image.

        Returns:
            QPixmap: generated automaton frame
        """
        frame, data = self.ctrl.step()
        self.last_data = data

        size = self.ctrl.automaton.shape
        hsv_img = np.zeros((size[0], size[1], 3), dtype=np.uint8)
        for position, cell in data.items():
            x, y = position
            hsv_img[x, y] = self._cell_to_hsv(cell)
        im_rgb = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
        
        h, w, _ = im_rgb.shape
        bytes_per_line = 3 * w
        qimage = QImage(im_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return frame, QPixmap.fromImage(qimage).scaled(
            target_size,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
        )
