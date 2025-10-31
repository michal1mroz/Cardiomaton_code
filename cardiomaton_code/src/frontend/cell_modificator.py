from PyQt6.QtGui import QColor



class CellModificator:
    def __init__(self, name : str = "martwica", color: QColor = QColor(0, 0, 0, 127)):
        self.name = name
        self.color = color
        self.selected_cells = []

    def add_cells(self, cells):
        if isinstance(cells, tuple):
            if cells not in self.selected_cells:
                self.selected_cells.append(cells)
        elif isinstance(cells, list):
            for cell in cells:
                if cell not in self.selected_cells:
                    self.selected_cells.append(cell)

    def remove_cells(self, cells):
        if isinstance(cells, tuple):
            if cells in self.selected_cells:
                self.selected_cells.remove(cells)
        elif isinstance(cells, list):
            for cell in cells:
                if cell in self.selected_cells:
                    self.selected_cells.remove(cell)

    def apply_change(self):
        ...