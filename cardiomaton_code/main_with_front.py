import sys
from PyQt6.QtWidgets import QApplication
from src.frontend.main_window import MainWindow
# from src.models.cell_type import ConfigLoader
from cardiomaton_code.src.backend.enums.cell_type import ConfigLoader
from src.database.db import init_db

def main():
    """
    Entry point for the Cardiomaton application.

    Initializes the Qt application, sets up the main window, and starts the event loop. Ensures a clean shutdown
    when the application is closed.
    """
    ConfigLoader.loadConfig()
    init_db()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
