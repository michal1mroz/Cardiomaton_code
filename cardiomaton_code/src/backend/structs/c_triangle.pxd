from src.backend.structs.c_cell cimport CCell


cdef enum TriangleOrientation:
    TRI_NE = 0  # (x,y) + (x+1,y+1), brak (x, y+1)
    TRI_NW = 1  # (x,y) + (x-1,y+1), brak (x, y+1)
    TRI_SE = 2  # (x,y) + (x+1,y-1), brak (x, y-1)
    TRI_SW = 3  # (x,y) + (x-1,y-1), brak (x, y-1)


cdef struct CTriangle:
    int x
    int y
    TriangleOrientation orient

cdef unsigned long long cell_key(int x, int y) noexcept nogil
cdef CTriangle* find_smoothing_triangles(CCell** cells, int n_cells, int* n_triangles)