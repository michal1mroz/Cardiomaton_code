from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel

from src.frontend.parameter_panel.parameter_panel import ParameterPanel
from src.frontend.ui_components.modification_panel import ModificationPanel
from src.frontend.ui_components.player_controls_widget import PlayerControlsWidget
from src.frontend.ui_components.top_bar_widget import TopBarWidget


class UiMainWindow(object):
    def __init__(self, main_window: QMainWindow):
        self._setup_main_window_properties(main_window)

        self.centralwidget = QWidget(main_window)
        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.topbar = TopBarWidget()
        self.main_layout.addWidget(self.topbar)

        self.bottom_container = QWidget()
        self.bottom_layout = QHBoxLayout(self.bottom_container)

        self._init_settings_panel()

        self._init_simulation_area()

        self.bottom_layout.addWidget(self.settings_container, stretch=4)
        self.bottom_layout.addWidget(self.simulation_widget, stretch=11)

        self.main_layout.addWidget(self.bottom_container)
        main_window.setCentralWidget(self.centralwidget)

        self._map_shortcuts()

    def _setup_main_window_properties(self, window):
        window.resize(1100, 600)
        window.setWindowTitle("Cardiomaton")

    def _init_settings_panel(self):
        self.settings_container = QWidget()
        layout = QVBoxLayout(self.settings_container)
        layout.setContentsMargins(20, 0, 12, 10)
        layout.setSpacing(20)

        self.presets_layout = QWidget()
        self.presets_layout.setObjectName("presets_container")

        self.modification_panel = ModificationPanel()

        self.parameters_scroll = QScrollArea()
        self.parameters_scroll.setWidgetResizable(True)

        self.parameters_inner_container = QWidget()
        self.parameters_inner_layout = QVBoxLayout(self.parameters_inner_container)

        self.parameters_inner_layout.addWidget(self.modification_panel)

        self.parameter_panel = ParameterPanel(self.parameters_inner_container)
        self.parameters_inner_layout.addWidget(self.parameter_panel)
        self.parameters_inner_layout.addStretch()

        self.parameters_scroll.setWidget(self.parameters_inner_container)

        self.player_controls = PlayerControlsWidget()
        self.players_layout = self.player_controls

        self.cell_inspector_container = QWidget()
        self.cell_inspector_layout = QVBoxLayout(self.cell_inspector_container)

        layout.addWidget(self.presets_layout)
        layout.addWidget(self.parameters_scroll)
        layout.addWidget(self.player_controls)

        self.settings_layout = self.settings_container
        self.verticalLayout_2 = layout

    def _init_simulation_area(self):
        self.simulation_widget = QWidget()
        self.simulation_layout = QVBoxLayout(self.simulation_widget)

        self.frame_counter_label = QLabel("Frame: 0", self.simulation_widget)
        self.frame_counter_label.setGeometry(40, 400, 150, 40)

    def _map_shortcuts(self):
        self.project_name = self.topbar.project_name

        self.play_button = self.player_controls.play_button
        self.prev_button = self.player_controls.prev_button
        self.next_button = self.player_controls.next_button
        self.speed_dropdown = self.player_controls.speed_dropdown
        self.toggle_render_button = self.player_controls.toggle_render_button

        self.commit_button = self.modification_panel.commit_button
        self.undo_button = self.modification_panel.undo_button
        self.brush_size_slider = self.modification_panel.brush_slider
        self.necrosis_switch = self.modification_panel.necrosis_switch