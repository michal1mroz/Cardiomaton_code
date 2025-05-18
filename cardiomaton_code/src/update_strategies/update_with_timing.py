from src.update_strategies.base import UpdateStrategy
from src.models.cell import Cell
from src.models.cell_state import CellState

class UpdateWithTiming(UpdateStrategy):
    def update(self, cell, current_frame):
        """
        Updates the cell's state based on neighbors and internal timing.

        Follows this rule:
        - a polarized cell waits for neighbor's depolarization
        - depolarization is a spike that lasts 1 frame
        - after that a fixed sequence of refractory states with timers starts.

        Returns:
            Tuple[CellState, bool] - a new state and a flag indicating spontaneous depolarization.
        """
        if cell.state == CellState.DEAD:
            return cell.state, False
        
        if cell.state in cell.state_durations:
            cell.update_timer()
            if cell.state_timer >= cell.state_durations[cell.state]:
                next_state = {
                    CellState.DEPOLARIZATION: CellState.ABS_REFRACTION,
                    CellState.ABS_REFRACTION: CellState.POLARIZATION,
                    # CellState.REFRACTION: CellState.POLARIZATION # the refraction does not work now
                }[cell.state]
                cell.reset_timer()
                return next_state, False
            else:
                return cell.state, False
            
        # Spontaneous depolarization
        if cell.self_polarization:
            if current_frame >= cell.self_polar_threshold:
                cell.reset_self_polar_timer()
                return CellState.DEPOLARIZATION, True
            else:
                cell.update_self_polar_timer()
                return cell.state, False

                
        # Depolarization induced by neighbor
        if cell.state == CellState.POLARIZATION:
            for nei in cell.neighbours:
                if nei.state == CellState.DEPOLARIZATION:
                    cell.reset_timer()
                    return CellState.DEPOLARIZATION, False
    
        return cell.state, False