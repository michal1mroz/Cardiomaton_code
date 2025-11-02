from src.backend.structs.cell_snapshot cimport CellSnapshot


cdef class FrameRecorder:
    cdef:
        int buff_size
        int grid_size
        int current_idx
        int count
        CellSnapshot** frames

    cdef inline int _normalize_index(self, int)

    cdef CellSnapshot* get_next_buffer(self)
    cdef CellSnapshot* get_buffer(self, int)
    cdef void remove_newer(self, int)
    cdef void remove_older(self, int)
    cdef int get_count(self)
