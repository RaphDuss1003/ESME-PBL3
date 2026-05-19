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

- **main.py**: Launches the app, that's it.

- **graph.py**: Our graph, implemented as an adjacency list. Each node is `"StationName|LineID"` so the same station on two different lines is two separate nodes connected by a transfer edge. We added dunder methods (`__contains__`, `__iter__`, `__getitem__`) so the algorithms can do things like `node in graph` or `graph[node]` without extra boilerplate. We went with an adjacency list instead of a matrix because metro networks don't have that many connections per station, so the matrix would mostly be zeros.

- **data_loader.py**: Reads the JSON files, builds the graph, and prints an error if a file is missing or broken instead of just crashing.

- **algorithms.py**: BFS, DFS and Dijkstra.

- **itinerary.py**: Takes the steps from Dijkstra and turns them into something readable (board / continue / transfer / alight). Also covers edge cases like already being at the destination.

- **visualize_metro.py**: Draws an interactive map with Folium, lines in their real colors, stations you can click on.

- **Interface/interface.py + style.qss**: The PyQt5 interface. City, departure and arrival on the left with the itinerary below, map on the right.


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
- **Route highlighting on the map**: After calculating a route, highlight the selected journey in red directly on the map.

*AAP3 2025-2026*