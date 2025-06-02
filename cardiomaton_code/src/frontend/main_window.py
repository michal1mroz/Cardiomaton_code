from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy,
    QPushButton, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QTimer
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
        layout.addWidget(self.simulation_label)

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
        self.speed_slider.setFixedWidth(300)
        slider_layout.addWidget(self.speed_slider, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(slider_layout)
        # layout.addWidget(self.speed_slider)

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
            self.timer.start(int(self.sim.frame_time * 1000))
            self.play_button.setText("Stop")
            self.running = True

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
        pixmap = self.renderer.render_next_frame(self.simulation_label.size())
        self.simulation_label.setPixmap(pixmap)
