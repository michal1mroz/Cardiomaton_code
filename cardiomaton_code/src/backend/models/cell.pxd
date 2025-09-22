cimport src.backend.models.cell_state as cstate 
cimport src.backend.models.cell_type as ctype 

cdef class Cell:
    cdef public int pos_x
    cdef public int pos_y

    cdef public cstate.CellStateC state 
    cdef public bint self_polarization
    cdef public int state_timer

    cdef public int period
    cdef public object _charges_array
    cdef public double[:] charges_mv

    cdef public int charge_max
    cdef public double charge

    cdef public object cell_type_py
    cdef public object cell_data
    cdef public object neighbours
    cdef public object _dict_cache

    cpdef dict to_dict(self)
    cpdef void update_data(self, dict data_dict)
    cdef double _update_charge_nogil(self)
    cpdef double update_charge(self)
    cdef double _depolarize_nogil(self) 
    cpdef double depolarize(self)
    cdef void _reset_timer_nogil(self)
    cpdef void reset_timer(self)
    cdef void _update_timer_nogil(self) 
    cpdef void update_timer(self)