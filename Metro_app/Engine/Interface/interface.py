import sys

from PyQt5.QtWidgets import (
    QWidget, QComboBox, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QApplication,
    QPlainTextEdit, QDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont

from pathlib import Path

# Add project root to import path and import the single visualizer file
PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from visualize_metro import MetroMapVisualizer, get_available_cities
from Engine.data_loader import load_city_into_graph
from Engine.algorithms import dijkstra
from Engine.itinerary import create_itinerary_steps, format_time


# ======================================== HELPERS ========================================
 
def _resolve_node(station_name: str, graph) -> str | None:
    """Return the first graph node whose station part matches station_name."""
    for node in graph.get_all_nodes():
        if node.startswith(station_name + "|"):
            return node
    return None
 
 
def _format_itinerary_bst(steps, total_time) -> str:
    """
    Render the itinerary in the same visual style as the BST screenshot:
 
        Action  | StationName <- annotation
        Action  | StationName
        ...
        Estimated time: X min Y sec
 
    Column widths are fixed so the pipe character lines up neatly.
    """
    if not steps:
        return "No route found."
 
    lines_out = []
    ACTION_W = 14          # left column width (action label)
 
    for step in steps:
        station_raw = step.get("station", "")
        line_id     = step.get("line")
        action      = step.get("action", "")
 
        # strip the "|LineId" suffix that sometimes leaks through
        if "|" in station_raw:
            station_name, _ = station_raw.rsplit("|", 1)
        else:
            station_name = station_raw
 
        # build annotation (shown after a "<-")
        if action == "board":
            label      = "Board"
            annotation = f"line {line_id}" if line_id else "← start"
        elif action == "transfer":
            label      = "Transfer"
            annotation = f"← take line {line_id}" if line_id else "← transfer"
        elif action == "alight":
            label      = "Alight"
            annotation = f"line {line_id}" if line_id else "← end"
        else:                           # "continue"
            label      = "Continue"
            annotation = ""
 
        left = f"{label:<{ACTION_W}}"
 
        if annotation:
            lines_out.append(f"{left}| {station_name} <- {annotation}")
        else:
            lines_out.append(f"{left}| {station_name}")
 
    lines_out.append("")
    lines_out.append(f"Estimated time : {format_time(total_time)}")
    return "\n".join(lines_out)
 
 
# ======================================= VISUALIZER =======================================
 
class ItineraryPopup(QDialog):
    """
    Modal popup that shows the itinerary in BST style.
    Stays on top of the main window; closed with the Close button.
    """
    def __init__(self, text: str, dep: str, arr: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Route  {dep}  →  {arr}")
        self.setMinimumSize(520, 420)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
 
        # --- text area ---
        self.text_box = QPlainTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setFont(QFont("Courier New", 13))
        self.text_box.setPlainText(text)
 
        # --- close button ---
        btn_close = QPushButton("Close")
        btn_close.setMinimumHeight(50)
        btn_close.clicked.connect(self.accept)
 
        # --- layout ---
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.addWidget(QLabel(f"<b>{dep}</b>  →  <b>{arr}</b>"))
        layout.addWidget(self.text_box)
        layout.addWidget(btn_close)
        self.setLayout(layout)
 
        # inherit the parent's stylesheet so it looks consistent
        if parent is not None:
            self.setStyleSheet(parent.styleSheet())

# ======================================= INTERFACE =======================================

class Interface(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Maps")
        self.setMinimumSize(1400, 900)

        # internal state
        self._graph     = None   # loaded Graph object
        self._data      = None   # raw JSON dict
        self._city_code = None
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
        self.combo2.setCurrentIndex(0)
        self.combo2.setMinimumHeight(50)
        self.combo2.setEnabled(False)  # disabled until a city is chosen

        # --- Combo 3 : Arrival ---
        self.combo3 = QComboBox()
        self.combo3.addItem("Select arrival")  # placeholder
        self.combo3.setCurrentIndex(0)
        self.combo3.setMinimumHeight(50)
        self.combo3.setEnabled(False)  # disabled until a city is chosen

        # --- Labels ---
        label_city = QLabel("Find Your City")
        label_city.setStyleSheet("font-size: 22px; font-weight: bold;")

        label_dep = QLabel("Departure Station")
        label_dep.setStyleSheet("font-size: 22px; font-weight: bold;")

        label_arr = QLabel("Arrival Station")
        label_arr.setStyleSheet("font-size: 22px; font-weight: bold;")

        # --- Calculate button ---
        self.btn_calc = QPushButton("Calculate & Show Route")
        self.btn_calc.setMinimumHeight(60)
        self.btn_calc.clicked.connect(self.on_calculate)

        # --- Itinerary display (scrollable, monospace, BST style) ---
        self.itinerary_box = QPlainTextEdit()
        self.itinerary_box.setReadOnly(True)
        self.itinerary_box.setFont(QFont("Courier New", 12, QFont.Normal)) # QFont.Normal overrides the bold from the QSS stylesheet
        self.itinerary_box.setStyleSheet("font-weight: normal;")       
        self.itinerary_box.setPlaceholderText("Itinerary will appear here...")
        # no fixed height: it will stretch to fill available space between btn_calc and btn_exit

        # --- Exit Button ---
        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setMinimumHeight(60)
        self.btn_exit.clicked.connect(self.close)

        # --- Left Layout ---
        # Top section: city / departure / arrival / calculate — aligned to top
        top_layout = QVBoxLayout()
        top_layout.setSpacing(18)
        top_layout.addWidget(label_city)
        top_layout.addWidget(self.combo1)
        top_layout.addWidget(label_dep)
        top_layout.addWidget(self.combo2)
        top_layout.addWidget(label_arr)
        top_layout.addWidget(self.combo3)
        top_layout.addSpacing(10)
        top_layout.addWidget(self.btn_calc)

        # Full left layout: top section + stretching itinerary box + pinned exit button
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)
        left_layout.addLayout(top_layout)         # controls at the top
        left_layout.addWidget(self.itinerary_box) # stretches to fill remaining space
        left_layout.addWidget(self.btn_exit)      # pinned at the bottom
 
        left_group = QGroupBox("Your Destination")
        left_group.setMaximumWidth(460)
        left_group.setStyleSheet("font-size: 24px; font-weight: bold;")
        left_group.setLayout(left_layout)

        # ==================== RIGHT PANEL ====================

        self.web_view = QWebEngineView()   # to display the map
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

    # ==================== EVENT HANDLERS ====================

    def on_city_changed(self, index):
        if index == 0:
            return
        city_code = self.combo1.currentData()
        if not city_code:
            return
        self._city_code = city_code
        self._load_graph(city_code)
        self._populate_station_combos()
        self._load_city_map(city_code)
 
    def _load_graph(self, city_code: str):
        """Load the graph for the chosen city and keep it in self._graph."""
        data_path = Path(__file__).resolve().parents[2] / "Data files" / f"{city_code}.json"
        if not data_path.exists():
            self._graph = None
            self._data  = None
            return
        self._graph, self._data = load_city_into_graph(city_code, str(data_path.parent))
 
    def _populate_station_combos(self):
        """Fill departure / arrival combos with the unique station names of the loaded city."""
        self.combo2.clear()
        self.combo3.clear()
        self.combo2.addItem("Select departure")
        self.combo3.addItem("Select arrival")
 
        if self._graph is None:
            return
 
        station_names = sorted(
            set(node.split("|")[0] for node in self._graph.get_all_nodes())
        )
        self.combo2.addItems(station_names)
        self.combo3.addItems(station_names)
        self.combo2.setEnabled(True)   # city is loaded, user can now pick stations
        self.combo3.setEnabled(True)   # city is loaded, user can now pick stations
 
    def on_calculate(self):
        """Run Dijkstra and display the BST-style itinerary in the inline text box."""

        def show_error(text: str):
            self.itinerary_box.setPlainText(text)  # errors go in the same box, no popup

        # --- guards ---
        if self._graph is None:
            show_error("Please select a city first.")
            return

        dep_name = self.combo2.currentText()
        arr_name = self.combo3.currentText()

        if dep_name == "Select departure" or arr_name == "Select arrival":
            show_error("Please select both a departure and an arrival station.")
            return

        if dep_name == arr_name:
            show_error("You are already at your destination!")
            return

        start_node = _resolve_node(dep_name, self._graph)
        end_node   = _resolve_node(arr_name, self._graph)

        if start_node is None or end_node is None:
            show_error("Station not found in graph.")
            return

        # --- compute ---
        total_time, steps = dijkstra(self._graph, start_node, end_node)

        if steps is None:
            show_error("No route found between these two stations.")
            return

        # --- display inline in the scrollable text box ---
        text = _format_itinerary_bst(steps, total_time)
        self.itinerary_box.setPlainText(text)
 
    def _load_city_map(self, city_code: str):
        data_path = Path(__file__).resolve().parents[2] / "Data files" / f"{city_code}.json"
        if not data_path.exists():
            self.web_view.setHtml(f"<h2>Data file not found: {city_code}.json</h2>")
            return
        try:
            visualizer = MetroMapVisualizer(str(data_path), city_code=city_code)
            visualizer.create_map(zoom_start=12)
            html = visualizer.render_html()
            base_url = QUrl.fromLocalFile(str(data_path.parent) + "/")
            self.web_view.setHtml(html, base_url)
        except Exception as exc:
            self.web_view.setHtml(f"<h2>Error loading map:</h2><pre>{exc}</pre>")

