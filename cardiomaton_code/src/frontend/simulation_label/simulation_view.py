from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPainter

from src.frontend.simulation_label.cell_brush import CellBrush
from src.frontend.simulation_label.cell_coordinate_mapper import CellCoordinateMapper
from src.frontend.simulation_label.cell_data_provider import CellDataProvider
from src.frontend.simulation_label.cell_highlight_painter import CellHighlightPainter
from src.frontend.simulation_label.cell_tooltip_manager import CellTooltipManager

class SimulationView(QLabel):
    cellClicked = pyqtSignal(object)

    def __init__(self, cell_data_provider: CellDataProvider, brush_size_slider, cell_modificator, parent=None) -> None:
        super().__init__(parent)

        self.cell_data_provider = cell_data_provider
        self.running = False

        self._cell_modificator = cell_modificator
        self._brush_size_slider = brush_size_slider

        simulation_shape = self.cell_data_provider.shape
        self._coordinate_mapper = CellCoordinateMapper(simulation_shape)
        self._brush = CellBrush(simulation_shape, cell_modificator, brush_size_slider)
        self._tooltip = CellTooltipManager(cell_data_provider, debug=False)
        self._highlight_painter = CellHighlightPainter(simulation_shape, cell_modificator)

        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setMinimumSize(1, 1)

        self.setStyleSheet("""
            QToolTip {
                background-color: #cfe3fc;
                padding: 12px;
            }
        """)

    def set_running(self, state: bool) -> None:
        self.running = state

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self.pixmap() is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._highlight_painter.paint_highlights(painter, self)
        painter.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.running:
            if self.pixmap() is None:
                return

            pos = self._coordinate_mapper.map_event_to_cell(self, event)
            if pos:
                cell_info = self.cell_data_provider.get_cell_data(pos)
                if cell_info:
                    self.cellClicked.emit(cell_info)
            return

        pos = self._coordinate_mapper.map_event_to_cell(self, event)
        if event.button() == Qt.MouseButton.LeftButton:
            self._brush.apply_brush(pos, add=True)
            self.update()
        elif event.button() == Qt.MouseButton.RightButton:
            self._brush.apply_brush(pos, add=False)
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self._coordinate_mapper.map_event_to_cell(self, event)

        if self.running or self.pixmap() is None:
            if self.pixmap() is not None:
                self._tooltip.handle_mouse_move(self, pos, event)
            return

        if event.buttons() & Qt.MouseButton.LeftButton:
            self._brush.apply_brush(pos, add=True)
            self.update()
        elif event.buttons() & Qt.MouseButton.RightButton:
            self._brush.apply_brush(pos, add=False)
            self.update()

    def leaveEvent(self, event) -> None:
        self._tooltip.hide()
        super().leaveEvent(event)