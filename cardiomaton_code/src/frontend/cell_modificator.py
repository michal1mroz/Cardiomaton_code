from PyQt6.QtGui import QColor
from dataclasses import dataclass

@dataclass
class CellModification:
    cells: list[tuple[int, int]]
    purkinje_charge_parameters: dict[str, float]
    atrial_charge_parameters: dict[str, float]
    pacemaker_charge_parameters: dict[str, float]
    necrosis_enabled: bool = False
    modifier_name: str | None = None
    metadata: dict | None = None

class CellModificator:
    def __init__(self):
        self.selected_cells: dict[tuple[int, int], list[int]] = {}
        self.current_modification = 0

    def add_cell(self, cell):
        if cell not in self.selected_cells:
            self.selected_cells[cell] = [self.current_modification]
        else:
            if len(self.selected_cells[cell]) == 0 or self.selected_cells[cell][-1] != self.current_modification:
                self.selected_cells[cell].append(self.current_modification)

    def remove_cell(self, cell):
        if cell not in self.selected_cells:
            return

        history = self.selected_cells[cell]
        if self.current_modification in history:
            history.remove(self.current_modification)

        if len(history) == 0:
            del self.selected_cells[cell]

    def commit_change(self):
        committed = set()

        for cell, history in self.selected_cells.items():
            if len(history) > 0 and history[-1] == self.current_modification:
                committed.add(cell)

        self.current_modification += 1
        return committed

    def undo_change(self):
        if self.current_modification == 0:
            return

        last = self.current_modification - 1
        to_delete = []

        for cell, history in self.selected_cells.items():
            if last in history:
                history.remove(last)
                if len(history) == 0:
                    to_delete.append(cell)

        for cell in to_delete:
            del self.selected_cells[cell]

    def get_highlights(self):
        return self.selected_cells