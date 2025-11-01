from src.backend.models.cell_state cimport CellStateC
from src.backend.models.c_cell cimport CCell

cdef void draw_from_state(unsigned char*, int, CCell*)
cdef void draw_from_charge(unsigned char*, int, CCell*)