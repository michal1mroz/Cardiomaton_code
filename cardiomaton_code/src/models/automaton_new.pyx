from src.models.cell_state import CellState
from src.models.cell_type import CellType
from src.update_strategies.update_charge_ms import UpdateChargeMS
from src.models.cell_new cimport Cell


import numpy as np
cimport numpy as cnp
import os
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from typing import Dict, List, Tuple

cdef class Automaton:
    cdef public tuple shape
    cdef public object draw_array
    cdef public dict cells
    cdef public list grid_a
    cdef public list grid_b
    cdef public float frame_time
    cdef public bint is_running
    cdef public int frame_counter
    cdef public dict neighbour_map
    cdef public object update_method
    cdef public int num_workers
    cdef public object executor

    def __init__(self, object data_array, dict cells, float frame_time=0.2):
        self.shape = data_array.shape
        rows, cols = self.shape[:2]  # define rows and cols for array creation
        self.draw_array = np.zeros((rows, cols), dtype=object)  # object array for Cells
        self.cells = cells
        self.grid_a = self._create_automaton()
        self.grid_b = self._copy_grid(self.grid_a)
        self.frame_time = frame_time
        self.is_running = False
        self.frame_counter = 0
        self.neighbour_map = self._create_neighbour_map()
        self.update_method = UpdateChargeMS()
        self.num_workers = os.cpu_count() or 4
        self.executor = ThreadPoolExecutor(max_workers=self.num_workers)

    cpdef dict _create_neighbour_map(self):
        cdef dict mapping = {}
        cdef Cell c
        # cdef object c
        for c in self.grid_a:
            mapping[c.position] = tuple([nei.position for nei in c.neighbours])
        return mapping

    cpdef list _create_automaton(self):
        return [v for v in self.cells.values()]

    cpdef list _copy_grid(self, list cell_list):
        cdef list arr = []
        cdef dict help_dict = {}
        cdef int i
        cdef Cell cell, new_cell, nei
        # cdef object cell, new_cell, nei
        for cell in cell_list:
            new_cell = Cell(
                position=cell.position,
                cell_data=cell.cell_data,
                init_state=cell.state,
                cell_type=cell.cell_type,
                self_polarization=cell.self_polarization,
                self_polarization_timer=cell.self_polar_timer
            )
            help_dict[cell.position] = new_cell
            arr.append(new_cell)

        for i, cell in enumerate(cell_list):
            for nei in cell.neighbours:
                arr[i].add_neighbour(help_dict[nei.position])
        return arr

    def _create_automaton_grid(self, object binary_array):
        cdef dict value_to_state = {0: CellState.DEAD, 1: CellState.POLARIZATION}
        cdef int i, j
        rows, cols = binary_array.shape[:2]
        result = np.empty((rows, cols), dtype=object)
        for i in range(rows):
            for j in range(cols):
                result[i, j] = Cell(value_to_state[binary_array[i, j]])
        return result


    cpdef update_grid(self):
        cdef int ind
        # cdef Cell cell
        cdef object cell
        self.frame_counter += 1
        for ind, cell in enumerate(self.grid_a):
            new_charge, new_state = self.update_method.update(cell)
            self.grid_b[ind].state = new_state
            self.grid_b[ind].state_timer = cell.state_timer
            self.grid_b[ind].charge = new_charge
        self.grid_a, self.grid_b = self.grid_b, self.grid_a

    cpdef _to_numpy(self):
        cdef Cell cell
        # cdef object cell
        for cell in self.grid_a:
            self.draw_array[cell.position] = cell.to_int()
        return self.draw_array

    cpdef tuple to_cell_data(self):
        cdef Cell cell
        # cdef object cell
        return self.frame_counter, {cell.position: cell.to_dict() for cell in self.grid_a}

    cpdef recreate_from_dict(self, tuple data_tuple):
        cdef int frame = data_tuple[0]
        cdef dict data = data_tuple[1]
        cdef dict cells_a = {}
        cdef dict cells_b = {}
        cdef tuple pos
        cdef dict cell_dict
        cdef Cell cell_a, cell_b
        # cdef object cell_a, cell_b
        cdef list nei
        for pos, cell_dict in data.items():
            cell_a = CellType.create(
                position=cell_dict["position"],
                cell_type=CellType[cell_dict["cell_type"]],
                state=CellState[cell_dict["state_name"].upper()]
            )
            cell_b = CellType.create(
                position=cell_dict["position"],
                cell_type=CellType[cell_dict["cell_type"]],
                state=CellState[cell_dict["state_name"].upper()]
            )
            cell_a.charge, cell_a.self_polarization = cell_dict["charge"], cell_dict["auto_polarization"]
            cell_b.charge, cell_b.self_polarization = cell_dict["charge"], cell_dict["auto_polarization"]
            cells_a[pos] = cell_a
            cells_b[pos] = cell_b

        for pos, nei in self.neighbour_map.items():
            cell_a, cell_b = cells_a[pos], cells_b[pos]
            for n in nei:
                cell_a.add_neighbour(cells_a[n])
                cell_b.add_neighbour(cells_b[n])

        self.cells = cells_a
        self.grid_a = [v for v in cells_a.values()]
        self.grid_b = [v for v in cells_b.values()]
        self.frame_counter = frame

    cpdef update_cell_from_dict(self, dict data_dict):
        cdef int i
        cdef Cell cell
        # cdef object cell
        for i, cell in enumerate(self.grid_a):
            if cell.position == data_dict['position']:
                cell.update_data(data_dict)
                self.grid_b[i].update_data(data_dict)
                return
