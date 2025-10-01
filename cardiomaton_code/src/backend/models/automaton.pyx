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

@dataclass
class CellData:
    neighbors: list[Tuple[int, int]]
    cell_data: dict[str, float]

cdef class Automaton:

    def __init__(self, size: Tuple[int, int], cells: dict[Tuple[int, int], Cell], frame_time: float = 0.2):
        self.size = size
        cell_list = list(cells.values())

        self.n_nodes = <int> len(cell_list)

        grid_size = len(cell_list) * sizeof(CCell*)
        self.grid_a = <CCell**> malloc(grid_size)
        if self.grid_a == NULL:
            raise MemoryError("Failed to allocate CCell** array - grid_a")
        self.grid_b = <CCell**> malloc(grid_size)
        if self.grid_b == NULL:
            self._dealloc_grid(self.grid_a)
            raise MemoryError("Failed to allocate CCell** array - grid_b")

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
        print("grids done")

        self.cell_data = self._create_data_map(cells)

        self._generate_grid(self.grid_a, cell_list)
        self._generate_grid(self.grid_b, cell_list)
        print("Constructor done")

        #self.cell = create_c_cell(py_cell.pos_x, py_cell.pos_y)

        #add_cell_charges(self.cell, py_cell.charges_mv)
        #self.cell.c_state = state_to_cenum(py_cell.state)

    def __dealloc__(self):
        print("dealloc")
        if self.grid_a is not NULL:
            self._dealloc_grid(self.grid_a)
            self.grid_a = NULL
        print("grid_a done")
        if self.grid_b is not NULL:
            self._dealloc_grid(self.grid_b)
            self.grid_b = NULL
        print("grid_b done")

    cdef void _dealloc_grid(self, CCell** grid):
        if grid != NULL:
            # cdef int i
            for i in range(self.n_nodes):
                if grid[i] != NULL:
                    free_c_cell(grid[i])
                    grid[i] = NULL
            free(grid) 

    cpdef dict _create_data_map(self, dict cells):
        return {
            (pos): CellData(
                neighbors=[(nei.pos_x, nei.pos_y) for nei in cell.neighbors],
                cell_data=cell.cell_data
                ) 
            for pos, cell in cells.items()
        }

    cdef void _generate_grid(self, CCell** grid, list py_cells): 
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

            grid[i].charge = <double> py_cell.charge
            grid[i].period = <int> py_cell.period
            grid[i].timer = <int> py_cell.timer
            grid[i].charge_max = <int> py_cell.max_charge

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
        ...

    cpdef void update_cell(self):
        cdef CCell* cell_a
        cdef CCell* cell_b
        cdef int i
        for i in range(self.n_nodes):
            cell_a = self.grid_a[i]
            cell_b = self.grid_b[i]
            update_charge(cell_a, cell_b)
        
        cdef CCell** tmp = self.grid_a
        self.grid_a = self.grid_b
        self.grid_b = tmp

    cpdef dict _cells_to_dict(self):
        cdef int i
        cdef CCell* cell
        for i in range(self.n_nodes):
            cell = self.grid_a[i]
            self.dict_mapping[(cell.pos_x, cell.pos_y)] = cell_to_dict(cell, self.dict_mapping[(cell.pos_x, cell.pos_y)])
    
    cpdef tuple to_cell_data(self):
        self._cells_to_dict()
        return tuple((int(self.frame_counter), self.dict_mapping))

    cpdef void recreate_from_dict(self, tuple vals):
        ...

