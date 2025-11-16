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
        self.selected_cells = [set()]

    def add_cells(self, cells):
        if isinstance(cells, tuple):
            if cells not in self.selected_cells[-1]:
                self.selected_cells[-1].add(cells)
        elif isinstance(cells, list):
            for cell in cells:
                if cell not in self.selected_cells[-1]:
                    self.selected_cells[-1].add(cell)

    def remove_cells(self, cells):
        if isinstance(cells, tuple):
            if cells in self.selected_cells[-1]:
                self.selected_cells[-1].remove(cells)
        elif isinstance(cells, list):
            for cell in cells:
                if cell in self.selected_cells[-1]:
                    self.selected_cells[-1].remove(cell)

    def commit_change(self):
        cells = self.selected_cells[-1]
        self.selected_cells.append(set())
        return cells

    def undo_change(self):
        if len(self.selected_cells) > 1:
            self.selected_cells.pop(-2)

    def get_color(self, index, total=10):
        hue = int((index % total) * 360 / total)
        color = QColor.fromHsv(hue, 255, 255, 128)
        color.setAlpha(55)
        return color

    def get_highlights(self):
        return self.selected_cells