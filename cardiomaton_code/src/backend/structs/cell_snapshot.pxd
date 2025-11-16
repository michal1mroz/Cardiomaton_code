from src.backend.enums.cell_state cimport CellStateC

"""
Struct designed to store the snapshot of the dynamically
changing cell data.
"""
cdef struct CellSnapshot:
    int pos_x
    int pos_y
    CellStateC c_state
    float charge
    int timer
