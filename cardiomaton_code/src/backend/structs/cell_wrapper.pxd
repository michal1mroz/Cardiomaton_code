from src.backend.models.c_cell cimport CCell

cdef class CellWrapper:
    cdef CCell* cell_a
    cdef public list neighbors
    cdef public dict cell_data

    cpdef dict get_cell_dict(self)