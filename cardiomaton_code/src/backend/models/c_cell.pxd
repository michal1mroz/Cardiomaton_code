from libc.stdlib cimport malloc, free

from src.backend.models.cell_state cimport CellStateC
from src.backend.models.cell_type cimport CellTypeC

cdef struct CCell:
    # General atributes
    int pos_x
    int pos_y

    CellStateC c_state 
    CellTypeC c_type
    int self_polarization # 0 for False, non zero for True

    # Neighbors     
    int n_neighbors
    CCell** neighbors # Needs manual allocation and deallocation!
    
    # Charges
    double charge
    int period
    int timer 

    double* charges # Needs manual allocation and deallocation!
    int n_charges
    int charge_max

cdef CCell* create_c_cell(int, int)
cdef void add_cell_charges(CCell*, double[:])
cdef void free_cell_charges(CCell*)
cdef void free_c_cell(CCell*)

cdef void reset_cell_timer(CCell*)
cdef void update_cell_timer(CCell*)
cdef double update_charge(CCell*)
cdef double depolarize(CCell*)
