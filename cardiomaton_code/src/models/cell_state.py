from enum import Enum

class CellState(Enum):
    """
    Enum class to store the state of the cell.
    """
    WAITING = 0
    POLARIZATION = 1
    DEPOLARIZATION = 2
    ABS_REFRACTION = 3
    REFRACTION = 4
    DEAD = 5
