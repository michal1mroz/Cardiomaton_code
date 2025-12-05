from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt

from src.frontend.ui_components.ui_factory import UIFactory


class TopBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(80)

        self.setObjectName("TopBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(29, 20, 29, 20)
        layout.setSpacing(20)

        self.logo = QWidget()
        self.logo.setFixedSize(40, 40)
        self.logo.setObjectName("Logo")

        self.project_name = QLabel("Cardiomaton")
        self.project_name.setObjectName("ProjectName")

        self.btn_app = UIFactory.create_pushbutton(self)
        self.btn_app.setText("App")
        self.btn_app.setObjectName("BtnApp")

        self.btn_help = UIFactory.create_pushbutton(self)
        self.btn_help.setText("Help")
        self.btn_help.setObjectName("BtnHelp")

        self.btn_about = UIFactory.create_pushbutton(self)
        self.btn_about.setText("About us")
        self.btn_about.setObjectName("BtnAbout")

        self.btn_theme = UIFactory.create_pushbutton(self)
        self.btn_theme.setText("☀")
        self.btn_theme.setObjectName("BtnTheme")
        self.btn_theme.setFixedWidth(40)

        self.btn_access = UIFactory.create_pushbutton(self)
        self.btn_access.setText("◉")
        self.btn_access.setObjectName("BtnAccess")
        self.btn_access.setFixedWidth(40)

        layout.addWidget(self.logo)
        layout.addWidget(self.project_name)
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addWidget(self.btn_app)
        layout.addWidget(self.btn_help)
        layout.addWidget(self.btn_about)
        layout.addWidget(self.btn_theme)
        layout.addWidget(self.btn_access)

        layout.setStretch(0, 1)
        layout.setStretch(1, 1)
        layout.setStretch(2, 4)
        layout.setStretch(3, 1)
        layout.setStretch(4, 1)
        layout.setStretch(5, 1)
        layout.setStretch(6, 0)