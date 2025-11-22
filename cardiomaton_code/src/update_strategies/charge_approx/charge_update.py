from typing import Dict, Tuple, List
import numpy as np
from functools import lru_cache

from src.update_strategies.charge_approx.ms_final import pacemaker_AP_full
from src.update_strategies.charge_approx.pacemakers import pacemaker_AP 
from src.update_strategies.charge_approx.atrial import atrial_AP
from src.update_strategies.charge_approx.purkinje import purkinje_AP

"""
    Wrapper on pacemaker_AP_full working as a function factor.
    Returns mapping of time in frames to charge values for specified arguments
"""

# Constant used to calculate the threshold between absolute and relative refraction.
# This can be changed to more elaborate method
REF_CONSTANT = 1./3

# To add new function just log it here and make sure the arguments follow the
# convention in `resources/data/cell_data.json`
CHARGE_FUNCTIONS = {
    "PACEMAKER": pacemaker_AP, 
    "ATRIAL": atrial_AP,
    "PURKINJE": purkinje_AP,
}

class ChargeUpdate():
    @staticmethod
    def _get_max_arg(func, period: int) -> int:
        """
            Find the time argument for update method that returns max
            charge value

            Args:
                func - function accepting time as int and returning 
                    charge value as an int

            Returns:
                int - greatest value from the func
            """
        args = list(map(func, list(range(int(period)))))
        return np.argmax(args)

    @lru_cache(maxsize=128)
    @staticmethod    
    def _get_func(cell_data: Dict, period: float, n_range: int, fun) -> Tuple[List[float], int, float]:
        """
            Helper method for get_func() that performs most calculations. Operates on the frozenset
            to allow caching of the dictionary.

            Args:
                cell_data: Dict - dictionary with the cell arguments

            Returns:
                Dict[int, float] - map of time in frames (modulo range) -> charge values
                int - time % range for the greatest argument
        """
        # period = cell_data["range"]
        # a = cell_data['period'] / period
        # func = lambda t: pacemaker_AP_full((t % period) * a, **cell_data)
        # args = list(range(int(period)))
        # m = [func(t) for t in args]
        # return m, ChargeUpdate._get_max_arg(func, period)
        cell_data = dict(cell_data)
        a = period / n_range
        func = lambda t: fun((t % n_range) * a, **cell_data)
        args = list(range(int(n_range)))
        m = [func(t) for t in args]
        charge_max = ChargeUpdate._get_max_arg(func, n_range)
        max_val = m[charge_max]
        min_val = np.min(m)

        return m, charge_max, (min_val + (max_val - min_val) * REF_CONSTANT)
    
    @staticmethod
    def get_func(config: Dict) -> Tuple[List[float], int, float]:
        """
            Main method, accepts the dictionary cell_data from the json file and
            returns mapping of the generated function over the specified range.

            Args:
                cell_data: Dict - dictionary with the arguments for pacemaker_AP_full
            
            Returns:
                Dict[int, float] - map of time in frames (modulo range) -> charge values
                int - time % range for the greatest argument
        """
        fun = CHARGE_FUNCTIONS.get(config["charge_function"], pacemaker_AP_full) 
        key = frozenset(config["cell_data"].items())
        res = ChargeUpdate._get_func(key, config["period"], config["range"], fun)
        return res