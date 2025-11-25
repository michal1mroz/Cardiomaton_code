from typing import Tuple, Optional

from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMouseEvent

class CellCoordinateMapper:
    def __init__(self, simulation_size: Tuple[int, int]) -> None:
        self._simulation_size = simulation_size

    def map_event_to_cell(self, label: QLabel, event: QMouseEvent) -> Optional[Tuple[int, int]]:
        pixmap = label.pixmap()
        if pixmap is None:
            return None

        pixmap_size = pixmap.size()
        label_size = label.size()

        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2

        x = event.position().x() - offset_x
        y = event.position().y() - offset_y

        if x < 0 or y < 0 or x >= pixmap_size.width() or y >= pixmap_size.height():
            return None

        rows, cols = self._simulation_size
        col = int(x / pixmap_size.width() * cols)
        row = int(y / pixmap_size.height() * rows)

        if 0 <= row < rows and 0 <= col < cols:
            return row, col
        return None