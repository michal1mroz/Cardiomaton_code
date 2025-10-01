from __future__ import annotations
from typing import Dict, Tuple, List, TypedDict

from src.backend.models.cell_type import CellType
from src.backend.models.cell_state import CellState
from src.update_strategies.charge_approx.charge_update import ChargeUpdate

class CellDict(TypedDict):
    position: Tuple[int, int]
    state_value: int
    state_name: str
    charge: float
    ccs_part: str
    cell_type: str
    auto_polarization: bool

class Cell:
    def __init__(self, position: Tuple[int, int], cell_type: CellType, cell_state: CellState = CellState.POLARIZATION,
                 cell_data: Dict[str, float] = None, self_polarization: bool = None):
        
        self.pos_x, self.pos_y = position
        self.cell_type = cell_type
        cfg = cell_type.config
        self.cell_data = cfg["cell_data"] if cell_data is None else cell_data
        self.self_polarization = bool(cfg.get("self_polarization", False)) if self_polarization is None else self_polarization
        self.state = cell_state
        self.timer = 0
        self.charge = 0.0
        self.neighbors = []
        self.period = int(self.cell_data.get("range", 200))
        self.charges, self.max_charge = ChargeUpdate.get_func(self.cell_data)

    def __repr__(self) -> str:
        return f"<Cell>: position: ({self.pos_x}, {self.pos_y}), charge: {self.charge}, state: {self.state}, self_polar: {self.self_polarization}, type: {self.cell_type}"

    def add_neighbor(self, neighbor: Cell) -> None:
        self.neighbors.append(neighbor)
        
    def neighbors_to_tuple_list(self) -> List[Tuple[int, int]]:
        return [
            (self.pos_x - nei.pos_x, self.pos_y - nei.pos_y)
            for nei in self.neighbors
        ]
