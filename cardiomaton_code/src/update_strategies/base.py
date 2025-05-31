from typing import Tuple
from src.models.cell import Cell
from src.models.cell_state import CellState

class UpdateStrategy:
    def update(self, cell: Cell, current_frame: int) -> Tuple[CellState, bool]:
        raise NotImplementedError
