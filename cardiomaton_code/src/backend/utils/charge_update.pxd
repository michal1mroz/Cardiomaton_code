from src.backend.enums.cell_state cimport CellStateC
from src.backend.structs.c_cell cimport CCell

cdef void update_charge(CCell*, CCell*)
