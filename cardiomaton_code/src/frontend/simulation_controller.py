from typing import Dict, List, Tuple

from src.models.cell import CellDict
from src.utils.data_reader import load_to_binary_array, extract_conduction_pixels
from src.models.cellular_graph import Space
from src.models.automaton import Automaton
from src.frontend.frame_recorder import FrameRecorder


class SimulationController:
    """
    Manages the cellular automaton simulation and exposes control over timing and frame updates.
    """
    def __init__(self, frame_time: float):
        """
        Initialize the simulation controller.

        Args:
            frame_time (float): Time between frames in seconds.
        """
        # graph, av_pos = load_to_binary_array()
        graph, A, B = extract_conduction_pixels()
        space = Space(graph)
        # _, cell_map = space.capped_neighbours_graph(graph, cap=8)
        _, cell_map = space.capped_neighbours_graph_from_regions(A,B,cap = 8)

        self.automaton = Automaton(graph, cell_map, frame_time=frame_time)
        self.recorder = FrameRecorder(capacity = 200)

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

    # def step(self) -> "np.ndarray[int]":
    #     """
    #     Advances the simulation by one frame.
    #
    #     Returns:
    #         np.ndarray[int]: Grid state as a 2D NumPy integer array.
    #     """
    #     self.automaton.frame_counter += 1
    #     self.automaton.update_grid()
    #     return self.automaton._to_numpy().astype(int)

    def update_automaton(self, ix) -> None:
        """
        Updates the automaton by setting the state to that from the index ix in the recorders buffer.
        Also modifies the recorder to remove newer entries.

        Args:
            ix (int): index of the selected frame.
        """
        frame = self.recorder.get_frame(ix)
        self.automaton.recreate_from_dict(frame)
        self.recorder.drop_newer(ix)

    def update_cell(self, updated_data: CellDict) -> None:
        """
        Updates a single cell of the automaton with the data from the cell inspector.

        Args
            updated_data (CellDict): A new data for the specific cell.
        """
        self.automaton.update_cell_from_dict(updated_data)        

    def step(self) -> Tuple[int, Dict[Tuple[int, int], CellDict]]:
        """
        Alternative step method. Advances the simulation by one frame.
        Returns:
            Tuple[int, Dict[Tuple[int, int], CellDict]]: First value is a frame number, the dict is a
            mapping of the cell position to the cell state
        """
        self.automaton.update_grid()
        return self.automaton.to_cell_data()