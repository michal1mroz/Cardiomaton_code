from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QSizePolicy

from collections import deque
import pyqtgraph as pq

from src.controllers.simulation_controller import SimulationController
from src.models.cell import CellDict

class CellInspector(QWidget):
    """
    CellInspector is a class that defines the widget that opens next
    to the main window. It prints the values inside and allows for the modification
    of the values.
    """
    def __init__(self, cell_data: CellDict, on_close_callback, running: bool, ctrl: SimulationController, parent = None):
        super().__init__(parent)
        self.keys = []
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

        self.charge_buffer = deque(maxlen=500)

        font = QFont("Mulish", 12)
        self.setFont(font)

        self.__init_ui()

    def __init_ui(self):
        # clean before the update
        self._clear_layout()

        # button setup
        top_layout = QHBoxLayout()
        top_layout.addStretch()

        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.close_button.setStyleSheet("""
                QPushButton {
                    background-color: #EF8481;  
                    color: white;
                    border-radius: 15px;      
                    font-weight: bold;
                    font-family: Mulish;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #E74440;
                }
            """)
        self.close_button.clicked.connect(self.close_inspector)
        top_layout.addWidget(self.close_button)

        self.layout.addLayout(top_layout)

        button_style = """
                QPushButton {
                    font-family: Mulish ExtraBold;
                    font-weight: bold;
                    font-size: 13px;
                    background-color: #6D98F4;
                    color: white;
                    border-radius: 10px;
                    padding: 2px 2px;
                }
                QPushButton:hover {
                    background-color: #3466CF;
                }
            """
        """
        self.submit_button = QPushButton("Submit")
        self.submit_button.setStyleSheet(button_style)
        self.submit_button.clicked.connect(self._submit_data)
        self.layout.addWidget(self.submit_button)
        """

        self.dep_button = QPushButton("Depolarize")
        self.dep_button.setStyleSheet(button_style)
        self.dep_button.setFixedWidth(100)
        self.dep_button.clicked.connect(self._dep_callback)
        self.layout.addWidget(self.dep_button)
        self.layout.addSpacing(10)

        self.setLayout(self.layout)

        # state labels
        for key, value in self.data.items():
            h_layout = QHBoxLayout()

            key_label = QLabel(f"{key.replace('_', ' ').title()}:", self)
            key_label.setFixedWidth(135)
            self.key_labels[key] = key_label
            h_layout.addWidget(key_label)

            if key in self.keys and not self.running:
                edit = QLineEdit(str(value), self)
                self.edit_fields[key] = edit
                h_layout.addWidget(edit)
            else:
                value_label = QLabel(str(value), self)
                self.labels[key] = value_label
                h_layout.addWidget(value_label)

            self.layout.addLayout(h_layout)

        # Plot setup
        self.plot_widget = pq.PlotWidget()
        self.plot_curve = self.plot_widget.plot(pen=pq.mkPen(color='r', width=2))
        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle('Charge over time')
        self.plot_widget.setLabel('left', 'Charge')
        self.plot_widget.setLabel('bottom', 'Time [Frames]')
        self.plot_widget.showGrid(x=True, y=True)

        self.layout.addWidget(self.plot_widget)

        """
        if not self.running:
            self.layout.addWidget(self.submit_button)
            self.submit_button.setEnabled(True)
        """

    def update(self, cell_data: CellDict) -> None:
        """
        Update method called by the main application. If the cell inspector
        exists the main_window passes the CellDict corresponding to position of CellInspector.position.
        Using the values it updates all the widgets on the screen.

        Args
            cell_data (CellDict): New values of the given cell
        """
        self.data = cell_data.copy()

        charge = self.data.get('charge', None)
        if charge is not None:
            self.charge_buffer.append(charge)
            self._update_plot()

        for key, value in self.data.items():
            if self.running and key in self.labels:
                self.labels[key].setText(str(value))
            elif key in self.edit_fields and key in self.keys:
                self.edit_fields[key].setText(str(value))

    def set_running(self, running: bool) -> None:
        """
        Changes state of flag CellInspector.running and updates the ui

        Args:
            running (bool): value from MainWindow.running
        """
        if self.running != running:
            self.running = running
            self.__init_ui()

    def _clear_layout(self):
        """
        Simple method to clear all the widgets under CellInspector before updating it.
        """
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout:
                    while child_layout.count():
                        subitem = child_layout.takeAt(0)
                        subwidget = subitem.widget()
                        if subwidget:
                            subwidget.deleteLater()

    def _update_plot(self):
        """
        Method for updating the plot using values of charge stored in charge_buffer
        """
        y_data = list(self.charge_buffer)
        x_data = list(range(len(y_data)))
        self.plot_curve.setData(x=x_data, y=y_data)

    def _dep_callback(self):
        """
        Simple callback that depolarizes given cell.
        Will have to be reworked in the future
        """
        payload = self.data
        payload['state_value'] = 2
        self.ctrl.update_cell(payload)

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
