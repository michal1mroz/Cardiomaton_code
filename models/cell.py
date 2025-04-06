from models.cell_state import CellState


class Cell:
    """
    Class to store information about specific cell.
    """
    def __init__(self, init_state: CellState = CellState.WAITING, self_polarization: bool = False, self_polarization_timer: int = 0):
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

    def __repr__(self):
        """
        Debug print method
        """
        return f"State: {self.state}, auto polar: {self.self_polarization}, last polarized: {self.last_polarized}"

    def get_color(self) -> str:
        """
        Simple method to retrieve colour based on the state

        Returns:
            color (str): Color coresponding to the state
        """
        return {
            CellState.WAITING: 'white',
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
        return self.state.value

