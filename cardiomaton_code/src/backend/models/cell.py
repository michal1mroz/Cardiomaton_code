from __future__ import annotations
from typing import Dict, Tuple, List, TypedDict

from cardiomaton_code.src.backend.enums.cell_type import CellType
from cardiomaton_code.src.backend.enums.cell_state import CellState
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
    """
    Helper class used to store the cell before it can be loaded to the automaton
    """
    def __init__(self, position: Tuple[int, int], cell_type: CellType, cell_config: Dict = None, init_state: CellState = CellState.POLARIZATION,
                 self_polarization: bool = None, self_polarization_timer: int = 0):

        self.config = cell_config if cell_config is not None else cell_type.config 
        self.pos_x, self.pos_y = position
        self.cell_type = cell_type

        self.cell_data = self.config["cell_data"]
        self.self_polarization = self_polarization if self_polarization is not None else self.config.get("self_polarization", False)
        self.state = init_state
        # cells withot self-depolarization can have the timer set to 0
        if cell_type in [CellType.INTERNODAL_ANT, CellType.INTERNODAL_MID, CellType.INTERNODAL_POST]:
            self.timer = 0
        else: # cells with self-depolarization have shifted initial timer so that the user does not wait too long for the first action potential
            self.timer = 2200
        # self.timer = 0
        self.neighbors = []
        self.period = self.config["period"]
        self.n_range = self.config["range"]
        self.charges, self.max_charge, self.ref_threshold = ChargeUpdate.get_func(self.config)
        self.charge = self.charges[self.timer]

    def __repr__(self) -> str:
        return f"<Cell>: position: ({self.pos_x}, {self.pos_y}), charge: {self.charge}, state: {self.state}, self_polar: {self.self_polarization}, type: {self.cell_type}"

    def add_neighbor(self, neighbor: Cell) -> None:
        self.neighbors.append(neighbor)
        
    def neighbors_to_tuple_list(self) -> List[Tuple[int, int]]:
        return [
            (self.pos_x - nei.pos_x, self.pos_y - nei.pos_y)
            for nei in self.neighbors
        ]
