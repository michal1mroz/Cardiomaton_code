import sys
from PyQt6.QtWidgets import QApplication
from src.frontend.ui_components.loading_window import PlaceholderWindow




def main():
    """
    Entry point for the Cardiomaton application.

    Initializes the Qt application, shows a loading window,
    and initializes the backend asynchronously in a separate thread.
    """
    K = 5
    SIZE = (292 * K, 400 * K)
    BASE_FRAME_TIME = 0.05

    app = QApplication(sys.argv)

    loading = PlaceholderWindow()
    loading.show()

    app.processEvents()

    # --- Backend classes import ---
    from PyQt6.QtGui import QImage
    from src.backend.controllers.simulation_controller import SimulationController
    from src.frontend.frame_rendering.frame_renderer import FrameRenderer
    from src.backend.enums.cell_type import ConfigLoader
    from src.database.db import init_db

    app.processEvents()
    # --- Backend initialization ---
    ConfigLoader.loadConfig()
    init_db()
    image = QImage(SIZE[1], SIZE[0], QImage.Format.Format_RGBA8888)
    sim = SimulationController(frame_time=BASE_FRAME_TIME, image=image)
    renderer = FrameRenderer(sim, image)

    app.processEvents()
    # --- Frontend initialization ---
    from src.frontend.main_window import MainWindow
    main_window = MainWindow(
        simulationController=sim,
        frameRenderer=renderer,
        image=image
    )
    loading.close()
    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()