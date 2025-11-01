from src.backend.enums.cell_state cimport CellStateC
from src.backend.structs.c_cell cimport CCell

"""
Function pointer type. Used to select the draw function without branching in the loop
"""
ctypedef void (*DrawFunc)(unsigned char*, int, CCell*)

cdef void draw_from_state(unsigned char*, int, CCell*)
cdef void draw_from_charge(unsigned char*, int, CCell*)