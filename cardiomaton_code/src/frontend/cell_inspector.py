from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit

from collections import deque
import pyqtgraph as pq

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
        
        self.__init_ui()

    def __init_ui(self):
        # clean before the update
        self._clear_layout()

        # button setup
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close_inspector)
        self.layout.addWidget(self.close_button)
        
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self._submit_data)
        #self.layout.addWidget(self.submit_button)

        self.dep_button = QPushButton("Depolarize")
        self.dep_button.clicked.connect(self._dep_callback)
        self.layout.addWidget(self.dep_button)

        self.setLayout(self.layout)

        # state labels
        for key, value in self.data.items():
            h_layout = QHBoxLayout()

            key_label = QLabel(f"{key}:", self)
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
