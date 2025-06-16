from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
    QPushButton, QLabel, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from cardiomaton_code.src.frontend.cell_inspector import CellInspector
from cardiomaton_code.src.models.cell import CellDict
from src.frontend.simulation_controller import SimulationController
from src.frontend.frame_renderer import FrameRenderer
from src.frontend.main_label import MainLabel


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
        self.setWindowTitle("Cardiomaton")
        self.setGeometry(0, 0, 1000, 600)

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
        self.frame_counter_label.setStyleSheet(
            "font-size: 14pt; color: black; background-color: white; padding: 6px;"
        )
        self.frame_counter_label.setFixedHeight(40)
        self.frame_counter_label.setText(f"Frame: 0")
        self.frame_counter_label.adjustSize()
        #self.frame_counter_label.setFixedWidth(110)
        self.frame_counter_label.show()

        # Start/stop button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self._start)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(button_layout)
        # layout.addWidget(self.play_button)

        # Speed slider
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 500)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self._change_speed)
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.speed_slider, alignment = Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(slider_layout)

        # Playback slider
        self.playback_slider = QSlider(Qt.Orientation.Horizontal)
        self.playback_slider.setRange(0, 0)
        self.playback_slider.setValue(0)
        self.playback_slider.valueChanged.connect(self._on_slider_change)
        slider2_layout = QHBoxLayout()
        slider2_layout.addWidget(QLabel("Playback:"), alignment = Qt.AlignmentFlag.AlignCenter)
        slider2_layout.addWidget(self.playback_slider, alignment = Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(slider2_layout)

        # Color by charge / state option
        self.render_next_frame_method = self.renderer.render_next_frame_charge
        self.render_next_frame_method = self.renderer.render_next_frame_charge
        self.state_checkbox = QCheckBox("Color by state")
        self.state_checkbox.setChecked(False)
        self.state_checkbox.stateChanged.connect(self.state_checkbox_changed)
        layout.addWidget(self.state_checkbox)

    def state_checkbox_changed(self, state):
        """
        Handle state change of the 'Color by state' checkbox.
        """
        if state == Qt.CheckState.Checked.value:
            # self.render_next_frame_method = self.renderer.render_next_frame
            self.render_charged = False
        else:
            # self.render_next_frame_method = self.renderer.render_next_frame_charge
            self.render_charged = True
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
            if self.playback_slider.value() < self.sim.recorder.__len__() - 1:
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