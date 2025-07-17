from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
    QPushButton, QLabel, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from src.frontend.cell_inspector import CellInspector
from src.models.cell import CellDict
from src.frontend.simulation_controller import SimulationController
from src.frontend.frame_renderer import FrameRenderer
from src.frontend.main_label import MainLabel
from src.utils.data_reader import get_qss_styling


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

        self.sim = SimulationController(frame_time=self.base_frame_time)
        self.renderer = FrameRenderer(self.sim)
        self.label = MainLabel(self.renderer)

        self.render_charged = True
        self.running = False

        self._init_ui()
        self._init_timer()

    def _init_ui(self):
        """
        Builds the user interface layout and widgets.
        """

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.label.setMinimumSize(800, 600)

        # Simulation display
        # self.simulation_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.simulation_label = self.label
        #layout.addWidget(self.simulation_label)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.label)
        layout.addLayout(self.main_layout)

        self.cell_inspector = None
        self.label.cellClicked.connect(self._show_cell_inspector)

        # Frame counter display
        self.frame_counter_label = QLabel(self.label)
        self.frame_counter_label.move(10, 10)
        self.frame_counter_label.setObjectName("counterLabel") # ref for QSS styling
        self.setStyleSheet(self.styleSheet())
        self.frame_counter_label.setFixedHeight(40)
        self.frame_counter_label.setText(f"Frame: 0")
        self.frame_counter_label.adjustSize()
        self.frame_counter_label.show()

        # Start/stop button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self._start)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(button_layout)

        # Speed slider
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 500)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self._change_speed)
        self.speed_slider.setMinimumWidth(200)
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.speed_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(slider_layout)

        # Playback slider
        self.playback_slider = QSlider(Qt.Orientation.Horizontal)
        self.playback_slider.setRange(0, 0)
        self.playback_slider.setValue(0)
        self.playback_slider.valueChanged.connect(self._on_slider_change)
        slider2_container = QWidget()
        slider2_container.setMaximumWidth(400)
        slider2_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        slider2_layout = QHBoxLayout(slider2_container)

        label = QLabel("Playback:")
        label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.playback_slider.setMinimumWidth(200)
        self.playback_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        slider2_layout.addWidget(label)
        slider2_layout.addWidget(self.playback_slider)

        layout.addWidget(slider2_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Color by charge / state option
        self.toggle_render_button = QPushButton("Color by state")
        self.toggle_render_button.setCheckable(True)
        self.toggle_render_button.setChecked(False)
        self.toggle_render_button.toggled.connect(self.toggle_render_mode)
        self.toggle_render_button.setMaximumWidth(180)
        layout.addWidget(self.toggle_render_button, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def _start(self):
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

        if self.cell_inspector is not None:
            self.cell_inspector.set_running(self.running)
        self.label.set_running(self.running)

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

    def _update_frame(self):
        """
        Renders and displays the next frame of the simulation.
        """
        frame, pixmap = self.renderer.render_next_frame(self.simulation_label.size(), self.render_charged)
        self.simulation_label.setPixmap(pixmap)
        self.frame_counter_label.setText(f"Frame: {frame}")
        self.frame_counter_label.adjustSize()
        
        # Maybe let's think of some observers or other callbacks to update widgets. MM
        if self.cell_inspector is not None:
            self.cell_inspector.update(self.renderer.current_data.get(self.cell_inspector.position))

        buf_len = len(self.sim.recorder)
        if buf_len > 0:
            self.playback_slider.blockSignals(True)
            self.playback_slider.setRange(0, buf_len - 1)
            self.playback_slider.setValue(buf_len - 1)
            self.playback_slider.blockSignals(False)

    def _on_slider_change(self, value: int):
        if self.running:
            self.timer.stop()
            self.play_button.setText("Start")
            self.running = False
            self.label.set_running(False)
        try:
            self._remove_inspector()
            frame, data = self.sim.recorder.get_frame(value)
            self.frame_counter_label.setText(f"Frame: {frame}")
            self.frame_counter_label.adjustSize()
            pixmap = self.renderer.render_frame(self.simulation_label.size(), data, self.render_charged)
            self.label.setPixmap(pixmap)
            # self.playback_slider.setValue(self.playback_slider.value() + 1)

        except Exception:
            pass

    def _show_cell_inspector(self, cell_data: CellDict):
        if self.cell_inspector:
            self.main_layout.removeWidget(self.cell_inspector)
            self.cell_inspector.deleteLater()

        self.cell_inspector = CellInspector(cell_data, on_close_callback=self._remove_inspector, running=self.running, ctrl = self.sim)
        self.main_layout.addWidget(self.cell_inspector)

    def _remove_inspector(self):
        if self.cell_inspector:
            self.main_layout.removeWidget(self.cell_inspector)
            self.cell_inspector.deleteLater()
            self.cell_inspector = None