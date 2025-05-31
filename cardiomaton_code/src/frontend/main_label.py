from PyQt6.QtWidgets import QLabel, QToolTip
from PyQt6.QtCore import Qt

from src.frontend.frame_renderer import FrameRenderer


class MainLabel(QLabel):
    """
    QLabel subclass that displays an image rendered by FrameRenderer and shows
    detailed information about cells under the mouse cursor.

    """
    def __init__(self, renderer: FrameRenderer, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

        self.running = False

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setScaledContents(False)
        self.setMinimumSize(1, 1)
        self.setStyleSheet("background-color: navy;border: 2px solid black;")

        self.last_tooltip = None

    def mouseMoveEvent(self, event):
        """
        Handles mouse move events to show tooltips with cell information
        when hovering over the pixmap.

        """
        if not self.pixmap() or self.running:
            return

        pixmap_size = self.pixmap().size()
        label_size = self.size()

        offset_x = (label_size.width() - pixmap_size.width()) / 2
        offset_y = (label_size.height() - pixmap_size.height()) / 2

        x = event.position().x() - offset_x
        y = event.position().y() - offset_y

        if x < 0 or y < 0 or x >= pixmap_size.width() or y >= pixmap_size.height():
            return

        data = self.renderer.last_data
        if data is None:
            return

        rows = len(data)
        cols = len(data[0])

        col = int(x / pixmap_size.width() * cols)
        row = int(y / pixmap_size.height() * rows)

        if 0 <= row < rows and 0 <= col < cols:
            cell_info = data[row][col]
            if cell_info is not None:
                if self.last_tooltip != (row, col):
                    QToolTip.hideText()
                    self.show_cell_info(cell_info, event.globalPosition().toPoint())
                    self.last_tooltip = (row, col)
        else:
            QToolTip.hideText()
    def show_cell_info(self, info, global_pos):
        """
        Shows information about cell at the given global position.
        """
        is_self_polarizing = "Tak" if info[1] else "Nie"
        polarization_state = info[2]

        voltage = "200 Volt (placeholder)"
        cell_type = "Komórka rozrusznikowa (placeholder)"
        ccs_part = "pęczek Hisa (placeholder)"

        text = (
            f"<b>Samopolaryzacja:</b> {is_self_polarizing}<br>"
            f"<b>Stan polaryzacji:</b> {polarization_state}<br><br>"
            f"<b>Napięcie:</b> {voltage}<br>"
            f"<b>Rodzaj komórki:</b> {cell_type}<br>"
            f"<b>Część układu przewodzącego:</b> {ccs_part}"
        )

        QToolTip.showText(global_pos, text, self)

    def set_running(self, state):
        self.running = state