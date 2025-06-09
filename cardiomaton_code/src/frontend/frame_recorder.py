from collections import deque
from PyQt6.QtGui import QPixmap

class FrameRecorder:
    """
    A recorder that stores the last N rendered frames as QPixmaps.
    Enables smooth playback control and frame-by-frame navigation through the simulation history.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def record(self, pixmap: QPixmap) -> None:
        """
        Store a copy of the given QPixmap in the buffer.
        """
        self.buffer.append(pixmap)

    def get_frame(self, index: int) -> QPixmap:
        """
        Get a frame by buffer index (0 = oldest, -1 = newest).
        """
        return self.buffer[index]

    def __len__(self) -> int:
        return len(self.buffer)

    def get_all(self) -> list[QPixmap]:
        """
        Return a list of all stored frames in order.
        """
        return list(self.buffer)