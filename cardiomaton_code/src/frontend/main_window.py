import os

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QStackedWidget, QLabel)

from src.frontend.simulation_window import SimulationWindow
from src.frontend.ui_components.top_bar_widget import TopBarWidget
from src.frontend.ui_components.ui_factory import UIFactory


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(1100, 600)
        self.setMinimumSize(QSize(1100, 600))
        self.setMaximumSize(QSize(1100, 600))
        self.setWindowTitle("Cardiomaton")

        UIFactory.load_fonts()

        self.dark_mode = False
        self.accessibility_mode = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.topbar = TopBarWidget()
        self.main_layout.addWidget(self.topbar)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self._init_views()
        self._connect_topbar()
        self._apply_style()

    def _init_views(self):
        self.simulation_window = SimulationWindow()
        self.stack.addWidget(self.simulation_window)

        self.help_view = QWidget()
        lbl_help = QLabel("Tutaj będzie pomoc", self.help_view)
        lbl_help.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_help.setStyleSheet("font-size: 20px; color: gray;")
        help_layout = QVBoxLayout(self.help_view)
        help_layout.addWidget(lbl_help)
        self.stack.addWidget(self.help_view)

        self.about_view = QWidget()
        lbl_about = QLabel("O nas", self.about_view)
        lbl_about.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout = QVBoxLayout(self.about_view)
        about_layout.addWidget(lbl_about)
        self.stack.addWidget(self.about_view)

    def _connect_topbar(self):
        self.topbar.btn_app.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.topbar.btn_help.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.topbar.btn_about.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        self.topbar.btn_theme.clicked.connect(self._toggle_theme)
        self.topbar.btn_access.clicked.connect(self._toggle_accessibility_mode)

    def _toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.accessibility_mode = False
        self._apply_style()

    def _toggle_accessibility_mode(self):
        self.accessibility_mode = not self.accessibility_mode
        self.dark_mode = False
        self._apply_style()

    def _apply_style(self):
        if self.accessibility_mode:
            path = "./resources/style/accessibility_mode.qss"
            icon_text = "☾"
            access_text = "◎"
        elif self.dark_mode:
            path = "./resources/style/dark_mode.qss"
            icon_text = "☀"
            access_text = "◉"
        else:
            path = "./resources/style/light_mode.qss"
            icon_text = "☾"
            access_text = "◉"

        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as f:
                style = f.read()
                self.setStyleSheet(style)
        else:
            print(f"Warning: Style file not found at {path}")

        self.topbar.btn_theme.setText(icon_text)
        self.topbar.btn_access.setText(access_text)