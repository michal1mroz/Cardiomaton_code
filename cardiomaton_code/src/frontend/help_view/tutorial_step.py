from dataclasses import dataclass
from PyQt6.QtWidgets import QWidget


@dataclass
class TutorialStep:
    widget: QWidget
    title: str
    description: str