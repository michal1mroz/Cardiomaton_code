from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit

from src.frontend.ui_components.ui_factory import UIFactory

from src.database.db import SessionLocal
from src.database.crud.automaton_crud import list_entries

class PresetsWidget(QWidget):
    preset_selected = pyqtSignal(object)  
    preset_changed = pyqtSignal(str)  
    save_preset_request = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QHBoxLayout(self)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.label = UIFactory.create_label(self, "Select Preset", font_size=14)
        self.main_layout.addWidget(self.label)
        self.main_layout.addStretch(1)

        self.dropdown = QComboBox()
        self.dropdown.setObjectName("presetComboBox")
        self.main_layout.addWidget(self.dropdown)
        self.main_layout.addStretch(1)

        self._load_database_entries()

        self.text_input = QLineEdit()
        self.text_input.setObjectName("presetNameInput")
        self.text_input.setPlaceholderText("Enter preset name...")
        self.text_input.setMaximumWidth(150)  # Limit width
        self.text_input.setVisible(False)  # Hidden by default
        self.text_input.returnPressed.connect(self.on_input_return_pressed)
        self.main_layout.addWidget(self.text_input)

        # Button
        self.button = UIFactory.create_pushbutton(self, font_size=15)
        self.button.setText("+")
        self.button.setObjectName("presetBtn")
        self.button.setFixedSize(30, 30)  # Make it square
        self.main_layout.addWidget(self.button)

        self.main_layout.setContentsMargins(30, 5, 30, 5)

        self._init_connections()
        self.current_entry = None
        self.is_adding_preset = False

        self.setLayout(self.main_layout)

    def _init_connections(self):
        self.dropdown.currentTextChanged.connect(self.on_preset_changed)
        self.button.clicked.connect(self.toggle_input_field)
    
    def on_preset_changed(self, text):
        """Handler for when combobox selection changes."""
        entry = self._get_selected_entry()
        self.current_entry = entry

        self.dropdown.hidePopup()
 
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
        self._load_database_entries()

        if current_text != "Custom":
            index = self.dropdown.findText(current_text)
            if index >= 0:
                self.dropdown.setCurrentIndex(index)
    
    def _get_selected_entry(self):
        """Get the currently selected entry from database based on combobox selection."""
        current_text = self.dropdown.currentText()
        self.dropdown.hidePopup()
        return current_text
    
    def toggle_input_field(self):
        """Toggle the text input field visibility."""
        if self.is_adding_preset:
            self.cancel_input()
        else:
            self.show_input_field()

    def show_input_field(self):
        """Show the text input field for entering a new preset name."""
        self.is_adding_preset = True
        
        self.button.setText("✓")
        
        self.text_input.setVisible(True)
        self.text_input.clear()
        self.text_input.setFocus()
        
        self.dropdown.setEnabled(False)
        self.dropdown.setCurrentText("Custom")

    def hide_input_field(self):
        """Hide the text input field."""
        self.is_adding_preset = False
        
        self.button.setText("+")
        
        self.text_input.setVisible(False)
        
        self.dropdown.setEnabled(True)

    def cancel_input(self):
        """Cancel the input operation."""
        self.hide_input_field()
        
    def validate_preset_name(self, name):
        """Validate the preset name."""
        name = name.strip()
        
        if not name:
            return False, "Preset name cannot be empty"
        
        if len(name) > 50:
            return False, "Preset name too long (max 50 characters)"
        
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                return False, f"Preset name cannot contain '{char}'"
        
        
        return True, name

    def silent_refresh(self, entry: str = None):
        current_text = self.current_entry if hasattr(self, 'current_entry') else self.dropdown.currentText()
        was_blocked = self.dropdown.signalsBlocked()

        try:
            self.dropdown.blockSignals(True)
            self._load_database_entries()

            if entry:
                index = self.dropdown.findText(entry)
                if index >= 0:
                    self.dropdown.setCurrentIndex(index)
                    self.current_entry = entry
            else:
                if current_text:
                    index = self.dropdown.findText(current_text)
                    if index >= 0:
                        self.dropdown.setCurrentIndex(index)
                        self.current_entry = current_text
        except Exception as e:
            print(f'Error silently refreshing automaton preset list: {e}')
            self.dropdown.clear()
        finally:
            self.dropdown.blockSignals(was_blocked)
        self.current_entry = self._get_selected_entry() 

    def on_input_return_pressed(self):
        self.save_preset_from_input()


    def save_preset_from_input(self):
        name = self.text_input.text()
        
        is_valid, result = self.validate_preset_name(name)
        
        if not is_valid:
            self.text_input.setPlaceholderText(f"Error: {result}")
            self.text_input.clear()
            QTimer.singleShot(2000, lambda: self.text_input.setPlaceholderText("Enter preset name..."))
            return
        
        self.save_preset_request.emit(result)
        
        self.hide_input_field()
         