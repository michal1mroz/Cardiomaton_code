from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QWidget

from src.backend.controllers.simulation_controller import SimulationController
from src.backend.services.action_potential_generator import ActionPotentialGenerator
from src.database.crud.automaton_crud import get_automaton
from src.database.db import SessionLocal
from src.frontend.cell_inspecting.cell_inspector_manager import CellInspectorManager
from src.frontend.frame_rendering.frame_renderer import FrameRenderer
from src.frontend.ui_components.potential_graph_widget import GraphWidget
from src.backend.controllers.playback_navigator import PlaybackNavigator
from src.frontend.simulation_display.cell_data_provider import CellDataProvider
from src.frontend.simulation_display.cell_modificator import CellModificator, CellModification
from src.frontend.simulation_display.simulation_view import SimulationView
from src.backend.services.simulation_loop import SimulationRunner
from src.frontend.ui_simulation_window import UiSimulationWindow
from src.models.cell import CellDict


class SimulationWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiSimulationWindow(self)

        automaton_size = (292, 400)
        self.base_frame_time = 0.05
        self.image = QImage(automaton_size[1], automaton_size[0], QImage.Format.Format_RGBA8888)

        self.sim = SimulationController(frame_time=self.base_frame_time, image=self.image)
        self.renderer = FrameRenderer(self.sim, self.image)
        self.cell_data_provider = CellDataProvider(self.sim)
        self.cell_modificator = CellModificator()

        self.runner = SimulationRunner(base_frame_time=self.base_frame_time)
        self.runner.set_speed_level("2x", self.sim)
        self.navigator = PlaybackNavigator()
        self.inspector_manager = CellInspectorManager(self.ui)
        self.generator = ActionPotentialGenerator()
        self.plot_windows = {}

        self.overlay_graph = GraphWidget(parent=self)
        self.overlay_graph.hide()

        self.render_label = SimulationView(self.cell_data_provider, self.ui.brush_size_slider, self.cell_modificator)
        self.render_charged = True
        self.inspection_set = True

        self._init_ui_layout()
        self._connect_signals()

        self._reposition_overlay_graph()

    def _init_ui_layout(self):
        self.ui.simulation_layout.addWidget(self.render_label)

    def _connect_signals(self):
        self.runner.frame_tick.connect(self._update_live_frame)

        self.navigator.interaction_started.connect(self._pause_simulation)
        self.navigator.request_render_buffer.connect(self._render_history_frame)

        self.ui.play_button.clicked.connect(self._toggle_simulation)
        self.ui.speed_dropdown.currentTextChanged.connect(self._on_speed_change)
        self.ui.toggle_render_button.clicked.connect(self._toggle_render_mode)
        self.ui.toggle_interaction_button.clicked.connect(self._toggle_interaction_mode)

        self.ui.prev_button.pressed.connect(self.navigator.start_backward_hold)
        self.ui.prev_button.released.connect(self.navigator.stop_backward_hold)
        self.ui.next_button.pressed.connect(self.navigator.start_forward_hold)
        self.ui.next_button.released.connect(self.navigator.stop_forward_hold)

        self.render_label.cellClicked.connect(self._on_cell_clicked)
        self.ui.commit_button.clicked.connect(self._modify_cells)
        self.ui.undo_button.clicked.connect(self._undo_cell_modification)
        self.ui.restart_button.clicked.connect(self._restart_automaton)

        self.ui.parameter_panel.sigParametersChanged.connect(self._on_parameter_slider_moved)

        self.ui.presets_layout.preset_selected.connect(self._on_preset_selected)
        self.ui.presets_layout.save_preset_request.connect(self._save_preset)

    def _toggle_simulation(self):
        if not self.runner.running and self.navigator.current_buffer_index != -1:
            self.sim.set_frame_counter(self.navigator.current_buffer_index)
            self.navigator.reset_index()

        is_running = self.runner.toggle()
        self._update_ui_state(is_running)

    def _pause_simulation(self):
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
        self.ui.frame_counter_label.setText(f"Time: {frame_num // 2} ms")

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
            global_parameters=all_params["__GLOBAL__"],
            necrosis_enabled=self.ui.necrosis_switch.isChecked(),
            modifier_name="user_slider",
        )

        self.ui.parameter_panel.reset_all_sliders()
        self.ui.necrosis_switch.setChecked(False)
        self.sim.modify_cells(modification)

    def _undo_cell_modification(self):
        self.cell_modificator.undo_change()
        self.sim.undo_modification()

    def _on_parameter_slider_moved(self, changed_cell_type: str):
        if self.overlay_graph.isHidden():
            self.overlay_graph.show()
        self.overlay_graph.raise_()
        if changed_cell_type != "__GLOBAL__":
            self.refresh_overlay_plot(changed_cell_type)

    def refresh_overlay_plot(self, cell_type: str):
        params = self.ui.parameter_panel.get_current_values(cell_type)
        t, v = self.generator.generate(cell_type, params, n_cycles=3)
        self.overlay_graph.update_data(t, v, title=f"Preview {cell_type}")

    def _reposition_overlay_graph(self):
        self.overlay_graph.setGeometry(500, 230, 585, 250)

        self.overlay_graph.raise_()

    def _restart_automaton(self):
        self.sim.restart_automaton()
        self.cell_modificator.reset()
        self._update_live_frame()

    def _toggle_interaction_mode(self):
        self.inspection_set = not self.inspection_set
        self.render_label.set_interaction_mode(self.inspection_set)
        self.ui.toggle_interaction_button.setText("⌕" if self.inspection_set else "️✐")

    def _on_preset_selected(self, entry):
        self._pause_simulation()
        db = SessionLocal()
        try:
            dto = get_automaton(db, entry)
            size = dto.shape
            self.image = QImage(size[1], size[0], QImage.Format.Format_RGBA8888)

            self.sim.update_automaton(dto, self.image)
            self.renderer = FrameRenderer(self.sim, self.image)

            self._update_live_frame()

        except Exception as e:
            print(f'Error retrieving entry: {entry}')

    def _save_preset(self, entry):
        self._pause_simulation()
        self.sim.save_automaton(entry)
        self.ui.presets_layout.silent_refresh()