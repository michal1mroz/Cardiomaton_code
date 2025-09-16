import os
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QFontDatabase, QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget


class UiMainWindow(object):
    def setup_ui(self, main_window):
        self.load_fonts()
        main_window.setObjectName("MainWindow")
        main_window.resize(1100, 600)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(main_window.sizePolicy().hasHeightForWidth())
        main_window.setSizePolicy(size_policy)
        main_window.setMinimumSize(QtCore.QSize(1100, 600))
        main_window.setMaximumSize(QtCore.QSize(1100, 600))
        main_window.setAutoFillBackground(False)
        main_window.setStyleSheet(
            "background-image: url(./resources/style/background.png);\n"
            "background-repeat: no-repeat;\n"
            "background-position: center;\n"
        )

        # Central widget
        self.centralwidget = self.create_widget(main_window)

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)

        # Main layout container
        self.layout = QtWidgets.QWidget(parent=self.centralwidget)
        self.layout.setEnabled(True)
        self.layout.setObjectName("layout")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.layout)
        self.verticalLayout.setObjectName("verticalLayout")

        # Upper layout
        self.upper_layout = QtWidgets.QWidget(parent=self.layout)
        self.upper_layout.setEnabled(True)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding
        )
        size_policy.setHeightForWidth(self.upper_layout.sizePolicy().hasHeightForWidth())
        self.upper_layout.setSizePolicy(size_policy)
        self.upper_layout.setStyleSheet("background: transparent;")
        self.upper_layout.setObjectName("upper_layout")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.upper_layout)
        self.horizontalLayout.setContentsMargins(29, -1, 29, -1)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Logo
        self.logo = QtWidgets.QWidget(parent=self.upper_layout)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.logo.sizePolicy().hasHeightForWidth())
        self.logo.setSizePolicy(size_policy)
        self.logo.setMinimumSize(QtCore.QSize(50, 50))
        self.logo.setMaximumSize(QtCore.QSize(50, 50))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Emoji")
        self.logo.setFont(font)
        self.logo.setStyleSheet("border-radius: 25px;\n"
                                "background-color: #6D98F4;\n"
                                "color: white;\n"
                                "font-size: 24px;\n"
                                "")
        self.logo.setObjectName("logo")
        self.add_shadow(self.logo)
        self.horizontalLayout.addWidget(self.logo)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.logo)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout.addWidget(self.logo)

        # Project name label
        self.project_name = self.create_label(self.upper_layout, "Cardiomaton", "Mulish ExtraBold", 22)
        self.horizontalLayout.addWidget(self.project_name)

        spacerItem = QtWidgets.QSpacerItem(
            40, 20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)

        # Upper buttons
        self.pushButton_app = self.create_pushbutton(self.upper_layout, font_family= "Mulish ExtraBold")
        self.horizontalLayout.addWidget(self.pushButton_app)

        self.pushButton_help = self.create_pushbutton(self.upper_layout)
        self.horizontalLayout.addWidget(self.pushButton_help)

        self.pushButton_about_us = self.create_pushbutton(self.upper_layout)
        self.horizontalLayout.addWidget(self.pushButton_about_us)

        # Stretch settings
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 4)
        self.horizontalLayout.setStretch(3, 1)
        self.horizontalLayout.setStretch(4, 1)
        self.horizontalLayout.setStretch(5, 1)

        self.verticalLayout.addWidget(self.upper_layout)

        # Bottom layout
        self.bottom_layout = QtWidgets.QWidget(parent=self.layout)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        size_policy.setHeightForWidth(self.bottom_layout.sizePolicy().hasHeightForWidth())
        self.bottom_layout.setSizePolicy(size_policy)
        self.bottom_layout.setStyleSheet("background-color: transparent;")
        self.bottom_layout.setObjectName("bottom_layout")

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.bottom_layout)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_3.setSpacing(40)

        # Settings layout
        self.settings_layout = QtWidgets.QWidget(parent=self.bottom_layout)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        size_policy.setHeightForWidth(self.settings_layout.sizePolicy().hasHeightForWidth())
        self.settings_layout.setSizePolicy(size_policy)
        self.settings_layout.setObjectName("settings_layout")

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.settings_layout)
        self.verticalLayout_2.setContentsMargins(20, 0, 12, 10)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        # Presets, parameters, players layouts
        self.presets_layout = QtWidgets.QWidget(parent=self.settings_layout)
        self.presets_layout.setStyleSheet(
            "background-color: white;\n"
            "border-radius: 20px;\n"
        )
        self.presets_layout.setObjectName("presets_layout")
        self.add_shadow(self.presets_layout)
        self.verticalLayout_2.addWidget(self.presets_layout)

        self.parameters_layout = QtWidgets.QWidget(parent=self.settings_layout)
        self.parameters_layout.setStyleSheet(
            "background-color: white;\n"
            "border-radius: 20px;\n"
        )
        self.parameters_layout.setObjectName("parameters_layout")
        self.add_shadow(self.parameters_layout)
        self.verticalLayout_2.addWidget(self.parameters_layout)

        self.players_layout = QtWidgets.QWidget(parent=self.settings_layout)
        self.players_layout.setStyleSheet(
            "background-color: white;\n"
            "border-radius: 20px;\n"
        )
        self.players_layout.setObjectName("players_layout")
        self.add_shadow(self.players_layout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.players_layout)

        self.verticalLayout_3.setObjectName("verticalLayout_3")

        # Buttons layout
        self.buttons_layout = QtWidgets.QWidget(parent=self.players_layout)
        self.buttons_layout.setStyleSheet("")
        self.buttons_layout.setObjectName("buttons_layout")

        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.buttons_layout)
        self.horizontalLayout_5.setContentsMargins(55, -1, 55, -1)
        self.horizontalLayout_5.setSpacing(40)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")

        self.play_button = QtWidgets.QPushButton(parent=self.buttons_layout)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        size_policy.setHeightForWidth(self.play_button.sizePolicy().hasHeightForWidth())
        self.play_button.setSizePolicy(size_policy)
        self.play_button.setMinimumSize(QtCore.QSize(40, 40))
        self.play_button.setMaximumSize(QtCore.QSize(40, 40))
        self.play_button.setStyleSheet(
            "border-radius: 20px;\n"
            "background-color: #EF8481;\n"
            "color: white;\n"
            "font-size: 35px;\n"
            "padding-bottom: 2px;\n"
        )
        self.play_button.setObjectName("play_button")
        self.add_shadow(self.play_button)
        self.horizontalLayout_5.addWidget(self.play_button)

        self.toggle_render_button = QtWidgets.QPushButton(parent=self.buttons_layout)
        font = QtGui.QFont()
        font.setFamily("Mulish")
        font.setPointSize(12)
        font.setBold(True)
        self.toggle_render_button.setFont(font)
        self.toggle_render_button.setStyleSheet(
            "color: white;\n"
            "background-color: #6D98F4;\n"
            "border: 4px solid #6D98F4;\n"
            "border-radius: 12px;\n"
        )
        self.toggle_render_button.setObjectName("toggle_render_button")
        self.toggle_render_button.setCheckable(True)
        self.toggle_render_button.setChecked(False)
        self.add_shadow(self.toggle_render_button)
        self.horizontalLayout_5.addWidget(self.toggle_render_button)

        self.verticalLayout_3.addWidget(self.buttons_layout)

        # Speed slider
        self.speed_slider_layout = QtWidgets.QWidget(parent=self.players_layout)
        self.speed_slider_layout.setObjectName("speed_slider_layout")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.speed_slider_layout)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")

        self.speed_slider_label = self.create_label(self.speed_slider_layout, "Speed")
        self.horizontalLayout_6.addWidget(self.speed_slider_label)

        self.speed_slider = QtWidgets.QSlider(parent=self.speed_slider_layout)
        self.speed_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.speed_slider.setObjectName("speed_slider")
        self.speed_slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    border: 1px solid #DBE3F1;
                    height: 4px;
                    border-radius: 2px;
                    background: #DBE3F1;
                }

                QSlider::handle:horizontal {
                    border: 1px solid #6D98F4;
                    width: 10px;
                    margin: -3px 0;
                    border-radius: 5px;
                    background: #6D98F4;
                }

                QSlider::sub-page:horizontal {
                    background: #6D98F4;
                    border-radius: 2px;
                }
                """)
        self.speed_slider.setRange(1, 500)
        self.speed_slider.setValue(100)

        self.horizontalLayout_6.addWidget(self.speed_slider)

        self.horizontalLayout_6.setStretch(0, 1)
        self.horizontalLayout_6.setStretch(1, 4)
        self.verticalLayout_3.addWidget(self.speed_slider_layout)

        # Playback slider
        self.playback_slider_layout = QtWidgets.QWidget(parent=self.players_layout)
        self.playback_slider_layout.setObjectName("playback_slider_layout")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.playback_slider_layout)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")

        self.playback_slider_label = self.create_label(self.playback_slider_layout, "Playback")
        self.horizontalLayout_7.addWidget(self.playback_slider_label)

        self.playback_slider = QtWidgets.QSlider(parent=self.playback_slider_layout)
        self.playback_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.playback_slider.setObjectName("playback_slider")
        self.playback_slider.setStyleSheet("""
                        QSlider::groove:horizontal {
                            border: 1px solid #DBE3F1;
                            height: 4px;
                            border-radius: 2px;
                            background: #DBE3F1;
                        }

                        QSlider::handle:horizontal {
                            border: 1px solid #6D98F4;
                            width: 10px;
                            margin: -3px 0;
                            border-radius: 5px;
                            background: #6D98F4;
                        }

                        QSlider::sub-page:horizontal {
                            background: #6D98F4;
                            border-radius: 2px;
                        }
                        """)
        self.playback_slider.setRange(0, 0)
        self.playback_slider.setValue(0)
        self.horizontalLayout_7.addWidget(self.playback_slider)

        self.horizontalLayout_7.setStretch(0, 1)
        self.horizontalLayout_7.setStretch(1, 4)
        self.verticalLayout_3.addWidget(self.playback_slider_layout)

        self.verticalLayout_2.addWidget(self.players_layout)
        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 4)
        self.verticalLayout_2.setStretch(2, 3)

        self.horizontalLayout_3.addWidget(self.settings_layout)

        # Simulation widget
        self.simulation_widget = QtWidgets.QWidget(parent=self.bottom_layout)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.simulation_widget.setSizePolicy(size_policy)
        self.simulation_widget.setObjectName("simulation_widget")

        self.simulation_layout = QtWidgets.QVBoxLayout(self.simulation_widget)

        self.horizontalLayout_3.addWidget(self.simulation_widget)
        self.horizontalLayout_3.setStretch(0, 11)
        self.horizontalLayout_3.setStretch(1, 13)

        # Frame counter label
        self.frame_counter_label = self.create_label(self.simulation_widget, "Frame: 0", font_size= 14)
        self.frame_counter_label.setGeometry(10, 10, 150, 40)

        self.verticalLayout.addWidget(self.bottom_layout)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 6)

        self.horizontalLayout_4.addWidget(self.layout)
        main_window.setCentralWidget(self.centralwidget)

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Cardiomaton"))
        self.project_name.setText(_translate("MainWindow", "Cardiomaton"))
        self.pushButton_app.setText(_translate("MainWindow", "App"))
        self.pushButton_help.setText(_translate("MainWindow", "Help"))
        self.pushButton_about_us.setText(_translate("MainWindow", "About us"))
        self.play_button.setText(_translate("MainWindow", "▶"))
        self.toggle_render_button.setText(_translate("MainWindow", "Colored by charge"))
        self.speed_slider_label.setText(_translate("MainWindow", "Speed"))
        self.playback_slider_label.setText(_translate("MainWindow", "Playback"))

    @staticmethod
    def load_fonts():
        fonts_dir = "resources/fonts"
        for filename in os.listdir(fonts_dir):
            if filename.lower().endswith(".ttf"):
                QFontDatabase.addApplicationFont(os.path.join(fonts_dir, filename))

    @staticmethod
    def add_shadow(widget, blur=30, offset_x=2, offset_y=2,
                   color=QColor(150, 150, 150, 100)) -> None:
        """Adds shadow to a widget."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setOffset(offset_x, offset_y)
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)

    @staticmethod
    def create_label(parent, text="", font_family="Mulish",
                     font_size=12, bold=True, color="#233348") -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(parent)
        font = QtGui.QFont()
        font.setFamily(font_family)
        font.setPointSize(font_size)
        font.setBold(bold)
        label.setFont(font)
        label.setStyleSheet(f"color: {color};")
        label.setText(text)
        return label

    @staticmethod
    def create_pushbutton(parent, font_family="Mulish",
                           font_size=13, bold=True, color="#233348", hover_color="#6D98F4") -> QtWidgets.QPushButton:
        pushbutton = QtWidgets.QPushButton(parent)
        font = QtGui.QFont()
        font.setFamily(font_family)
        font.setPointSize(font_size)
        font.setBold(bold)
        pushbutton.setFont(font)
        pushbutton.setStyleSheet(f"""
            QPushButton {{
                border: none;             
                color: {color};            
            }}
            QPushButton:hover {{
                color: {hover_color}; 
            }}
        """)
        return pushbutton

    def create_widget(self, parent) -> QWidget:
        widget = QtWidgets.QWidget(parent)
        widget.setEnabled(True)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        size_policy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(size_policy)
        widget.setStyleSheet("background: transparent;")