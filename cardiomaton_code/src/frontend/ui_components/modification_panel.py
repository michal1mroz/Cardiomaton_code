from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel, QCheckBox


class ModificationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 0, 0)
        layout.setSpacing(15)
        layout.setObjectName("Layout")

        self.commit_button = QPushButton("Commit")
        self.commit_button.setObjectName("BlueBtn")
        self.undo_button = QPushButton("Undo")
        self.undo_button.setObjectName("UndoBtn")

        self.brush_container = QWidget()
        self.brush_container.setObjectName("brushContainer")
        self.brush_layout = QHBoxLayout()
        self.brush_slider = QSlider(Qt.Orientation.Horizontal)
        self.brush_slider.setRange(1, 8)
        self.brush_slider.setFixedWidth(100)
        self.brush_value_label = QLabel("1")
        self.brush_value_label.setObjectName("BrushSliderLabel")

        self.brush_slider.valueChanged.connect(lambda v: self.brush_value_label.setText(str(v)))

        self.brush_layout.addWidget(self.brush_slider)
        self.brush_layout.addWidget(self.brush_value_label)
        self.brush_container.setLayout(self.brush_layout)
        self.brush_layout.setObjectName("Layout")

        self.necrosis_switch = QCheckBox("Necrosis")
        self.necrosis_switch.setObjectName("NecrosisSwitch")

        layout.addWidget(self.commit_button)
        layout.addWidget(self.undo_button)
        layout.addWidget(self.brush_container)
        layout.addWidget(self.necrosis_switch)
        layout.addStretch()