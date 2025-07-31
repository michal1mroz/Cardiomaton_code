from typing import Tuple
from src.models.cell import Cell
from src.models.cell_state import CellState
from abc import ABC, abstractmethod

class UpdateStrategy(ABC):
    @abstractmethod
    def update(self, cell: Cell, current_frame: int) -> Tuple[CellState, bool]:
        pass
    
class UpdateBaseCharge(ABC):
    @abstractmethod
    def update(self, cell: Cell) -> Tuple[int, CellState]:
        pass
