from libc.stdio cimport printf

from src.backend.models.cell_state cimport CellStateC
from src.backend.models.c_cell cimport CCell

cdef void update_charge(CCell* cell_a, CCell* cell_b):
    cdef state = cell_a.c_state
    if state == CellStateC.NECROSIS:
        print("NECROSIS")
    elif state == CellStateC.REPOLARIZATION_ABSOLUTE_REFRACTION:
        print("REPOLARIZATION_ABSOLUTE_REFRACTION")
    elif state == CellStateC.REPOLARIZATION_RELATIVE_REFRACTION:
        print("REPOLARIZATION_RELATIVE_REFRACTION")
    elif state == CellStateC.POLARIZATION:
        print("POLARIZATION")
    elif state == CellStateC.SLOW_DEPOLARIZATION:
        print("SLOW_DEPOLARIZATION")
    elif state == CellStateC.RAPID_DEPOLARIZATION:
        print("RAPID_DEPOLARIZATION")


