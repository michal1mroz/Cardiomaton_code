from src.utils.data_reader import load_to_binary_array
from src.models.cellular_graph import Space
from src.models.automaton import Automaton

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
        graph, av_pos = load_to_binary_array()
        space = Space(graph, av_pos)
        _, cell_map = space.capped_neighbours_graph(graph, cap=8)
        self.automaton = Automaton(graph, cell_map, frame_time=frame_time)

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

    def step(self) -> "np.ndarray[int]":
        """
        Advances the simulation by one frame.

        Returns:
            np.ndarray[int]: Grid state as a 2D NumPy integer array.
        """
        self.automaton.frame_counter += 1
        self.automaton.update_grid()
        return self.automaton._to_numpy().astype(int)
