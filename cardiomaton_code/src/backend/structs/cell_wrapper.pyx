from src.backend.structs.c_cell cimport CCell
from src.backend.enums.cell_state cimport CellStateC, cell_state_name
from src.backend.enums.cell_type cimport CellTypeC, type_to_pyenum
from libc.stdint cimport uintptr_t

from src.backend.models.cell import CellDict

cdef class CellWrapper:
    def __cinit__(self, uintptr_t cell_a, list neighbors, dict cell_data):
        self.cell_a = <CCell*> cell_a
        self.neighbors = neighbors
        self.cell_data = cell_data

    cpdef dict get_cell_dict(self):
        py_type = type_to_pyenum(self.cell_a.c_type)
        return CellDict(
            position=(self.cell_a.pos_x, self.cell_a.pos_y),
            state_name = cell_state_name(self.cell_a.c_state),
            state_value = self.cell_a.c_state + 1,
            charge = float(self.cell_a.charge),
            ccs_part = py_type.value,
            cell_type = py_type.name,
            auto_polarization = False if self.cell_a.self_polarization == 0 else True
        )

    cpdef uintptr_t get_cell(self):
        return <uintptr_t>self.cell_a