from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QListView
from PyQt6 import QtWidgets

from src.frontend.parameter_panel.parameter_panel import ParameterPanel
from src.frontend.ui_components.modification_panel import ModificationPanel
from src.frontend.ui_components.player_controls_widget import PlayerControlsWidget
from src.frontend.ui_components.presets_widget import PresetsWidget
from src.frontend.ui_components.ui_factory import UIFactory


class UiSimulationWindow(object):
    def __init__(self, parent_widget: QWidget):
        self.layout = QVBoxLayout(parent_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.simulation_background = UIFactory.create_widget(parent_widget)
        self.simulation_background.setGeometry(450, -40, 700, 600)
        self.simulation_background.setObjectName("simulation_background_widget")

        self.bottom_container = UIFactory.create_widget(parent_widget)
        self.bottom_layout = QtWidgets.QHBoxLayout(self.bottom_container)
        self.bottom_layout.setSpacing(30)

        self._init_settings_panel()
        self._init_simulation_area()

        self.empty_right_padding = QWidget()
        self.empty_right_padding.setFixedWidth(1)

        self.bottom_layout.addWidget(self.settings_container, stretch=12)
        self.bottom_layout.addWidget(self.simulation_outer, stretch=13)
        self.bottom_layout.addWidget(self.empty_right_padding, stretch=0)

        self.layout.addWidget(self.bottom_container)

        self._map_shortcuts()

    def _init_settings_panel(self):
        self.settings_container = QWidget()
        layout = QVBoxLayout(self.settings_container)
        layout.setContentsMargins(20, 0, 12, 10)
        layout.setSpacing(20)

        self.presets_layout = PresetsWidget()
        self.presets_layout.setObjectName("Layout")
        UIFactory.add_shadow(self.presets_layout)

        layout.addWidget(self.presets_layout, stretch=0)

        self.tools_container = QWidget()
        UIFactory.add_shadow(self.tools_container)
        self.tools_container.setObjectName("Layout")

        tools_layout = QVBoxLayout(self.tools_container)
        tools_layout.setContentsMargins(0, 10, 0, 10)

        self.modification_panel = ModificationPanel()


        tools_layout.addWidget(self.modification_panel, stretch=1)

        self.parameters_scroll = QScrollArea()
        self.parameters_scroll.setWidgetResizable(True)
        self.parameters_scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.parameters_scroll.setObjectName("parametersScroll")
        self.parameter_panel = ParameterPanel()
        self.parameter_panel.setObjectName("ParameterPanel")
        self.parameters_scroll.setWidget(self.parameter_panel)

        tools_layout.addWidget(self.parameters_scroll)
        layout.addWidget(self.tools_container, stretch=1)

        self.player_controls = PlayerControlsWidget()

        self._configure_player_controls(self.player_controls)

        UIFactory.add_shadow(self.player_controls)

        layout.addWidget(self.player_controls, stretch=0)

        self.cell_inspector_container = QWidget()
        self.cell_inspector_container.setObjectName("CellInspectorContainer")
        UIFactory.add_shadow(self.cell_inspector_container)
        layout.addWidget(self.cell_inspector_container)
        self.cell_inspector_container.hide()

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
        self.simulation_outer_layout.setContentsMargins(10, 110, 0, 0)
        self.simulation_outer_layout.setSpacing(0)

        self.simulation_widget = QWidget()
        self.simulation_layout = QVBoxLayout(self.simulation_widget)

        self.frame_counter_label = UIFactory.create_label(
            self.bottom_container, "Time: 0 ms", font_size=13, bold=True
        )
        self.frame_counter_label.setGeometry(520, 450, 170, 40)
        self.frame_counter_label.setObjectName("frame_counter_label")

        self.simulation_outer_layout.addWidget(self.simulation_widget)

    def _map_shortcuts(self):
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
