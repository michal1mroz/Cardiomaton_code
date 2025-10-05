from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QTimer
from src.frontend.cell_inspector import CellInspector
from src.models.cell import CellDict
from src.controllers.simulation_controller import SimulationController
from src.frontend.frame_renderer import FrameRenderer
from src.frontend.main_label import MainLabel
from src.frontend.ui_main_window import UiMainWindow

class MainWindow(QMainWindow):
    """
    Main application window for the Cardiomaton simulator.

    This window initializes and manages the simulation rendering, playback controls.
    """

    def __init__(self):
        """
        Initialize the main window and its components.
        """
        super().__init__()
        self.ui = UiMainWindow(self)

        self.base_frame_time = 0.05

        self.sim = SimulationController(frame_time=self.base_frame_time)
        self.renderer = FrameRenderer(self.sim)
        self.render_label = MainLabel(self.renderer)

        self.render_charged = True # flag telling how simulation is rendered : True - showing charge; False - showing state
        self.running = False

        self.cell_inspector = None

        self.frames_per_click = 10
        self.current_playback_buffer_index = -1

        self._init_ui()
        self._init_timer()

    def _init_ui(self):
        """
        Builds the user interface layout and widgets.
        """

        # Simulation display
        self.ui.simulation_layout.addWidget(self.render_label)

        self.cell_inspector = None
        self.render_label.cellClicked.connect(self._show_cell_inspector)

        # Start/stop button
        self.ui.play_button.clicked.connect(self.toggle_simulation)

        # Speed dropdown
        self.ui.speed_dropdown.currentTextChanged.connect(self._change_speed)

        # Playback hold
        self.ui.prev_button.pressed.connect(self._start_playback_hold)
        self.ui.prev_button.released.connect(self._stop_playback_hold)

        # Forward hold
        self.ui.next_button.pressed.connect(self._start_forward_hold)
        self.ui.next_button.released.connect(self._stop_forward_hold)

        # Timers for playback and forward buttons
        self.playback_timer = QTimer(self)
        self.playback_timer.timeout.connect(self._on_playback)

        self.forward_timer = QTimer(self)
        self.forward_timer.timeout.connect(self._on_forward)

        # Color by charge / state option
        self.ui.toggle_render_button.clicked.connect(self.toggle_render_mode)

    def toggle_render_mode(self):
        """
        Toggle between rendering modes: by charge or by state.
        """
        self.render_charged = not self.render_charged
        self.ui.toggle_render_button.setText("↯" if self.render_charged else "️⏣")

    def _init_timer(self):
        """
        Initializes the QTimer for frame updates.
        """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        QTimer.singleShot(0, self._update_frame)

    def toggle_simulation(self):
        """
        Toggles the simulation loop between start and stop.
        """
        if self.running:
            self.timer.stop()
            self.ui.play_button.setText("▸")
            self.running = False
        else:
            self.sim.update_automaton(self.current_playback_buffer_index)
            self.timer.start(int(self.sim.frame_time * 1000))
            self.ui.play_button.setText("▪")
            self.running = True

        if self.cell_inspector:
            self.cell_inspector.set_running(self.running)
        self.render_label.set_running(self.running)

    def _set_running_state(self, running: bool):
        self.running = running
        self.ui.play_button.setText("▪" if running else "▸")
        if self.cell_inspector:
            self.cell_inspector.set_running(running)
        self.render_label.set_running(running)
        if not running:
            self.timer.stop()
    def _change_speed(self):
        """
        Updates the simulation speed based on slider value.
        """
        current_speed = self.ui.speed_dropdown.currentText()
        speed_int = int(current_speed[0])

        multiplier = 2 ** (speed_int - 1)

        new_frame_time = self.base_frame_time / multiplier
        self.sim.frame_time = new_frame_time
        if self.timer.isActive():
            self.timer.start(int(new_frame_time * 1000))

    def _update_frame_counter(self, frame: int):
        self.ui.frame_counter_label.setText(f"Frame: {frame}")

    def _update_frame(self):
        """
        Renders and displays the next frame of the simulation.
        """
        frame, pixmap = self.renderer.render_next_frame(self.render_label.size(), self.render_charged)
        self.render_label.setPixmap(pixmap)
        self.ui.frame_counter_label.setText(f"Frame: {frame}")
        
        # Maybe let's think of some observers or other callbacks to update widgets. MM
        if self.cell_inspector:
            self.cell_inspector.update(self.renderer.current_data.get(self.cell_inspector.position))

    def _start_playback_hold(self):
        self._on_playback()
        self.playback_timer.start(100)

    def _stop_playback_hold(self):
        self.playback_timer.stop()

    def _start_forward_hold(self):
        self._on_forward()
        self.forward_timer.start(100)

    def _stop_forward_hold(self):
        self.forward_timer.stop()

    def _on_playback(self) -> None:
        if self.running:
            self._set_running_state(False)

        try:
            new_index = self.current_playback_buffer_index - self.frames_per_click
            if new_index < -self.sim.recorder.get_buffer_size():
                new_index = -self.sim.recorder.get_buffer_size()

            self._render_buffer_frame(new_index)
        except Exception:
            pass

    def _on_forward(self) -> None:
        if self.running:
            self._set_running_state(False)

        try:
            new_index = self.current_playback_buffer_index + self.frames_per_click
            if new_index > -1:
                new_index = -1

            self._render_buffer_frame(new_index)
        except Exception:
            pass

    def _render_buffer_frame(self, index: int) -> None:
        """Load and render a frame from the simulation recorder buffer."""
        self.current_playback_buffer_index = index
        self._remove_inspector()
        frame, data = self.sim.recorder.get_frame(index)
        self._update_frame_counter(frame)
        pixmap = self.renderer.render_frame(self.render_label.size(), data, self.render_charged)
        self.render_label.setPixmap(pixmap)

    def _show_cell_inspector(self, cell_data: CellDict) -> None:
        if self.cell_inspector:
            self._remove_inspector()

        self.cell_inspector = CellInspector(
            cell_data, on_close_callback=self._remove_inspector,
            running=self.running, ctrl=self.sim
        )
        self.ui.cell_inspector_layout.addWidget(self.cell_inspector)
        self.ui.parameters_layout.setVisible(False)
        self.ui.presets_layout.setVisible(False)
        self.ui.cell_inspector_container.setParent(self.ui.settings_layout)

        self.ui.verticalLayout_2.insertWidget(0, self.ui.cell_inspector_container, 7)

    def _remove_inspector(self) -> None:
        if self.cell_inspector:
            self.ui.cell_inspector_container.setParent(None)
            self.ui.parameters_layout.setVisible(True)
            self.ui.presets_layout.setVisible(True)
            self.cell_inspector.deleteLater()
            self.cell_inspector = None