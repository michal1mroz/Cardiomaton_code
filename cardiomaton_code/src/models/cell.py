from __future__ import annotations
from typing import List, Tuple, Dict, TypedDict
from src.models.cell_state import CellState

# from src.models.cell_type import CellType

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
    Class to store information about specific cell.
    """

    # To be moved to better location
    # For now, we have one(?) self-depolarizing cell and the rest of the cells is treated like regular cardiomycytes
    # which is not tru biologically, but works well in the first version of simulation

    # CELL DATA MOVED TO CellType enum values (for now?)
    # cell_data = {
    #     "default": {
    #         "resting_membrane_potential": -90,
    #         "peak_potential": 30,
    #         "threshold_potential": -5,
    #         "duration": 60,
    #         "repolarization_potential_drop": 2, # more values to be established because repolarization pace changes
    #         "relative_refractory_period_threshold": -60,
    #     },
    #     "auto": {
    #         "resting_membrane_potential": -60,
    #         "peak_potential": 20,
    #         "threshold_potential": -35,
    #         "duration": 40,
    #         "spontaneous_depolarization_step_slow": 0.13,
    #         "spontaneous_depolarization_step_fast": 27.5,
    #         "repolarization_potential_drop": 2,
    #         "relative_refractory_period_threshold": -40,
    #     },
    # }

    self_polar_threshold = 200

    def __init__(self, position: Tuple[int, int],cell_type: CellType, cell_data : Dict, init_state: CellState = CellState.POLARIZATION, self_polarization: bool = False, self_polarization_timer: int = 0):
        """
        Cell constructor.
        
        Args:
            init_state (CellState, optional): Initial state of the cell before the simulation started. Default is CellState.POLARIZATION.
            self_polarization (bool, optional): Controls the cells ability to self polarize. Default state is False.
        """
        self.state = init_state
        self.self_polarization = self_polarization
        self.cell_type = cell_type

        # self.state_durations = durations

        self.self_polar_timer = 0
        self.state_timer = 0

        self.position = position 
        self.neighbours = []
        self.charge = 0

        self.cell_data = cell_data

        # # To be changed according to some type of dict
        # self.type = "default"
        # if self.self_polarization:
        #     self.type = "auto"

    def reset_timer(self):
        self.state_timer = 0

    def update_timer(self):
        self.state_timer += 1

    def reset_self_polar_timer(self):
        self.self_polar_timer = 0

    def update_self_polar_timer(self):
        self.self_polar_timer += 1

    def __repr__(self):
        """
        Debug print method
        """
        return f"[Cell]: State: {self.state}, auto polar: {self.self_polarization}, charge: {self.charge}, position: {self.position}, neighbour count: {len(self.neighbours)}"

    def add_neighbour(self, neighbour: Cell) -> None:
        """
        Add single neighbour to the cell
        
        Args:
            neighbour (Cell): cell to be added as a neighbour
        """
        self.neighbours.append(neighbour)

    def get_color(self) -> str:
        """
        Simple method to retrieve colour based on the state

        Returns:
            color (str): Color coresponding to the state
        """
        return {
            # CellState.WAITING: 'gray',
            CellState.POLARIZATION: 'gray',
            CellState.RAPID_DEPOLARIZATION: 'yellow',
            CellState.SLOW_DEPOLARIZATION: 'pink',
            CellState.REPOLARIZATION: 'red',
            CellState.DEAD: 'black',
            }[self.state]

    def to_int(self) -> int:
        """
        Simple method to map the current state to the corresponding numerical value
        
        Returns:
            state (int): Numerical value from CellState class
        """
        return self.state.value + 1

    def to_tuple(self) -> Tuple[int, bool, str, str, float]:
        """
        Simple method to map the current state to tuple with the most important information
        The tuple contains:
         - self_polarization (bool): Whether the cell can self-polarize.
         - state (str): Human-readable name of the cell's current state (e.g., 'Waiting', 'Polarization').

        Returns:
            Tuple[int, bool, str]: A tuple with the cell's Numerical value, self-polarization flag, and state name.
        """
        return (self.state.value + 1,
                self.self_polarization,
                self.state.name.capitalize(),
                self.cell_type.value["name"],
                self.charge)

    def to_dict(self) -> CellDict:
        """
        Method to serialize the cell data for rendering on the front end. Can be changed to dto if the need arises.

        Returns:
            Dict: dictionary that stores all the relevant fields of the cell
        """
        return {
            "position": self.position,
            "state_value": self.state.value + 1,
            "state_name": self.state.name.capitalize(),
            "charge": self.charge,
            "ccs_part": self.cell_type.value["name"],
            "cell_type": self.cell_type.name,
            "auto_polarization": self.self_polarization,
        }

    def update_data(self, data_dict: CellDict) -> None:
        """
        Method to update state of cell from the CellDict. For now allows only
        for the depolarization of the cell.

        Args:
            data_dict (CellDict): Dict with new values for the cell
        """
        self.state = CellState(int(data_dict['state_value'])) 
        if self.state == CellState.RAPID_DEPOLARIZATION:
            self.charge = self.cell_data.get('peak_potential', 0)

    def copy(self) -> Cell:
        """
        Creates a copy of the cell with the same state, timers, and configuration.
        Neighbours are not copied (they must be reconnected externally).

        Returns:
            Cell: A new instance of Cell with the same attributes.
        """
        copied_cell = Cell(
            position=self.position,
            cell_type=self.cell_type,
            durations=self.state_durations,
            init_state=self.state,
            self_polarization=self.self_polarization,
            self_polarization_timer=self.self_polar_timer
        )
        copied_cell.state_timer = self.state_timer
        # Neighbours are intentionally not copied

        return copied_cell
