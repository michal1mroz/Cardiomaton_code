from typing import Tuple
import numpy as np
from src.models.cell import Cell
from src.models.cell_state import CellState
from src.update_strategies.charge_approx.ms_final import pacemaker_AP_full
"""
    Wrapper module exposing methods to update cell state according to approximated graphs.
"""

class ChargeUpdate():

    def __init__(self):
        self.period = 100

        # Arguments for the method used. Should correspond to those present in the cell data for the given cell type
        self.args = {"V_rest": -60.0, "V_thresh": -40.0, "V_peak": 15.0,
                    "t_thresh": 0.35, "t_peak": 0.60, "t_end": 0.60,
                    "eps":0.005}     

        # Period of the pacemaker_AP_full is 0.8. a is used to cast the frame time to that period
        self.a = 0.8 / float(self.period) 

        # Update method        
        def ap_full(t):
            return pacemaker_AP_full((t % self.period) * self.a, **self.args)
        self.function = ap_full

        # Value for which self.function returns max value
        self.max_arg = self._get_max_arg()

    def _get_max_arg(self) -> int:
        """
            Find the time argument for update method that returns max
            charge value
        """
        args = list(map(self.function, list(range(self.period))))
        return np.argmax(args)

    def depolarize(self, cell: Cell) -> float:
        """
            Returns the max charge available for that function.
            Updates the state_timer of a call to the max_arg value
        """
        cell.state_timer = self.max_arg
        return self.function(cell.state_timer)

    def update(self, timer: int) -> float:
        """
            Returns the new charge of the cell
        """
        return self.function(timer)
       