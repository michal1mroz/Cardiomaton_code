from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton

from src.frontend.ui_components.ui_factory import UIFactory

from src.database.db import SessionLocal
from src.database.crud.automaton_crud import list_entries

class PresetsWidget(QWidget):
    preset_selected = pyqtSignal(object)  
    # custom_preset_selected = pyqtSignal()
    preset_changed = pyqtSignal(str)  
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QHBoxLayout(self)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.label = UIFactory.create_label(self, "Select Preset", font_size=14)
        self.main_layout.addWidget(self.label)
        self.main_layout.addStretch(1)

        self.dropdown = QComboBox()
        # self.dropdown.addItem("Preset 1")
        # self.dropdown.addItem("Preset 2")
        self.dropdown.setObjectName("presetComboBox")
        self.main_layout.addWidget(self.dropdown)
        self.main_layout.addStretch(1)

        self._load_database_entries()

        self.button = UIFactory.create_pushbutton(self, font_size=15)
        self.button.setText("+")
        self.main_layout.addWidget(self.button)
        self.button.setObjectName("presetBtn")

        self.main_layout.setContentsMargins(30, 5, 30, 5)

        self._init_connections()
        self.current_entry = None

        self.setLayout(self.main_layout)

    def _init_connections(self):
        self.dropdown.currentTextChanged.connect(self.on_preset_changed)

    def on_preset_changed(self, text):
        """Handler for when combobox selection changes."""
        entry = self._get_selected_entry()
        self.current_entry = entry
        
        self.preset_changed.emit(text)
 
        if entry:
            self.preset_selected.emit(entry)

    def _load_database_entries(self):
        self.dropdown.clear()
        
        try:
            db = SessionLocal()
            entries = list_entries(db)

            if entries:
                for entry in entries:
                    self.dropdown.addItem(entry['name'])
            else:
                self.dropdown.addItem("No presets available")
        except Exception as e:
            print(f"Error loading database entries: {e}")
            self.dropdown.addItem("Error loading presets")

    def _refresh_entries(self):
        current_text = self.dropdown.currentText()
        self.load_database_entries()

        if current_text != "Custom":
            index = self.dropdown.findText(current_text)
            if index >= 0:
                self.dropdown.setCurrentIndex(index)
    
    def _get_selected_entry(self):
        """Get the currently selected entry from database based on combobox selection."""
        current_text = self.dropdown.currentText()
        return current_text