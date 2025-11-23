from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy)

class TopBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(29, 0, 29, 0)
        layout.setSpacing(20)

        self.logo = QWidget()
        self.logo.setFixedSize(50, 50)

        self.project_name = QLabel("Cardiomaton")

        self.btn_app = QPushButton("App")
        self.btn_help = QPushButton("Help")
        self.btn_about = QPushButton("About us")

        layout.addWidget(self.logo)
        layout.addWidget(self.project_name)
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addWidget(self.btn_app)
        layout.addWidget(self.btn_help)
        layout.addWidget(self.btn_about)