from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
    QPushButton, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QTimer
from src.frontend.cell_inspector import CellInspector
from src.models.cell import CellDict
from src.controllers.simulation_controller import SimulationController
from src.frontend.frame_renderer import FrameRenderer
from src.frontend.main_label import MainLabel
from src.frontend.ui_mainwindow import Ui_MainWindow

class MainWindow(QMainWindow):
    """
    Main application window for the Cardiomaton simulator.

    This window initializes and manages the simulation rendering,
    playback controls, and UI layout.
    """

    def __init__(self):
        """
        Initialize the main window and its components.
        """
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.base_frame_time = 0.05

        self.sim = SimulationController(frame_time=self.base_frame_time)
        self.renderer = FrameRenderer(self.sim)
        self.render_label = MainLabel(self.renderer)

        self.render_charged = True # flag telling how simulation is rendered : True - showing charge; False - showing state
        self.running = False

        self.cell_inspector = None

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

        # Frame counter display
        self._setup_frame_counter()
        self.setStyleSheet(self.styleSheet())

        # Start/stop button
        self.ui.play_button.clicked.connect(self.toggle_simulation)

        # Speed slider
        self.ui.speed_slider.setRange(1, 500)
        self.ui.speed_slider.setValue(100)
        self.ui.speed_slider.valueChanged.connect(self._change_speed)

        # Playback slider
        self.ui.playback_slider.setRange(0, 0)
        self.ui.playback_slider.setValue(0)
        self.ui.playback_slider.valueChanged.connect(self._on_slider_change)

        # Color by charge / state option
        self.ui.toggle_render_button.setCheckable(True)
        self.ui.toggle_render_button.setChecked(False)
        self.ui.toggle_render_button.toggled.connect(self.toggle_render_mode)

    def _setup_frame_counter(self):
        self.frame_counter_label = QLabel(self.render_label)
        self.frame_counter_label.move(10, 10)
        self.frame_counter_label.setObjectName("counterLabel")
        self.frame_counter_label.setFixedHeight(40)
        self._update_frame_counter(0)
        self.frame_counter_label.show()

    def toggle_render_mode(self, checked: bool):
        """
        Toggle between rendering modes: by charge or by state.
        """
        self.render_charged = not checked
        if checked:
            self.ui.toggle_render_button.setText("Color by charge")
        else:
            self.ui.toggle_render_button.setText("Color by state")

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
            # Checks if playback was changed and updates the automaton accordingly
            if self.ui.playback_slider.value() < len(self.sim.recorder) - 1:
                self.sim.update_automaton(self.ui.playback_slider.value())
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
    def _change_speed(self, percent: int):
        """
        Updates the simulation speed based on slider value.

        Args:
            prercent (int): % of change speed
        """
        multiplier = percent / 100
        new_frame_time = self.base_frame_time / multiplier
        self.sim.frame_time = new_frame_time
        if self.timer.isActive():
            self.timer.start(int(new_frame_time * 1000))

    def _update_frame_counter(self, frame: int):
        self.frame_counter_label.setText(f"Frame: {frame}")
        self.frame_counter_label.adjustSize()

    def _update_frame(self):
        """
        Renders and displays the next frame of the simulation.
        """
        frame, pixmap = self.renderer.render_next_frame(self.render_label.size(), self.render_charged)
        self.render_label.setPixmap(pixmap)
        self.frame_counter_label.setText(f"Frame: {frame}")
        self.frame_counter_label.adjustSize()
        
        # Maybe let's think of some observers or other callbacks to update widgets. MM
        if self.cell_inspector:
            self.cell_inspector.update(self.renderer.current_data.get(self.cell_inspector.position))

        buf_len = len(self.sim.recorder)
        if buf_len > 0:
            self.ui.playback_slider.blockSignals(True)
            self.ui.playback_slider.setRange(0, buf_len - 1)
            self.ui.playback_slider.setValue(buf_len - 1)
            self.ui.playback_slider.blockSignals(False)

    def _on_slider_change(self, value: int):
        if self.running:
            self._set_running_state(False)

        try:
            self._remove_inspector()
            frame, data = self.sim.recorder.get_frame(value)
            self._update_frame_counter(frame)
            pixmap = self.renderer.render_frame(self.render_label.size(), data, self.render_charged)
            self.render_label.setPixmap(pixmap)
        except Exception:
            pass


    def _show_cell_inspector(self, cell_data: CellDict):
        if self.cell_inspector:
            self._remove_inspector()

        self.cell_inspector = CellInspector(
            cell_data, on_close_callback=self._remove_inspector,
            running=self.running, ctrl=self.sim
        )
        self.ui.simulation_layout.addWidget(self.cell_inspector)

    def _remove_inspector(self):
        if self.cell_inspector:
            self.ui.simulation_layout.removeWidget(self.cell_inspector)
            self.cell_inspector.deleteLater()
            self.cell_inspector = None