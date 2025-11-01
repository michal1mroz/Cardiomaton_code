from enum import Enum
import json
from typing import Any, Dict, Tuple

from src.models.cell import Cell
from cardiomaton_code.src.backend.enums.cell_state import CellState
#from src.models.cell_state import CellState

class ConfigLoader:
    _config: Dict[str, Any] = {}

    @classmethod
    def loadConfig(cls, filepath: str = "resources/data/cell_data.json"):
        with open(filepath, "r", encoding="utf-8") as f:
            cls._config = json.load(f)
    
    @classmethod
    def getConfig(cls, key: str) -> Dict[str, Any]: 
        if key not in cls._config:
            raise KeyError(f"Cell type {key} not found in config.")
        return cls._config[key]

class CellType(Enum):
    JUNCTION = "JUNCTION" 
    HIS_LEFT = "HIS_LEFT" 
    HIS_RIGHT = "HIS_RIGHT" 
    BACHMANN = "BACHMANN" 
    INTERNODAL_POST = "INTERNODAL_POST" 
    INTERNODAL_ANT = "INTERNODAL_ANT" 
    INTERNODAL_MID = "INTERNODAL_MID" 
    HIS_BUNDLE = "HIS_BUNDLE" 
    SA_NODE = "SA_NODE" 
    AV_NODE = "AV_NODE"

    @property
    def config(self) -> Dict[str, Any]:
        return ConfigLoader.getConfig(self.value)

    @staticmethod
    def create(position: Tuple[int, int], cell_type : "CellType", state : CellState = CellState.POLARIZATION ) -> Cell:
        config = cell_type.config 
        return Cell(
            position = position,
            cell_type = cell_type,
            cell_config = config,
            init_state=state,
            self_polarization=config["self_polarization"],
        )