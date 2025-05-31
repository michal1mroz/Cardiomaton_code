import sys
from PyQt6.QtWidgets import QApplication
from src.frontend.main_window import MainWindow

def main():
    """
    Entry point for the Cardiomaton application.

    Initializes the Qt application, sets up the main window, and starts the event loop. Ensures a clean shutdown
    when the application is closed.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
