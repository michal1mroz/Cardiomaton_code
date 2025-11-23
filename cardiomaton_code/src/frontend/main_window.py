from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QMainWindow

from src.controllers.simulation_controller import SimulationController
from src.frontend.cell_inspecting.cell_inspector_manager import CellInspectorManager
from src.frontend.frame_rendering.frame_renderer import FrameRenderer
from src.frontend.playback_navigation import HistoryNavigator
from src.frontend.simulation_label.cell_data_provider import CellDataProvider
from src.frontend.simulation_label.cell_modificator import CellModificator, CellModification
from src.frontend.simulation_label.simulation_view import SimulationView
from src.frontend.simulation_loop import SimulationRunner
from src.frontend.ui_main_window import UiMainWindow
from src.models.cell import CellDict


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = UiMainWindow(self)

        automaton_size = (220, 250)
        self.base_frame_time = 0.05
        self.image = QImage(automaton_size[1], automaton_size[0], QImage.Format.Format_RGBA8888)

        self.sim = SimulationController(frame_time=self.base_frame_time, image=self.image)
        self.renderer = FrameRenderer(self.sim, self.image)
        self.cell_data_provider = CellDataProvider(self.sim)
        self.cell_modificator = CellModificator()

        self.runner = SimulationRunner(base_frame_time=self.base_frame_time)
        self.navigator = HistoryNavigator()
        self.inspector_manager = CellInspectorManager(self.ui)

        self.render_label = SimulationView(self.cell_data_provider, self.ui.brush_size_slider, self.cell_modificator)
        self.render_charged = True

        self._init_ui_layout()
        self._connect_signals()

    def _init_ui_layout(self):
        self.ui.simulation_layout.addWidget(self.render_label)

    def _connect_signals(self):
        self.runner.frame_tick.connect(self._update_live_frame)

        self.navigator.interaction_started.connect(self._pause_simulation_for_history)
        self.navigator.request_render_buffer.connect(self._render_history_frame)

        self.ui.play_button.clicked.connect(self._toggle_simulation)
        self.ui.speed_dropdown.currentTextChanged.connect(self._on_speed_change)
        self.ui.toggle_render_button.clicked.connect(self._toggle_render_mode)

        self.ui.prev_button.pressed.connect(self.navigator.start_backward_hold)
        self.ui.prev_button.released.connect(self.navigator.stop_backward_hold)
        self.ui.next_button.pressed.connect(self.navigator.start_forward_hold)
        self.ui.next_button.released.connect(self.navigator.stop_forward_hold)

        self.render_label.cellClicked.connect(self._on_cell_clicked)
        self.ui.commit_button.clicked.connect(self._modify_cells)
        self.ui.undo_button.clicked.connect(self._undo_cell_modification)

    def _toggle_simulation(self):
        if not self.runner.running and self.navigator.current_buffer_index != -1:
            self.sim.set_frame_counter(self.navigator.current_buffer_index)
            self.navigator.reset_index()

        is_running = self.runner.toggle()
        self._update_ui_state(is_running)

    def _pause_simulation_for_history(self):
        if self.runner.running:
            self.runner.stop()
            self._update_ui_state(False)

        self.navigator.set_buffer_size(self.sim.get_buffer_size())

    def _update_ui_state(self, is_running: bool):
        self.ui.play_button.setText("▪" if is_running else "▶")
        self.render_label.set_running(is_running)
        self.inspector_manager.set_running_state(is_running)

    def _on_speed_change(self):
        self.runner.set_speed_level(self.ui.speed_dropdown.currentText(), self.sim)

    def _toggle_render_mode(self):
        self.render_charged = not self.render_charged
        self.ui.toggle_render_button.setText("↯" if self.render_charged else "️⏣")

        if not self.runner.running:
            if self.navigator.current_buffer_index != -1:
                self._render_history_frame(self.navigator.current_buffer_index)
            else:
                self._update_live_frame()

    def _update_live_frame(self):
        frame, pixmap = self.renderer.render_next_frame(self.render_label.size(), self.render_charged)
        self._display_frame(frame, pixmap)

        if self.inspector_manager.is_active:
            pos = self.inspector_manager.get_current_position()
            self.inspector_manager.update_data(self.sim.get_cell_data(pos))

    def _render_history_frame(self, index: int):
        self.inspector_manager.hide_inspector()

        frame, pixmap = self.renderer.render_frame(self.render_label.size(), index, self.render_charged,
                                                   drop_newer=False)
        self._display_frame(frame, pixmap)

    def _display_frame(self, frame_num, pixmap):
        self.render_label.setPixmap(pixmap)
        self.ui.frame_counter_label.setText(f"Frame {frame_num}")

    def _on_cell_clicked(self, cell_data: CellDict):
        self.inspector_manager.show_inspector(
            cell_data,
            on_close_callback=self.inspector_manager.hide_inspector,
            is_running=self.runner.running
        )

    def _modify_cells(self):
        all_params = self.ui.parameter_panel.get_current_values()

        modification = CellModification(
            cells=self.cell_modificator.commit_change(),
            purkinje_charge_parameters=all_params["PURKINJE"],
            atrial_charge_parameters=all_params["ATRIAL"],
            pacemaker_charge_parameters=all_params["PACEMAKER"],
            necrosis_enabled=self.ui.necrosis_switch.isChecked(),
            modifier_name="user_slider",
        )

        self.ui.parameter_panel.reset_all_sliders()
        self.ui.necrosis_switch.setChecked(False)
        self.sim.modify_cells(modification)

    def _undo_cell_modification(self):
        self.cell_modificator.undo_change()
        self.sim.undo_modification()