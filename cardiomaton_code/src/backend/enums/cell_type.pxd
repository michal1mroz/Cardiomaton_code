cdef enum CellTypeC:
    JUNCTION = 0
    HIS_LEFT = 1
    HIS_RIGHT = 2
    BACHMANN = 3
    INTERNODAL_POST = 4
    INTERNODAL_ANT = 5
    INTERNODAL_MID = 6
    HIS_BUNDLE = 7
    SA_NODE = 8
    AV_NODE = 9

cpdef CellTypeC type_to_cenum(object)
cpdef object type_to_pyenum(CellTypeC)