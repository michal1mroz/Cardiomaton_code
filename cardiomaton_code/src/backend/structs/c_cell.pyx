from libc.stdlib cimport malloc, free
from libc.string cimport memcpy
from libc.stdio cimport printf
from src.backend.enums.cell_state cimport CellStateC, cell_state_name
from src.backend.enums.cell_type cimport CellTypeC, type_to_pyenum

from src.backend.enums.cell_type import CellType
from src.backend.models.cell import CellDict

##########################################################
# Simple module providing rudimentary operations on cell.
# In this approach cell is represented as a struct,
# so to manipulate it you need to use free functions instead of object methods.
#
# Neighbors need to be added manualy.
##########################################################

cdef CCell* create_c_cell(int pos_x, int pos_y):
    """
    Creates a pointer to CCell struct and returns it. Assigns its position to the
    one specified with the passed arguments and zeroes the rest of the data.

    Args:
        pos_x int - x position of the cell.
        pos_y int - y position of the cell.
    
    Returns:
        CCell* ptr - pointer to the allocated object.
    
    Throws:
        MemoryError - on the failed malloc
    """
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
    """
    Method to allocate the memory for the charges array and copy the values from the passed
    memory view.

    Args:
        cell CCell* - pointer to the cell
        py_charges double[:] - memory view of the float list

    Throws:
        RuntimeError - on the empty cell pointer
        MemoryError - on the failed malloc call
    """
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
    """
    Function to allocate the memory for the cell neighbors.

    Args:
        cell CCell* - target cell
        size int - neighbor count

    Throws:
        runtimeError - on the empty cell pointer.
        MemoryError - on the failed malloc
    """
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
    """
    Helper method to free the memory used to store the charges

    Args:
        cell CCell* - pointer to the target cell

    Throws:
        RuntimeError - on the empty cell pointer
    """
    if cell == NULL:
        raise RuntimeWarning("Trying to free memory from the NULL pointer")
    if cell.charges != NULL:
        free(cell.charges)
        cell.charges = NULL
        cell.n_charges = 0

cdef void free_c_cell(CCell* cell):
    """
    Attempts to remove all the memory for the cell. Doesn't remove/dereference neighbors,
    only frees the array used to store their pointers

    Args:
        cell CCell* - pointer to the target cell
    """
    if cell != NULL:
        if cell.neighbors != NULL:
            free(cell.neighbors)
            cell.n_neighbors = 0

        free_cell_charges(cell)
        
        free(cell)

cdef dict cell_to_dict(CCell* cell, dict target):
    """
    Fills the dynamic data to the target dict. Assumes that it follows the structure of the
    CellDict python object.

    Args:
        cell CCell* - mapped cell
        target dict - python dictionary object
    """

    target["state_value"] = cell.c_state + 1
    target["state_name"] = cell_state_name(cell.c_state)
    target["charge"] = float(cell.charge)
    return target

##################################################
# Currently not used. I've rewrote them since they were present in the pure python version
##################################################

cdef void reset_cell_timer(CCell* cell):
    cell.timer = 0

cdef void update_cell_timer(CCell* cell):
    cell.timer = (cell.timer + 1) % cell.period

cdef double update_charge(CCell* cell):
    return cell.charges[cell.timer]

cdef double depolarize(CCell* cell):
    cell.timer = cell.charge_max
    return cell.charges[cell.charge_max]

#############################################################

cdef int is_neighbor_depolarized(CCell* cell):
    """
    Check if at least NEIGHBOR_DEPOLARIZATION_COUNT neighbors of the cell 
    are in RAPID_DEPOLARIZATION state

    Args:
        cell CCell* - target cell
    
    Returns:
        int 1 if true, else 0
    """
    if cell == NULL or cell.neighbors == NULL:
        return 0
    
    cdef int i = 0
    cdef int count = 0
    cdef CCell* neighbor

    for i in range(cell.n_neighbors):
        neighbor = cell.neighbors[i]
        if neighbor != NULL and neighbor.can_propagate == 1 and neighbor.propagation_count > neighbor.propagation_time:
        # if neighbor != NULL and neighbor.c_state == CellStateC.RAPID_DEPOLARIZATION:
            count += 1
            if count >= NEIGHBOR_DEPOLARIZATION_COUNT: # current models doesn't work for >= 2 or more
                return 1
    return 0

cdef int is_relative_repolarization(CCell* cell):
    """
    Check if the repolarization in relative refraction is possible.
    For it to be possible at least NEIGHBOR_REFRACTION_POLAR neighbors must have
    the charge greater or equal to REFRACTION_POLAR constant

    Args:
        cell CCell* - pointer to the target cell
    
    Returns:
        int 1 if true, 0 else
    """
    
    if cell == NULL or cell.neighbors == NULL:
        return 0 
    cdef int i = 0
    cdef int count = 0
    cdef CCell* neighbor

    for i in range(cell.n_neighbors):
        neighbor = cell.neighbors[i]
        if neighbor != NULL and (neighbor.charge - cell.charge >= REFRACTION_POLAR):
            count += 1
            if count >= NEIGHBOR_REFRACTION_POLAR:
                return 1
    return 0

#############################################################


cdef CCell* create_mimic_cell(CCell* src):
    """
    Creates copy of a CCell as a snapshot without neighbourhood.
    """
    cdef CCell* dst = <CCell*> malloc(sizeof(CCell))
    memcpy(dst, src, sizeof(CCell))

    dst.neighbors = NULL


    if src.charges != NULL:
        dst.charges = <double*> malloc(src.n_charges * sizeof(double))
        memcpy(dst.charges, src.charges, src.n_charges * sizeof(double))

    return dst

cdef void recreate_cell_from_mimic(CCell* dst, CCell* mimic):
    """
    Copies parameters from src CCell into dst CCell, without neighbourhood.
    """
    if dst == NULL or mimic == NULL:
        return

    # Positional data
    dst.pos_x = mimic.pos_x
    dst.pos_y = mimic.pos_y

    # Basic attributes
    dst.c_state = mimic.c_state
    dst.c_type = mimic.c_type
    dst.self_polarization = mimic.self_polarization

    # Charge parameters
    dst.charge = mimic.charge
    dst.period = mimic.period
    dst.timer = mimic.timer

    dst.n_charges = mimic.n_charges
    dst.charge_max = mimic.charge_max

    if mimic.charges != NULL and mimic.n_charges > 0:

        if dst.charges == NULL or dst.n_charges != mimic.n_charges:
            if dst.charges != NULL:
                free(dst.charges)
            dst.charges = <double*> malloc(mimic.n_charges * sizeof(double))
            if dst.charges == NULL:
                return

        memcpy(dst.charges, mimic.charges, mimic.n_charges * sizeof(double))

    else:
        if dst.charges != NULL:
            free(dst.charges)
        dst.charges = NULL

    # Voltage model parameters
    dst.V_thresh = mimic.V_thresh
    dst.V_rest = mimic.V_rest
    dst.V_peak = mimic.V_peak
    dst.ref_threshold = mimic.ref_threshold