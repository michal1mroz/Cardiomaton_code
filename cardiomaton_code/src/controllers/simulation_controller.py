from typing import Tuple, Dict
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

    def update_automaton(self, ix: int) -> None:
        """
        Updates the automaton by setting the state to that from the index ix in the recorders buffer.
        Also modifies the recorder to remove newer entries.

        Args:
            ix (int): index of the selected frame.
        """
        frame = self.recorder.get_frame(ix)
        self.service.recreate_from_frame(frame)
        self.recorder.drop_newer(ix)

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
