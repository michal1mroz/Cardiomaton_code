from src.utils.image_loader import *
from src.backend.models.cell_state import CellState

from src.backend.models.cell import Cell
from src.backend.models.automaton import Automaton
from src.backend.models.cell_type import CellType, ConfigLoader, type_to_cenum, type_to_pyenum
from src.backend.models.cell_state import CellState

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(CellState.POLARIZATION.value)
    ConfigLoader.loadConfig()
    # cell = Cell((123,321), CellType.SA_NODE)
    # print(cell)
    # print(cell.charges)
    py_type = CellType.BACHMANN
    print(py_type.name, py_type.value)
    c_type = type_to_cenum(py_type)
    print(c_type)
    py_rev = type_to_pyenum(c_type)
    print(py_rev, py_rev.name, py_rev.value)
