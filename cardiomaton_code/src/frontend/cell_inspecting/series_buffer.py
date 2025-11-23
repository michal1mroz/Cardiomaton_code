from collections import deque
from typing import Deque, Tuple, List

class SeriesBuffer:
    def __init__(self, maxlen: int = 500) -> None:
        self._buf: Deque[float] = deque(maxlen=maxlen)

    def add(self, value: float) -> None:
        self._buf.append(value)

    def clear(self) -> None:
        self._buf.clear()

    def xy(self) -> Tuple[List[int], List[float]]:
        y = list(self._buf)
        x = list(range(len(y)))
        return x, y
