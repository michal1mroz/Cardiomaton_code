from PyQt6.QtWidgets import QMainWindow, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QSize, Qt


class PlaceholderWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Rozmiary takie same jak MainWindow
        self.resize(1100, 600)
        self.setMinimumSize(QSize(1100, 600))
        self.setMaximumSize(QSize(1100, 600))
        self.setWindowTitle("Cardiomaton - Loading...")

        # Wyświetlenie tła
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap("./resources/style/light_background.png")
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)  # dopasowuje do okna
        self.setCentralWidget(self.label)

        # Opcjonalnie okno bez ramek (ładniej jako splash)
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
