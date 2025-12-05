from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class HelpWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(50, 40, 50, 40)

        self.main_layout.setSpacing(40)

        self.image_container = QWidget()
        self.image_container.setObjectName("Layout")  # Nazwa dla QSS
        self.image_container.setFixedHeight(250)  # Stała wysokość (dostosuj)

        # 2. Wewnętrzny layout do centrowania
        # Używamy QHBoxLayout (poziomego) lub QVBoxLayout,
        # oba zadziałają z flagą AlignCenter.
        container_layout = QVBoxLayout(self.image_container)
        # Zerujemy marginesy wewnętrzne, żeby obrazek nie był odpychany od krawędzi kontenera
        container_layout.setContentsMargins(0, 0, 0, 0)

        # 3. Etykieta z obrazkiem
        image_label = QLabel()
        # PODMIEŃ ŚCIEŻKĘ NA SWOJĄ:
        pixmap = QPixmap("./resources/images/twoj_obrazek.png")

        if not pixmap.isNull():
            # Opcjonalnie: Jeśli obrazek jest większy niż kontener,
            # przeskaluj go zachowując proporcje (SmoothTransformation daje lepszą jakość)
            if pixmap.height() > 250 or pixmap.width() > 800:
                pixmap = pixmap.scaled(
                    800, 240,  # Maksymalne wymiary (trochę mniejsze niż kontener)
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("Image not found")
            image_label.setStyleSheet("color: red;")

        # 4. Dodanie obrazka do layoutu kontenera z wycentrowaniem
        # align=Qt.AlignmentFlag.AlignCenter jest tu kluczowe
        container_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- KONIEC TWORZENIA KONTENERA ---

        # Dodanie gotowego kontenera do głównego layoutu okna
        # (rozciągnie się na szerokość automatycznie dzięki QVBoxLayout rodzica)
        self.main_layout.addWidget(self.image_container)

        # Wypychacz na dole, żeby kontener trzymał się góry
        self.main_layout.addStretch()