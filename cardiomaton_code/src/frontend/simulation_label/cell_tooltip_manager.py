from typing import Tuple, Optional

from PyQt6.QtWidgets import QLabel, QToolTip
from PyQt6.QtGui import QMouseEvent


from src.frontend.simulation_label.cell_data_provider import CellDataProvider
from src.models.cell import CellDict

class CellTooltipManager:
    def __init__(self, cell_data_provider: CellDataProvider, debug: bool = False) -> None:
        self._cell_data_provider = cell_data_provider
        self._debug = debug
        self._last_cell: Optional[Tuple[int, int]] = None

    def handle_mouse_move(self, widget: QLabel, pos: Optional[Tuple[int, int]], event: QMouseEvent) -> None:
        if widget.pixmap() is None:
            self.hide()
            return

        if pos is None:
            if self._last_cell is not None:
                self.hide()
            return

        if pos == self._last_cell:
            return

        cell_info: Optional[CellDict] = self._cell_data_provider.get_cell_data(pos)
        if cell_info is not None:
            text = self._build_tooltip_text(cell_info, pos)
            QToolTip.showText(event.globalPosition().toPoint(), text, widget)
            self._last_cell = pos
        else:
            self.hide()

    def hide(self) -> None:
        QToolTip.hideText()
        self._last_cell = None

    def _build_tooltip_text(self, info: CellDict, pos: Tuple[int, int]) -> str:
        is_self_polarizing = "Tak" if info["auto_polarization"] else "Nie"
        polarization_state = info["state_name"]
        voltage = info["charge"]
        ccs_part = info["ccs_part"]

        if self._debug:
            return (
                f"<b>Pozycja:<b> {pos}<br><br>"
                f"<b>Samopolaryzacja:</b> {is_self_polarizing}<br>"
                f"<b>Stan polaryzacji:</b> {polarization_state}<br><br>"
                f"<b>Napięcie:</b> {voltage}<br>"
                f"<b>Rodzaj komórki:</b> (placeholder)<br>"
                f"<b>Część układu przewodzącego:</b> {ccs_part}"
            )

        return f"""
        <div style='font-family:Mulish;font-size:11pt;color:#233348;'>
            <b>Location:</b> {ccs_part.replace('_', ' ')}<br><br>
            <b>Current state:</b> {polarization_state.replace('_', ' ')}<br><br>
            <b>Current voltage:</b> {voltage:.0f} mV<br>
        </div>
        <b style='font-family:Mulish;font-size:1pt;color:#ffffff;'>{pos}</b>
        """
