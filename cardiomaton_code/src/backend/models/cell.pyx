from __future__ import annotations
from typing import Tuple, Dict, TypedDict

import array
cimport cython
import time

from src.backend.models.cell_state import CellState as PyCellState, CellStateName, state_to_cenum, state_to_pyenum
from src.backend.models.cell_type import CellType as PyCellType, to_cenum, to_pyenum

from src.update_strategies.charge_approx.charge_update import ChargeUpdate

cimport src.backend.models.cell_state as cstate
cimport src.backend.models.cell_type as ctype

class CellDict(TypedDict):
    position: Tuple[int, int]
    state_value: int
    state_name: str 
    charge: float
    ccs_part: str 
    cell_type: str
    auto_polarization: bool

cdef class Cell:
    # Class to store information about specific cell.

    def __init__(self, position: Tuple[int, int], cell_type: PyCellType,
                 cell_data: Dict = None, init_state: PyCellState = None,
                 self_polarization: bool = None):
        
        self.pos_x = int(position[0])
        self.pos_y = int(position[1])

        self.cell_type_py = cell_type

        cfg = cell_type.config
        if cell_data is None:
            self.cell_data = cfg["cell_data"]
        else:
            self.cell_data = cell_data

        if self_polarization is None:
            self.self_polarization = bool(cfg.get("self_polarization", False))
        else:
            self.self_polarization = bool(self_polarization)

        if init_state is None:
            init_state = cstate.CellStateC.POLARIZATION

        self.state = state_to_cenum(init_state)

        self.state_timer = 0
        self.charge = 0.0
        self.neighbours = []    

        self.period = int(self.cell_data.get("range", 100))

        py_charges, py_charge_max = ChargeUpdate.get_func(self.cell_data)
        arr = array.array('d', py_charges)    
        self._charges_array = arr             
        self.charges_mv = arr                 
        self.charge_max = int(py_charge_max)

        self._dict_cache = {
            "position": (self.pos_x, self.pos_y),
            "state_value": self.state + 1,
            "state_name": CellStateName(self.state).capitalize(),
            "charge": float(self.charge),
            "ccs_part": self.cell_type_py.value,
            "cell_type": self.cell_type_py.name,
            "auto_polarization": self.self_polarization,
        }


    cdef void _reset_timer_nogil(self) nogil:
        self.state_timer = 0

    cpdef void reset_timer(self):
        self._reset_timer_nogil()

    cdef void _update_timer_nogil(self) nogil:
        self.state_timer = (self.state_timer + 1) % self.period

    cpdef void update_timer(self):
        self._update_timer_nogil()

    cdef double _update_charge_nogil(self) nogil:
        cdef int idx = self.state_timer
        return self.charges_mv[idx]

    cpdef double update_charge(self):
        return self._update_charge_nogil()

    cdef double _depolarize_nogil(self) nogil:
        self.state_timer = self.charge_max
        return self.charges_mv[self.charge_max]

    cpdef double depolarize(self):
        return self._depolarize_nogil()

    cpdef dict to_dict(self):
        """
        Method to serialize the cell data for rendering on the front end. Can be changed to dto if the need arises.

        Returns:
            Dict: dictionary that stores all the relevant fields of the cell
        """
        state_name = CellStateName(self.state).capitalize()
        d = self._dict_cache
        d["state_value"] = int(self.state) + 1
        d["state_name"] = state_name
        d["charge"] = float(self.charge)
        return d


    cpdef void update_data(self, dict data_dict):
        """
        Method to update state of cell from the CellDict. For now allows only
        for the depolarization of the cell.

        Args:
            data_dict (CellDict): Dict with new values for the cell
        """
        cdef int val = int(data_dict['state_value']) - 1
        self.state = <cstate.CellStateC> val
        if self.state == cstate.RAPID_DEPOLARIZATION:
            self.charge = float(self.cell_data.get('V_peak', 0.0))

    def add_neighbour(self, neighbour: Cell) -> None:
        """
        Add single neighbour to the cell
        
        Args:
            neighbour (Cell): cell to be added as a neighbour
        """
        self.neighbours.append(neighbour)
