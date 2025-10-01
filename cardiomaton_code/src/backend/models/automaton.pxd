from src.backend.models.c_cell cimport CCell, create_c_cell, add_cell_charges, free_c_cell, allocate_neighbors
from src.models.cell import Cell

cdef class Automaton:
    cdef CCell** grid_a
    cdef CCell** grid_b
    cdef int frame_counter
    cdef int is_running
    cdef int n_nodes
    
    cdef public tuple size
    cdef public dict cell_data
    cdef public dict dict_mapping

    cpdef void recreate_from_dict(self, tuple)
    cpdef void update_cell(self)
    cpdef tuple to_cell_data(self)

    cpdef dict _create_data_map(self, dict)
    cpdef dict _cells_to_dict(self)

    cdef void _dealloc_grid(self, CCell**)    
    cdef void _generate_grid(self, CCell**, list)
    cdef void _update_grid_nogil(self) nogil



