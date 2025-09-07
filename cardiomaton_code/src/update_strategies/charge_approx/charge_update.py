from typing import Tuple
import numpy as np
from src.models.cell import Cell
from src.models.cell_type import CellType

from src.update_strategies.charge_approx.ms_final import pacemaker_AP_full

"""
    Wrapper module exposing methods to update cell state according to approximated graphs.
"""

class ChargeUpdate():

    def __init__(self):
        self.period = 200 # modify to change the time (in frames) per function cycle

        # Potential improvement - change cell_data in cell_data.json to the uniform dict
        # that can be passed as an argument to those functions 
        conf = CellType.SA_NODE.config['cell_data']
        # Arguments for the method used. Should correspond to those present in the cell data for the given cell type
        # Period of the pacemaker_AP_full is 0.8. a is used to cast the frame time to that period
        self.a = 0.8 / float(self.period) 

        self.functions = {
            CellType.SA_NODE: lambda t: pacemaker_AP_full((t % self.period) * self.a, **conf)
                }

        # Value for which self.function returns max value
        self.max_args = {
            CellType.SA_NODE: self._get_max_arg(self.functions[CellType.SA_NODE])
            }
        self.default_func = lambda t: pacemaker_AP_full((t % self.period) * (1.2 / 200), **CellType.INTERNODAL_ANT.config['cell_data'])
        self.default_arg = self._get_max_arg(self.default_func)

    def _get_max_arg(self, func) -> int:
        """
            Find the time argument for update method that returns max
            charge value

            Args:
                func - function accepting time as int and returning 
                    charge value as an int

            Returns:
                int - greatest value from the func
            """
        args = list(map(func, list(range(self.period))))
        return np.argmax(args)

    def depolarize(self, cell: Cell) -> float:
        """
            Returns the max charge available for that function.
            Updates the state_timer of a call to the max_arg value
        """
        cell.state_timer = self.max_args.get(cell.cell_type, self.default_arg)
        return self.functions.get(cell.cell_type, self.default_func)(cell.state_timer)

    def update(self, cell: Cell) -> float:
        """
            Returns the new charge of the cell
        """
        return self.functions.get(cell.cell_type, self.default_func)(cell.state_timer)
       