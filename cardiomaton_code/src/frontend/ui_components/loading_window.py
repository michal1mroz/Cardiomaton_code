from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QSize


class PlaceholderWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Rozmiar splash screen
        self.setFixedSize(QSize(400, 400))

        # Okno bez ramek + zawsze na wierzchu
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Centralny widget i layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        # Logo aplikacji
        logo_label = QLabel(self)
        logo_pixmap = QPixmap("resources/style/logo.png")
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setScaledContents(True)
        logo_label.setFixedSize(150, 150)

        # Tytuł aplikacji
        title_label = QLabel("Cardiomaton", self)
        title_font = QFont("Arial", 18, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Dodanie elementów do layoutu
        layout.addWidget(logo_label)
        layout.addWidget(title_label)

        self.setCentralWidget(central_widget)
