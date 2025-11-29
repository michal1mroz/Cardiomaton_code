import os
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QFontDatabase, QColor, QFont
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QSizePolicy, QGraphicsDropShadowEffect


class UIFactory:
    @staticmethod
    def load_fonts():
        fonts_dir = "resources/fonts"
        if os.path.exists(fonts_dir):
            for filename in os.listdir(fonts_dir):
                if filename.lower().endswith(".ttf"):
                    QFontDatabase.addApplicationFont(os.path.join(fonts_dir, filename))

    @staticmethod
    def add_shadow(widget: QWidget, blur: int = 30, offset_x: int = 2, offset_y: int = 2,
                   color: QColor = QColor(150, 150, 150, 100)) -> None:
        '''
        TODO: Customize shadows between dark and light modes
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(offset_x, offset_y)
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)
        '''

    @staticmethod
    def create_label(parent: QWidget, text: str = "", font_family: str = "Mulish",
                     font_size: int = 12, bold: bool = True) -> QLabel:
        label = QLabel(parent)
        font = QFont()
        font.setFamily(font_family)
        font.setPointSize(font_size)
        font.setBold(bold)
        label.setFont(font)
        label.setText(text)
        return label

    @staticmethod
    def create_pushbutton(parent: QWidget, font_family: str = "Mulish",
                          font_size: int = 13, bold: bool = True) -> QPushButton:
        pushbutton = QPushButton(parent)
        font = QFont()
        font.setFamily(font_family)
        font.setPointSize(font_size)
        font.setBold(bold)
        pushbutton.setFont(font)
        return pushbutton

    @staticmethod
    def create_widget(parent: QWidget) -> QWidget:
        widget = QWidget(parent)
        widget.setEnabled(True)
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        size_policy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(size_policy)
        return widget

    @staticmethod
    def create_slider(parent: QWidget) -> QtWidgets.QSlider:
        slider = QtWidgets.QSlider(parent)
        slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        return slider