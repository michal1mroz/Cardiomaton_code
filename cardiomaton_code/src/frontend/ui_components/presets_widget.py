from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox, QPushButton, 
    QLineEdit, QListWidget, QListWidgetItem, QAbstractItemView)

from src.frontend.ui_components.ui_factory import UIFactory

from src.database.db import SessionLocal
from src.database.crud.automaton_crud import list_entries, delete_entry

class PresetsWidget(QWidget):
    preset_selected = pyqtSignal(object)  
    preset_changed = pyqtSignal(str)  
    save_preset_request = pyqtSignal(str)

    display_mapping = {
        "PHYSIOLOGICAL" : "Physiological Rhythm",
        "SINUS_BRADYCARDIA" : "Sinus Bradycardia",
        "SINUS_TACHYCARDIA": "Sinus Tachycardia",
        "AV_BLOCK_I": "First Degree Atrioventricular Block",
        "SINUS_PAUSE_RETROGRADE": "Sinus Pause with Retrograde",
        "SA_BLOCK_RETROGRADE": "Sinoatrial Block with Retrograde",
    }

    backward_display_mapping = {
        v: k for k, v in display_mapping.items()
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedHeight(60)

        self.main_layout = QHBoxLayout(self)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.label = UIFactory.create_label(self, "Select Preset", font_size=13)
        self.main_layout.addWidget(self.label)
        self.main_layout.addStretch(1)

        self.dropdown = QComboBox()
        self.dropdown.setObjectName("presetComboBox")

        self.list_widget = QListWidget()
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSpacing(2)

        font = QFont('Mulish')
        font.setPointSize(10)
        self.list_widget.setFont(font)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.dropdown.setModel(self.list_widget.model())
        self.dropdown.setView(self.list_widget)

        self.main_layout.addWidget(self.dropdown)

        self._load_database_entries()

        self.text_input = QLineEdit()
        self.text_input.setObjectName("presetNameInput")
        self.text_input.setPlaceholderText("Enter preset name...")
        self.text_input.setVisible(False)
        self.main_layout.addWidget(self.text_input)

        self.main_layout.addStretch(1)

        self.button = UIFactory.create_pushbutton(self)
        self.button.setObjectName("presetBtn")
        self.button.setFixedSize(30, 30)
        self.button.setIcon(QIcon("./resources/style/icons/plus.png"))
        self.button.setIconSize(QSize(14, 14))
        self.main_layout.addWidget(self.button)
        UIFactory.add_shadow(self.button)


        self.exit_button = UIFactory.create_pushbutton(self)
        self.exit_button.setObjectName("exitBtn")
        self.exit_button.setFixedSize(30, 30)
        self.exit_button.setIcon(QIcon("./resources/style/icons/cancel.png"))
        self.exit_button.setIconSize(QSize(14, 14))
        self.main_layout.addWidget(self.exit_button)
        self.exit_button.hide()
        UIFactory.add_shadow(self.exit_button)

        self.main_layout.setContentsMargins(30, 5, 30, 5)

        self._init_connections()

        self.current_entry = None
        self.is_adding_preset = False

        self.setLayout(self.main_layout)

    def get_display_name(self, internal_name):
        return self.display_mapping.get(internal_name, internal_name)
    
    def get_internal_name(self, display_name):
        return self.backward_display_mapping.get(display_name, display_name)

    def _init_connections(self):
        self.dropdown.currentTextChanged.connect(self.on_preset_changed)
        self.button.clicked.connect(self.handle_button_click)
        self.exit_button.clicked.connect(self.hide_input_field)

    def handle_button_click(self):
        if self.is_adding_preset:
            self.save_preset_from_input()
        else:
            self.show_input_field()
    
    def on_preset_changed(self, text):
        entry = self._get_selected_entry()
        self.current_entry = entry

        self.dropdown.hidePopup()
 
        if entry:
            self.preset_selected.emit(entry)

    def _remove_entry(self, name):
        try:
            db = SessionLocal()
            delete_entry(db, name)

        except Exception as e:
            print(f"Failed to remove: {name}. Error: {e}")

    def _load_database_entries(self):
        self.list_widget.clear()
        self.dropdown.clear()
        
        try:
            db = SessionLocal()
            entries = list_entries(db)

            if entries:
                for entry in entries:
                    internal_name = entry['name']
                    display_name = self.get_display_name(internal_name)
                    item = QListWidgetItem()
                    item.setText(display_name)

                    self.list_widget.addItem(item)
                    row_widget = QWidget()
                    row_widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

                    row_layout = QHBoxLayout(row_widget)
                    row_layout.setContentsMargins(6,2,6,2)
                    label = QLabel(display_name)
                    label.setFont(QFont('Mulish', 10))
                    row_layout.addStretch()
                    
                    if not entry.get('is_default', False):
                        del_btn = QPushButton()
                        del_btn.setFixedSize(16, 16)
                        del_btn.setIcon(QIcon("./resources/style/icons/cancel.png"))
                        del_btn.setIconSize(QSize(8, 8))
                        del_btn.setToolTip(f"Delete preset {display_name}")
                        del_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

                        del_btn.setStyleSheet("""
                            QPushButton {
                                padding: 0px;
                                margin: 0px;
                                border: none;
                                background-color: #E1605D;
                                border-radius: 8px;
                            }
                            QPushButton:hover {
                                background-color: #CD4B48;
                            }
                        """)

                        def make_delete_handler(name, item_ref):
                            def on_delete():
                                prev_index = self.dropdown.currentIndex()
                                internal = self.get_internal_name(name)

                                row = self.list_widget.row(item_ref)
                                taken = self.list_widget.takeItem(row)

                                self._remove_entry(internal)

                                del taken
                                if prev_index >= 0 and prev_index < self.list_widget.count():
                                    self.dropdown.setCurrentIndex(prev_index)
                                else:
                                    if self.list_widget.count() > 0:
                                        self.dropdown.setCurrentIndex(0)
                                    else:
                                        self.dropdown.setCurrentIndex(-1)
                            return on_delete

                        del_btn.clicked.connect(make_delete_handler(display_name, item))
                        row_layout.addWidget(del_btn)
                    
                    self.list_widget.setItemWidget(item, row_widget)
                    item.setToolTip(display_name)

            else:
                placeholder = QListWidgetItem("No presets available")
                placeholder.setFlags(placeholder.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.list_widget.addItem(placeholder)

        except Exception as e:
            print(f"Error loading database entries: {e}")
            placeholder = QListWidgetItem("No presets available")
            placeholder.setFlags(placeholder.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.list_widget.addItem(placeholder)


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
        return self.get_internal_name(current_text)
    
    def toggle_input_field(self):
        """Toggle the text input field visibility."""
        if self.is_adding_preset:
            self.cancel_input()
        else:
            self.show_input_field()

    def show_input_field(self):
        """Show the text input field for entering a new preset name."""
        self.is_adding_preset = True
        
        self.button.setIcon(QIcon("./resources/style/icons/okay.png"))
        self.exit_button.show()
        
        self.text_input.setVisible(True)
        self.text_input.clear()
        self.text_input.setFocus()

        self.label.setText("Save Preset")
        self.dropdown.hide()

    def hide_input_field(self):
        """Hide the text input field."""
        self.is_adding_preset = False

        self.button.setIcon(QIcon("./resources/style/icons/plus.png"))
        self.exit_button.hide()

        self.text_input.setVisible(False)

        self.label.setText("Select Preset")
        self.dropdown.show()
        
    def validate_preset_name(self, name):
        """Validate the preset name."""
        name = name.strip()
        
        if not name:
            return False, "Name cannot be empty"
        
        if len(name) > 50:
            return False, "Name too long (max 50 characters)"
        
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                return False, f"Name cannot contain '{char}'"
        
        
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
         
    # def _on_list_item_clicked(self, item: QListWidgetItem):
    #     row = self.list_widget.row(item)
    #     if row >= 0:
    #         self.dropdown.setCurrentIndex(row)
    #         internal = self.get_internal_name(item.text())
    #         self.current_entry = internal
    #         self.preset_selected.emit(internal)
    #         self.dropdown.hidePopup()