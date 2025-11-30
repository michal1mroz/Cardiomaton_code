from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Final


@dataclass(frozen=True)
class ParameterDefinition:
    default: float
    minimum: float
    maximum: float
    is_time: bool = False

    @property
    def use_thousand_scale(self) -> bool:
        return abs(self.default) < 1

    def slider_minimum(self) -> int:
        return int(self.minimum * 1000) if self.use_thousand_scale else int(self.minimum)

    def slider_maximum(self) -> int:
        return int(self.maximum * 1000) if self.use_thousand_scale else int(self.maximum)

    def slider_default(self) -> int:
        return int(self.default * 1000) if self.use_thousand_scale else int(self.default)

    def to_real_value(self, slider_value: int) -> float:
        return slider_value / 1000.0 if self.use_thousand_scale else float(slider_value)

    def format_default_text(self) -> str:
        if self.use_thousand_scale:
            return f"{self.default:.3f}"
        return str(int(self.default))


CELL_PARAMETER_DEFINITIONS: Final[Dict[str, Dict[str, ParameterDefinition]]] = {
    "__GLOBAL__": {
        "propagation_time": ParameterDefinition(default=1, minimum=1, maximum=7),
    },
    "PACEMAKER": {
        "V_rest":   ParameterDefinition(default=-65,   minimum=-80,    maximum=-40),
        "V_thresh": ParameterDefinition(default=-40,   minimum=-60,    maximum=-20),
        "V_peak":   ParameterDefinition(default=10,    minimum=-10,    maximum=40),
        "t40":      ParameterDefinition(default=0.100, minimum=0.050,  maximum=0.400, is_time=True),
        "t03":      ParameterDefinition(default=0.010, minimum=0.002,  maximum=0.020, is_time=True),
        "t34":      ParameterDefinition(default=0.200, minimum=0.050,  maximum=0.300, is_time=True),
    },
    "ATRIAL": {
        # TODO : figure out why those parameters are not working
        # "V_rest": {"default": -75.0, "min": -90.0, "max": -45.0},
        # "V_peak": {"default": 20.0, "min": -10.0, "max": 50.0},
        # "V12": {"default": 10, "min": -20.0, "max": 30.0},
        # "V23": {"default": -40.0, "min": -70.0, "max": -10.0},
        # "t01": {"default": 0.001, "min": 0.001, "max": 0.004},
        # "t12": {"default": 0.008, "min": 0.001, "max": 0.020},
        # "t23": {"default": 0.100, "min": 0.020, "max": 0.180},
        # "t34": {"default": 0.080, "min": 0.010, "max": 0.140},
        "V_rest": ParameterDefinition(default=-85.0, minimum=-110.5, maximum=-59.5),
        "V_peak": ParameterDefinition(default=20.0,  minimum=14.0,   maximum=26.0),
        "V12":    ParameterDefinition(default=5.0,   minimum=3.5,    maximum=6.5),
        "V23":    ParameterDefinition(default=-15.0, minimum=-19.5,  maximum=-10.5),
        "t01":    ParameterDefinition(default=0.004, minimum=0.0028, maximum=0.0052, is_time=True),
        "t12":    ParameterDefinition(default=0.008, minimum=0.0056, maximum=0.0104, is_time=True),
        "t23":    ParameterDefinition(default=0.158, minimum=0.110,  maximum=0.205, is_time=True),
        "t34":    ParameterDefinition(default=0.238, minimum=0.167,  maximum=0.309, is_time=True),
        # "t40": {"default": 0.268, "min": 0.188, "max": 0.348},
    },
    "PURKINJE": {
        # TODO : figure out why those parameters are not working
        # "V_rest": {"default": -90.0, "min": -100.0, "max": -70.0},
        # "V40": {"default": -75.0, "min": -85.0, "max": -60.0},
        # "V_peak": {"default": 30.0, "min": 0.0, "max": 50.0},
        # "V12": {"default": 5.0, "min": -30.0, "max": 20.0},
        # "V23": {"default": -20.0, "min": -50.0, "max": 0.0},
        # "t01": {"default": 0.002, "min": 0.001, "max": 0.010},
        # "t12": {"default": 0.007, "min": 0.002, "max": 0.020},
        # "t23": {"default": 0.200, "min": 0.050, "max": 0.400},
        # "t34": {"default": 0.100, "min": 0.030, "max": 0.250},
        # "t40": {"default": 0.200, "min": 0.080, "max": 0.600},
        "V_rest": ParameterDefinition(default=-90.0, minimum=-117.0, maximum=-63.0),
        "V40":    ParameterDefinition(default=-75.0, minimum=-97.5,  maximum=-52.5),
        "V_peak": ParameterDefinition(default=30.0,  minimum=21.0,   maximum=39.0),
        "V12":    ParameterDefinition(default=0.0,   minimum=-0.3,   maximum=0.3),
        "V23":    ParameterDefinition(default=-20.0, minimum=-26.0,  maximum=-14.0),
        "t01":    ParameterDefinition(default=0.002, minimum=0.0014, maximum=0.0026, is_time=True),
        "t12":    ParameterDefinition(default=0.007, minimum=0.0049, maximum=0.0091, is_time=True),
        "t23":    ParameterDefinition(default=0.207, minimum=0.145,  maximum=0.269, is_time=True),
        "t34":    ParameterDefinition(default=0.307, minimum=0.215,  maximum=0.399, is_time=True),
        "t40":    ParameterDefinition(default=0.507, minimum=0.355,  maximum=0.659, is_time=True),
    },
}

CELL_PARAMETER_LABELS: Final[Dict[str, Dict[str, str]]] = {
    "__GLOBAL__": {
        "propagation_time": "Signal propagation delay"
    },
    "PACEMAKER": {
        "V_rest": "Maximum Diastolic Potential (mV)",
        "V_thresh": "Threshold Potential (mV)",
        "V_peak": "Peak Membrane Potential (mV)",
        "t40": "Slow Depolarization Duration (ms)",
        "t03": "Rapid Depolarization Duration (ms)",
        "t34": "Repolarization Duration (ms)",
    },
    "ATRIAL": {
        "V_rest": "Resting Membrane Potential (mV)",
        "V_peak": "Peak Membrane Potential (mV)",
        "V12": "Plateau Potential (mV)",
        "V23": "Late Repolarization Potential (mV)",
        "t01": "Rapid Depolarization Duration (ms)",
        "t12": "Early Rapid Repolarization Duration (ms)",
        "t23": "Plateau Duration (ms)",
        "t34": "Final Repolarization Duration (ms)",
    },
    "PURKINJE": {
        "V_rest": "Maximum Diastolic Potential (mV)",
        "V40": "Threshold Potential (mV)",
        "V_peak": "Peak Membrane Potential (mV)",
        "V12": "Plateau Potential (mV)",
        "V23": "Late Repolarization Potential (mV)",
        "t01": "Rapid Depolarization Duration (ms)",
        "t12": "Early Rapid Repolarization Duration (ms)",
        "t23": "Plateau Duration (ms)",
        "t34": "Final Repolarization Duration (ms)",
        "t40": "Slow Depolarization Duration (ms)",
    },
}

