from typing import Optional, Dict

from PyQt6 import QtWidgets, QtCore

from src.frontend.parameter_panel.parameter_definition import ParameterDefinition, CELL_PARAMETER_DEFINITIONS, \
    CELL_PARAMETER_LABELS
from src.frontend.parameter_panel.parameter_slider import ParameterSlider


class ParameterPanel(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None,
                 definitions: Optional[Dict[str, Dict[str, ParameterDefinition]]] = None) -> None:
        super().__init__(parent)

        self._definitions: Dict[str, Dict[str, ParameterDefinition]] = (
            definitions if definitions is not None else CELL_PARAMETER_DEFINITIONS
        )

        self._sliders: Dict[str, Dict[str, ParameterSlider]] = {}

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setObjectName("Layout")

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)

        container = QtWidgets.QWidget()
        container.setObjectName("Layout")
        scroll_layout = QtWidgets.QVBoxLayout(container)

        for cell_type, parameters in self._definitions.items():
            scroll_layout.addWidget(self._create_section_header(cell_type))

            section_widget = QtWidgets.QWidget()
            section_widget.setObjectName("Layout")
            section_layout = QtWidgets.QVBoxLayout(section_widget)
            section_layout.setContentsMargins(10, 0, 10, 0)
            section_layout.setSpacing(10)

            self._sliders[cell_type] = {}

            for name, definition in parameters.items():
                row = QtWidgets.QWidget()
                row_layout = QtWidgets.QVBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(5)

                name_label = QtWidgets.QLabel(name)
                row_layout.addWidget(name_label)

                slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
                slider.setMinimumWidth(150)
                slider.setSingleStep(1)
                slider.setObjectName(f"{cell_type}_{name}")

                label_text = CELL_PARAMETER_LABELS[cell_type][name]
                value_label = QtWidgets.QLabel(f"{label_text}:")
                value_label.setObjectName("ParameterValueLabel")

                row_layout.addWidget(slider)
                row_layout.addWidget(value_label)
                section_layout.addWidget(row)

                binding = ParameterSlider(definition=definition, slider=slider, value_label=value_label)
                self._sliders[cell_type][name] = binding

            scroll_layout.addWidget(section_widget)

        scroll_layout.addStretch()
        scroll_layout.setObjectName("Layout")
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self._link_parameters("PACEMAKER", "V_rest", "V_thresh")
        self._link_parameters("ATRIAL", "V12", "V_peak")
        self._link_parameters("PURKINJE", "V_rest", "V40")
        self._link_parameters("PURKINJE", "V12", "V_peak")
        self._link_parameters("PURKINJE", "V23", "V12")

    def get_current_values(self, cell_type: str | None = None) -> dict:
        if cell_type is not None:
            return {
                name: slider.current_value()
                for name, slider in self._sliders[cell_type].items()
            }

        result: Dict[str, Dict[str, float]] = {}
        for type_name, sliders in self._sliders.items():
            result[type_name] = {
                name: slider.current_value()
                for name, slider in sliders.items()
            }
        return result

    def reset_all_sliders(self) -> None:
        for sliders in self._sliders.values():
            for slider in sliders.values():
                slider.reset()

    def _link_parameters(self, cell_type: str, param_low: str, param_high: str) -> None:
        binding_low = self._sliders[cell_type][param_low]
        binding_high = self._sliders[cell_type][param_high]

        slider_low = binding_low.get_slider_widget()
        slider_high = binding_high.get_slider_widget()

        def enforce_constraint_low(value):
            if value > slider_high.value():
                slider_high.blockSignals(True)
                slider_high.setValue(value)
                slider_high.blockSignals(False)
                binding_high.update_label(value)

        def enforce_constraint_high(value):
            if value < slider_low.value():
                slider_low.blockSignals(True)
                slider_low.setValue(value)
                slider_low.blockSignals(False)
                binding_low.update_label(value)

        slider_low.valueChanged.connect(enforce_constraint_low)
        slider_high.valueChanged.connect(enforce_constraint_high)

    def _create_section_header(self, title: str) -> QtWidgets.QWidget:
        line_left = QtWidgets.QFrame()
        line_left.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line_left.setObjectName("ParametersLine")

        label = QtWidgets.QLabel(title)
        label.setObjectName("ParameterTitle")

        line_right = QtWidgets.QFrame()
        line_right.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line_right.setObjectName("ParametersLine")

        container = QtWidgets.QWidget()
        container.setObjectName("Layout")
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(10)
        layout.addWidget(line_left)
        layout.addWidget(label)
        layout.addWidget(line_right)

        return container