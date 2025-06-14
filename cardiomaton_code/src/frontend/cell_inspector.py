from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit

from cardiomaton_code.src.frontend.simulation_controller import SimulationController
from cardiomaton_code.src.models.cell import CellDict

class CellInspector(QWidget):
    """
    CellInspector is a class that defines the widget that opens next
    to the main window. It prints the values inside and allows for the modification
    of the values.
    """
    def __init__(self, cell_data: CellDict, on_close_callback, running: bool, ctrl: SimulationController, parent = None):
        super().__init__(parent)
        self.keys = ["charge", "auto_polarization"]
        self.ctrl = ctrl
        self.position = cell_data["position"]
        self.running = running
        self.on_close_callback = on_close_callback
        self.data =cell_data.copy()

        self.edit_fields = {}
        self.labels = {}
        self.key_labels = {}
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.__init_ui()

    def __init_ui(self):
        self._clear_layout()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_inspector)
        self.layout.addWidget(self.close_button)
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self._submit_data)
        self.layout.addWidget(self.submit_button)

        self.setLayout(self.layout)

        for key in self.keys:
            value = self.data[key]
            
            h_layout = QHBoxLayout()

            key_label = QLabel(f"{key}:", self)
            key_label.setFixedWidth(80)
            self.key_labels[key] = key_label
            h_layout.addWidget(key_label)

            if self.running:
                value_label = QLabel(str(value), self)
                self.labels[key] = value_label
                h_layout.addWidget(value_label)
            else:
                edit = QLineEdit(str(value), self)
                self.edit_fields[key] = edit
                h_layout.addWidget(edit)

            self.layout.addLayout(h_layout)
        if not self.running:
            self.layout.addWidget(self.submit_button)
            self.submit_button.setEnabled(True)

    def update(self, cell_data: CellDict) -> None:
        self.data = cell_data.copy()
        for key in self.keys:
            value = self.data[key]
            if self.running:
                if key in self.labels:
                    self.labels[key].setText(str(value))
            else:
                if key in self.edit_fields:
                    self.edit_fields[key].setText(str(value))

    def set_running(self, running: bool):
        if self.running != running:
            self.running = running
            self.__init_ui()

    def _clear_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout:
                    while child_layout.count():
                        subitem = child_layout.takeAt(0)
                        subwidget = subitem.widget()
                        if subwidget:
                            subwidget.deleteLater()

    def _submit_data(self):
        ...
        """
        updated_data = self.data.copy()
        print("old", self.data)
        for key, field in self.edit_fields.items():
            expected_type = type(updated_data[key])
            try:
                updated_data[key] = expected_type(field.text())
            except Exception as e:
                print(f"Error when casting value for {key}: {e}")
                return

        updated_data["auto_polarization"] = False
        print("new", updated_data)
        self.ctrl.update_cell(updated_data)
        """
        
    def close_inspector(self):
        """ Call to method in MainWindow to kill the inspector"""
        if self.on_close_callback:
            self.on_close_callback()
