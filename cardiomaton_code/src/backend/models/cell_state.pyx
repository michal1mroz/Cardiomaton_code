from enum import IntEnum
cimport cell_state

class CellState(IntEnum):
    """
    Enum class to store the state of the cell
    """

    POLARIZATION = 0
    SLOW_DEPOLARIZATION = 1
    RAPID_DEPOLARIZATION = 2
    REPOLARIZATION_ABSOLUTE_REFRACTION = 3
    REPOLARIZATION_RELATIVE_REFRACTION = 4
    # ABS_REFRACTION = 2
    # REFRACTION = 3
    NECROSIS = 5
    # HYPERPOLARIZATION - to determine if we will need this

cdef dict _CELLSTATE_NAMES = {
    cell_state.CellStateC.POLARIZATION: "POLARIZATION",
    cell_state.CellStateC.SLOW_DEPOLARIZATION: "SLOW_DEPOLARIZATION",
    cell_state.CellStateC.RAPID_DEPOLARIZATION: "RAPID_DEPOLARIZATION",
    cell_state.CellStateC.REPOLARIZATION_ABSOLUTE_REFRACTION: "REPOLARIZATION_ABSOLUTE_REFRACTION",
    cell_state.CellStateC.REPOLARIZATION_RELATIVE_REFRACTION: "REPOLARIZATION_RELATIVE_REFRACTION",
    cell_state.CellStateC.NECROSIS: "NECROSIS",
}

cpdef str CellStateName(cell_state.CellStateC val):
    """
    Return the string name of the enum value.
    """
    return _CELLSTATE_NAMES.get(val, f"<UNKNOWN:{val}>")

cpdef cell_state.CellStateC state_to_cenum(object py_val):
    return py_val

cpdef object state_to_pyenum(cell_state.CellStateC c_val):
    return CellState(int(c_val))

