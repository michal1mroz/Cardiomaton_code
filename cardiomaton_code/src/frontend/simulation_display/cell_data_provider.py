from typing import Tuple, Optional

from src.backend.controllers.simulation_controller import SimulationController
from src.models.cell import CellDict


class CellDataProvider:
    def __init__(self, simulation_controller: SimulationController):
        self.simulation_controller = simulation_controller
    @property
    def shape(self) -> Tuple[int, int]:
        return self.simulation_controller.shape

    def get_cell_data(self, pos: Tuple[int, int]) -> Optional[CellDict]:
        return self.simulation_controller.get_cell_data(pos)