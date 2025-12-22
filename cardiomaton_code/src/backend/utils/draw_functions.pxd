from src.backend.enums.cell_state cimport CellStateC
from src.backend.structs.c_cell cimport CCell
from libc.stdint cimport uint8_t
from src.backend.structs.c_triangle cimport CTriangle, TriangleOrientation


"""
Function pointer type. Used to select the draw function without branching in the loop
"""
ctypedef void (*DrawFunc)(unsigned char*, int, CCell*) noexcept nogil

cdef void draw_from_state(unsigned char*, int, CCell*) noexcept nogil
cdef void draw_from_charge(unsigned char*, int, CCell*) noexcept nogil
cdef void draw_cell_soft(unsigned char* img, int bytes_per_line, int cx, int cy, uint8_t r, uint8_t g, uint8_t b, uint8_t a) noexcept nogil
cdef void draw_triangle_soft(unsigned char* img, int bytes_per_line, CTriangle tri) noexcept nogil