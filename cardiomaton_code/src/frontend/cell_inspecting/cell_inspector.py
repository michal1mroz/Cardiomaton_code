from typing import Optional, Iterable

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy

from src.frontend.cell_inspecting.cell_details import CellDetails
from src.frontend.cell_inspecting.series_plot import SeriesPlot
from src.frontend.ui_components.ui_factory import UIFactory
from src.models.cell import CellDict

class CellInspector(QWidget):
    def __init__(self, cell_data: CellDict, on_close_callback, running: bool, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.position = cell_data["position"]
        self._running = running
        self._on_close_callback = on_close_callback
        self._data: CellDict = cell_data.copy()

        self._editable_keys: Iterable[str] = []

        self._root = QVBoxLayout()
        self.setLayout(self._root)

        self._details = CellDetails(editable_keys=self._editable_keys, parent=self)
        self._plot = SeriesPlot(title="Charge over time", y_label="Charge", x_label="Time [Frames]", maxlen=500,
                                parent=self)

        self._init_ui()

        self._details.set_running(self._running)
        self._details.set_data(self._data)

    def update(self, cell_data: CellDict) -> None:
        self._data = cell_data.copy()
        self._details.set_data(self._data)

        charge = self._data.get("charge", None)
        if charge is not None:
            self._plot.add(charge)

    def set_running(self, running: bool) -> None:
        if self._running != running:
            self._running = running
            self._details.set_running(self._running)

    def close_inspector(self) -> None:
        if self._on_close_callback:
            self._on_close_callback()

    def _init_ui(self) -> None:
        self._root.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        top.setContentsMargins(0, 15, 0, 0)
        top.addStretch()

        close_btn = UIFactory.create_pushbutton(self)
        close_btn.setFixedSize(30, 30)
        close_btn.setObjectName("CloseBtn")
        close_btn.setIcon(QIcon("./resources/style/icons/cancel.png"))
        close_btn.setIconSize(QSize(14, 14))
        close_btn.clicked.connect(self.close_inspector)
        top.addWidget(close_btn)
        self._root.addLayout(top)
        self._root.addWidget(self._details)
        self._root.addWidget(self._plot)

