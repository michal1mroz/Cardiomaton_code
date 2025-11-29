from src.backend.structs.c_cell cimport CCell
from libc.stdint cimport uintptr_t

cdef class CellWrapper:
    cdef CCell* cell_a
    cdef public list neighbors
    cdef public dict cell_data

    cpdef dict get_cell_dict(self)
    cpdef uintptr_t get_cell(self)