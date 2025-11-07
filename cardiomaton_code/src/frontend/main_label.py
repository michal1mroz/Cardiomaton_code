from typing import Tuple, Union
from PyQt6.QtWidgets import QLabel, QToolTip
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from src.models.cell import CellDict
from src.frontend.frame_renderer import FrameRenderer

from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import QRectF



class MainLabel(QLabel):
    """
    QLabel subclass that displays an image rendered by FrameRenderer and shows
    detailed information about cells under the mouse cursor.

    """
    cellClicked = pyqtSignal(object)

    def __init__(self, renderer: FrameRenderer, brush_size_slider, cell_modificator, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.running = False
        self.last_tooltip = None

        self.cell_modificator = cell_modificator
        self.brush_size_slider = brush_size_slider

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

    def paintEvent(self, event):
        """Draws automaton pixmap and then cell modification highlights"""
        super().paintEvent(event)
        if self.pixmap() is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        brush = QBrush(QColor(109, 152, 244, 100))  # deafult color
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)

        rows, cols = self.renderer.ctrl.shape
        pixmap = self.pixmap()
        pixmap_size = pixmap.size()
        label_size = self.size()

        cell_width = pixmap_size.width() / cols
        cell_height = pixmap_size.height() / rows

        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2

        for i, h in enumerate(self.cell_modificator.get_highlights()):
            for (r, c) in h:
                color = self.cell_modificator.get_color(i)
                brush = QBrush(color)
                painter.setBrush(brush)
                x = offset_x + c * cell_width
                y = offset_y + r * cell_height
                rect = QRectF(x, y, cell_width, cell_height)
                painter.drawRect(rect)

        painter.end()
    def _mouse_position(self, event: QMouseEvent) -> Union[None, Tuple[int, int]]:
        """
        Helper method to get the mouse position in term of pixmaps rows and columns.
        
        Args:
            event (QMouseEvent): Callback event from the mouse action
        Returns:
            Tuple[int, int] or None: position on the pixmap (row, col) 
                or None if there's no pixmap / mouse is outside of it
        """
        pixmap = self.pixmap()
        if pixmap is None:
            return None

        pixmap_size = pixmap.size()
        label_size = self.size()

        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2

        x = event.position().x() - offset_x
        y = event.position().y() - offset_y

        if 0 > x or x >= pixmap_size.width() or 0 > y  or y >= pixmap_size.height():
            return None

        rows, cols = self.renderer.ctrl.shape
        col = int(x / pixmap_size.width() * cols)
        row = int(y / pixmap_size.height() * rows)

        return (row, col) if (0 <= row < rows and 0 <= col < cols) else None
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.running:
            if self.pixmap() is None:
                return
            else:
                pos = self._mouse_position(event)
                if pos:
                    cell_info = self.renderer.ctrl.get_cell_data(pos)
                    if cell_info:
                        self.cellClicked.emit(cell_info)
        else:
            # self._paint_cells(self._mouse_position(event))

            pos = self._mouse_position(event)
            if event.button() == Qt.MouseButton.LeftButton:
                self._paint_cells(pos, add=True)
            elif event.button() == Qt.MouseButton.RightButton:
                self._paint_cells(pos, add=False)
        # if self.pixmap() is None:
        #     return
        #
        # pos = self._mouse_position(event)
        # if pos and self.renderer.current_data:
        #     cell_info = self.renderer.current_data.get(pos)
        #     if cell_info:
        #         self.cellClicked.emit(cell_info)


    def mouseMoveEvent(self, event: QMouseEvent):
        if self.running or self.pixmap() is None:
            if self.pixmap() is not None:
                """
                Show tooltip only if the mouse moves to a new cell.
                Tooltip remains visible as long as the mouse stays over the same cell.
                """
                if self.running or self.pixmap() is None:
                    return

                pos = self._mouse_position(event)
                if pos is None and self.last_tooltip is not None:
                    QToolTip.hideText()
                    self.last_tooltip = None


                data = self.renderer.current_data
                if data is not None and self.last_tooltip != pos:
                    cell_info = data.get(pos)
                    if cell_info is not None:
                        self._show_cell_info(cell_info, event.globalPosition().toPoint(), pos, False)
                        self.last_tooltip = pos
                    else:
                        QToolTip.hideText()
                        self.last_tooltip = None
            return
        else:
            pos = self._mouse_position(event)
            if event.buttons() & Qt.MouseButton.LeftButton:
                self._paint_cells(pos, add=True)
            elif event.buttons() & Qt.MouseButton.RightButton:
                self._paint_cells(pos, add=False)


    def _paint_cells(self, pos, add=True):
        if pos is None:
            return
        radius = self.brush_size_slider
        row, col = pos
        rows, cols = self.renderer.ctrl.shape

        for i in range(row - radius, row + radius + 1):
            for j in range(col - radius, col + radius + 1):
                if 0 <= i < rows and 0 <= j < cols:
                    if (i - row) ** 2 + (j - col) ** 2 <= radius ** 2:
                        if add:
                            self.cell_modificator.add_cells((i, j))
                        else:
                            self.cell_modificator.remove_cells((i, j))

        self.update()
    def _show_cell_info(self, info, global_pos, pos, debug = False):
        """
        Shows information about cell at the given global position.
        """
        is_self_polarizing = "Tak" if info["auto_polarization"] else "Nie"
        polarization_state = info["state_name"]
        voltage = info["charge"]
        cell_type = "(placeholder)"
        ccs_part = info["ccs_part"]
        if debug: # I leave the old version because it may be useful for debugging, especially the position (MS)
            text = (
                f"<b>Pozycja:<b> {pos}<br><br>"
                f"<b>Samopolaryzacja:</b> {is_self_polarizing}<br>"
                f"<b>Stan polaryzacji:</b> {polarization_state}<br><br>"
                f"<b>Napięcie:</b> {voltage}<br>"
                f"<b>Rodzaj komórki:</b> {cell_type}<br>"
                f"<b>Część układu przewodzącego:</b> {ccs_part}"
            )
        else:
            text = f"""
            <div style='font-family:Mulish;font-size:11pt;color:#233348;'>
                <b>Location:</b> {ccs_part.replace('_', ' ')}<br><br>
                <b>Current state:</b> {polarization_state.replace('_', ' ')}<br><br>
                <b>Current voltage:</b> {voltage:.0f} mV<br>
            </div>
            """

        QToolTip.showText(global_pos, text, self)

    def leaveEvent(self, event):
        """
        Hide tooltip when mouse leaves the label.
        """
        QToolTip.hideText()
        self.last_tooltip = None
        super().leaveEvent(event)
    def set_running(self, state):
        self.running = state


