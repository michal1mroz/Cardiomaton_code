from enum import Enum

class CellState(Enum):
    """
    Enum class to store the state of the cell.
    """
    POLARIZATION = 0
    SLOW_DEPOLARIZATION = 1
    RAPID_DEPOLARIZATION = 2
    REPOLARIZATION_ABS_REFRACTION = 3
    REPOLARIZATION_REL_REFRACTION = 4
    # ABS_REFRACTION = 2
    # REFRACTION = 3
    DEAD = 5
    # HYPERPOLARIZATION - to determine if we will need this
