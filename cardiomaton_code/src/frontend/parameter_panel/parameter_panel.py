from typing import Optional, Dict

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6 import QtGui

from src.frontend.parameter_panel.parameter_definition import ParameterDefinition, CELL_PARAMETER_DEFINITIONS, \
    CELL_PARAMETER_LABELS
from src.frontend.parameter_panel.parameter_slider import ParameterSlider


class ParameterPanel(QtWidgets.QWidget):

    sigParametersChanged = pyqtSignal(str)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None,
                 definitions: Optional[Dict[str, Dict[str, ParameterDefinition]]] = None) -> None:
        super().__init__(parent)

        self._definitions: Dict[str, Dict[str, ParameterDefinition]] = (
            definitions if definitions is not None else CELL_PARAMETER_DEFINITIONS
        )

        self._sliders: Dict[str, Dict[str, ParameterSlider]] = {}
        self._constraint_labels: Dict[str, Dict[str, QtWidgets.QLabel]] = {}

        main_layout = QtWidgets.QVBoxLayout(self)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)

        container = QtWidgets.QWidget()
        container.setObjectName("Layout")
        scroll_layout = QtWidgets.QVBoxLayout(container)

        for cell_type, parameters in self._definitions.items():
            scroll_layout.addWidget(self._create_section_header(cell_type))

            section_widget = QtWidgets.QWidget()
            section_layout = QtWidgets.QVBoxLayout(section_widget)
            section_layout.setContentsMargins(10, 0, 10, 0)
            section_layout.setSpacing(10)

            self._sliders[cell_type] = {}
            self._constraint_labels[cell_type] = {}

            for name, definition in parameters.items():
                row = QtWidgets.QWidget()
                row_layout = QtWidgets.QVBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(5)

                label_text = CELL_PARAMETER_LABELS[cell_type][name]
                name_label = QtWidgets.QLabel(label_text)
                name_label.setObjectName("ParameterNameLabel")
                row_layout.addWidget(name_label)

                bottom_row = QtWidgets.QWidget()
                bottom_layout = QtWidgets.QHBoxLayout(bottom_row)
                bottom_layout.setContentsMargins(0, 0, 0, 0)
                bottom_layout.setSpacing(10)

                slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
                slider.setMinimumWidth(150)
                slider.setSingleStep(1)
                slider.setObjectName(f"{cell_type}_{name}")

                value_edit = QtWidgets.QLineEdit(definition.format_default_text())
                value_edit.setFixedWidth(60)
                value_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
                value_edit.setObjectName("ValueEdit")

                bottom_layout.addWidget(slider)
                bottom_layout.addWidget(value_edit)

                row_layout.addWidget(bottom_row)

                constraint_label = QtWidgets.QLabel("")
                constraint_label.setObjectName("ConstraintLabel")
                constraint_label.setStyleSheet("""
                    QLabel {
                        color: #e74c3c;
                        font-size: 10px;
                        font-style: italic;
                    }
                """)
                constraint_label.setVisible(False)
                row_layout.addWidget(constraint_label)
                self._constraint_labels[cell_type][name] = constraint_label

                section_layout.addWidget(row)

                binding = ParameterSlider(definition=definition, slider=slider, value_edit=value_edit)
                self._sliders[cell_type][name] = binding

                if name != "propagation_time":
                    binding.parameterChanged.connect(lambda ct=cell_type: self.sigParametersChanged.emit(ct))

            scroll_layout.addWidget(section_widget)

        scroll_layout.addStretch()
        self.scroll.setWidget(container)
        main_layout.addWidget(self.scroll)

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
        
        constraint_label_low = self._constraint_labels[cell_type][param_low]
        constraint_label_high = self._constraint_labels[cell_type][param_high]
        
        slider_low = binding_low.get_slider_widget()
        slider_high = binding_high.get_slider_widget()

        # Assuming that the unit uses the last 5 chars in the CELL_PARAMETER_LABELS...
        def enforce_constraint_low(value):
            if value > slider_high.value():
                constraint_label_low.setText(f"Value of '{CELL_PARAMETER_LABELS[cell_type][param_high][:-5]}' changed to {value} due to the constraints.")
                constraint_label_low.setVisible(True)
                
                QtCore.QTimer.singleShot(2000, lambda: constraint_label_low.setVisible(False)) 
                
                slider_high.blockSignals(True)
                binding_high.set_slider_value(value)
                slider_high.blockSignals(False)

                binding_high.parameterChanged.emit()
            else:
                constraint_label_low.setVisible(False)

        def enforce_constraint_high(value):
            if value < slider_low.value():
                constraint_label_high.setText(f"Value of '{CELL_PARAMETER_LABELS[cell_type][param_low][:-5]}' changed to {value} due to the constraints.")
                constraint_label_high.setVisible(True)
                
                QtCore.QTimer.singleShot(2000, lambda: constraint_label_high.setVisible(False)) 
                
                slider_low.blockSignals(True)
                binding_low.set_slider_value(value)
                slider_low.blockSignals(False)

                binding_low.parameterChanged.emit()
            else:
                constraint_label_high.setVisible(False)

        slider_low.valueChanged.connect(enforce_constraint_low)
        slider_high.valueChanged.connect(enforce_constraint_high)

    @staticmethod
    def _create_section_header(title: str) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(10)
        if title != "__GLOBAL__":
            line_left = QtWidgets.QFrame()
            line_left.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            line_left.setObjectName("ParametersLine")

            label = QtWidgets.QLabel(title)
            label.setObjectName("ParameterTitle")

            line_right = QtWidgets.QFrame()
            line_right.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            line_right.setObjectName("ParametersLine")

            layout.addWidget(line_left)
            layout.addWidget(label)
            layout.addWidget(line_right)

        return container