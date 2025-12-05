from typing import Tuple

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtCore import QRectF

class CellHighlightPainter:
    def __init__(self, simulation_size: Tuple[int, int], cell_modificator) -> None:
        self._simulation_size = simulation_size
        self._cell_modificator = cell_modificator
        self.brushes = [QBrush(self._get_color(i)) for i in range(10)]

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

        default_brush = QBrush(QColor(109, 152, 244, 100))
        painter.setBrush(default_brush)
        painter.setPen(Qt.PenStyle.NoPen)

        highlights = self._cell_modificator.get_highlights()

        for (r, c), history in highlights.items():
            if not history:
                continue
            painter.setBrush(self.brushes[history[-1] % 10])

            x = offset_x + c * cell_width
            y = offset_y + r * cell_height
            painter.drawRect(QRectF(x, y, cell_width, cell_height))

    @staticmethod
    def _get_color(index):
        fixed_colors = [
            QColor.fromHsv(0, 255, 180),
            QColor.fromHsv(108, 255, 180),
            QColor.fromHsv(180, 255, 180),
            QColor.fromHsv(252, 255, 180),
            QColor.fromHsv(324, 255, 180),
        ]

        color = fixed_colors[index % len(fixed_colors)]
        return color