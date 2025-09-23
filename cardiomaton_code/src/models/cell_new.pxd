from src.models.cell_state import CellState

cdef class Cell:
    cdef public object state
    cdef public bint self_polarization
    cdef public object cell_type
    cdef public int self_polar_timer
    cdef public int state_timer
    cdef public tuple position
    cdef public list neighbours
    cdef public double charge
    cdef public dict cell_data

    cdef public int self_polar_threshold

    cpdef reset_timer(self)
    cpdef update_timer(self)
    cpdef reset_self_polar_timer(self)
    cpdef update_self_polar_timer(self)
    cpdef add_neighbour(self, Cell neighbour)
    cpdef double to_int(self)
    cpdef tuple to_tuple(self)
    cpdef update_data(self, dict data_dict)
    cpdef get_color(self)
    cpdef to_dict(self)
