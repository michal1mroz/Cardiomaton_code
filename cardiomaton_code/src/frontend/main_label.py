from typing import Tuple, Union
from PyQt6.QtWidgets import QLabel, QToolTip
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent

from src.models.cell import CellDict
from src.frontend.frame_renderer import FrameRenderer


class MainLabel(QLabel):
    """
    QLabel subclass that displays an image rendered by FrameRenderer and shows
    detailed information about cells under the mouse cursor.

    """
    cellClicked = pyqtSignal(object)

    def __init__(self, renderer: FrameRenderer, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.running = False
        self.last_tooltip = None

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
        if self.pixmap() is None:
            return

        pos = self._mouse_position(event)
        if pos:
            cell_info = self.renderer.get_cell_data(pos)
            if cell_info:
                self.cellClicked.emit(cell_info)


    def mouseMoveEvent(self, event: QMouseEvent):
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

        if self.last_tooltip != pos:
            cell_info = self.renderer.get_cell_data(pos)
            if cell_info is not None:
                self._show_cell_info(cell_info, event.globalPosition().toPoint(), pos, False)
                self.last_tooltip = pos
            else:
                QToolTip.hideText()
                self.last_tooltip = None

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
