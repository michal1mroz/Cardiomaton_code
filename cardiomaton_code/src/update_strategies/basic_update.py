from src.update_strategies.base import UpdateStrategy

#from src.models.cell_state import CellState
from cardiomaton_code.src.backend.enums.cell_state import CellState

class BasicUpdate(UpdateStrategy):
    def update(self, cell, current_frame):
        """
        Public method to update the state of the cell. Does not modify the state of the cell - that would break down the automaton.

        Args:
            cell (Cell): Cell which state will be updated
            current_frame (int): Frame from the automaton, used to measure time (to be changed to some kind of delta time value in the future)

        Returns:
            Tuple[CellState, bool] - a new state and a flag indicating spontaneous depolarization.
        """
        if cell.state == CellState.DEAD:
            return cell.state, False  
         # Losing charge
        if cell.state != CellState.POLARIZATION:
            return CellState((cell.state.value + 1) % (len(CellState) - 1)), False
        # Check if it can take in charge
        for nei in cell.neighbours:
            if nei.state == CellState.DEPOLARIZATION:
                return CellState.DEPOLARIZATION, False
            
        # Check if can self polarize
        if cell.self_polarization and current_frame >= cell.self_polar_threshold: 
            return CellState.POLARIZATION, True 

        # No update
        return cell.state, False
            
       