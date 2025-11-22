from libc.stdio cimport printf
from libc.stdlib cimport malloc, realloc, free
from libc.string cimport memset, memcpy
from libc.stdint cimport uintptr_t


from src.backend.structs.c_cell cimport CCell, create_c_cell, add_cell_charges, free_c_cell, allocate_neighbors, cell_to_dict, create_mimic_cell, recreate_cell_from_mimic
from src.backend.enums.cell_state cimport CellStateC,state_to_cenum
from src.backend.enums.cell_type cimport type_to_cenum
from src.backend.enums.cell_type cimport CellTypeC
from src.backend.utils.charge_update cimport update_charge
from src.backend.utils.draw_functions cimport draw_from_state, draw_from_charge, DrawFunc
from src.backend.structs.cell_wrapper cimport CellWrapper
from src.backend.structs.cell_snapshot cimport CellSnapshot
from src.backend.models.frame_recorder cimport FrameRecorder


import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict

from src.backend.models.cell import Cell, CellDict
from src.backend.enums.cell_type import CellType
from src.backend.enums.cell_state import CellState
from src.update_strategies.charge_approx.charge_update import ChargeUpdate


@dataclass
class CellData:
    neighbors: list[Tuple[int, int]]
    cell_data: dict[str, float]

cdef class Automaton:

    def __init__(self, size: Tuple[int, int], cells: dict[Tuple[int, int], Cell], img_ptr,
            int img_bytes, frame_time: float = 0.2):
        """
        Constructor. Assumes size is the size of the image on which the grid is projected. Uses the same values
        as the previous version, but stores as much data as possible in c containers.
        """
        cdef int i
        cdef uintptr_t addr_val

        self.size = size
        self.frame_time = <double> frame_time
        cell_list = list(cells.values())

        self.n_nodes = <int> len(cell_list)

        grid_size = len(cell_list) * sizeof(CCell*)
        self.grid_a = <CCell**> malloc(grid_size)
        
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

        self.cell_data = dict()
        self._generate_grid(self.grid_a, cell_list)
        self._generate_grid(self.grid_b, cell_list)

        self.frame_recorder = FrameRecorder(len(cells), 200)

        # Img setup
        addr_val = <uintptr_t> img_ptr
        self.img_buffer = <unsigned char*> addr_val
        self.bytes_per_line = <int> img_bytes

        self._init_img()

        # Modification buffer

        cdef CCell ***modification_snapshot_grids
        self.modification_snapshot_grids = <CCell***> malloc(8 * sizeof(CCell**))

        self.buf_size = 0


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

            self.cell_data[(py_cell.pos_x, py_cell.pos_y)] = CellWrapper(<uintptr_t> grid[i],
                                        [(nei.pos_x, nei.pos_y) for nei in py_cell.neighbors],
                                        py_cell.config)
            
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


    cdef void _init_img(self):
        cdef CCell* cell
        cdef int i
        self._clear_img()
        for i in range(self.n_nodes):
            cell = self.grid_a[i]
            # draw_from_state(self.img_buffer, self.bytes_per_line, cell)
            draw_from_charge(self.img_buffer, self.bytes_per_line, cell)
    
    cdef void _clear_img(self):
        cdef size_t total_bytes = self.bytes_per_line * <int>self.size[0]
        memset(self.img_buffer, 0, total_bytes)

    cdef void _update_grid_nogil(self, DrawFunc draw_function):
        """
        %ToDo
        For now this function already has a great increase in time efficiency.
        Requires that all the underlying functions are nogil compatible.
        """
        cdef CCell** tmp = self.grid_a
        cdef CCell* cell_a
        cdef CCell* cell_b
        cdef int i
        cdef CellSnapshot* snapshot = self.frame_recorder.get_next_buffer()
        self.frame_counter += 1

        for i in range(self.n_nodes):
            cell_a = self.grid_a[i]
            cell_b = self.grid_b[i]
            update_charge(cell_a, cell_b)
            draw_function(self.img_buffer, self.bytes_per_line, cell_b)

            # Inline write to the buffer
            snapshot[i].pos_x = cell_b.pos_x
            snapshot[i].pos_y = cell_b.pos_y
            snapshot[i].c_state = cell_b.c_state
            snapshot[i].charge = cell_b.charge
            snapshot[i].timer = cell_b.timer
        self.grid_a = self.grid_b
        self.grid_b = tmp

    cpdef void update_grid(self, show_charge: bool):
        """
        Simple update method for the python API. The logic should be moved to the nogil pure C implementation.
        """
        cdef DrawFunc func
        if show_charge:
            func = draw_from_charge
        else:
            func = draw_from_state
        self._update_grid_nogil(func)

    cpdef int render_frame(self, int idx, object if_charged, object drop_newer):
        cdef int i
        cdef CellSnapshot* snapshots = self.frame_recorder.get_buffer(idx)
        cdef DrawFunc func
        cdef CCell* cell
        if if_charged:
            func = draw_from_charge
        else:
            func = draw_from_state
        
        for i in range(self.n_nodes):
            cell = self.grid_a[i]
            cell.c_state = snapshots[i].c_state
            cell.charge = snapshots[i].charge
            cell.timer = snapshots[i].timer 
            func(self.img_buffer, self.bytes_per_line, cell)

        if drop_newer:
            self.frame_recorder.remove_newer(idx)
            self.frame_recorder.remove_older(idx)

        return self.frame_counter + idx

    cpdef dict _cells_to_dict(self):
        """
        Helper method to map the cell objects to the cached dictionary. Performed in-place
        """
        cdef int i
        cdef CCell* cell
        for i in range(self.n_nodes):
            cell = self.grid_a[i]
            self.dict_mapping[(cell.pos_x, cell.pos_y)] = cell_to_dict(cell, self.dict_mapping[(cell.pos_x, cell.pos_y)])

    cpdef int to_cell_data(self):
        """
        Getter for the serialized data. Returns the Tuple with the current frame and the serialized cells.
        """
        # self._cells_to_dict()
        return int(self.frame_counter)#tuple((int(self.frame_counter), self.dict_mapping))

    cpdef void modify_cell_state(self, set coords, object new_state):
        """
        Modifies state of picked cells
        coords : set[tuple[int, int]] - set of modified cells cooridnates(x, y)
        new_state : CellState - new state
        """
        cdef int i
        cdef CCell* cell
        cdef int x, y
        cdef CellStateC c_state_val = <CellStateC> state_to_cenum(new_state)

        for i in range(self.n_nodes):
            cell = self.grid_a[i]
            x, y = cell.pos_x, cell.pos_y

            if (x, y) in coords:
                cell.c_state = c_state_val

    cpdef void modify_charge_data(self, set coords, dict atrial_charge_parameters, dict pacemaker_charge_parameters,
    dict purkinje_charge_parameters):
        """
        Modifies structs CCell with new charges made with updated charge parameters.
        """
        cdef int i
        cdef CCell* cell
        cdef int x, y
        cdef dict charge_params
        cdef dict cell_config
        cdef dict cell_data

        for i in range(self.n_nodes):
            cell = self.grid_a[i]
            x, y = cell.pos_x, cell.pos_y

            if (x, y) not in coords:
                continue

            wrapper = self.cell_data.get((x, y), None)
            if wrapper is None:
                continue

            config = wrapper.cell_data

            if cell.c_type in {CellTypeC.HIS_LEFT, CellTypeC.HIS_RIGHT, CellTypeC.HIS_BUNDLE}:
                # PURKINJE
                config["cell_data"].update(purkinje_charge_parameters)
            elif cell.c_type in {CellTypeC.SA_NODE, CellTypeC.AV_NODE}:
                # PACEMAKERS
                config["cell_data"].update(pacemaker_charge_parameters)
            else:
                # ATRIAL CELLS
                config["cell_data"].update(atrial_charge_parameters)

            charges, max_charge, ref_threshold = ChargeUpdate.get_func(config)

            cell.charge_max = <int> max_charge
            cell.V_peak = <double> config["cell_data"].get("V_peak")
            cell.V_rest = <double> config["cell_data"].get("V_rest")
            cell.V_thresh = <double> config["cell_data"].get("V_thresh", 0)
            cell.ref_threshold = <double> ref_threshold

            if charges is not None:
                add_cell_charges(cell, np.asarray(charges, dtype=np.float64))
            else:
                raise RuntimeError("Attempted construction of a cell with no charge function")

    cpdef void commit_current_automaton(self):
        """
        Takes current version of automaton and saves it in modification buffer.
        It saves current automaton by copying CCell structures, without neighbours, just parameters.
        """
        cdef CCell** snap
        cdef int i

        snap = <CCell**> malloc(self.n_nodes * sizeof(CCell*))
        if snap == NULL:
            raise MemoryError("Failed to allocate snapshot grid")

        for i in range(self.n_nodes):
            snap[i] = create_mimic_cell(self.grid_a[i])
            if snap[i] == NULL:
                while i > 0:
                    i -= 1
                    free(snap[i].charges)
                    free(snap[i])
                free(snap)
                raise MemoryError("Failed to create mimic cell")

        if self.buf_size % 8 == 0:
            self.modification_snapshot_grids = <CCell***> realloc(
                self.modification_snapshot_grids,
                (self.buf_size + 8) * sizeof(CCell**)
            )
            if self.modification_snapshot_grids == NULL:
                raise MemoryError("Failed to realloc snapshot buffer")

        self.modification_snapshot_grids[self.buf_size] = snap
        self.buf_size += 1
        self.frame_recorder.clear_all()


    cpdef void undo_modification(self):
        """
        Takes last snapshot saved in modification buffer and loads it into automaton.
        Takes snapshot CCell structures (mimics) and copy their values into automaton cells leaving neighbours connected.
        """
        if self.buf_size == 0:
            return

        self.buf_size -= 1
        cdef CCell** snap = self.modification_snapshot_grids[self.buf_size]
        cdef int i

        for i in range(self.n_nodes):
            recreate_cell_from_mimic(self.grid_a[i], snap[i])
            recreate_cell_from_mimic(self.grid_b[i], snap[i])

        self._dealloc_grid(snap)

        self.modification_snapshot_grids[self.buf_size] = NULL
        self.frame_recorder.clear_all()

    """
    Set of getters and setters for the python API
    """ 
    cpdef float get_frame_time(self):
        return float(self.frame_time)
    
    cpdef void set_frame_time(self, double frame_time):
        self.frame_time = <double> frame_time

    cpdef tuple get_shape(self):
        return self.size

    cpdef void set_frame_counter(self, int idx):
        self.frame_recorder.remove_newer(idx)
        self.frame_counter += idx

    cpdef dict get_cell_data(self, tuple position):
        data = self.cell_data.get(position, None)
        if data is not None:
            return data.get_cell_dict()
        return None

    cpdef int get_buffer_size(self):
        return self.frame_recorder.get_count()