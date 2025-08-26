from src.update_strategies.base import UpdateBaseCharge
from src.models.cell import Cell 
from src.models.cell_state import CellState
from src.update_strategies.charge_approx.charge_update import ChargeUpdate

from typing import Tuple

from random import uniform

"""
    Updates:
        - cells with self_polarize use ChargeUpdate class to update the value of the charge
"""

class UpdateChargeMSCopy(UpdateBaseCharge):
    def __init__(self):
        self.chargeUpdate = ChargeUpdate()

    def update(self, cell: Cell) -> Tuple[int, CellState]:
        """
        Updates discrete state together with the new charge. Each leaf can be modified, so that
        it represents the behaviour more accurately.
        REFRACTION_POLAR is a constant - minimal difference between the charge in the current cell and
        a neighbour to allow for the depolarization in CellState.REPOLARIZATION, when relative refraction
        threshold is reached.

        Args:
            cell (Cell): updated cell

        Returns:
            charge (int): new charge of the cell
            state (CellState): new state of the cell
        """
        REFRACTION_POLAR = 1000
        
        # cell_data_dict = cell.cell_data[cell.type]
        cell_data_dict = cell.cell_data
        
        cell.update_timer()

        match cell.state:
            case CellState.NECROSIS:
                return 0, cell.state

            case CellState.REPOLARIZATION_ABSOLUTE_REFRACTION:
                if cell.self_polarization:
                    charge = self.chargeUpdate.update(cell.state_timer)
                    if charge <= cell_data_dict["relative_refractory_period_threshold"]:
                        return charge, CellState.REPOLARIZATION_RELATIVE_REFRACTION
                    return charge, cell.state
                else:
                    charge = cell.charge - cell_data_dict["repolarization_potential_drop"]
                    if charge <= cell_data_dict["relative_refractory_period_threshold"]:
                        return charge, CellState.REPOLARIZATION_RELATIVE_REFRACTION
                    return charge, cell.state
            
            case CellState.REPOLARIZATION_RELATIVE_REFRACTION:
                if len(list(filter(lambda x: x.charge - cell.charge >= REFRACTION_POLAR, cell.neighbours))) >= 1:
                    if cell.self_polarization:
                        return self.chargeUpdate.depolarize(cell), CellState.RAPID_DEPOLARIZATION
                    return cell_data_dict["peak_potential"], CellState.RAPID_DEPOLARIZATION

                if cell.self_polarization:
                    charge = self.chargeUpdate.update(cell.state_timer)

                    if charge <= cell_data_dict["resting_membrane_potential"]:
                        return cell_data_dict["resting_membrane_potential"], CellState.SLOW_DEPOLARIZATION
                    return charge, cell.state
                else:
                    charge = cell.charge - cell_data_dict["repolarization_potential_drop"]
                    if charge <= cell_data_dict["resting_membrane_potential"]:
                        return cell_data_dict["resting_membrane_potential"], CellState.POLARIZATION
                    return charge, cell.state


            case CellState.POLARIZATION:
                if len(list(filter(lambda x: x.state == CellState.RAPID_DEPOLARIZATION, cell.neighbours))) >= 1:
                    if cell.self_polarization:
                        return self.chargeUpdate.depolarize(cell), CellState.RAPID_DEPOLARIZATION
                    return cell_data_dict["peak_potential"], CellState.RAPID_DEPOLARIZATION
                if cell.self_polarization:
                    charge = self.chargeUpdate.update(cell.state_timer)
                    return charge, CellState.SLOW_DEPOLARIZATION
                else:
                    return cell.charge, cell.state


            case CellState.SLOW_DEPOLARIZATION:
                # only self-depolarizing cells have this state
                if cell.charge >= cell_data_dict["peak_potential"]:
                    return cell_data_dict["peak_potential"], CellState.RAPID_DEPOLARIZATION
                if cell.charge >= cell_data_dict["threshold_potential"]: # ???
                    return self.chargeUpdate.update(cell.state_timer), CellState.RAPID_DEPOLARIZATION
                    # return cell.charge + cell_data_dict["spontaneous_depolarization_step_fast"], CellState.RAPID_DEPOLARIZATION
                else:
                    charge = self.chargeUpdate.update(cell.state_timer)

                    return charge, CellState.SLOW_DEPOLARIZATION

            case CellState.RAPID_DEPOLARIZATION:
                if cell.self_polarization:
                    return self.chargeUpdate.update(cell.state_timer), CellState.REPOLARIZATION_ABSOLUTE_REFRACTION
                return cell.charge, CellState.REPOLARIZATION_ABSOLUTE_REFRACTION
