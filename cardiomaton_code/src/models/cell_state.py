from enum import Enum

class CellState(Enum):
    """
    Enum class to store the state of the cell.
    """
    POLARIZATION = 0
    DEPOLARIZATION = 1
    ABS_REFRACTION = 2
    REFRACTION = 3
    DEAD = 4
