# src/backend/models/cell.pyi
from __future__ import annotations
from typing import Tuple, Dict, List, Optional
from typing_extensions import TypedDict

from src.backend.models.cell_state import CellState
from src.backend.models.cell_type import CellType


class CellDict(TypedDict):
    position: Tuple[int, int]
    state_value: int
    state_name: str
    charge: float
    ccs_part: str
    cell_type: str
    auto_polarization: bool


class Cell:
    # basic positional attributes
    pos_x: int
    pos_y: int

    # logical/state attributes
    state: CellState                 # Python-visible enum (stubs show python type)
    self_polarization: bool
    state_timer: int

    period: int
    charge_max: int
    charge: float

    # internal/backing data (kept as Python objects in implementation)
    _charges_array: object
    charges_mv: object               # memoryview-like object (double[:]) — typed as object in stub
    cell_type_py: CellType
    cell_data: Dict[str, float]
    neighbours: List["Cell"]

    def __init__(
        self,
        position: Tuple[int, int],
        cell_type: CellType,
        cell_data: Optional[Dict[str, float]] = ...,
        init_state: Optional[CellState] = ...,
        self_polarization: Optional[bool] = ...,
    ) -> None: ...

    def to_dict(self) -> CellDict: ...
    def update_data(self, data_dict: Dict) -> None: ...
    def reset_timer(self) -> None: ...
    def update_timer(self) -> None: ...
    def update_charge(self) -> float: ...
    def depolarize(self) -> float: ...
