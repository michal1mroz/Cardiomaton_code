from src.update_strategies.base import UpdateStrategy
from src.models.cell import Cell
from src.models.cell_state import CellState

class TestUpdate(UpdateStrategy):
    """
    The simplest version of cell state update with two states only: POLARIZATION and DEPOLARIZATION.

    Returns:
            Tuple[CellState, bool] - a new state and a flag indicating spontaneous depolarization.
    """
    def update(self, cell, current_frame = None):
        if cell.state == CellState.POLARIZATION:
            for nei in cell.neighbours:
                if nei.state == CellState.DEPOLARIZATION:
                    return CellState.DEPOLARIZATION, True
        return cell.state, False
    