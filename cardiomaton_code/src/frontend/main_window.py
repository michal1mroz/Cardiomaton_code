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
from src.utils.style_utils import get_qss_styling
from src.workers.backend_init_worker import BackendInitWorker
from PyQt6.QtCore import QThread
from src.workers.simulation_worker import SimulationWorker


class MainWindow(QMainWindow):
    """
    Main application window for the Cardiomaton simulator.

    This window initializes and manages the simulation rendering,
    playback controls, and UI layout.
    """
    QSS_PATH = "../../resources/style/main_window.qss"

    def __init__(self):
        """
        Initialize the main window and its components.
        """
        super().__init__()
        self.setWindowTitle("Cardiomaton")
        self.setGeometry(0, 0, 1000, 600)
        self.setStyleSheet(get_qss_styling())
        self.base_frame_time = 0.05

        self.render_label = QLabel("Loading simulation...", self)
        self.render_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.render_label)

        self.backend_thread = QThread()
        self.backend_worker = BackendInitWorker()
        self.backend_worker.moveToThread(self.backend_thread)

        self.backend_thread.started.connect(self.backend_worker.run)
        self.backend_worker.finished.connect(self.on_backend_ready)
        self.backend_worker.finished.connect(self.backend_thread.quit)
        self.backend_worker.finished.connect(self.backend_worker.deleteLater)
        self.backend_thread.finished.connect(self.backend_thread.deleteLater)

        self.backend_thread.start()

    def on_backend_ready(self, sim: SimulationController):
        self.sim = sim

        self.sim = SimulationController(frame_time=self.base_frame_time)
        self.renderer = FrameRenderer(self.sim)
        self.render_label = MainLabel(self.renderer)

        self.render_charged = True # flag telling how simulation is rendered : True - showing charge; False - showing state
        self.running = False

        self.cell_inspector = None

        self._init_ui()
        self._init_timer()
        self._init_worker()

    def _init_ui(self):
        """
        Builds the user interface layout and widgets.
        """

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        self.render_label.setMinimumSize(800, 600)

        # Simulation display
        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.render_label)
        main_layout.addLayout(self.main_layout)

        self.cell_inspector = None
        self.render_label.cellClicked.connect(self._show_cell_inspector)

        # Frame counter display
        self._setup_frame_counter()
        self.setStyleSheet(self.styleSheet())

        # Start/stop button
        button_layout = self._setup_play_button()
        main_layout.addLayout(button_layout)

        # Speed slider
        slider_layout = self._setup_speed_slider()
        main_layout.addLayout(slider_layout)

        # Playback slider
        playback_slider_container = self._setup_playback_slider()
        main_layout.addWidget(playback_slider_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Color by charge / state option
        self.toggle_render_button = self._setup_render_toggle_button()
        main_layout.addWidget(self.toggle_render_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def _setup_frame_counter(self):
        self.frame_counter_label = QLabel(self.render_label)
        self.frame_counter_label.move(10, 10)
        self.frame_counter_label.setObjectName("counterLabel")
        self.frame_counter_label.setFixedHeight(40)
        self._update_frame_counter(0)
        self.frame_counter_label.show()

    def _setup_play_button(self) -> QHBoxLayout:
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_simulation)
        layout = QHBoxLayout()
        layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)
        return layout

    def _setup_speed_slider(self) -> QHBoxLayout:
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 500)
        self.speed_slider.setValue(100)
        self.speed_slider.setMinimumWidth(200)
        self.speed_slider.valueChanged.connect(self._change_speed)

        layout = QHBoxLayout()
        layout.addWidget(self.speed_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        return layout

    def _setup_playback_slider(self) -> QWidget:
        container = QWidget()
        container.setMaximumWidth(400)
        container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.playback_slider = QSlider(Qt.Orientation.Horizontal)
        self.playback_slider.setRange(0, 0)
        self.playback_slider.setValue(0)
        self.playback_slider.setMinimumWidth(200)
        self.playback_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.playback_slider.valueChanged.connect(self._on_slider_change)

        label = QLabel("Playback:")
        label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(container)
        layout.addWidget(label)
        layout.addWidget(self.playback_slider)

        return container

    def _setup_render_toggle_button(self) -> QPushButton:
        self.toggle_render_button = QPushButton("Color by state")
        self.toggle_render_button.setCheckable(True)
        self.toggle_render_button.setChecked(False)
        self.toggle_render_button.setMaximumWidth(180)
        self.toggle_render_button.toggled.connect(self.toggle_render_mode)
        return self.toggle_render_button

    def toggle_render_mode(self, checked: bool):
        """
        Toggle between rendering modes: by charge or by state.
        """
        self.render_charged = not checked
        if checked:
            self.toggle_render_button.setText("Color by charge")
        else:
            self.toggle_render_button.setText("Color by state")

    def _init_timer(self):
        """
        Initializes the QTimer for frame updates.
        """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        QTimer.singleShot(0, self._update_frame)

    def _init_worker(self):
        self.worker = SimulationWorker(self.sim)

        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        self.worker.frame_ready.connect(self.on_frame_ready)
        self.worker_thread.started.connect(lambda: None)

        self.worker_thread.start()

    def toggle_simulation(self):
        """
        Toggles the simulation loop between start and stop.
        """
        if self.running:
            self.timer.stop()
            self.play_button.setText("Start")
            self.running = False
        else:
            # Checks if playback was changed and updates the automaton accordingly
            if self.playback_slider.value() < len(self.sim.recorder) - 1:
                self.sim.update_automaton(self.playback_slider.value())
            self.timer.start(int(self.sim.frame_time * 1000))
            self.play_button.setText("Stop")
            self.running = True

        if self.cell_inspector:
            self.cell_inspector.set_running(self.running)
        self.render_label.set_running(self.running)

    def _set_running_state(self, running: bool):
        self.running = running
        self.play_button.setText("Stop" if running else "Start")
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
        if self.running:
            self.worker.request_next_frame.emit()

    def on_frame_ready(self, frame: int, data: dict):
        pixmap = self.renderer.render_frame(
            self.render_label.size(),
            data,
            self.sim.shape,
            self.render_charged
        )
        self.render_label.setPixmap(pixmap)

        self._update_frame_counter(frame)

        if self.cell_inspector:
            frame_data = self.sim.recorder.get_frame(-1)
            if frame_data:
                cell_data = frame_data[1].get(self.cell_inspector.position)

                self.cell_inspector.update(cell_data)

        buf_len = len(self.sim.recorder)
        if buf_len > 0:
            self.playback_slider.blockSignals(True)
            self.playback_slider.setRange(0, buf_len - 1)
            self.playback_slider.setValue(buf_len - 1)
            self.playback_slider.blockSignals(False)

    def _on_slider_change(self, value: int):
        if self.running:
            self._set_running_state(False)

        try:
            self._remove_inspector()
            frame, data = self.sim.recorder.get_frame(value)
            self._update_frame_counter(frame)
            pixmap = self.renderer.render_frame(self.render_label.size(), data, self.render_charged)
            self.render_label.setPixmap(pixmap)
            if self.cell_inspector:
                cell_data = data.get(self.cell_inspector.position)
                self.cell_inspector.update(cell_data)

        except Exception:
            pass

    def _show_cell_inspector(self, cell_data: CellDict):
        if self.cell_inspector:
            self._remove_inspector()

        self.cell_inspector = CellInspector(
            cell_data, on_close_callback=self._remove_inspector,
            running=self.running, ctrl=self.sim
        )
        self.main_layout.addWidget(self.cell_inspector)

    def _remove_inspector(self):
        if self.cell_inspector:
            self.main_layout.removeWidget(self.cell_inspector)
            self.cell_inspector.deleteLater()
            self.cell_inspector = None

    def closeEvent(self, event):
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()

        if hasattr(self, 'worker_thread'):
            self.worker_thread.quit()
            self.worker_thread.wait()

        event.accept()
