from src.utils.image_loader import *
from src.backend.models.cell_state import CellState

from src.backend.models.cell import Cell
from src.backend.models.automaton import Automaton
from src.backend.models.cell_type import CellType, ConfigLoader
from src.backend.models.cell_state import CellState

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print(CellState.POLARIZATION.value)
    ConfigLoader.loadConfig()
    cell = Cell((123,321), CellType.AV_NODE, init_state = CellState.REPOLARIZATION_RELATIVE_REFRACTION)
    auto = Automaton(cell)
    auto.print_state()
    auto.update_cell()