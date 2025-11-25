from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtProperty, Qt
from PyQt6.QtGui import QColor
from src.frontend.cell_inspecting.series_buffer import SeriesBuffer
import pyqtgraph as pq


class SeriesPlot(QWidget):
    def __init__(self, title: str, y_label: str, x_label: str, maxlen: int = 500,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._buffer = SeriesBuffer(maxlen=maxlen)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._current_title = title
        self._trace_color = QColor('#CD4B48')
        self._axis_color = QColor('#6c7c91')
        self._title_color = QColor('#233348')

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.plot_widget = pq.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle(self._current_title, color=self._title_color.name())
        self.plot_widget.setLabel("left", y_label)
        self.plot_widget.setLabel("bottom", x_label)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getPlotItem().getViewBox().setBorder(None)

        self.plot_curve = self.plot_widget.plot(pen=pq.mkPen(color=self._trace_color, width=2))

        self.plot_widget.getAxis('left').setTextPen(self._axis_color)
        self.plot_widget.getAxis('bottom').setTextPen(self._axis_color)

        layout.addWidget(self.plot_widget)

    def add(self, value: float) -> None:
        self._buffer.add(value)
        self._update()

    def _update(self) -> None:
        x, y = self._buffer.xy()
        self.plot_curve.setData(x=x, y=y)

    @pyqtProperty(QColor)
    def plotBackground(self):
        return self.plot_widget.backgroundBrush().color()

    @plotBackground.setter
    def plotBackground(self, color: QColor):
        self.plot_widget.setBackground(color)

    @pyqtProperty(QColor)
    def traceColor(self):
        return self._trace_color

    @traceColor.setter
    def traceColor(self, color: QColor):
        self._trace_color = color
        self.plot_curve.setPen(pq.mkPen(color=color, width=2))

    @pyqtProperty(QColor)
    def axisColor(self):
        return self._axis_color

    @axisColor.setter
    def axisColor(self, color: QColor):
        self._axis_color = color
        self.plot_widget.getAxis('left').setTextPen(color)
        self.plot_widget.getAxis('bottom').setTextPen(color)
        styles = {'color': color.name()}
        self.plot_widget.getPlotItem().getAxis('left').setLabel(**styles)
        self.plot_widget.getPlotItem().getAxis('bottom').setLabel(**styles)

    @pyqtProperty(QColor)
    def titleColor(self):
        return self._title_color

    @titleColor.setter
    def titleColor(self, color: QColor):
        self._title_color = color
        self.plot_widget.setTitle(self._current_title, color=color.name())