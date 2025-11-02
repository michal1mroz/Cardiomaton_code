from src.backend.structs.c_cell cimport CCell
from src.models.cell import Cell
from src.backend.utils.draw_functions cimport DrawFunc
from src.backend.models.frame_recorder cimport FrameRecorder

cdef class Automaton:
    # C exclusive attributes
    cdef CCell** grid_a
    cdef CCell** grid_b
    cdef int frame_counter
    cdef int is_running
    cdef int n_nodes
    cdef double frame_time

    cdef FrameRecorder frame_recorder

    cdef unsigned char* img_buffer
    cdef int bytes_per_line 

    # Python helping attributes
    cdef public tuple size
    cdef public dict cell_data
    cdef public dict dict_mapping

    # Public python API
    cpdef void update_grid(self, object is_charged)
    cpdef tuple to_cell_data(self)

    cpdef float get_frame_time(self)
    cpdef void set_frame_time(self, double)
    cpdef tuple get_shape(self)
    cpdef dict get_cell_data(self, tuple)

    cpdef int get_buffer_size(self)
    cpdef int render_frame(self, int idx, object if_charged, object drop_newer)
    cpdef void set_frame_counter(self, int)

    # Private python compatible methods
    cpdef dict _create_data_map(self, dict)
    cpdef dict _cells_to_dict(self)

    # C exclusive methods
    cdef void _dealloc_grid(self, CCell**)    
    cdef void _generate_grid(self, CCell**, list)
    cdef void _update_grid_nogil(self, DrawFunc)
    cdef void _init_img(self)
    cdef void _clear_img(self)


