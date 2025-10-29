from libc.stdio cimport printf
from libc.stdlib cimport malloc, free
from libc.stdint cimport uintptr_t

from src.backend.models.c_cell cimport CCell, create_c_cell, add_cell_charges, free_c_cell, allocate_neighbors, cell_to_dict
from src.backend.models.cell_state cimport CellStateC, state_to_cenum
from src.backend.models.cell_type cimport CellTypeC, type_to_cenum
from src.backend.utils.charge_update cimport update_charge

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict

from src.backend.models.cell import Cell, CellDict
from src.backend.models.cell_type import CellType
from src.backend.models.cell_state import CellState

@dataclass
class CellData:
    neighbors: list[Tuple[int, int]]
    cell_data: dict[str, float]

cdef class Automaton:

    def __init__(self, size: Tuple[int, int], cells: dict[Tuple[int, int], Cell], frame_time: float = 0.2):
        """
        Constructor. Assumes size is the size of the image on which the grid is projected. Uses the same values
        as the previous version, but stores as much data as possible in c containers.
        """
        self.size = size
        self.frame_time = <double> frame_time
        cell_list = list(cells.values())

        self.n_nodes = <int> len(cell_list)

        grid_size = len(cell_list) * sizeof(CCell*)
        self.grid_a = <CCell**> malloc(grid_size)
        
        cdef int i
        if self.grid_a == NULL:
            raise MemoryError("Failed to allocate CCell** array - grid_a")
        for i in range(len(cell_list)):
            self.grid_a[i] = NULL

        self.grid_b = <CCell**> malloc(grid_size)
        if self.grid_b == NULL:
            self._dealloc_grid(self.grid_a)
            raise MemoryError("Failed to allocate CCell** array - grid_b")
        for i in range(len(cell_list)):
            self.grid_b[i] = NULL

        self.is_running = 0
        self.frame_counter = 0

        self.dict_mapping = {
            pos: CellDict(position = pos,
                    state_value= cell.state.value,
                    state_name = cell.state.name.capitalize(),
                    charge = cell.charge,
                    ccs_part=cell.cell_type.value,
                    cell_type = cell.cell_type.name,
                    auto_polarization=cell.self_polarization)
            for pos, cell in cells.items()
        }

        self.cell_data = self._create_data_map(cells)

        self._generate_grid(self.grid_a, cell_list)
        self._generate_grid(self.grid_b, cell_list)

    def __dealloc__(self):
        """
        Destructor to free the resources for grids
        """
        if self.grid_a is not NULL:
            self._dealloc_grid(self.grid_a)
            self.grid_a = NULL
        if self.grid_b is not NULL:
            self._dealloc_grid(self.grid_b)
            self.grid_b = NULL

    cdef void _dealloc_grid(self, CCell** grid):
        """
        Helper function to deallocate the data in one grid.
        Can possibly fail if the grid has non NULL not allocated fields
        """
        cdef int i
        if grid != NULL:
            for i in range(self.n_nodes):
                if grid[i] != NULL:
                    free_c_cell(grid[i])
                    grid[i] = NULL
            free(grid) 

    cpdef dict _create_data_map(self, dict cells):
        """
        Helper method to provide the python object with the data mapping.
        Stores the information about the cell_data and neighbor positions for each cell
        """
        return {
            (pos): CellData(
                neighbors=[(nei.pos_x, nei.pos_y) for nei in cell.neighbors],
                cell_data=cell.cell_data
                ) 
            for pos, cell in cells.items()
        }

    cdef void _generate_grid(self, CCell** grid, list py_cells): 
        """
        Automaton grid creator. Expects the caller to allocate the required memory for the CCell** grid.
        list py_cells should contain the python list of python Cell class objects.
        For each creates CCell object and maps the data from py_cells onto it.
        """
        
        cdef dict pos_to_ccell = {}
        cdef int n = len(py_cells)
        cdef int i, j 

        for i in range(n):
            py_cell = py_cells[i]
            grid[i] = create_c_cell(<int>py_cell.pos_x, <int>py_cell.pos_y)
            if grid[i] == NULL:
                raise MemoryError()
            pos_to_ccell[(py_cell.pos_x, py_cell.pos_y)] = <uintptr_t> grid[i]

            grid[i].c_state = state_to_cenum(py_cell.state)
            grid[i].c_type = type_to_cenum(py_cell.cell_type)
            grid[i].self_polarization = 1 if py_cell.self_polarization else 0

            grid[i].period = <int> py_cell.n_range
            grid[i].timer = <int> py_cell.timer
            grid[i].charge_max = <int> py_cell.max_charge
            
            # If the retrieval from cell_data failes the data is not correct
            # and so probably it's not possible to construct the automaton.
            # The caller of the automatons constructor should handle any exception,
            # automaton will only free its memory
            grid[i].V_peak = <double> py_cell.cell_data.get("V_peak")
            grid[i].V_rest = <double> py_cell.cell_data.get("V_rest")
            grid[i].V_thresh = <double> py_cell.cell_data.get("V_thresh", 0) # Default since some cells don't have this value
            grid[i].ref_threshold = <double> py_cell.ref_threshold
            grid[i].charge = 0
            
            if py_cell.charges is not None:
                add_cell_charges(grid[i], np.asarray(py_cell.charges, dtype=np.float64))
            else:
                raise RuntimeError("Attempted construction of a cell with no charge function")

        cdef CCell* this_c

        for i in range(n):
            py_cell = py_cells[i]
            this_c = grid[i]

            if py_cell.neighbors is not None:
                allocate_neighbors(this_c, len(py_cell.neighbors))
                for j in range(this_c.n_neighbors):
                    neigh = py_cell.neighbors[j]
                    try:
                        this_c.neighbors[j] = <CCell*> (<uintptr_t> pos_to_ccell[(neigh.pos_x, neigh.pos_y)])
                    except KeyError:
                        this_c.neighbors[j] = NULL
            else:
                this_c.neighbors = NULL
                this_c.n_neighbors = 0

    cdef void _update_grid_nogil(self) nogil:
        """
        %ToDo
        For now this function already has a great increase in time efficiency.
        Requires that all the underlying functions are nogil compatible.
        """
        ...

    cpdef void update_grid(self):
        """
        Simple update method for the python API. The logic should be moved to the nogil pure C implementation.
        """
        cdef CCell* cell_a
        cdef CCell* cell_b
        cdef int i
        self.frame_counter += 1
        for i in range(self.n_nodes):
            cell_a = self.grid_a[i]
            cell_b = self.grid_b[i]
            update_charge(cell_a, cell_b)
        cdef CCell** tmp = self.grid_a
        self.grid_a = self.grid_b
        self.grid_b = tmp

    cpdef dict _cells_to_dict(self):
        """
        Helper method to map the cell objects to the cached dictionary. Performed in-place
        """
        cdef int i
        cdef CCell* cell
        for i in range(self.n_nodes):
            cell = self.grid_a[i]
            self.dict_mapping[(cell.pos_x, cell.pos_y)] = cell_to_dict(cell, self.dict_mapping[(cell.pos_x, cell.pos_y)])
    
    cpdef tuple to_cell_data(self):
        """
        Getter for the serialized data. Returns the Tuple with the current frame and the serialized cells.
        """
        self._cells_to_dict()
        return tuple((int(self.frame_counter), self.dict_mapping))

    cpdef void recreate_from_dict(self, tuple vals):
        """
        Code here works, but the serialization relies on resuage of a single dict.
        In result frame recorder needs a deepcopy to save the data which
        is prohibitively slow
        """
        # Remove the old grid objects
        self._dealloc_grid(self.grid_a)
        self._dealloc_grid(self.grid_b)
        self.grid_a = NULL
        self.grid_b = NULL

        # Generate cell mapping on python objects:
        cells = {}
        frame, serialized_cells = vals
        for pos, cell_dict in serialized_cells.items():
            data_dict = self.cell_data[cell_dict["position"]].cell_data
            py_cell = Cell(position = cell_dict["position"], cell_type=CellType[cell_dict["cell_type"]],
                            init_state = CellState[cell_dict["state_name"].upper()], 
                            self_polarization=cell_dict["auto_polarization"])
            py_cell.charge = cell_dict["charge"]
            cells.update({pos: py_cell})

        for pos, cell_dict in self.cell_data.items():
            for nei in cell_dict.neighbors:
                cells[pos].add_neighbor(cells[nei])

        cell_list = list(cells.values())
        self.n_nodes = <int> len(cell_list)

        grid_size = len(cell_list) * sizeof(CCell*)
        self.grid_a = <CCell**> malloc(grid_size)
        if self.grid_a is NULL:
            raise MemoryError()
        self.grid_b = <CCell**> malloc(grid_size)
        if self.grid_b is NULL:
            free(self.grid_a)
            raise MemoryError()

        self.frame_counter = <int> frame
        self._generate_grid(self.grid_a, cell_list)
        self._generate_grid(self.grid_b, cell_list)

    """
    Set of getters and setters for the python API
    """ 
    cpdef float get_frame_time(self):
        return float(self.frame_time)
    
    cpdef void set_frame_time(self, double frame_time):
        self.frame_time = <double> frame_time

    cpdef tuple get_shape(self):
        return self.size
