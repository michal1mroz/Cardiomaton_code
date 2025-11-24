from PyQt6 import QtWidgets
from src.frontend.parameter_panel.parameter_definition import ParameterDefinition

class ParameterSlider:
    def __init__(self, definition: ParameterDefinition, slider: QtWidgets.QSlider,
                 value_label: QtWidgets.QLabel) -> None:
        self._definition = definition
        self._slider = slider
        self._value_label = value_label

        self._configure_slider()
        self._update_label(self._slider.value())

        self._slider.valueChanged.connect(self._on_slider_changed)

    def _configure_slider(self) -> None:
        self._slider.setRange(
            self._definition.slider_minimum(),
            self._definition.slider_maximum(),
        )
        self._slider.setValue(self._definition.slider_default())
        self._value_label.setText(self._definition.format_default_text())

    def _on_slider_changed(self, value: int) -> None:
        self._update_label(value)

    def _update_label(self, slider_value: int) -> None:
        real_value = self._definition.to_real_value(slider_value)
        self._value_label.setText(self._to_slider_value(real_value))

    def reset(self) -> None:
        self._slider.setValue(self._definition.slider_default())
        self._value_label.setText(self._definition.format_default_text())

    def current_value(self) -> float:
        return self._definition.to_real_value(self._slider.value())

    def get_slider_widget(self) -> QtWidgets.QSlider:
        return self._slider

    def _to_slider_value(self, value: float) -> str:
        if self._definition.is_time:
            return str(int(round(value * 1000.0)))
        return str(int(round(value)))