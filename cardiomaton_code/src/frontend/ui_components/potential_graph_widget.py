from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QFont, QResizeEvent, QColor
from PyQt6.QtCore import pyqtProperty, Qt
import pyqtgraph as pg
import pyqtgraph as pq


class GraphWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GraphContainer")

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._current_title_text = "Preview"
        self._trace_color = QColor('#CD4B48')
        self._axis_color = QColor('#6c7c91')
        self._title_color = QColor('#233348')
        self._font_family = "Mulish"

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getPlotItem().getViewBox().setBorder(None)

        self.tick_font = QFont(self._font_family, 10)

        self._apply_axis_styles()

        self.curve = self.plot_widget.plot(pen=pg.mkPen(color=self._trace_color, width=2))
        layout.addWidget(self.plot_widget)

        self.close_btn = QtWidgets.QPushButton("X", self)
        self.close_btn.setObjectName("GraphCloseBtn")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        padding_x = 10
        padding_y = 10
        x = self.width() - self.close_btn.width() - padding_x
        y = padding_y
        self.close_btn.move(x, y)
        self.close_btn.raise_()

    def update_data(self, t, v, title="Preview"):
        self._current_title_text = title
        self._refresh_title()
        self.curve.setData(t, v)

    def _refresh_title(self):
        self.plot_widget.setTitle(
            self._current_title_text,
            color=self._title_color.name(),
            size="11pt",
            **{'font-family': self._font_family}
        )

    def _apply_axis_styles(self):
        label_styles = {
            'color': self._axis_color.name(),
            'font-size': '10pt',
            'font-family': self._font_family
        }

        left_axis = self.plot_widget.getAxis('left')
        left_axis.setTextPen(self._axis_color)
        left_axis.setTickFont(self.tick_font)
        self.plot_widget.setLabel('left', 'Voltage (mV)', **label_styles)

        bottom_axis = self.plot_widget.getAxis('bottom')
        bottom_axis.setTextPen(self._axis_color)
        bottom_axis.setTickFont(self.tick_font)
        self.plot_widget.setLabel('bottom', 'Time (s)', **label_styles)

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
        self.curve.setPen(pg.mkPen(color=color, width=2))

    @pyqtProperty(QColor)
    def axisColor(self):
        return self._axis_color

    @axisColor.setter
    def axisColor(self, color: QColor):
        self._axis_color = color
        self._apply_axis_styles()

    @pyqtProperty(QColor)
    def titleColor(self):
        return self._title_color

    @titleColor.setter
    def titleColor(self, color: QColor):
        self._title_color = color
        self._refresh_title()
