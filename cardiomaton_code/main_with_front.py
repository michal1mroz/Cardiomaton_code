import sys
from PyQt6.QtWidgets import QApplication
# from src.models.cell_type import ConfigLoader

from src.frontend.ui_components.loading_window import PlaceholderWindow


def main():
    """
    Entry point for the Cardiomaton application.

    Initializes the Qt application, sets up the main window, and starts the event loop. Ensures a clean shutdown
    when the application is closed.
    """


    app = QApplication(sys.argv)

    window = PlaceholderWindow()
    window.show()


    app.processEvents()

    from src.backend.enums.cell_type import ConfigLoader
    from src.database.db import init_db
    from src.frontend.main_window import MainWindow

    ConfigLoader.loadConfig()
    init_db()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
