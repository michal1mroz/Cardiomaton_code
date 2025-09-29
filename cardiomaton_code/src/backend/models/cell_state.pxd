cdef enum CellStateC:
    POLARIZATION = 0
    SLOW_DEPOLARIZATION = 1
    RAPID_DEPOLARIZATION = 2
    REPOLARIZATION_ABSOLUTE_REFRACTION = 3
    REPOLARIZATION_RELATIVE_REFRACTION = 4
    NECROSIS = 5

cpdef CellStateC state_to_cenum(object)
cpdef object state_to_pyenum(CellStateC)