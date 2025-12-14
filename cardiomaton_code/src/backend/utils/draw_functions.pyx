from libc.stdint cimport uint8_t

from src.backend.enums.cell_state cimport CellStateC
from src.backend.structs.c_cell cimport CCell

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


cdef void draw_from_state(unsigned char* img, int bytes_per_line, CCell* cell):
    """
        Helper function that uses color mapping for states to mark the
        corresponding cells on the image.

        Args:
            img unsigned char*: pointer to the image buffer
            bytes_per_line int: number of bytes in on image line
            cell CCell*: pointer to the drawn cell struct
    """
    cdef int x = cell.pos_x
    cdef int y = cell.pos_y
    cdef int st = <int>cell.c_state
    cdef unsigned char* pixel

    pixel = img + x * bytes_per_line + y * 4

    pixel[0] = COLOR_TABLE[st][0]
    pixel[1] = COLOR_TABLE[st][1]
    pixel[2] = COLOR_TABLE[st][2]
    pixel[3] = COLOR_TABLE[st][3]

cdef void draw_from_charge(unsigned char* img, int bytes_per_line, CCell* cell):
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
    hi = int(h / 60.0) % 6
    f = (h / 60.0) - int(h / 60.0)
    x = c * (1.0 - abs((f * 2.0) - 1.0))
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

    pixel = img + pos_x * bytes_per_line + pos_y * 4
    pixel[0] = <unsigned char> r
    pixel[1] = <unsigned char> g
    pixel[2] = <unsigned char> b
    pixel[3] = 255