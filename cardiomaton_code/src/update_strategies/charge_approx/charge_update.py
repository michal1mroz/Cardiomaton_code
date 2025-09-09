from typing import Dict, Tuple
import numpy as np
from functools import lru_cache

from src.update_strategies.charge_approx.ms_final import pacemaker_AP_full

"""
    Wrapper on pacemaker_AP_full working as a function factor.
    Returns mapping of time in frames to charge values for specified arguments
"""

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
    def _get_func(cell_data: Dict) -> Tuple[Dict[int, float], int]:
        """
            Helper method for get_func() that performs most calculations. Operates on the frozenset
            to allow caching of the dictionary.

            Args:
                cell_data: Dict - dictionary with the arguments for pacemaker_AP_full

            Returns:
                Dict[int, float] - map of time in frames (modulo range) -> charge values
                int - time % range for the greatest argument
        """
        cell_data = dict(cell_data)
        period = cell_data["range"]
        a = cell_data['period'] / period
        func = lambda t: pacemaker_AP_full((t % period) * a, **cell_data)
        args = list(range(int(period)))
        m = {t: func(t) for t in args}
        return m, ChargeUpdate._get_max_arg(func, period)
    
    @staticmethod
    def get_func(cell_data: Dict) -> Tuple[Dict[int, float], int]:
        """
            Main method, accepts the dictionary cell_data from the json file and
            returns mapping of the generated function over the specified range.

            Args:
                cell_data: Dict - dictionary with the arguments for pacemaker_AP_full
            
            Returns:
                Dict[int, float] - map of time in frames (modulo range) -> charge values
                int - time % range for the greatest argument
        """
        
        key = frozenset(cell_data.items())
        return ChargeUpdate._get_func(key)
