from PyQt6 import QtWidgets, QtCore


class ParameterPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.cell_defaults = {
            "PACEMAKER": {
                "V_rest": {"default": -65, "min": -80, "max": -40},
                "V_thresh": {"default": -40, "min": -60, "max": -20},
                "V_peak": {"default": 10, "min": -10, "max": 40},
                "t40": {"default": 0.100, "min": 0.050, "max": 0.400},
                "t03": {"default": 0.010, "min": 0.002, "max": 0.020},
                "t34": {"default": 0.200, "min": 0.050, "max": 0.300},
            },
            "ATRIAL": {
                "V_rest": {"default": -75.0, "min": -90.0, "max": -45.0},
                "V_peak": {"default": 20.0, "min": -10.0, "max": 50.0},
                "V12": {"default": 10, "min": -20.0, "max": 30.0},
                "V23": {"default": -40.0, "min": -70.0, "max": -10.0},
                "t01": {"default": 0.001, "min": 0.001, "max": 0.004},
                "t12": {"default": 0.008, "min": 0.001, "max": 0.020},
                "t23": {"default": 0.100, "min": 0.020, "max": 0.180},
                "t34": {"default": 0.080, "min": 0.010, "max": 0.140},
                # "t40": {"default": 0.268, "min": 0.188, "max": 0.348},
            },
            "PURKINJE": {
                "V_rest": {"default": -90.0, "min": -100.0, "max": -70.0},
                "V40": {"default": -75.0, "min": -85.0, "max": -60.0},
                "V_peak": {"default": 30.0, "min": 0.0, "max": 50.0},
                "V12": {"default": 5.0, "min": -30.0, "max": 20.0},
                "V23": {"default": -20.0, "min": -50.0, "max": 0.0},
                "t01": {"default": 0.002, "min": 0.001, "max": 0.010},
                "t12": {"default": 0.007, "min": 0.002, "max": 0.020},
                "t23": {"default": 0.200, "min": 0.050, "max": 0.400},
                "t34": {"default": 0.100, "min": 0.030, "max": 0.250},
                "t40": {"default": 0.200, "min": 0.080, "max": 0.600},
            },
        }

        self.param_labels = {
            "PACEMAKER": {
                "V_rest": "Maximum Diastolic Potential (mV)",
                "V_thresh": "Threshold Potential (mv)",
                "V_peak": "Peak Membrane Potential (mV)",
                "t40": "Slow Depolarization Duration (ms)",
                "t03": "Rapid Depolarization Duration (ms)",
                "t34": "Repolarizarion Duration (ms)",
            },
            "ATRIAL": {
                "V_rest": "Resting Membrane Potential (mV)",
                "V_peak": "Peak Membrane Potential (mv)",
                "V12": "Plateau Potential (mv)",
                "V23": "Late Repolarization Potential (mV)",
                "t01": "Rapid Depolarization Duration (ms)",
                "t12": "Early Rapid Repolarization Duration (ms)",
                "t23": "Plateau Duration (ms)",
                "t34": "Final Repolarizarion Duration (ms)",
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
                "t34": "Final Repolarizarion Duration (ms)",
                "t40": "Slow Depolarization Duration (ms)",
            },
        }

        main_layout = QtWidgets.QVBoxLayout(self)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        container = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(container)

        self.parameter_sliders = {}
        for cell_type, params in self.cell_defaults.items():
            scroll_layout.addWidget(self._create_section_header(cell_type))

            section_widget = QtWidgets.QWidget()
            section_layout = QtWidgets.QVBoxLayout(section_widget)
            section_layout.setContentsMargins(10, 0, 10, 0)
            section_layout.setSpacing(10)

            self.parameter_sliders[cell_type] = {}

            for name, data in params.items():
                default = data["default"]
                min_val = data["min"]
                max_val = data["max"]

                row = QtWidgets.QWidget()
                row_layout = QtWidgets.QVBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(5)

                label = QtWidgets.QLabel(f"{self.param_labels[cell_type][name]}:")
                label.setStyleSheet("color: black; font-family: 'Mulish'; font-size: 13px;")
                row_layout.addWidget(label)

                bottom_row = QtWidgets.QWidget()
                bottom_layout = QtWidgets.QHBoxLayout(bottom_row)
                bottom_layout.setContentsMargins(0, 0, 0, 0)
                bottom_layout.setSpacing(10)

                slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
                slider.setStyleSheet("""
                    QSlider::groove:horizontal {
                        border: 1px solid #DBE3F1;
                        height: 4px;
                        border-radius: 2px;
                        background: #DBE3F1;
                    }
                    QSlider::handle:horizontal {
                        border: 1px solid #6D98F4;
                        width: 10px;
                        margin: -3px 0;
                        border-radius: 5px;
                        background: #6D98F4;
                    }
                    QSlider::sub-page:horizontal {
                        background: #6D98F4;
                        border-radius: 2px;
                    }
                """)
                slider.setMinimumWidth(150)
                slider.setSingleStep(1)
                slider.setObjectName(f"{cell_type}_{name}")

                if abs(default) > 1:
                    slider.setRange(int(min_val), int(max_val))
                    slider.setValue(int(default))
                    label_text = str(int(default))
                else:
                    slider.setRange(int(min_val * 1000), int(max_val * 1000))
                    slider.setValue(int(default * 1000))
                    label_text = str(int(default * 1000))

                value_label = QtWidgets.QLabel(label_text)
                value_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
                value_label.setFixedWidth(60)
                value_label.setStyleSheet("color: black; font-family: 'Mulish'; font-size: 13px;")

                bottom_layout.addWidget(slider)
                bottom_layout.addWidget(value_label)
                row_layout.addWidget(bottom_row)

                section_layout.addWidget(row)

                self.parameter_sliders[cell_type][name] = (slider, value_label)

                slider.valueChanged.connect(lambda val, c=cell_type, n=name: self._update_label(c, n, val))

            scroll_layout.addWidget(section_widget)

        scroll_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        self._link_parameters("PACEMAKER", "V_rest", "V_thresh")
        self._link_parameters("ATRIAL", "V12", "V_peak")
        self._link_parameters("PURKINJE", "V_rest", "V40")
        self._link_parameters("PURKINJE", "V12", "V_peak")
        self._link_parameters("PURKINJE", "V23", "V12")


    def get_current_values(self, cell_type: str | None = None) -> dict:
        result = {}

        def _extract_for_type(c_type):
            sub = {}
            for name, (slider, _) in self.parameter_sliders[c_type].items():
                default = self.cell_defaults[c_type][name]["default"]
                value = slider.value() / 1000.0 if abs(default) < 1 else slider.value()
                sub[name] = value
            return sub

        if cell_type is not None:
            return _extract_for_type(cell_type)

        for c_type in self.parameter_sliders.keys():
            result[c_type] = _extract_for_type(c_type)

        return result

    def reset_all_sliders(self):
        for cell_type, params in self.cell_defaults.items():
            for name, data in params.items():
                default = data["default"]
                slider, value_label = self.parameter_sliders[cell_type][name]

                if abs(default) < 1:
                    slider.setValue(int(default * 1000))
                    value_label.setText(f"{default:.3f}")
                else:
                    slider.setValue(int(default))
                    value_label.setText(str(default))

    def _update_label(self, cell_type, param_name, value):
        _, label = self.parameter_sliders[cell_type][param_name]
        default = self.cell_defaults[cell_type][param_name]["default"]

        if abs(default) < 1:
            real_value = value / 1000.0
            label.setText(f"{real_value:.3f}")
        else:
            real_value = value
            label.setText(str(real_value))

    def _create_section_header(self, title):
        line_left = QtWidgets.QFrame()
        line_left.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line_left.setStyleSheet("background-color: #2e2e2e; max-height: 1px;")

        label = QtWidgets.QLabel(f"{title}")
        label.setStyleSheet("""
            color: #6D98F4;
            font-family: 'Mulish ExtraBold';
            font-size: 14px;
        """)

        line_right = QtWidgets.QFrame()
        line_right.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line_right.setStyleSheet("background-color: #2e2e2e; max-height: 1px;")

        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(10)
        layout.addWidget(line_left)
        layout.addWidget(label)
        layout.addWidget(line_right)

        return container

    def _link_parameters(self, cell_type, param_low, param_high):
            """
            A helper function to establish dependencies between some sliders.
            """
            slider_low = self.parameter_sliders[cell_type][param_low][0]
            slider_high = self.parameter_sliders[cell_type][param_high][0]

            def enforce_constraint_low(value):
                if value > slider_high.value():
                    slider_high.blockSignals(True)
                    slider_high.setValue(value)
                    slider_high.blockSignals(False)
                    self._update_label(cell_type, param_high, value)
            
            def enforce_constraint_high(value):
                if value < slider_low.value():
                    slider_low.blockSignals(True)
                    slider_low.setValue(value)
                    slider_low.blockSignals(False)
                    self._update_label(cell_type, param_low, value)

            slider_low.valueChanged.connect(enforce_constraint_low)
            slider_high.valueChanged.connect(enforce_constraint_high)
