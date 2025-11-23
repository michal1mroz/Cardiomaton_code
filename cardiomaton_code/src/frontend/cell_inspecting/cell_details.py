from typing import Iterable, Optional, Dict
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout
from src.models.cell import CellDict

class CellDetails(QWidget):
    def __init__(self, editable_keys: Iterable[str] = (), parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._editable_keys = set(editable_keys)
        self._running: bool = False
        self._data: CellDict = {}

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        self._labels: Dict[str, QLabel] = {}
        self._edit_fields: Dict[str, QLineEdit] = {}
        self._key_labels: Dict[str, QLabel] = {}

    @property
    def data(self) -> CellDict:
        return self._data

    def set_running(self, running: bool) -> None:
        if self._running != running:
            self._running = running
            self._rebuild()

    def set_data(self, cell_data: CellDict) -> None:
        self._data = cell_data.copy()

        if not self._labels and not self._edit_fields:
            self._rebuild()
            return

        for key, value in self._data.items():
            if self._running and key in self._labels:
                self._labels[key].setText(str(value))
            elif not self._running and key in self._edit_fields:
                self._edit_fields[key].setText(str(value))

    def edited_values(self) -> Dict[str, str]:
        return {key: field.text() for key, field in self._edit_fields.items()}

    def _clear_layout(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    while child_layout.count():
                        subitem = child_layout.takeAt(0)
                        subwidget = subitem.widget()
                        if subwidget:
                            subwidget.deleteLater()

    def _rebuild(self) -> None:
        self._clear_layout()
        self._labels.clear()
        self._edit_fields.clear()
        self._key_labels.clear()

        for key, value in self._data.items():
            h = QHBoxLayout()

            key_label = QLabel(f"{key.replace('_', ' ').title()}:", self)
            key_label.setFixedWidth(135)
            self._key_labels[key] = key_label
            h.addWidget(key_label)

            is_editable = key in self._editable_keys and not self._running

            if is_editable:
                edit = QLineEdit(str(value), self)
                self._edit_fields[key] = edit
                h.addWidget(edit)
            else:
                value_label = QLabel(str(value), self)
                self._labels[key] = value_label
                h.addWidget(value_label)

            self._layout.addLayout(h)