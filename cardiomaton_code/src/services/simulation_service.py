from typing import Dict, Tuple
from src.models.cell import CellDict
from src.utils.graph_builder import extract_conduction_pixels
from src.models.cellular_graph import Space
from src.models.automaton import Automaton


class SimulationService:
    """
    Handles the core logic of the cellular automaton simulation.
    """

    def __init__(self, frame_time: float):
        """
        Initialize the simulation service.

        Args:
            frame_time (float): Time between frames in seconds.
        """
        graph, A, B = extract_conduction_pixels()
        space = Space(graph)
        _, cell_map = space.build_capped_neighbours_graph_from_regions(A, B, cap=8)

        self.automaton = Automaton(graph, cell_map, frame_time=frame_time)

    def step(self) -> Tuple[int, Dict[Tuple[int, int], CellDict]]:
        """
        Advances the simulation by one frame.
        Returns:
            Tuple[int, Dict[Tuple[int, int], CellDict]]: First value is a frame number, the dict is a
            mapping of the cell position to the cell state
        """
        self.automaton.update_grid()
        return self.automaton.to_cell_data()

    def update_cell(self, data: CellDict) -> None:
        """
        Updates a single cell of the automaton with the data from the cell inspector.

        Args
            updated_data (CellDict): A new data for the specific cell.
        """
        self.automaton.update_cell_from_dict(data)

    def recreate_from_frame(self, frame: Dict[Tuple[int, int], CellDict]) -> None:
        """
        Restores the simulation state from a given frame.

        Args
            frame (Dict[Tuple[int, int], CellDict]): Mapping of the cell position to the cell state.
        """
        self.automaton.recreate_from_dict(frame)

    @property
    def frame_time(self) -> float:
        """
        Current time between frames.

        Returns:
            float: Frame time in seconds.
        """
        return self.automaton.frame_time

    @frame_time.setter
    def frame_time(self, t: float):
        """
        Set a new frame time.

        Args:
            t (float): New frame time in seconds.
        """
        self.automaton.frame_time = t
