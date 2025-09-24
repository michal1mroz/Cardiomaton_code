from collections import deque
from typing import List, Tuple, Dict

from src.models.cell import CellDict


class FrameRecorder:
    """
    A recorder that stores the last N rendered frames as QPixmaps.
    Enables smooth playback control and frame-by-frame navigation through the simulation history.
    """

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def record(self, data: Tuple[int, Dict[Tuple[int, int], CellDict]]) -> None:
        """
        Store the automaton data in the buffer.
        """
        self.buffer.append(data)

    def get_frame(self, index: int) -> Tuple[int, Dict[Tuple[int, int], CellDict]]:
        """
        Get a frame by buffer index (0 = oldest, -1 = newest).
        """
        return self.buffer[index]

    def __len__(self) -> int:
        return len(self.buffer)

    def get_all(self) -> List[Tuple[int, Dict[Tuple[int, int], CellDict]]]:
        """
        Return a list of all stored frames in order.
        """
        return list(self.buffer)

    def drop_newer(self, idx: int) -> None:
        """
        Slices and removes all the entries newer then the specified index. Changes buffer in place.

        Args:
            idx (int): selected index.
        """
        self.buffer = deque(list(self.buffer)[: idx + 1], maxlen=self.buffer.maxlen)

    def get_buffer_size(self) -> int:
        return len(self.buffer)
