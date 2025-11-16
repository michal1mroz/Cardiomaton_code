from PyQt6 import QtWidgets, QtCore


class ParameterPanel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.cell_defaults = {
            "PACEMAKER": {
                "V_rest": {"default": -60, "min": -78, "max": -42},
                "V_thresh": {"default": -40, "min": -52, "max": -28},
                "V_peak": {"default": 10, "min": 7, "max": 13},
                "t40": {"default": 0.12, "min": 0.084, "max": 0.156},
                "t03": {"default": 0.128, "min": 0.090, "max": 0.166},
                "t34": {"default": 0.278, "min": 0.195, "max": 0.361},
            },
            "ATRIAL": {
                "V_rest": {"default": -85.0, "min": -110.5, "max": -59.5},
                "V_peak": {"default": 20.0, "min": 14.0, "max": 26.0},
                "V12": {"default": 5.0, "min": 3.5, "max": 6.5},
                "V23": {"default": -15.0, "min": -19.5, "max": -10.5},
                "t01": {"default": 0.004, "min": 0.0028, "max": 0.0052},
                "t12": {"default": 0.008, "min": 0.0056, "max": 0.0104},
                "t23": {"default": 0.158, "min": 0.110, "max": 0.205},
                "t34": {"default": 0.238, "min": 0.167, "max": 0.309},
                # "t40": {"default": 0.268, "min": 0.188, "max": 0.348},
            },
            "PURKINJE": {
                "V_rest": {"default": -90.0, "min": -117.0, "max": -63.0},
                "V40": {"default": -75.0, "min": -97.5, "max": -52.5},
                "V_peak": {"default": 30.0, "min": 21.0, "max": 39.0},
                "V12": {"default": 0.0, "min": -0.3, "max": 0.3},
                "V23": {"default": -20.0, "min": -26.0, "max": -14.0},
                "t01": {"default": 0.002, "min": 0.0014, "max": 0.0026},
                "t12": {"default": 0.007, "min": 0.0049, "max": 0.0091},
                "t23": {"default": 0.207, "min": 0.145, "max": 0.269},
                "t34": {"default": 0.307, "min": 0.215, "max": 0.399},
                "t40": {"default": 0.507, "min": 0.355, "max": 0.659},
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
                row_layout = QtWidgets.QHBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(10)

                label = QtWidgets.QLabel(name)
                label.setFixedWidth(80)
                label.setStyleSheet("color: black; font-family: 'Mulish'; font-size: 13px;")
                row_layout.addWidget(label)

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
                else:
                    slider.setRange(int(min_val * 1000), int(max_val * 1000))
                    slider.setValue(int(default * 1000))

                value_label = QtWidgets.QLabel(str(default))
                value_label.setFixedWidth(60)
                value_label.setStyleSheet("color: black; font-family: 'Mulish'; font-size: 13px;")

                row_layout.addWidget(slider)
                row_layout.addWidget(value_label)
                section_layout.addWidget(row)

                self.parameter_sliders[cell_type][name] = (slider, value_label)

                slider.valueChanged.connect(lambda val, c=cell_type, n=name: self._update_label(c, n, val))

            scroll_layout.addWidget(section_widget)

        scroll_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

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
        slider, label = self.parameter_sliders[cell_type][param_name]
        default = self.cell_defaults[cell_type][param_name]["default"]

        if abs(default) < 1:
            real_value = value / 1000.0
        else:
            real_value = value
        label.setText(f"{real_value:.3f}")

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


