from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QComboBox, QPushButton


class PlayerControlsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(60)

        self.main_layout = QHBoxLayout(self)

        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.speed_dropdown = QComboBox()
        self.speed_dropdown.addItems(["1x", "2x", "5x"])
        self.speed_dropdown.setObjectName("speedComboBox")

        self.restart_button = QPushButton()
        self.restart_button.setFixedSize(25, 25)
        self.restart_button.setObjectName("RestartBtn")
        self.prev_button = QPushButton()
        self.prev_button.setFixedSize(25, 25)
        self.prev_button.setObjectName("PrevBtn")
        self.play_button = QPushButton()
        self.play_button.setFixedSize(35, 35)
        self.play_button.setIcon(QIcon("./resources/style/icons/play.png"))
        self.play_button.setIconSize(QSize(15, 15))
        self.play_button.setObjectName("play_button")
        self.next_button = QPushButton()
        self.next_button.setFixedSize(25, 25)
        self.next_button.setObjectName("NextBtn")
        self.toggle_interaction_button = QPushButton()
        self.toggle_interaction_button.setFixedSize(25, 25)
        self.toggle_interaction_button.setObjectName("InvestigateBtn")
        self.toggle_render_button = QPushButton()
        self.toggle_render_button.setFixedSize(25, 25)
        self.toggle_render_button.setObjectName("PotentialBtn")

        self.main_layout.addStretch(2)
        self.main_layout.addWidget(self.speed_dropdown)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.restart_button)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.prev_button)
        self.main_layout.addWidget(self.play_button)
        self.main_layout.addWidget(self.next_button)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.toggle_interaction_button)
        self.main_layout.addStretch(1)
        self.main_layout.addWidget(self.toggle_render_button)
        self.main_layout.addStretch(2)
