from PyQt5.QtWidgets import (
    QWidget, QComboBox, QVBoxLayout, QHBoxLayout,
    QGroupBox, QPlainTextEdit, QLabel, QPushButton, QApplication
)
from PyQt5.QtCore import Qt
import sys


class Interface(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simple UI")
        self.setFixedSize(1400, 900)

        # ==================== LEFT PANEL ====================

        # --- Combo 1 : City ---
        self.combo1 = QComboBox()
        self.combo1.addItem("Select your city")  # placeholder
        self.combo1.addItems(["Paris", "Bordeaux", "Lille", "Lyon"])
        self.combo1.setCurrentIndex(0)
        self.combo1.setMinimumHeight(50)

        # --- Combo 2 : Departure ---
        self.combo2 = QComboBox()
        self.combo2.addItem("Select departure")  # placeholder
        self.combo2.addItems(["A", "B", "C"])
        self.combo2.setCurrentIndex(0)
        self.combo2.setMinimumHeight(50)

        # --- Combo 3 : Arrival ---
        self.combo3 = QComboBox()
        self.combo3.addItem("Select arrival")  # placeholder
        self.combo3.addItems(["A", "B", "C"])
        self.combo3.setCurrentIndex(0)
        self.combo3.setMinimumHeight(50)

        # --- Labels ---
        label_city = QLabel("Find Your City")
        label_city.setStyleSheet("font-size: 22px; font-weight: bold;")

        label_dep = QLabel("Departure Station")
        label_dep.setStyleSheet("font-size: 22px; font-weight: bold;")

        label_arr = QLabel("Arrival Station")
        label_arr.setStyleSheet("font-size: 22px; font-weight: bold;")

        # --- Exit Button ---
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setMinimumHeight(60)
        self.btn_exit.clicked.connect(self.close)

        # --- Left Layout ---
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)
        left_layout.setSpacing(25)

        left_layout.addWidget(label_city)
        left_layout.addWidget(self.combo1)

        left_layout.addWidget(label_dep)
        left_layout.addWidget(self.combo2)

        left_layout.addWidget(label_arr)
        left_layout.addWidget(self.combo3)

        left_layout.addSpacing(20)
        left_layout.addWidget(self.btn_exit)

        left_group = QGroupBox("Your Destination")
        left_group.setMaximumWidth(400)
        left_group.setStyleSheet("font-size: 24px; font-weight: bold;")
        left_group.setLayout(left_layout)

        # ==================== RIGHT PANEL ====================

        self.right_area = QPlainTextEdit()
        self.right_area.setPlaceholderText("Grand espace à droite…")            # Mettre ici le truc de damien
        self.right_area.setStyleSheet("font-size: 20px;")

        # ==================== MAIN LAYOUT ====================

        main_layout = QHBoxLayout()
        main_layout.setSpacing(40)
        main_layout.addWidget(left_group)
        main_layout.addWidget(self.right_area)

        self.setLayout(main_layout)


        self.setStyleSheet(open("Metro_app/Engine/Interface/style.qss").read())         # Load the QSS file


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Interface()
    window.show()

    sys.exit(app.exec_())
