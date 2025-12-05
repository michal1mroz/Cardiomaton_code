from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject, pyqtSignal

from src.frontend.parameter_panel.parameter_definition import ParameterDefinition

class ParameterSlider(QObject):

    parameterChanged = pyqtSignal()

    def __init__(self, definition: ParameterDefinition, slider: QtWidgets.QSlider,
                 value_edit: QtWidgets.QLineEdit) -> None:
        super().__init__()
        self._definition = definition
        self._slider = slider
        self._value_edit = value_edit

        self._configure_slider()

        self._slider.valueChanged.connect(self._on_slider_changed)

        self._value_edit.editingFinished.connect(self._on_text_change)

    def _configure_slider(self) -> None:
        self._slider.setRange(
            self._definition.slider_minimum(),
            self._definition.slider_maximum(),
        )
        self._slider.setValue(self._definition.slider_default())
        self._slider.setTracking(True)

        real_default = self._definition.to_real_value(self._slider.value())
        self._value_edit.setText(self._definition.format_value(real_default))

    def _on_slider_changed(self, value: int) -> None:
        real_value = self._definition.to_real_value(value)

        self._value_edit.blockSignals(True)
        self._value_edit.setText(self._definition.format_value(real_value))
        self._value_edit.blockSignals(False)

        self.parameterChanged.emit()

    def _on_text_change(self):
        text = self._value_edit.text().strip()

        try:
            value = float(text)
        except ValueError:
            value = self._definition.minimum
        value = max(self._definition.minimum, min(self._definition.maximum, value))

        formatted = self._definition.format_value(value)
        self._value_edit.blockSignals(True)
        self._value_edit.setText(formatted)
        self._value_edit.blockSignals(False)

        slider_val = self._definition.to_slider_value(value)

        self._slider.blockSignals(True)
        self._slider.setValue(slider_val)
        self._slider.blockSignals(False)

        self.parameterChanged.emit()

    def reset(self) -> None:
        self._slider.setValue(self._definition.slider_default())
        real_value = self._definition.to_real_value(self._slider.value())
        self._value_edit.setText(self._definition.format_value(real_value))

    def current_value(self) -> float:
        return self._definition.to_real_value(self._slider.value())

    def get_slider_widget(self) -> QtWidgets.QSlider:
        return self._slider

    def _to_slider_value(self, value: float) -> str:
        if self._definition.is_time:
            return str(int(round(value * 1000.0)))
        return str(int(round(value)))