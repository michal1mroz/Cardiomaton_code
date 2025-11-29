from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QComboBox, QPushButton


class PlayerControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QHBoxLayout(self)

        self.main_layout.setSpacing(40)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.speed_dropdown = QComboBox()
        self.speed_dropdown.addItems(["1x", "2x", "3x"])

        self.prev_button = QPushButton("❮❮")
        self.prev_button.setObjectName("ControlBtn")
        self.play_button = QPushButton("▶")
        self.play_button.setObjectName("play_button")
        self.next_button = QPushButton("❯❯")
        self.next_button.setObjectName("ControlBtn")
        self.toggle_render_button = QPushButton("↯")
        self.toggle_render_button.setObjectName("ToggleBtn")

        self.main_layout.addWidget(self.speed_dropdown)
        self.main_layout.addWidget(self.prev_button)
        self.main_layout.addWidget(self.play_button)
        self.main_layout.addWidget(self.next_button)
        self.main_layout.addWidget(self.toggle_render_button)