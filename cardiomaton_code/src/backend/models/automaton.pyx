from libc.stdio cimport printf

from src.backend.models.c_cell cimport CCell, create_c_cell, add_charges, free_c_cell
from src.backend.models.cell_state cimport CellStateC, state_to_cenum
from src.backend.utils.charge_update cimport update_charge

from src.backend.models.cell import Cell


cdef class Automaton:

    def __cinit__(self, py_cell: Cell):
        self.py_cell = py_cell
        self.cell = create_c_cell(py_cell.pos_x, py_cell.pos_y)

        add_charges(self.cell, py_cell.charges_mv)
        self.cell.c_state = state_to_cenum(py_cell.state)

    def __dealloc__(self):
        if self.cell is not NULL:
            free_c_cell(self.cell)
            self.cell = NULL

    cpdef void print_state(self):
        if self.cell is NULL:
            print("<Automaton: Empty>")
            return
        print(self.cell.pos_x, self.cell.pos_y, self.cell.n_neighbors)

    cpdef void update_cell(self):
        update_charge(self.cell.c_state)
   