from collections import deque
from typing import List, Tuple

from PyQt6.QtGui import QPixmap

class FrameRecorder:
    """
    A recorder that stores the last N rendered frames as QPixmaps.
    Enables smooth playback control and frame-by-frame navigation through the simulation history.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def record(self, data: List[List[Tuple[int, bool, str, str]]]) -> None:
        """
        Store the automaton data in the buffer.
        """
        self.buffer.append(data)

    def get_frame(self, index: int) -> List[Tuple[int, bool, str, str]]:
        """
        Get a frame by buffer index (0 = oldest, -1 = newest).
        """
        return self.buffer[index]

    def __len__(self) -> int:
        return len(self.buffer)

    def get_all(self) -> List[List[Tuple[int, bool, str, str]]]:
        """
        Return a list of all stored frames in order.
        """
        return list(self.buffer)

    """
        Not working version - frame counter display

        def record(self, frame_index: int, data: List[List[Tuple[int, bool, str, str]]]) -> None:
            self.buffer.append((frame_index, data))

        def get_frame(self, index: int) -> tuple[int, List[List[Tuple[int, bool, str, str]]]]:
            return self.buffer[index]

        def get_all(self) -> list[tuple[int, List[List[Tuple[int, bool, str, str]]]]]:
            return list(self.buffer)
    """