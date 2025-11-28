from dataclasses import dataclass
from typing import Dict, Tuple

from src.backend.models.cell import Cell


@dataclass
class AutomatonDto():
    cell_map: Dict[Tuple[int, int], Cell]
    shape: Tuple[int, int]
    frame: int
