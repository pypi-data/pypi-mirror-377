from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit,
    QComboBox, QCheckBox, QSlider
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

class CustomButton(QPushButton):
    def __init__(self, text, width=120, height=40):
        super().__init__(text)
        self.setMinimumSize(QSize(width, height))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("class", "custom-button")

class CustomLabel(QLabel):
    def __init__(self, text, font_size=12, bold=False):
        super().__init__(text)
        font = QFont()
        font.setPointSize(font_size)
        font.setBold(bold)
        self.setFont(font)
        self.setProperty("class", "custom-label")

class CustomEntry(QLineEdit):
    def __init__(self, placeholder="", width=200, height=30):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumSize(QSize(width, height))
        self.setProperty("class", "custom-entry")

class CustomComboBox(QComboBox):
    def __init__(self, items=None, width=200, height=30):
        super().__init__()
        self.setMinimumSize(QSize(width, height))
        if items:
            self.addItems(items)
        self.setProperty("class", "custom-combobox")

class CustomCheckBox(QCheckBox):
    def __init__(self, text):
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("class", "custom-checkbox")

class CustomSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, min_val=0, max_val=100):
        super().__init__(orientation)
        self.setMinimum(min_val)
        self.setMaximum(max_val)
        self.setValue(0)
        self.setProperty("class", "custom-slider")