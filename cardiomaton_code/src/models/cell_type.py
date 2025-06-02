from enum import Enum
from typing import Tuple

from src.models.cell import Cell
from src.models.cell_state import CellState


class CellType(Enum):
    JUNCTION = {
        "durations": {
            CellState.DEPOLARIZATION: 1,
            CellState.ABS_REFRACTION: 51,
            CellState.REFRACTION: 10,
        },
        "self_polarization": False
    }
    HIS_LEFT = {
        "durations": {
            CellState.DEPOLARIZATION: 1,
            CellState.ABS_REFRACTION: 52,
            CellState.REFRACTION: 10,
        },
        "self_polarization": False
    }
    HIS_RIGHT = {
            "durations": {
                CellState.DEPOLARIZATION: 1,
                CellState.ABS_REFRACTION: 53,
                CellState.REFRACTION: 10,
            },
            "self_polarization": False
        }
    BACHMANN = {
        "durations": {
            CellState.DEPOLARIZATION: 1,
            CellState.ABS_REFRACTION: 54,
            CellState.REFRACTION: 10,
        },
        "self_polarization": False
    }
    INTERNODAL_POST = {
        "durations": {
            CellState.DEPOLARIZATION: 1,
            CellState.ABS_REFRACTION: 55,
            CellState.REFRACTION: 10,
        },
            "self_polarization": False
    }
    INTERNODAL_ANT = {
        "durations": {
            CellState.DEPOLARIZATION: 1,
            CellState.ABS_REFRACTION: 56,
            CellState.REFRACTION: 10,
        },
            "self_polarization": False
    }
    INTERNODAL_MID = {
        "durations": {
            CellState.DEPOLARIZATION: 1,
            CellState.ABS_REFRACTION: 57,
            CellState.REFRACTION: 10,
        },
            "self_polarization": False

    }
    HIS_BUNDLE = {
        "durations": {
            CellState.DEPOLARIZATION: 1,
            CellState.ABS_REFRACTION: 58,
            CellState.REFRACTION: 10,
        },
            "self_polarization": False
    }
    SA_NODE = {
        "durations": {
            CellState.DEPOLARIZATION: 1,
            CellState.ABS_REFRACTION: 59,
            CellState.REFRACTION: 10,
        },
            "self_polarization": True
    }
    AV_NODE = {
        "durations": {
            CellState.DEPOLARIZATION: 1,
            CellState.ABS_REFRACTION: 49,
            CellState.REFRACTION: 10,
        },
            "self_polarization": False
    }

    @staticmethod
    def create(position: Tuple[int, int], cell_type, state : CellState = CellState.POLARIZATION ) -> Cell:
        config = cell_type.value
        return Cell(
            position=position,
            cell_type=cell_type,
            durations = config["durations"],
            init_state=state,
            self_polarization=config["self_polarization"]
        )