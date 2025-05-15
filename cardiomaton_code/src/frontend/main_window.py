from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QTimer
from src.frontend.simulation_controller import SimulationController
from src.frontend.frame_renderer import FrameRenderer

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

        self.sim = SimulationController(frame_time=0.05)
        self.renderer = FrameRenderer(self.sim)

        self._init_ui()
        self._init_timer()

    def _init_ui(self):
        """
        Builds the user interface layout and widgets.
        """

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Simulation display
        self.simulation_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.simulation_label)

        # Play button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self._start)
        layout.addWidget(self.play_button)

        # Speed slider
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 200)
        self.speed_slider.setValue(int(self.sim.frame_time * 1000))
        self.speed_slider.valueChanged.connect(self._change_speed)
        layout.addWidget(self.speed_slider)

    def _init_timer(self):
        """
        Initializes the QTimer for frame updates.
        """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_frame)
        QTimer.singleShot(0, self._update_frame)

    def _start(self):
        """
        Starts the simulation loop.
        """
        self.play_button.setEnabled(False)
        self.timer.start(int(self.sim.frame_time * 1000))

    def _change_speed(self, ms: int):
        """
        Updates the simulation speed based on slider value.

        Args:
            ms (int): Milliseconds per frame.
        """
        self.sim.frame_time = ms / 1000
        if self.timer.isActive():
            self.timer.start(ms)

    def _update_frame(self):
        """
        Renders and displays the next frame of the simulation.
        """
        pixmap = self.renderer.render_next_frame(self.simulation_label.size())
        self.simulation_label.setPixmap(pixmap)
