from libc.stdlib cimport malloc, realloc, free

cdef unsigned long long cell_key(int x, int y) noexcept nogil:
    return (<unsigned long long><unsigned int>x << 32) | <unsigned int>y

cdef CTriangle* find_smoothing_triangles(CCell** cells, int n_cells, int* n_triangles):
    cdef int i
    cdef CCell* c
    cdef int x, y

    cdef dict occupied = {}

    for i in range(n_cells):
        c = cells[i]
        occupied[cell_key(c.pos_x, c.pos_y)] = True

    cdef CTriangle* result = <CTriangle*>malloc(
        n_cells * 4 * sizeof(CTriangle)
    )
    if result == NULL:
        n_triangles[0] = 0
        return NULL

    cdef int count = 0

    for i in range(n_cells):
        c = cells[i]
        x = c.pos_x
        y = c.pos_y

        # SE
        if (cell_key(x + 1, y + 1) in occupied and
            cell_key(x,     y + 1) not in occupied):
            result[count].x = x
            result[count].y = y + 1
            result[count].orient = TRI_SE
            count += 1

        # NE
        if (cell_key(x - 1, y + 1) in occupied and
            cell_key(x,     y + 1) not in occupied):
            result[count].x = x
            result[count].y = y + 1
            result[count].orient = TRI_NE
            count += 1

        # SW
        if (cell_key(x + 1, y - 1) in occupied and
            cell_key(x,     y - 1) not in occupied):
            result[count].x = x
            result[count].y = y - 1
            result[count].orient = TRI_SW
            count += 1

        # NW
        if (cell_key(x - 1, y - 1) in occupied and
            cell_key(x,     y - 1) not in occupied):
            result[count].x = x
            result[count].y = y - 1
            result[count].orient = TRI_NW
            count += 1

    n_triangles[0] = count

    if count == 0:
        free(result)
        return NULL

    cdef CTriangle* shrunk = <CTriangle*>realloc(
        result,
        count * sizeof(CTriangle)
    )

    if shrunk == NULL:
        return result

    return result