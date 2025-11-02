from typing import Optional, Tuple, Dict
from src.models.cell import CellDict
from src.frontend.frame_recorder import FrameRecorder
from src.services.simulation_service import SimulationService
from PyQt6.QtGui import QImage

class SimulationController:
    def __init__(self, frame_time: float, image: QImage = None):
        """
        Initialize the simulation controller.

        Args:
            frame_time (float): Time between frames in seconds.
        """
        self.service = SimulationService(frame_time, image)
        self.recorder = FrameRecorder(capacity=200)

    def step(self, if_charged: bool) -> Tuple[int, Dict[Tuple[int, int], CellDict]]:
        """
        Alternative step method. Advances the simulation by one frame.

        Returns:
           Tuple[int, Dict[Tuple[int, int], CellDict]]: First value is a frame number, the dict is a
           mapping of the cell position to the cell state
        """
        return self.service.step(if_charged)

    def update_cell(self, data: CellDict) -> None:
        """
        Updates a single cell of the automaton with the data from the cell inspector.

        Args
            updated_data (CellDict): A new data for the specific cell.
        """
        self.service.update_cell(data)

    def render_frame(self, idx, if_charged, drop_newer) -> int:
        return self.service.render_frame(idx, if_charged, drop_newer)

    @property
    def frame_time(self) -> float:
        """
        Current time between frames.

        Returns:
            float: Frame time in seconds.
        """
        return self.service.frame_time

    @frame_time.setter
    def frame_time(self, t: float):
        """
        Set a new frame time.

        Args:
            t (float): New frame time in seconds.
        """
        self.service.frame_time = t

    @property
    def shape(self) -> Tuple[int, int]:
        """ """
        return self.service.get_shape()

    def get_cell_data(self, position: Tuple[int, int]) -> Optional[Dict]:
        return self.service.get_cell_data(position)
    
    def get_buffer_size(self) -> int:
        return self.service.get_buffer_size()
    
    def set_frame_counter(self, idx: int):
        self.service.set_frame_counter(idx)