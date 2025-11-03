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

        self.highlighted_cells = [set()]

        self.setStyleSheet("""
            QToolTip {
                background-color: #cfe3fc;
                padding: 12px;
            }
        """)

    def paintEvent(self, event):
        """Rysuje podstawowy pixmap, a następnie półprzezroczyste podświetlenie."""
        super().paintEvent(event)
        if not self.highlighted_cells or self.pixmap() is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # kolor półprzezroczysty (np. jasnoniebieski)
        brush = QBrush(QColor(109, 152, 244, 100))  # RGBA — 100 to przezroczystość
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)

        rows, cols = self.renderer.ctrl.shape
        pixmap = self.pixmap()
        pixmap_size = pixmap.size()
        label_size = self.size()

        # dopasowanie rozmiaru komórki do aktualnego wyświetlenia
        cell_width = pixmap_size.width() / cols
        cell_height = pixmap_size.height() / rows

        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2

        # narysuj wszystkie zaznaczone komórki
        for i, h in enumerate(self.highlighted_cells):
            for (r, c) in h:
                color = self.get_color(i)
                color.setAlpha(55)
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
                if pos and self.renderer.current_data:
                    cell_info = self.renderer.current_data.get(pos)
                    if cell_info:
                        self.cellClicked.emit(cell_info)
        else:
            self._paint_cells(self._mouse_position(event))

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
            return

        pos = self._mouse_position(event)
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._paint_cells(pos, add=True)
        elif event.buttons() & Qt.MouseButton.RightButton:
            self._paint_cells(pos, add=False)
        # """
        # Show tooltip only if the mouse moves to a new cell.
        # Tooltip remains visible as long as the mouse stays over the same cell.
        # """
        # if self.running or self.pixmap() is None:
        #     return
        #
        # pos = self._mouse_position(event)
        # if pos is None and self.last_tooltip is not None:
        #     QToolTip.hideText()
        #     self.last_tooltip = None
        #
        #
        # data = self.renderer.current_data
        # if data is not None and self.last_tooltip != pos:
        #     cell_info = data.get(pos)
        #     if cell_info is not None:
        #         self._show_cell_info(cell_info, event.globalPosition().toPoint(), pos, False)
        #         self.last_tooltip = pos
        #     else:
        #         QToolTip.hideText()
        #         self.last_tooltip = None

    # def _paint_cells(self, pos, add = True):
    #     if pos is None:
    #         return
    #     radius = self.brush_size_slider
    #     brush_obj = self.cell_modificator
    #     row, col = pos
    #     pixmap = self.pixmap()
    #     pixmap_size = pixmap.size()
    #
    #     if brush_obj is None:
    #         return
    #
    #     for i in range(row - radius, row + radius + 1):
    #         for j in range(col - radius, col + radius + 1):
    #             if 0 <= i < pixmap_size.width() and 0 <= j < pixmap_size.height():
    #                 if (i - row) ** 2 + (j - col) ** 2 <= radius ** 2:
    #
    #                     if add:
    #                         brush_obj.add_cells((i, j))
    #                         payload = self.renderer.current_data.get((i,j))
    #                         if payload is not None:
    #                             payload["state_value"] = 5
    #                             self.renderer.ctrl.update_cell(payload)
    #                     else:
    #                         brush_obj.remove_cells((i, j))
    def _paint_cells(self, pos, add=True):
        if pos is None:
            return
        radius = self.brush_size_slider
        brush_obj = self.cell_modificator
        row, col = pos
        rows, cols = self.renderer.ctrl.shape

        if brush_obj is None:
            return

        for i in range(row - radius, row + radius + 1):
            for j in range(col - radius, col + radius + 1):
                if 0 <= i < rows and 0 <= j < cols:
                    if (i - row) ** 2 + (j - col) ** 2 <= radius ** 2:
                        if add:
                            brush_obj.add_cells((i, j))
                            self.highlighted_cells[-1].add((i, j))
                        else:
                            brush_obj.remove_cells((i, j))
                            self.highlighted_cells[-1].discard((i, j))

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

    def new_highlight(self):
        self.highlighted_cells.append(set())

    def undo_highlight(self):
        self.highlighted_cells.pop(-1)
        if len(self.highlighted_cells) == 0: self.highlighted_cells.append(set())
        self.update()

    def get_color(self, index, total=10):
        hue = int((index % total) * 360 / total)
        return QColor.fromHsv(hue, 255, 255, 128)
