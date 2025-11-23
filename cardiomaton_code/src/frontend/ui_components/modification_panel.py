from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel, QCheckBox


class ModificationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        self.commit_button = QPushButton("Commit")
        self.undo_button = QPushButton("Undo")

        brush_layout = QHBoxLayout()
        self.brush_slider = QSlider(Qt.Orientation.Horizontal)
        self.brush_slider.setRange(1, 8)
        self.brush_slider.setFixedWidth(100)
        self.brush_value_label = QLabel("1")

        self.brush_slider.valueChanged.connect(lambda v: self.brush_value_label.setText(str(v)))

        brush_layout.addWidget(self.brush_slider)
        brush_layout.addWidget(self.brush_value_label)

        self.necrosis_switch = QCheckBox("Necrosis")

        layout.addWidget(self.commit_button)
        layout.addWidget(self.undo_button)
        layout.addLayout(brush_layout)
        layout.addWidget(self.necrosis_switch)