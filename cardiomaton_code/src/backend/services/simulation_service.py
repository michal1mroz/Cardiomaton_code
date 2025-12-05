from typing import Dict, Optional, Tuple
from src.models.cell import CellDict
from src.utils.graph_builder import extract_conduction_pixels
from src.models.cellular_graph import Space
from src.backend.models.automaton import Automaton
from src.backend.enums.cell_state import CellState
from PyQt6.QtGui import QImage

from src.database.db import init_db, SessionLocal
from src.database.crud.automaton_crud import get_automaton, create_or_overwrite_entry
from src.database.dto.automaton_dto import AutomatonDto

class SimulationService:
    """
    Handles the core logic of the cellular automaton simulation.
    """

    def __init__(self, frame_time: float, image: QImage):
        """
        Initialize the simulation service.

        Args:
            frame_time (float): Time between frames in seconds.
        """
        # graph, A, B = extract_conduction_pixels()
        # space = Space(graph)
        # _, cell_map = space.build_capped_neighbours_graph_from_regions(A, B, cap=8)
        self.ft = frame_time
        self.image = image
        ptr = image.bits()
        if hasattr(ptr, "setsize"):
            ptr.setsize(image.bytesPerLine() * image.height())
        init_db()
        db = SessionLocal()
        self.current_automaton_preset = "PHYSIOLOGICAL"
        dto = get_automaton(db, "PHYSIOLOGICAL")


        self.automaton = Automaton(dto.shape, dto.cell_map, img_ptr = int(ptr), img_bytes=image.bytesPerLine(), frame=dto.frame, frame_time=self.ft)
        # self.automaton = Automaton(graph.shape, cell_map, int(ptr), image.bytesPerLine(), frame_time=self.frame_time)

    def update_automaton(self, automaton: AutomatonDto, image: QImage):
        ptr = image.bits()
        if hasattr(ptr, "setsize"):
            ptr.setsize(image.bytesPerLine() * image.height())
        self.automaton = Automaton(automaton.shape, automaton.cell_map, img_ptr=int(ptr), img_bytes=image.bytesPerLine(), frame=automaton.frame)
        self.current_automaton_preset = automaton.name

    def save_automaton(self, entry: str) -> bool:
        automaton = self.automaton.serialize_automaton()
        shape = self.automaton.get_shape()
        frame = self.automaton.get_frame_counter()

        try:
            db = SessionLocal()
            res = create_or_overwrite_entry(db, entry, automaton.values(), shape[0], shape[1], frame)
            return True
        except Exception as e:
            print(f"Failed to save the entry: {e}")
            return False


    def step(self, if_charged: bool) -> int:#Tuple[int, Dict[Tuple[int, int], CellDict]]:
        """
        Advances the simulation by one frame.
        Returns:
            Tuple[int, Dict[Tuple[int, int], CellDict]]: First value is a frame number, the dict is a
            mapping of the cell position to the cell state
        """
        self.automaton.update_grid(if_charged)
        return self.automaton.to_cell_data()

    def update_cell(self, data: CellDict) -> None:
        """
        Updates a single cell of the automaton with the data from the cell inspector.

        Args
            updated_data (CellDict): A new data for the specific cell.
        """
        ... 
        #self.automaton.update_cell_from_dict(data)

    def modify_cells(self, modification):
        cells_positions = modification.cells
        if modification.depolarize: # cell depolarization
            self.automaton.modify_cell_state(cells_positions, CellState.RAPID_DEPOLARIZATION)
            return

        self.automaton.commit_current_automaton() # cell modification
        if modification.necrosis_enabled:
            self.automaton.modify_cell_state(cells_positions, CellState.NECROSIS)
        if "propagation_time" in modification.global_parameters.keys():
            self.automaton.modify_propagation_time(cells_positions, modification.global_parameters["propagation_time"])
        self.automaton.modify_charge_data(cells_positions,
                                          modification.atrial_charge_parameters,
                                          modification.pacemaker_charge_parameters,
                                          modification.purkinje_charge_parameters)
        # self.automaton.modify_cells(modification)

    def undo_modification(self):
        self.automaton.undo_modification()

    def restart_automaton(self):
        init_db()
        db = SessionLocal()

        dto = get_automaton(db, self.current_automaton_preset)

        ptr = self.image.bits()
        if hasattr(ptr, "setsize"):
            ptr.setsize(self.image.bytesPerLine() * self.image.height())

        self.automaton = Automaton(
            dto.shape,
            dto.cell_map,
            img_ptr=int(ptr),
            img_bytes=self.image.bytesPerLine(),
            frame=dto.frame,
            frame_time=self.ft
        )
    @property
    def frame_time(self) -> float:
        """
        Current time between frames.

        Returns:
            float: Frame time in seconds.
        """
        return self.automaton.get_frame_time()

    @frame_time.setter
    def frame_time(self, t: float):
        """
        Set a new frame time.

        Args:
            t (float): New frame time in seconds.
        """
        self.automaton.set_frame_time(t)

    def get_shape(self) -> Tuple[int, int]: 
        return self.automaton.get_shape()

    def get_cell_data(self, position: Tuple[int, int]) -> Optional[Dict]:
        """
        Returns the serialized cell under specified position, None if there's no cell
        """
        return self.automaton.get_cell_data(position)
    
    def get_buffer_size(self) -> int:
        return self.automaton.get_buffer_size()
    
    def render_frame(self, idx, if_charged, drop_newer) -> int:
        return self.automaton.render_frame(idx, if_charged, drop_newer)

    def set_frame_counter(self, idx: int) -> None:
        self.automaton.set_frame_counter(idx)