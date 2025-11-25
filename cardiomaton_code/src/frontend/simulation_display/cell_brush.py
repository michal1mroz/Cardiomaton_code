from typing import Tuple, Optional

class CellBrush:

    def __init__(self, simulation_size: Tuple[int, int], cell_modificator, brush_size_slider) -> None:
        self._simulation_size = simulation_size
        self._cell_modificator = cell_modificator
        self._brush_size_slider = brush_size_slider

    def apply_brush(self, center: Optional[Tuple[int, int]], add: bool) -> None:
        if center is None:
            return

        radius = max(self._brush_size_slider.value() - 1, 0)
        row, col = center
        rows, cols = self._simulation_size

        for i in range(row - radius, row + radius + 1):
            for j in range(col - radius, col + radius + 1):
                if 0 <= i < rows and 0 <= j < cols:
                    if (i - row) ** 2 + (j - col) ** 2 <= radius ** 2:
                        if add:
                            self._cell_modificator.add_cell((i, j))
                        else:
                            self._cell_modificator.remove_cell((i, j))