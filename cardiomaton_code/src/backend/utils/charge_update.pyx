from libc.stdio cimport printf

from src.backend.models.cell_state cimport CellStateC
from src.backend.models.c_cell cimport CCell

cdef void update_charge(CCell* cell_a, CCell* cell_b):
    return 