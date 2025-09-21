from src.update_strategies.base import UpdateBaseCharge
from src.models.cell import Cell 
#from src.models.cell_state import CellState
from src.backend.models.cell_state import CellState
from typing import Tuple

class UpdateCharge(UpdateBaseCharge):
    def update(self, cell: Cell) -> Tuple[int, CellState]:
        """
        Updates discrete state together with the new charge. Each leaf can be modified, so that
        it represents the behaviour more accurately.
        REFRACTION_POLAR is a constant - minimal difference between the charge in the current cell and
        a neighbour to allow for the depolarization in CellState.REFRACTION.

        Args:
            cell (Cell): updated cell

        Returns:
            charge (int): new charge of the cell
            state (CellState): new state of the cell
        """
        REFRACTION_POLAR = 1000
        
        cell_data_dict = cell.cell_data[cell.type]
        
        match cell.state:
            case CellState.DEAD:
                return 0, cell.state
            
            case CellState.ABS_REFRACTION:
                charge = cell.charge - cell_data_dict["step"]
                if cell.self_polarization:
                    if charge <= cell_data_dict["threshold"]:
                        return charge, CellState.REFRACTION
                    return charge, cell.state
                else:
                    if charge <= cell_data_dict["threshold"]:
                        return charge, CellState.REFRACTION
                    return charge, cell.state
            
            case CellState.REFRACTION:
                if len(list(filter(lambda x: x.charge - cell.charge >= REFRACTION_POLAR, cell.neighbours))) >= 1:
                    return cell_data_dict["peak_charge"], CellState.DEPOLARIZATION
                charge = cell.charge - cell_data_dict["step"]
                if cell.self_polarization:
                    if charge <= cell_data_dict["resting_charge"]:
                        return cell_data_dict["resting_charge"], CellState.POLARIZATION
                    return charge, cell.state
                else:
                    if charge <= cell_data_dict["resting_charge"]:
                        return cell_data_dict["resting_charge"], CellState.POLARIZATION
                    return charge, cell.state
                
            case CellState.POLARIZATION:
                if len(list(filter(lambda x: x.state == CellState.DEPOLARIZATION, cell.neighbours))) >= 1:
                    return cell_data_dict["peak_charge"], CellState.DEPOLARIZATION
                if cell.self_polarization:
                    if cell.charge >= cell_data_dict["peak_charge"]:
                        return cell_data_dict["peak_charge"], CellState.DEPOLARIZATION
                    if cell.charge >= cell_data_dict["threshold"]:
                        return cell.charge + cell_data_dict["step_2"], CellState.POLARIZATION
                    else:
                        return cell.charge + cell_data_dict["step_1"], CellState.POLARIZATION
                else:
                    return cell.charge, cell.state

            case CellState.DEPOLARIZATION:
                return cell.charge, CellState.ABS_REFRACTION