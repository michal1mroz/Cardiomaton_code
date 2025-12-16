import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from src.frontend.ui_components.loading_window import PlaceholderWindow
from time import sleep


def main():
    """
    Entry point for the Cardiomaton application.

    Initializes the Qt application, sets up the main window, and starts the event loop. Ensures a clean shutdown
    when the application is closed.
    """

    def start_app():
        from src.backend.enums.cell_type import ConfigLoader
        from src.database.db import init_db
        from src.frontend.main_window import MainWindow

        ConfigLoader.loadConfig()
        init_db()

        main_window = MainWindow()
        main_window.show()

        loading.close()

    app = QApplication(sys.argv)

    loading = PlaceholderWindow()
    loading.show()

    app.processEvents()

    # Uruchom inicjalizację PO starcie pętli zdarzeń
    QTimer.singleShot(0, start_app)

    sys.exit(app.exec())


    # app = QApplication(sys.argv)
    #
    # window = PlaceholderWindow()
    # window.show()
    #
    #
    # app.processEvents()
    #
    # from src.backend.enums.cell_type import ConfigLoader
    # from src.database.db import init_db
    # from src.frontend.main_window import MainWindow
    #
    # ConfigLoader.loadConfig()
    # init_db()
    #
    # window = MainWindow()
    # window.show()
    #
    # sys.exit(app.exec())

if __name__ == "__main__":
    main()