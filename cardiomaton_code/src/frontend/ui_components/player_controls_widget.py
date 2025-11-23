from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QComboBox, QPushButton

class PlayerControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setSpacing(40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.speed_dropdown = QComboBox()
        self.speed_dropdown.addItems(["1x", "2x", "3x"])

        self.prev_button = QPushButton("❮❮")
        self.play_button = QPushButton("▶")
        self.next_button = QPushButton("❯❯")
        self.toggle_render_button = QPushButton("↯")

        layout.addWidget(self.speed_dropdown)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.toggle_render_button)