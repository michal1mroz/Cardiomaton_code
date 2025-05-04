from __future__ import annotations
from typing import List, Tuple
from models.cell_state import CellState

class Cell:
    """
    Class to store information about specific cell.
    """
    def __init__(self, position: Tuple[int, int], init_state: CellState = CellState.WAITING, self_polarization: bool = False, self_polarization_timer: int = 0):
        """
        Cell constructor.
        
        Args:
            init_state (CellState, optional): Initial state of the cell before the simulation started. Defaulte is CellState.POLARIZATION.
            self_polarization (bool, optional): Controls the cells ability to self polarize. Default state is False.
        """
        self.state = init_state
        self.self_polarization = self_polarization

        self.last_polarized = 0
        self.self_polar_timer = 10 
        self.position = position 
        self.neighbours = []

    def __repr__(self):
        """
        Debug print method
        """
        return f"[Cell]: State: {self.state}, auto polar: {self.self_polarization}, last polarized: {self.last_polarized}, position: {self.position}, neighbour count: {len(self.neighbours)}"

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
            CellState.WAITING: 'gray',
            CellState.POLARIZATION: 'yellow',
            CellState.DEPOLARIZATION: 'red',
            CellState.ABS_REFRACTION: 'blue',
            CellState.REFRACTION: 'green',
            CellState.DEAD: 'black',
            }[self.state]

    def to_int(self) -> int:
        """
        Simple method to map the current state to the corresponding numerical value
        
        Returns:
            state (int): Numerical value from CellState class
        """
        return self.state.value + 1

