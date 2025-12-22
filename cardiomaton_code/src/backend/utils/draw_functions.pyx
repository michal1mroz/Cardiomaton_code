from libc.stdint cimport uint8_t
from libc.math cimport fabsf
from libc.math cimport sqrtf


from src.backend.enums.cell_state cimport CellStateC
from src.backend.structs.c_cell cimport CCell
from src.backend.structs.c_triangle cimport CTriangle, TriangleOrientation


"""
    Mapping CellStateC -> color in 8-bit RGBA, where first index
    is the state value (as defined in src/backed/models/cell_state),
    followed by the color values.
    To modify the color, change the respective values in the array.
"""
cdef uint8_t COLOR_TABLE[6][4]
COLOR_TABLE[0][:] = [255,  255, 255, 255] # Polarization: #FFFFFFFF
COLOR_TABLE[1][:] = [255,  255, 0  , 255] # Slow depolarization: #FFFF00FF
COLOR_TABLE[2][:] = [255,      0, 0, 255] # Rapid depolarization: #FF0000FF
COLOR_TABLE[3][:] = [0,   0,  255  , 255] # Repo. abs. refraction: #0000FFFF
COLOR_TABLE[4][:] = [  0,   128,  0, 255] # Repo. rel. refraction: #008000FF
COLOR_TABLE[5][:] = [  0,  0,   0,   255] # Necrosis #000000FF

cdef int K = 5
cdef int img_height = 292 * K
cdef int img_width = 400 * K

cdef float RADIUS = 1.5
cdef float INV_RADIUS = 1.0 / RADIUS

cdef void draw_from_state(unsigned char* img, int bytes_per_line, CCell* cell) noexcept nogil:
    """
        Helper function that uses color mapping for states to mark the 
        corresponding cells on the image.

        Args:
            img unsigned char*: pointer to the image buffer
            bytes_per_line int: number of bytes in on image line
            cell CCell*: pointer to the drawn cell struct
    """
    cdef int st = <int>cell.c_state
    cdef int cy = cell.pos_x * K + K // 2
    cdef int cx = cell.pos_y * K + K // 2

    draw_cell_soft(
        img,
        bytes_per_line,
        cx,
        cy,
        COLOR_TABLE[st][0],
        COLOR_TABLE[st][1],
        COLOR_TABLE[st][2],
        COLOR_TABLE[st][3]
    )

cdef void draw_from_charge(unsigned char* img, int bytes_per_line, CCell* cell) noexcept nogil:
    cdef float h, s, v
    cdef float r_f, g_f, b_f
    cdef int r, g, b
    cdef int hi
    cdef float f
    cdef int pos_x = cell.pos_x
    cdef int pos_y = cell.pos_y
    cdef unsigned char* pixel

    s = 1.0
    v = 1.0

    if (cell.self_polarization == 0) and (cell.c_state == CellStateC.POLARIZATION):
        h = 0
        s = 0
        v = 255.0 / 255.0
    elif cell.c_state == CellStateC.NECROSIS:
        h = 0
        s = 0
        v = 0
    else:
        h = -cell.charge * 0.25 + 7.5
        if h < 0:
            h = 0.0
        elif h > 30.0:
            h = 30.0
    while h < 0:
        h += 360.0
    while h >= 360.0:
        h -= 360.0
    
    c = v * s
    hi = <int> (h / 60.0) % 6
    f = (h / 60.0) - <int>(h / 60.0)
    x = c * (1.0 - fabsf((f * 2.0) - 1.0))
    m = v - c

    if hi == 0:
        r_f, g_f, b_f = c, x, 0
    elif hi == 1:
        r_f, g_f, b_f = x, c, 0
    elif hi == 2:
        r_f, g_f, b_f = 0, c, x
    elif hi == 3:
        r_f, g_f, b_f = 0, x, c
    elif hi == 4:
        r_f, g_f, b_f = x, 0, c
    else:
        r_f, g_f, b_f = c, 0, x
    
    r = <int>((r_f + m) * 255.0)
    g = <int>((g_f + m) * 255.0)
    b = <int>((b_f + m) * 255.0)

    if r < 0: r = 0
    elif r > 255: r = 255
    if g < 0: g = 0
    elif g > 255: g = 255
    if b < 0: b = 0
    elif b > 255: b = 255

    cdef int cy = cell.pos_x * K + K // 2
    cdef int cx = cell.pos_y * K + K // 2

    draw_cell_soft(
        img,
        bytes_per_line,
        cx,
        cy,
        <uint8_t>r,
        <uint8_t>g,
        <uint8_t>b,
        255
    )

cdef void draw_cell_soft(unsigned char* img, int bytes_per_line, int cx, int cy, uint8_t r, uint8_t g, uint8_t b, uint8_t a) noexcept nogil:
    cdef int px, py, idx
    cdef int half = K // 2

    for py in range(cy - half, cy - half + K):
        if py < 0 or py >= img_height:
            continue

        for px in range(cx - half, cx - half + K):
            if px < 0 or px >= img_width:
                continue

            idx = py * bytes_per_line + px * 4

            img[idx + 0] = r
            img[idx + 1] = g
            img[idx + 2] = b
            img[idx + 3] = a

cdef void draw_triangle_soft(unsigned char* img, int bytes_per_line, CTriangle tri) noexcept nogil:
    cdef int px, py, idx
    cdef int half = K // 2
    cdef float fx, fy
    cdef float A = K * 0.9
    cdef float B = K * 0.9

    cdef int cy = tri.x * K + half
    cdef int cx = tri.y * K + half

    cdef int base_y = cy - half
    cdef int base_x = cx - half

    cdef int sample_x, sample_y, sample_idx
    cdef uint8_t r, g, b, a

    if tri.orient == TriangleOrientation.TRI_NW or tri.orient == TriangleOrientation.TRI_SW:
        sample_x = base_x + K
        sample_y = cy
    else:  # TRI_NE, TRI_SE
        sample_x = base_x - 1
        sample_y = cy

    if sample_x < 0 or sample_x >= img_width or sample_y < 0 or sample_y >= img_height:
        return

    sample_idx = sample_y * bytes_per_line + sample_x * 4
    r = img[sample_idx + 0]
    g = img[sample_idx + 1]
    b = img[sample_idx + 2]
    a = img[sample_idx + 3]
    # r = 0
    # g = 255
    # b = 0
    # a = 255

    for py in range(K):
        for px in range(K):

            if tri.orient == TriangleOrientation.TRI_NE:
                if px + py >= K:
                    continue
            elif tri.orient == TriangleOrientation.TRI_NW:
                if (K - px - 1) + py >= K:
                    continue
            elif tri.orient == TriangleOrientation.TRI_SE:
                if px + (K - py - 1) >= K:
                    continue
            else:  # TRI_SW
                if (K - px - 1) + (K - py - 1) >= K:
                    continue

            idx = (base_y + py) * bytes_per_line + (base_x + px) * 4

            if idx < 0:
                continue

            img[idx + 0] = r
            img[idx + 1] = g
            img[idx + 2] = b
            img[idx + 3] = a
