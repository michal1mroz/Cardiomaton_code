from libc.stdlib cimport malloc, free
from src.backend.models.cell_state cimport CellStateC, cell_state_name
from src.backend.models.cell_type cimport CellTypeC, type_to_pyenum

from src.backend.models.cell_type import CellType
from src.backend.models.cell import CellDict

##########################################################
# Simple module providing rudimentary operations on cell.
# In this approach cell is represented as a struct,
# so to manipulate it you need to use free functions instead of object methods.
#
# Neighbors need to be added manualy.
##########################################################

cdef CCell* create_c_cell(int pos_x, int pos_y):
    cdef CCell* c_cell = <CCell*> malloc(sizeof(CCell))
    if c_cell == NULL:
        raise MemoryError()

    # Initialize
    c_cell.pos_x = pos_x
    c_cell.pos_y = pos_y
    c_cell.c_state = <CellStateC>0
    c_cell.c_type = <CellTypeC>0
    c_cell.self_polarization = 0

    c_cell.n_neighbors = 0
    c_cell.neighbors = NULL

    c_cell.charge = 0.0
    c_cell.period = 0
    c_cell.timer = 0

    c_cell.charges = NULL
    c_cell.n_charges = 0
    c_cell.charge_max = 0

    return c_cell 

cdef void add_cell_charges(CCell* cell, double[:] py_charges):
    # Allocates the memory for charges and adds them to the cell
    if cell == NULL:
        raise RuntimeError()

    free_cell_charges(cell) # When overwriting deallocate the memory first
    
    cell.n_charges = py_charges.shape[0]
    cell.charges = <double*> malloc(cell.n_charges * sizeof(double))
    if cell.n_charges > 0 and cell.charges == NULL:
        free(cell)
        raise MemoryError()

    cdef int i
    for i in range(cell.n_charges):
        cell.charges[i] = py_charges[i]

cdef void allocate_neighbors(CCell* cell, int size):
    if cell == NULL:
        raise RuntimeError()
    if cell.neighbors != NULL:
        free(cell.neighbors)
        cell.neighbors = NULL
        cell.n_neighbors = 0
    
    cell.n_neighbors = size
    cell.neighbors = <CCell**> malloc(size * sizeof(CCell*))
    if cell.n_neighbors > 0 and cell.neighbors == NULL:
        free_c_cell(cell)
        raise MemoryError()


cdef void free_cell_charges(CCell* cell):
    if cell == NULL:
        raise RuntimeWarning("Trying to free memory from the NULL pointer")
    if cell.charges != NULL:
        free(cell.charges)
        cell.charges = NULL
        cell.n_charges = 0

cdef void free_c_cell(CCell* cell):
    if cell != NULL:
        if cell.neighbors != NULL:
            free(cell.neighbors)
            cell.n_neighbors = 0

        free_cell_charges(cell)
        
        free(cell)

cdef dict cell_to_dict(CCell* cell, dict target):
    #py_type = type_to_pyenum(cell.c_type)
    #auto = False if cell.self_polarization == 0 else True
    target["state_value"] = cell.c_state + 1
    target["state_name"] = cell_state_name(cell.c_state)
    target["charge"] = float(cell.charge)
    return target

    
cdef void reset_cell_timer(CCell* cell):
    cell.timer = 0

cdef void update_cell_timer(CCell* cell):
    cell.timer = (cell.timer + 1) % cell.period

cdef double update_charge(CCell* cell):
    return cell.charges[cell.timer]

cdef double depolarize(CCell* cell):
    cell.timer = cell.charge_max
    return cell.charges[cell.charge_max]

cdef int is_neighbor_depolarized(CCell* cell):
    # Check if there are at least NEIGHBOR_DEPOLARIZATION_COUNT
    # references with the state set to RAPID_DEPOLARIZATION.
    # returns 1 if yes and 0 otherwise
    if cell == NULL or cell.neighbors == NULL:
        return 0
    
    cdef int i = 0
    cdef int count = 0
    cdef CCell* neighbor

    for i in range(cell.n_neighbors):
        neighbor = cell.neighbors[i]
        if neighbor != NULL and neighbor.c_state == CellStateC.RAPID_DEPOLARIZATION:
            count += 1
            if count > NEIGHBOR_DEPOLARIZATION_COUNT:
                return 1
    return 0

cdef int is_relative_repolarization(CCell* cell):
    if cell == NULL or cell.neighbors == NULL:
        return 0 
    cdef int i = 0
    cdef int count = 0
    cdef CCell* neighbor

    for i in range(cell.n_neighbors):
        neighbor = cell.neighbors[i]
        if neighbor != NULL and (neighbor.charge - cell.charge >= REFRACTION_POLAR):
            count += 1
            if count > NEIGHBOR_REFRACTION_POLAR:
                return 1
    return 0