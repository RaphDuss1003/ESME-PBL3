from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                            QSpinBox, QGroupBox, QDoubleSpinBox, QPlainTextEdit,
                            QDialog, QComboBox)
from PyQt5.QtCore import Qt

class Interface(QWidget):
    def __init__(self): 
        super().__init__()
        
        self.setObjectName("mainScreen")                                 # Sets an internal object name for styling
        self.setWindowTitle("MetroApp")                                  # Sets the window title
        self.showFullScreen()

        combo = QComboBox()
        combo.addItems(["Paris", "Lille", "Bordeaux", "Lyon"])
        