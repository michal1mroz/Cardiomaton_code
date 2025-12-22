from typing import Tuple

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtCore import QRectF

class CellHighlightPainter:
    def __init__(self, simulation_size: Tuple[int, int], cell_modificator) -> None:
        self._simulation_size = simulation_size
        self._cell_modificator = cell_modificator
        self.brush = QColor(57, 255, 20, 150)

    def paint_highlights(self, painter: QPainter, label: QLabel) -> None:
        pixmap = label.pixmap()
        if pixmap is None:
            return

        rows, cols = self._simulation_size
        pixmap_size = pixmap.size()
        label_size = label.size()

        cell_width = pixmap_size.width() / cols
        cell_height = pixmap_size.height() / rows

        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2

        painter.setBrush(self.brush)
        painter.setPen(Qt.PenStyle.NoPen)

        highlights = self._cell_modificator.get_highlights()

        for (r, c), history in highlights.items():
            if not history:
                continue
            painter.setBrush(self.brush)

            x = offset_x + c * cell_width
            y = offset_y + r * cell_height
            painter.drawRect(QRectF(x, y, cell_width, cell_height))
