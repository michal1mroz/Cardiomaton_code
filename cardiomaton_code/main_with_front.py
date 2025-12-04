import sys
from PyQt6.QtWidgets import QApplication
from src.frontend.main_window import MainWindow
# from src.models.cell_type import ConfigLoader
from cardiomaton_code.src.backend.enums.cell_type import ConfigLoader

CONFIG = "PHYSIOLOGICAL"
# CONFIG = "SINUS_BRADYCARDIA"
# CONFIG = "SINUS_TACHYCARDIA"
# CONFIG = "AV_BLOCK_I"
# CONFIG = "SA_BLOCK_RETROGRADE"
# CONFIG = "SINUS_PAUSE_RETROGRADE"

def main():
    """
    Entry point for the Cardiomaton application.

    Initializes the Qt application, sets up the main window, and starts the event loop. Ensures a clean shutdown
    when the application is closed.
    """

    configurations = {
        "PHYSIOLOGICAL" : "resources/data/cell_data.json",
        "SINUS_BRADYCARDIA" : "resources/data/sinus_bradycardia.json",
        "SINUS_TACHYCARDIA": "resources/data/sinus_tachycardia.json",
        "AV_BLOCK_I": "resources/data/av_block_i.json",
        "SINUS_PAUSE_RETROGRADE": "resources/data/sinus_pause_retrograde.json",
        "SA_BLOCK_RETROGRADE": "resources/data/sa_block_retrograde.json",
    }

    ConfigLoader.loadConfig(filepath=configurations[CONFIG])
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
