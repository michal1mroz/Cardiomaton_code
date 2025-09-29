from src.backend.models.c_cell cimport CCell, create_c_cell, add_charges, free_c_cell
from src.models.cell import Cell

# def __init__(self, data_array: np.ndarray, cells: Dict[Tuple[int, int], Cell], frame_time: float = 0.2):
#        """
#        Automaton constructor.
#
#        frame_time will probably be changed depending on the method used to control the speed.
#        grid_b is a copy of the array created to avoid the overhead of memory allocation and copying on each update.
#
#        Args:
#            cells Dict[Tuple[int, int], Cell]: mapping of the cell to a position
#            frame_time (float, optional): Frame time in seconds. Defaults to 0.2s.
#        """
#        self.shape = data_array.shape
#        self.draw_array = np.zeros(self.shape)
#        self.cells = cells
#        self.grid_a = self._create_automaton()
#        self.grid_b = self._copy_grid(self.grid_a)
#        self.frame_time = frame_time
#        self.is_running = False
#        self.frame_counter = 0
#        self.cell_data = self._create_data_map()
#        self.neighbour_map = self._create_neighbour_map()
#        self.update_method = UpdateChargeMSCopy()
#        self.fig = self.ax = self.img = None

cdef class Automaton:
    cdef CCell* cell
    cdef public object py_cell
    cpdef void print_state(self)
    cpdef void update_cell(self)