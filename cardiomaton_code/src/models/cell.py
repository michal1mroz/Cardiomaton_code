from __future__ import annotations
from typing import List, Tuple, Dict
from src.models.cell_state import CellState

# from src.models.cell_type import CellType


class Cell:
    """
    Class to store information about specific cell.
    """

    state_durations = {
        CellState.DEPOLARIZATION: 1,
        CellState.ABS_REFRACTION: 50,
        CellState.REFRACTION: 10
    }

    self_polar_threshold = 200

    def __init__(self, position: Tuple[int, int],cell_type: CellType, durations : Dict, init_state: CellState = CellState.POLARIZATION, self_polarization: bool = False, self_polarization_timer: int = 0):
        """
        Cell constructor.
        
        Args:
            init_state (CellState, optional): Initial state of the cell before the simulation started. Default is CellState.POLARIZATION.
            self_polarization (bool, optional): Controls the cells ability to self polarize. Default state is False.
        """
        self.state = init_state
        self.self_polarization = self_polarization
        self.type = cell_type

        self.state_durations = durations

        self.self_polar_timer = 0
        self.state_timer = 0

        self.position = position 
        self.neighbours = []
    
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
        return f"[Cell]: State: {self.state}, auto polar: {self.self_polarization}, position: {self.position}, neighbour count: {len(self.neighbours)}"

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
            CellState.DEPOLARIZATION: 'yellow',
            CellState.ABS_REFRACTION: 'red',
            CellState.REFRACTION: 'pink',
            CellState.DEAD: 'black',
            }[self.state]

    def to_int(self) -> int:
        """
        Simple method to map the current state to the corresponding numerical value
        
        Returns:
            state (int): Numerical value from CellState class
        """
        return self.state.value + 1

    def to_tuple(self) -> Tuple[int, bool, str, str]:
        """
        Simple method to map the current state to tuple with the most important information
        The tuple contains:
         - self_polarization (bool): Whether the cell can self-polarize.
         - state (str): Human-readable name of the cell's current state (e.g., 'Waiting', 'Polarization').

        Returns:
            Tuple[int, bool, str]: A tuple with the cell's Numerical value, self-polarization flag, and state name.
        """
        return (self.state.value + 1, self.self_polarization, self.state.name.capitalize(), self.type.name.capitalize())

    def copy(self) -> Cell:
        """
        Creates a copy of the cell with the same state, timers, and configuration.
        Neighbours are not copied (they must be reconnected externally).

        Returns:
            Cell: A new instance of Cell with the same attributes.
        """
        copied_cell = Cell(
            position=self.position,
            cell_type=self.type,
            durations=self.state_durations,
            init_state=self.state,
            self_polarization=self.self_polarization,
            self_polarization_timer=self.self_polar_timer
        )
        copied_cell.state_timer = self.state_timer
        # Neighbours are intentionally not copied

        return copied_cell

