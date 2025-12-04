from PyQt6.QtWidgets import QVBoxLayout

from src.frontend.cell_inspecting.cell_inspector import CellInspector
from src.frontend.ui_simulation_window import UiSimulationWindow
from src.models.cell import CellDict


class CellInspectorManager:
    def __init__(self, ui: UiSimulationWindow):
        self.ui = ui
        self._current_inspector: CellInspector | None = None

        if not self.ui.cell_inspector_container.layout():
            self.ui.cell_inspector_layout = QVBoxLayout(self.ui.cell_inspector_container)
            self.ui.cell_inspector_layout.setContentsMargins(0, 0, 0, 0)

    def show_inspector(self, cell_data: CellDict, on_close_callback, is_running: bool):
        self.hide_inspector()

        self._current_inspector = CellInspector(
            cell_data,
            on_close_callback=on_close_callback,
            running=is_running
        )

        self.ui.cell_inspector_container.layout().addWidget(self._current_inspector)
        self.ui.cell_inspector_container.show()
        self.ui.tools_container.setVisible(False)
        self.ui.presets_layout.setVisible(False)

        settings_layout = self.ui.settings_container.layout()

        settings_layout.insertWidget(0, self.ui.cell_inspector_container, stretch=1)

    def hide_inspector(self):
        if self._current_inspector:
            settings_layout = self.ui.settings_container.layout()
            settings_layout.removeWidget(self.ui.cell_inspector_container)
            self.ui.cell_inspector_container.hide()

            self.ui.tools_container.setVisible(True)
            self.ui.presets_layout.setVisible(True)

            self._current_inspector.setParent(None)
            self._current_inspector.deleteLater()
            self._current_inspector = None

    def update_data(self, new_data: CellDict):
        if self._current_inspector:
            self._current_inspector.update(new_data)

    def set_running_state(self, running: bool):
        if self._current_inspector:
            self._current_inspector.set_running(running)

    def get_current_position(self):
        if self._current_inspector:
            return self._current_inspector.position
        return None

    @property
    def is_active(self) -> bool:
        return self._current_inspector is not None