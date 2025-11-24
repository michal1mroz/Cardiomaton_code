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
        self.plot_curve = self.plot_widget.plot(pen=pq.mkPen(color='#CD4B48', width=2))
        self.plot_widget.setBackground('#303742')
        axis_color = (230, 234, 240)
        self.plot_widget.getAxis('left').setTextPen(axis_color)
        self.plot_widget.getAxis('bottom').setTextPen(axis_color)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getPlotItem().getViewBox().setBorder(None)
        self.plot_widget.setTitle('Charge over time', color="#E6EAF0", )
        self.plot_widget.setLabel("left", y_label)
        self.plot_widget.setLabel("bottom", x_label)
        self.plot_widget.showGrid(x=True, y=True)

        layout.addWidget(self.plot_widget)

    def add(self, value: float) -> None:
        self._buffer.add(value)
        self._update()

    def _update(self) -> None:
        x, y = self._buffer.xy()
        self.plot_curve.setData(x=x, y=y)
