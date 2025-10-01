from enum import Enum
from typing import Dict, Any, Tuple
from src.backend.models.cell_state import CellState

class ConfigLoader:
    _config: Dict[str, Any]

    @classmethod
    def loadConfig(cls, filepath: str):
        """
        Loads json config from the provided path
        """
        ...

    @classmethod
    def getConfig(cls, key: str) -> Dict[str, Any]:
        """
        Returns config for the provided cell type key
        """
        ...

class CellType(str, Enum):
    JUNCTION: str 
    HIS_LEFT: str
    HIS_RIGHT: str 
    BACHMANN: str 
    INTERNODAL_POST: str 
    INTERNODAL_ANT: str 
    INTERNODAL_MID: str 
    HIS_BUNDLE: str 
    SA_NODE: str 
    AV_NODE: str 

    @property
    def config(self) -> Dict[str, Any]:
        """
        Returns config data for the enum type
        """
        ...

def type_to_cenum(py_val: CellType) -> int:
    """
    Returns c-like enum for the provided CellType
    """
    ...

def type_to_pyenum(c_val: int) -> CellType:
    """
    Returns python-like CellType enum form the provided c-type enum
    """
    ...