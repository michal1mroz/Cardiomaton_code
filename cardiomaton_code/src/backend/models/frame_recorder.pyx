from libc.stdlib cimport malloc, free
from cython cimport sizeof

from src.backend.structs.cell_snapshot cimport CellSnapshot


cdef class FrameRecorder:

    def __init__(self, int grid_size, int buff_size):
        cdef int i
        self.buff_size = buff_size
        self.grid_size = grid_size
        self.current_idx = -1
        self.count = 0

        # Got to find this warning, don't know what causes it
        self.frames = <CellSnapshot**> malloc(<size_t>self.buff_size * sizeof(CellSnapshot*))
        if self.frames == NULL:
            raise MemoryError("Error [FrameRecorder]: Failed to allocate buffer array")
        
        for i in range(buff_size):
            self.frames[i] = <CellSnapshot*> malloc(<size_t>self.grid_size * sizeof(CellSnapshot))
            if self.frames[i] == NULL:
                for i in range(i):
                    free(self.frames[i])
                free(self.frames)
                self.frames = NULL
                raise MemoryError(f"Error [FrameRecorder]: Failed to allocate grid {i}")

    def __dealloc__(self):
        cdef int i
        if self.frames != NULL:
            for i in range(self.buff_size):
                if self.frames[i] != NULL:
                    free(self.frames[i])
            free(self.frames)
            self.frames = NULL

    cdef inline int _normalize_index(self, int idx):
        if self.count == 0:
            return -1
        if idx < 0:
            idx = self.current_idx + idx + 1
        
        if idx < 0:
            idx += self.buff_size
        elif idx >= self.buff_size:
            idx %= self.buff_size
        
        if idx < 0 or idx >= self.count:
            return -1
        
        return idx

    cdef CellSnapshot* get_next_buffer(self):
        self.current_idx = (self.current_idx + 1) % self.buff_size
        if self.count < self.buff_size:
            self.count += 1
        return self.frames[self.current_idx]

    cdef CellSnapshot* get_buffer(self, int idx):
        idx = self._normalize_index(idx)
        if idx == -1:
            return NULL
        return self.frames[idx]

    cdef void remove_newer(self, int idx):
        idx = self._normalize_index(idx)
        if idx < 0:
            self.current_idx = -1
            self.count = 0
            return

        if self.count < self.buff_size:
            self.current_idx = idx
            self.count = idx + 1
        else:
            self.current_idx = idx

    cdef void remove_older(self, int idx):
        idx = self._normalize_index(idx)
        
        if idx == -1:
            return

        if self.count < self.buff_size:
            if idx < self.count:
                self.count -= idx
            else:
                self.count = 0
        else:
            self.count = self.buff_size - idx

    cdef int get_count(self):
        return self.count

    cdef void clear_all(self):
        self.current_idx = -1
        self.count = 0