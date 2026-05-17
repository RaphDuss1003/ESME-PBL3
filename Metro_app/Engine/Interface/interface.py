from PyQt5.QtWidgets import (
    QWidget, QComboBox, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QApplication
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl
import sys
from pathlib import Path

# Add project root to import path and import the single visualizer file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from visualize_metro import MetroMapVisualizer, get_available_cities


class Interface(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Maps")
        self.setFixedSize(1400, 900)

        # ==================== LEFT PANEL ====================

        # --- Combo 1 : City ---
        self.combo1 = QComboBox()
        self.combo1.addItem("Select your city", None)  # placeholder

        for city_code, city_name in get_available_cities():
            self.combo1.addItem(city_name, city_code)

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

        self.web_view = QWebEngineView()
        self.web_view.setHtml('<h2 style="font-family: sans-serif; padding: 20px;">Select a city to display the metro map.</h2>')

        # ==================== MAIN LAYOUT ====================

        main_layout = QHBoxLayout()
        main_layout.setSpacing(40)
        main_layout.addWidget(left_group)
        main_layout.addWidget(self.web_view)

        self.setLayout(main_layout)

        self.combo1.currentIndexChanged.connect(self.on_city_changed)

        style_path = Path(__file__).resolve().parent / "style.qss"
        if style_path.exists():
            self.setStyleSheet(style_path.read_text(encoding='utf-8'))

    def on_city_changed(self, index):
        if index == 0:
            return
        city_code = self.combo1.currentData()
        if not city_code:
            return
        self.load_city_map(city_code)

    def load_city_map(self, city_code: str):
        data_path = Path(__file__).resolve().parents[2] / 'Data files' / f'{city_code}.json'
        if not data_path.exists():
            self.web_view.setHtml(f'<h2>Data file not found: {city_code}.json</h2>')
            return

        try:
            visualizer = MetroMapVisualizer(str(data_path), city_code=city_code)
            visualizer.create_map(zoom_start=12)
            html = visualizer.render_html()
            base_url = QUrl.fromLocalFile(str(data_path.parent) + '/')
            self.web_view.setHtml(html, base_url)
        except Exception as exc:
            self.web_view.setHtml(f'<h2>Error loading map:</h2><pre>{exc}</pre>')


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Interface()
    window.show()

    sys.exit(app.exec_())
