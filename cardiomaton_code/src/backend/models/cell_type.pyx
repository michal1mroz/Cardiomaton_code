from enum import Enum
import json
from typing import Any, Dict
cimport cell_type

class ConfigLoader:
    _config: Dict[str, Any] = {}

    @classmethod
    def loadConfig(cls, str filepath = "resources/data/cell_data.json"):
        """
        Load configuration from a JSON file
        """
        
        with open(filepath, "r", encoding="utf-8") as f:
            cls._config = json.load(f)
    
    @classmethod
    def getConfig(cls, str key) -> Dict[str, Any]: 
        """
        Return config dictionary for a given cell type key.
        """
        
        if key not in cls._config:
            raise KeyError(f"Cell type {key} not found in config.")
        return cls._config[key]

class CellType(str, Enum):
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

cdef dict _CELLTYPE_NAME_MAP = {
    cell_type.JUNCTION: "JUNCTION",
    cell_type.HIS_LEFT: "HIS_LEFT",
    cell_type.HIS_RIGHT: "HIS_RIGHT",
    cell_type.BACHMANN: "BACHMANN",
    cell_type.INTERNODAL_POST: "INTERNODAL_POST",
    cell_type.INTERNODAL_ANT: "INTERNODAL_ANT",
    cell_type.INTERNODAL_MID: "INTERNODAL_MID",
    cell_type.HIS_BUNDLE: "HIS_BUNDLE",
    cell_type.SA_NODE: "SA_NODE",
    cell_type.AV_NODE: "AV_NODE",
}

cpdef cell_type.CellTypeC to_cenum(object py_val):
    for k,v in _CELLTYPE_NAME_MAP.items():
        if v == py_val.value:
            return k
    raise ValueError(f"Unknown CellType: {py_val}")

cpdef object to_pyenum(cell_type.CellTypeC c_val):
    return CellType(_CELLTYPE_NAME_MAP[c_val])
