from PyQt6.QtWidgets import QMainWindow, QDialog, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, QSize
from .styles import StyleManager


class MainWindow(QMainWindow):
    def __init__(self, title="CustomPyQt6 App", size=(800, 600), theme="dark"):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(QSize(*size))

        # Центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Установка темы
        self.style_manager = StyleManager()
        self.set_theme(theme)

    def set_theme(self, theme_name):
        self.style_manager.set_theme(theme_name)
        self.setStyleSheet(self.style_manager.get_stylesheet())

    def add_widget(self, widget):
        self.layout.addWidget(widget)


class Dialog(QDialog):
    def __init__(self, title="Dialog", size=(400, 300), theme="dark"):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(QSize(*size))

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Установка темы
        self.style_manager = StyleManager()
        self.set_theme(theme)

    def set_theme(self, theme_name):
        self.style_manager.set_theme(theme_name)
        self.setStyleSheet(self.style_manager.get_stylesheet())

    def add_widget(self, widget):
        self.layout.addWidget(widget)