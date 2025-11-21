from libc.stdlib cimport malloc, free

from src.backend.enums.cell_state cimport CellStateC
from src.backend.enums.cell_type cimport CellTypeC

"""
This module contains the definition of the CCell struct - representation of the Cell object 
used in the simulation kernel.
"""

# Constants
cdef const double REFRACTION_POLAR = 1000
cdef const int NEIGHBOR_REFRACTION_POLAR = 1
cdef const int NEIGHBOR_DEPOLARIZATION_COUNT = 1

# Cell struct
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

    double V_thresh
    double V_rest
    double V_peak
    double ref_threshold

    int propagation_time
    int propagation_time_max
    int can_propagate
    int propagation_count

#####################################
# Function signatures

# helper functions
cdef CCell* create_c_cell(int, int)
cdef void add_cell_charges(CCell*, double[:])
cdef void allocate_neighbors(CCell*, int)
cdef void free_cell_charges(CCell*)
cdef void free_c_cell(CCell*)

cdef dict cell_to_dict(CCell*, dict)

# simple manipulations. Can be inlined in the future
cdef void reset_cell_timer(CCell*)
cdef void update_cell_timer(CCell*)
cdef double update_charge(CCell*)
cdef double depolarize(CCell*)

# helper functions for the charge update function
cdef int is_neighbor_depolarized(CCell*)
cdef int is_relative_repolarization(CCell*)
