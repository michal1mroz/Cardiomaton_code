from enum import Enum
import json
from typing import Any, Dict

class ConfigLoader:
    """
    Class to load config files for the cell data
    """
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
    """
    Python implemntation of the CellType enum
    """
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
        """
        Helper method. Provides config dictionary tied to the given CellType
        """
        return ConfigLoader.getConfig(self.value)

"""
Helper dictionary for the cython-python conversion
"""
cdef dict _CELLTYPE_NAME_MAP = {
    CellTypeC.JUNCTION: "JUNCTION",
    CellTypeC.HIS_LEFT: "HIS_LEFT",
    CellTypeC.HIS_RIGHT: "HIS_RIGHT",
    CellTypeC.BACHMANN: "BACHMANN",
    CellTypeC.INTERNODAL_POST: "INTERNODAL_POST",
    CellTypeC.INTERNODAL_ANT: "INTERNODAL_ANT",
    CellTypeC.INTERNODAL_MID: "INTERNODAL_MID",
    CellTypeC.HIS_BUNDLE: "HIS_BUNDLE",
    CellTypeC.SA_NODE: "SA_NODE",
    CellTypeC.AV_NODE: "AV_NODE",
}

cpdef CellTypeC type_to_cenum(object py_val):
    """
    Converts python CellType to the cython equivalent
    """
    for k,v in _CELLTYPE_NAME_MAP.items():
        if v == py_val.value:
            return k
    raise ValueError(f"Unknown CellType: {py_val}")

cpdef object type_to_pyenum(CellTypeC c_val):
    """
    Converts cython CellTypeC to the python equivalent
    """
    return CellType(_CELLTYPE_NAME_MAP[c_val])
