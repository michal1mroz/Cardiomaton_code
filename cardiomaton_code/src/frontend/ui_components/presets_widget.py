from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton

from src.frontend.ui_components.ui_factory import UIFactory


class PresetsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QHBoxLayout(self)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.label = UIFactory.create_label(self, "Select Preset", font_size=14)
        self.main_layout.addWidget(self.label)
        self.main_layout.addStretch(1)

        self.dropdown = QComboBox()
        self.dropdown.addItem("Preset 1")
        self.dropdown.addItem("Preset 2")
        self.dropdown.addItem("Custom")
        self.main_layout.addWidget(self.dropdown)
        self.dropdown.setObjectName("presetComboBox")
        self.main_layout.addStretch(1)

        self.button = UIFactory.create_pushbutton(self, font_size=15)
        self.button.setText("+")
        self.main_layout.addWidget(self.button)
        self.button.setObjectName("presetBtn")

        self.main_layout.setContentsMargins(30, 5, 30, 5)

        self.setLayout(self.main_layout)