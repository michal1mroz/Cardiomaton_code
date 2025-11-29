from src.backend.structs.c_cell cimport CCell, is_neighbor_depolarized, is_relative_repolarization
from src.backend.enums.cell_state cimport CellStateC
from src.backend.enums.cell_type cimport CellTypeC

cdef int eps = 1

cdef inline void update_cell(CCell* cell_a, CCell* cell_b):
    """
    Helper function that overwrites the state of cell_b with the updated charge of cell_a.
    """
    cdef int timer 
    cdef float charge
    timer = (cell_a.timer + 1) % cell_a.period
    cell_b.timer = timer
    cell_a.timer = timer
    cell_b.charge = cell_a.charges[timer] 

cdef inline void depolarize_cell(CCell* cell_a, CCell* cell_b):
    """
    Helper function that depolarizes cell and overwrites the state of cell_b with it
    """
    cell_a.timer = cell_a.charge_max
    cell_b.timer = cell_b.charge_max
    cell_b.charge = cell_b.charges[cell_b.charge_max]
    cell_b.c_state = CellStateC.RAPID_DEPOLARIZATION

cdef void update_charge(CCell* cell_a, CCell* cell_b):
    """
    Update method. Mirrors update_charge_ms.py, but performs changes in place.
    Cython doesn't support the switch-case syntax, so had to split it into if-elif chain :<<

    Args:
        cell_a CCell* - pointer to the current cell (taken from the grid_a of the automaton)
        cell_b CCell* - pointer to the next cell (taken from the grid_b of the automaton)
    """
    cdef int new_timer
    cdef double charge

    # Update counter for cell polarization
    if cell_a.can_propagate == 1:
        if cell_a.propagation_count >= cell_a.propagation_time_max:
            cell_b.can_propagate = 0
            cell_a.can_propagate = 0
            cell_a.propagation_count = 1
            cell_b.propagation_count = 1
        else:
            cell_a.propagation_count += 1
            cell_b.propagation_count += 1

    if cell_a.c_state == CellStateC.NECROSIS:
        cell_b.charge = 0
        cell_b.timer = cell_a.timer
        cell_b.c_state = cell_a.c_state
        return
    
    elif cell_a.c_state == CellStateC.REPOLARIZATION_ABSOLUTE_REFRACTION:
        update_cell(cell_a, cell_b)

        if cell_b.charge <= cell_a.ref_threshold:
            cell_b.c_state = CellStateC.REPOLARIZATION_RELATIVE_REFRACTION
        else:
            cell_b.c_state = cell_a.c_state
        return
    
    elif cell_a.c_state == CellStateC.REPOLARIZATION_RELATIVE_REFRACTION:
        if is_relative_repolarization(cell_a) == 1:
            depolarize_cell(cell_a, cell_b)
            return
        
        new_timer = (cell_a.timer + 1) % cell_a.period
        new_charge = cell_a.charges[new_timer]

        cell_a.timer = new_timer
        cell_b.timer = new_timer

        if (new_charge - cell_a.V_rest) <= eps:
            cell_b.charge = cell_a.V_rest
            if cell_a.self_polarization == 1:
                cell_b.c_state = CellStateC.SLOW_DEPOLARIZATION
                return
            else:
                cell_b.c_state = CellStateC.POLARIZATION
                return

        cell_b.charge = new_charge
        cell_b.c_state = cell_a.c_state
        return

    elif cell_a.c_state == CellStateC.POLARIZATION:
        if is_neighbor_depolarized(cell_a) == 1:
            depolarize_cell(cell_a, cell_b)
            return

        if cell_a.self_polarization == 1:
            update_cell(cell_a, cell_b)
            cell_b.c_state = CellStateC.SLOW_DEPOLARIZATION
            return
        else:
            cell_b.charge = cell_a.charge
            cell_b.c_state = cell_a.c_state
            cell_b.timer = cell_a.timer
            return

    elif cell_a.c_state == CellStateC.SLOW_DEPOLARIZATION:
        if is_neighbor_depolarized(cell_a) == 1:
            depolarize_cell(cell_a, cell_b)
            return
        
        if cell_a.charge >= cell_a.V_peak:
            cell_b.charge = cell_a.V_peak
            cell_b.timer = cell_a.timer

            cell_b.c_state = CellStateC.RAPID_DEPOLARIZATION
            return

        update_cell(cell_a, cell_b)

        if cell_a.charge >= cell_a.V_thresh:
            cell_b.c_state = CellStateC.RAPID_DEPOLARIZATION
        else:
            cell_b.c_state = CellStateC.SLOW_DEPOLARIZATION
        return

    elif cell_a.c_state == CellStateC.RAPID_DEPOLARIZATION:
        if cell_a.self_polarization == 1:
            update_cell(cell_a, cell_b)
        else:
            cell_b.charge = cell_a.charge
        
        cell_b.can_propagate = 1
        cell_a.can_propagate = 1
        cell_b.c_state = CellStateC.REPOLARIZATION_ABSOLUTE_REFRACTION