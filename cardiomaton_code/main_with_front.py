import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread

from src.frontend.ui_components.loading_window import PlaceholderWindow
from src.workers.backend_init_worker import BackendInitWorker


def main():
    """
    Entry point for the Cardiomaton application.

    Initializes the Qt application, shows a loading window,
    and initializes the backend asynchronously in a separate thread.
    """

    app = QApplication(sys.argv)

    loading = PlaceholderWindow()
    loading.show()

    # --- Backend initialization thread setup ---

    backend_thread = QThread()
    backend_worker = BackendInitWorker(base_frame_time=0.05, size = (292, 400))

    backend_worker.moveToThread(backend_thread)

    def on_backend_ready(simulation, renderer, image):
        from src.backend.enums.cell_type import ConfigLoader
        from src.database.db import init_db
        from src.frontend.main_window import MainWindow

        ConfigLoader.loadConfig()
        init_db()

        main_window = MainWindow(
            simulationController=simulation,
            frameRenderer=renderer,
            image=image
        )
        main_window.show()

        loading.close()

        backend_thread.quit()
        backend_thread.wait()

    backend_thread.started.connect(backend_worker.run)
    backend_worker.finished.connect(on_backend_ready)
    backend_worker.finished.connect(backend_worker.deleteLater)
    backend_thread.finished.connect(backend_thread.deleteLater)

    backend_thread.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()