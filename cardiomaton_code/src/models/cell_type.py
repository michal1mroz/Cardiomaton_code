from enum import Enum
from typing import Tuple

from src.models.cell import Cell
from src.models.cell_state import CellState


class CellType(Enum):
    JUNCTION = {
        "id": 1,
        "cell_data": {
            "resting_membrane_potential": -90,
            "peak_potential": 30,
            "threshold_potential": -5,
            "duration": 60,
            "repolarization_potential_drop": 2,  # more values to be established because repolarization pace changes
            "relative_refractory_period_threshold": -60,
        },
        "self_polarization": False,
        "name": "Junction"
    }
    HIS_LEFT = {
        "id": 2,
        "cell_data": {
            "resting_membrane_potential": -90,
            "peak_potential": 30,
            "threshold_potential": -5,
            "duration": 60,
            "repolarization_potential_drop": 2,  # more values to be established because repolarization pace changes
            "relative_refractory_period_threshold": -60,
        },
        "self_polarization": False,
        "name": "Left bundle branch"
    }
    HIS_RIGHT = {
            "id": 3,
        "cell_data": {
            "resting_membrane_potential": -90,
            "peak_potential": 30,
            "threshold_potential": -5,
            "duration": 60,
            "repolarization_potential_drop": 2,  # more values to be established because repolarization pace changes
            "relative_refractory_period_threshold": -60,
        },
            "self_polarization": False,
        "name": "Right bundle branch"
        }
    BACHMANN = {
        "id": 4,
        "cell_data": {
            "resting_membrane_potential": -90,
            "peak_potential": 30,
            "threshold_potential": -5,
            "duration": 60,
            "repolarization_potential_drop": 2,  # more values to be established because repolarization pace changes
            "relative_refractory_period_threshold": -60,
        },
        "self_polarization": False,
        "name": "Bachmann\'s bundle"
    }
    INTERNODAL_POST = {
        "id": 5,
        "cell_data": {
            "resting_membrane_potential": -90,
            "peak_potential": 30,
            "threshold_potential": -5,
            "duration": 60,
            "repolarization_potential_drop": 2,  # more values to be established because repolarization pace changes
            "relative_refractory_period_threshold": -60,
        },
            "self_polarization": False,
        "name": "Posterior internodal tract"
    }
    INTERNODAL_ANT = {
        "id": 6,
        "cell_data": {
            "resting_membrane_potential": -90,
            "peak_potential": 30,
            "threshold_potential": -5,
            "duration": 60,
            "repolarization_potential_drop": 2,  # more values to be established because repolarization pace changes
            "relative_refractory_period_threshold": -60,
        },
            "self_polarization": False,
        "name": "Aterior internodal tract"
    }
    INTERNODAL_MID = {
        "id": 7,
        "cell_data": {
            "resting_membrane_potential": -90,
            "peak_potential": 30,
            "threshold_potential": -5,
            "duration": 60,
            "repolarization_potential_drop": 2,  # more values to be established because repolarization pace changes
            "relative_refractory_period_threshold": -60,
        },
            "self_polarization": False,
        "name": "Middle internodal tract"

    }
    HIS_BUNDLE = {
        "id": 8,
        "cell_data": {
            "resting_membrane_potential": -90,
            "peak_potential": 30,
            "threshold_potential": -5,
            "duration": 60,
            "repolarization_potential_drop": 2,  # more values to be established because repolarization pace changes
            "relative_refractory_period_threshold": -60,
        },
            "self_polarization": False,
        "name": "Bundle o his"
    }
    SA_NODE = {
        "id": 9,
        "cell_data": {
            "resting_membrane_potential": -60,
            "peak_potential": 20,
            "threshold_potential": -35,
            "duration": 40,
            "spontaneous_depolarization_step_slow": 0.13,
            "spontaneous_depolarization_step_fast": 27.5,
            "repolarization_potential_drop": 2,
            "relative_refractory_period_threshold": -40,
        },
            "self_polarization": True,
        "name": "Sinoartial node"
    }
    AV_NODE = {
        "id": 10,
        "cell_data": {
            "resting_membrane_potential": -90,
            "peak_potential": 30,
            "threshold_potential": -5,
            "duration": 60,
            "repolarization_potential_drop": 2,  # more values to be established because repolarization pace changes
            "relative_refractory_period_threshold": -60,
        },
            "self_polarization": False,
        "name": "Atrioventricular node"
    }

    @staticmethod
    def create(position: Tuple[int, int], cell_type : "CellType", state : CellState = CellState.POLARIZATION ) -> Cell:
        config = cell_type.value
        return Cell(
            position=position,
            cell_type=cell_type,
            cell_data = config["cell_data"],
            init_state=state,
            self_polarization=config["self_polarization"]
        )