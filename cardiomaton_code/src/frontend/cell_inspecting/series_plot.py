from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from src.frontend.cell_inspecting.series_buffer import SeriesBuffer
import pyqtgraph as pq

class SeriesPlot(QWidget):
    def __init__(self, title: str, y_label: str, x_label: str, maxlen: int = 500,
                 parent: Optional[QWidget] = None ) -> None:
        super().__init__(parent)

        self._buffer = SeriesBuffer(maxlen=maxlen)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.plot_widget = pq.PlotWidget()
        self.plot_widget.setBackground("w")
        self.plot_widget.setTitle(title)
        self.plot_widget.setLabel("left", y_label)
        self.plot_widget.setLabel("bottom", x_label)
        self.plot_widget.showGrid(x=True, y=True)

        self.plot_curve = self.plot_widget.plot(pen=pq.mkPen(color="r", width=2))

        layout.addWidget(self.plot_widget)

    def add(self, value: float) -> None:
        self._buffer.add(value)
        self._update()

    def _update(self) -> None:
        x, y = self._buffer.xy()
        self.plot_curve.setData(x=x, y=y)
