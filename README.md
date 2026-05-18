# ESME-PBL3

🚇 **A Short Ride on the Metro and Tramway**

**Version:** [v1.0]

**Team:** Raphaël Dussart, Clovis Bogdan de Badereau, Damien d'Estienne du Bourguet, Zahed Al-Kassous, Gabriel Barbier


## 🎯 What is this project?

A **public transport route planner** for ESME Sudria students. Pick a city, a departure and an arrival station, and the app finds the fastest route across metro and tramway networks.

It runs fully offline. The network data lives in JSON files, and the engine is built to be generic: adding a new city only means dropping in a new JSON file, nothing else to change in the code.


## 🚀 Quick Start

1. **Clone the repo:**
   ```
   git clone https://github.com/RaphDuss1003/ESME-PBL3.git
   cd ESME-PBL3
   ```

2. **Setup Virtual Environment:**
   ```
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```
   pip install PyQt5 PyQtWebEngine folium
   ```

4. **Run the app:**
   ```
   python main.py
   ```


## 🛠️ Technical Architecture

We split the work into separate modules so each part of the team could work independently:

- **main.py**: Entry point. Launches the app and wires everything together.

- **graph.py**: Custom weighted graph using an adjacency list. Each node is `"StationName|LineID"` so the same physical station on two different lines is two distinct nodes, connected by a transfer edge.

- **data_loader.py**: Parses the JSON network files, builds the graph, and handles bad inputs gracefully (missing files, malformed data).

- **algorithms.py**: The core of the engine. Implements BFS, DFS and Dijkstra.

- **itinerary.py**: Formats the algorithm output into human-readable instructions (board / continue through / transfer / alight).

- **visualize_metro.py**: Builds an interactive HTML map with Folium. Lines are drawn in their real colors, stations are clickable markers.

- **Interface/interface.py + style.qss**: PyQt5 graphical interface. Dropdowns for city, departure and arrival on the left, interactive map on the right.


## 🗺️ Supported Cities

| City | File | Network |
|------|------|---------|
| Paris | paris.json | Metro lines 1-14 |
| Lyon | lyon.json | Metro A-D, Tramways T1-T7 |
| Lille | lille.json | Metro 1-2, Tramways T and R |
| Bordeaux | bordeaux.json | Tramways A-F, Express buses G-H |


## 🔍 How the algorithms work

### BFS
Finds the path with the **fewest stops**. Explores the graph level by level with a FIFO queue. Stations are marked white/grey/black to track which ones have been visited (same approach as in the course).

### DFS
Goes as deep as possible into one branch before backtracking, using a LIFO stack and the same coloring. Not optimal but required by the project specs.

### Dijkstra
The main one. Always expands the cheapest unvisited node using a min-heap. Switching lines at a station adds a **120 second penalty**. We track `(station, line)` as the state so the same station reached on two different lines is handled as two separate cases. That's how transfers work correctly.


## 📦 Dependencies

- **PyQt5 + PyQtWebEngine**: GUI and embedded map view.
- **Folium**: generates the interactive HTML maps.
- **json, os, heapq**: all standard Python, nothing extra to install.


## 🔮 What we'd add in v2.0

- **Disruption management**: mark a station or line as closed and reroute automatically.
- **Walking transfers**: handle transfers between nearby stations that aren't at the same stop.
- **Better error handling in the UI**: clearer messages when a station doesn't exist or no route is found.

*Advanced Algorithms 3 — PBL3, 2025-2026*