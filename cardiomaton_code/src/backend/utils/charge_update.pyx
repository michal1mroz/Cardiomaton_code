from src.backend.models.cell_state cimport CellStateC
from src.backend.models.c_cell cimport CCell, is_neighbor_depolarized, is_relative_repolarization
from src.backend.models.cell_type cimport CellTypeC

cdef void update_charge(CCell* cell_a, CCell* cell_b):
    cdef int new_timer
    cdef double charge

    if cell_a.c_state == CellStateC.NECROSIS:
        cell_b.charge = 0
        cell_b.timer = cell_a.timer
        cell_b.c_state = cell_a.c_state
        return
    
    elif cell_a.c_state == CellStateC.REPOLARIZATION_ABSOLUTE_REFRACTION:
        new_timer = (cell_a.timer + 1) % cell_a.period

        cell_a.timer = new_timer 
        cell_b.timer = new_timer
        charge = cell_a.charges[new_timer]
        cell_b.charge = charge
        if charge <= cell_a.V_thresh:
            cell_b.c_state = CellStateC.REPOLARIZATION_RELATIVE_REFRACTION
        else:
            cell_b.c_state = cell_a.c_state
        return
    
    elif cell_a.c_state == CellStateC.REPOLARIZATION_RELATIVE_REFRACTION:
        if is_relative_repolarization(cell_a) == 1:
            cell_a.timer = cell_a.charge_max
            cell_b.timer = cell_b.charge_max
            cell_b.charge = cell_b.charges[cell_b.charge_max]
            cell_b.c_state = CellStateC.RAPID_DEPOLARIZATION
            return
        
        new_timer = (cell_a.timer + 1) % cell_a.period
        new_charge = cell_a.charges[new_timer]

        cell_a.timer = new_timer
        cell_b.timer = new_timer

        if new_charge <= cell_a.V_rest:
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
            cell_b.timer = cell_b.charge_max
            cell_a.timer = cell_a.charge_max
            new_charge = cell_b.charges[cell_b.charge_max]
            cell_b.charge = new_charge
            cell_b.c_state = CellStateC.RAPID_DEPOLARIZATION
            return

        if cell_a.self_polarization == 1:
            new_timer = (cell_a.timer + 1) % cell_a.period
            cell_b.timer = new_timer
            cell_a.timer = new_timer
            cell_b.charge =  cell_a.charges[new_timer]
            cell_b.c_state = CellStateC.SLOW_DEPOLARIZATION
            return
        else:
            cell_b.charge = cell_a.charge
            cell_b.c_state = cell_a.c_state
            cell_b.timer = cell_a.timer
            return

    elif cell_a.c_state == CellStateC.SLOW_DEPOLARIZATION:
        if cell_a.charge >= cell_a.V_peak:
            cell_b.charge = cell_a.V_peak
            cell_b.timer = cell_a.timer
            cell_b.c_state = CellStateC.RAPID_DEPOLARIZATION
            return

        new_timer = (cell_a.timer + 1) % cell_a.period
        cell_a.timer = new_timer
        cell_b.timer = new_timer
        cell_b.charge = cell_a.charges[new_timer]

        if cell_a.charge >= cell_a.V_thresh:
            cell_b.c_state = CellStateC.RAPID_DEPOLARIZATION
        else:
            cell_b.c_state = CellStateC.SLOW_DEPOLARIZATION
        return

    elif cell_a.c_state == CellStateC.RAPID_DEPOLARIZATION:
        if cell_a.self_polarization == 1:
            new_timer = (cell_a.timer + 1) % cell_a.period
            cell_a.timer = new_timer
            cell_b.timer = new_timer
            cell_b.charge = cell_a.charges[new_timer]
        else:
            cell_b.charge = cell_a.charge
        cell_b.c_state = CellStateC.REPOLARIZATION_ABSOLUTE_REFRACTION