from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QScrollArea, QListView
from PyQt6 import QtWidgets, QtCore, QtGui

from src.frontend.parameter_panel.parameter_panel import ParameterPanel
from src.frontend.ui_components.modification_panel import ModificationPanel
from src.frontend.ui_components.player_controls_widget import PlayerControlsWidget
from src.frontend.ui_components.presets_widget import PresetsWidget
from src.frontend.ui_components.top_bar_widget import TopBarWidget
from src.frontend.ui_components.ui_factory import UIFactory


class UiMainWindow(object):
    def __init__(self, main_window: QMainWindow):
        UIFactory.load_fonts()
        self._setup_main_window_properties(main_window)

        self.central_widget = UIFactory.create_widget(main_window)

        self.simulation_background = UIFactory.create_widget(self.central_widget)
        self.simulation_background.setGeometry(450, 28, 700, 600)
        self.simulation_background.setObjectName("simulation_background_widget")

        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.central_widget)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)

        self.layout = UIFactory.create_widget(self.central_widget)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layout)

        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(10)

        self.topbar = TopBarWidget()
        self.verticalLayout.addWidget(self.topbar)

        self.bottom_container = UIFactory.create_widget(self.layout)
        self.bottom_layout = QtWidgets.QHBoxLayout(self.bottom_container)
        self.bottom_layout.setSpacing(30)

        self._init_settings_panel()
        self._init_simulation_area()

        self.empty_right_padding = QWidget()
        self.empty_right_padding.setFixedWidth(1)

        self.bottom_layout.addWidget(self.settings_container, stretch=12)
        self.bottom_layout.addWidget(self.simulation_outer, stretch=13)
        self.bottom_layout.addWidget(self.empty_right_padding, stretch=0)

        self.verticalLayout.addWidget(self.bottom_container)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 7)

        self.horizontalLayout_4.addWidget(self.layout)
        main_window.setCentralWidget(self.central_widget)

        self._map_shortcuts()

    @staticmethod
    def _setup_main_window_properties(window):
        window.resize(1100, 600)
        window.setWindowTitle("Cardiomaton")
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        window.setMinimumSize(QtCore.QSize(1100, 600))
        window.setMaximumSize(QtCore.QSize(1100, 600))
        window.setAutoFillBackground(False)
        window.setSizePolicy(size_policy)

    def _init_settings_panel(self):
        self.settings_container = QWidget()
        layout = QVBoxLayout(self.settings_container)
        layout.setContentsMargins(20, 0, 12, 10)
        layout.setSpacing(20)

        self.presets_layout = PresetsWidget()
        self.presets_layout.setObjectName("Layout")
        UIFactory.add_shadow(self.presets_layout)

        self.parameters_scroll = QScrollArea()
        self.parameters_scroll.setWidgetResizable(True)
        self.parameters_scroll.setObjectName("Layout")
        UIFactory.add_shadow(self.parameters_scroll)

        self.parameters_inner_container = QWidget()
        self.parameters_inner_layout = QVBoxLayout(self.parameters_inner_container)
        self.parameters_inner_container.setObjectName("Layout")

        self.modification_panel = ModificationPanel()
        self.parameters_inner_layout.addWidget(self.modification_panel)

        self.parameter_panel = ParameterPanel(self.parameters_inner_container)
        self.parameters_inner_layout.addWidget(self.parameter_panel)
        self.parameters_inner_layout.addStretch()

        self.parameters_scroll.setWidget(self.parameters_inner_container)

        self.player_controls = PlayerControlsWidget()

        self._configure_player_controls(self.player_controls)

        UIFactory.add_shadow(self.player_controls)

        self.cell_inspector_container = QWidget()
        self.cell_inspector_container.setObjectName("CellInspectorContainer")
        self.cell_inspector_layout = QVBoxLayout(self.cell_inspector_container)

        layout.addWidget(self.presets_layout)
        layout.addWidget(self.parameters_scroll)
        layout.addWidget(self.player_controls)

        layout.setStretch(0, 1)
        layout.setStretch(1, 6)
        layout.setStretch(2, 1)

        self.settings_layout = self.settings_container
        self.verticalLayout_2 = layout

    @staticmethod
    def _configure_player_controls(widget: PlayerControlsWidget):
        widget.speed_dropdown.setCurrentText("2x")
        view = QListView()
        widget.speed_dropdown.setView(view)

        widget.play_button.setFixedSize(40, 40)
        UIFactory.add_shadow(widget.play_button)

    def _init_simulation_area(self):
        self.simulation_outer = QWidget()
        self.simulation_outer_layout = QVBoxLayout(self.simulation_outer)
        self.simulation_outer_layout.setContentsMargins(10, 80, 0, 0)
        self.simulation_outer_layout.setSpacing(0)

        self.simulation_widget = QWidget()
        self.simulation_layout = QVBoxLayout(self.simulation_widget)

        self.frame_counter_label = UIFactory.create_label(
            self.bottom_container, "Time 0", font_size=15, bold=True
        )
        self.frame_counter_label.setGeometry(520, 450, 150, 40)
        self.frame_counter_label.setObjectName("frame_counter_label")

        self.simulation_outer_layout.addWidget(self.simulation_widget)

    def _map_shortcuts(self):
        self.project_name = self.topbar.project_name

        self.restart_button = self.player_controls.restart_button
        self.play_button = self.player_controls.play_button
        self.prev_button = self.player_controls.prev_button
        self.next_button = self.player_controls.next_button
        self.speed_dropdown = self.player_controls.speed_dropdown
        self.toggle_render_button = self.player_controls.toggle_render_button
        self.toggle_interaction_button = self.player_controls.toggle_interaction_button

        self.commit_button = self.modification_panel.commit_button
        self.undo_button = self.modification_panel.undo_button
        self.brush_size_slider = self.modification_panel.brush_slider
        self.necrosis_switch = self.modification_panel.necrosis_switch
