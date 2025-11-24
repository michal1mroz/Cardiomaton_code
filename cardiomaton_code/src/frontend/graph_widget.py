from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QFont, QResizeEvent
import pyqtgraph as pg


class GraphWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GraphContainer")

        font_family = "Mulish"
        base_font_size = 10
        self.tick_font = QFont(font_family, base_font_size)
        self.label_styles = {
            'color': '#E6EAF0',
            'font-size': '10pt',
            'font-family': font_family
        }

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#181C23')

        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.getPlotItem().getViewBox().setBorder(None)

        axis_pen_color = (230, 234, 240)

        left_axis = self.plot_widget.getAxis('left')
        left_axis.setTextPen(axis_pen_color)
        left_axis.setTickFont(self.tick_font)
        self.plot_widget.setLabel('left', 'Voltage (mV)', **self.label_styles)

        bottom_axis = self.plot_widget.getAxis('bottom')
        bottom_axis.setTextPen(axis_pen_color)
        bottom_axis.setTickFont(self.tick_font)
        self.plot_widget.setLabel('bottom', 'Time (s)', **self.label_styles)

        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='#CD4B48', width=2))
        layout.addWidget(self.plot_widget)

        self.close_btn = QtWidgets.QPushButton("X", self)
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide)

        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #5E83F2;
                color: white;
                border-radius: 12px;
                font-weight: bold;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #496BD3;
            }
        """)

        self.setStyleSheet("""
            #GraphContainer {
                background-color: #181C23;
                border-radius: 20px;
            }
        """)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        padding_x = 10
        padding_y = 10
        x = self.width() - self.close_btn.width() - padding_x
        y = padding_y
        self.close_btn.move(x, y)
        self.close_btn.raise_()

    def update_data(self, t, v, title="Preview"):
        self.plot_widget.setTitle(
            title,
            color="#E6EAF0",
            size="11pt",
            **{'font-family': 'Mulish'}
        )
        self.curve.setData(t, v)