import json
import os

from graph import Graph

# ===================================================== HELPERS =====================================================

def _list_available_cities(data_dir):
    """
    Return a list of city names available as JSON files in the given directory.
    Private helper function for list_cities().
    """

    if not os.path.isdir(data_dir):
        print(f"Error: directory not found: {data_dir}")
        return []

    cities = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            city_name = filename[:-5]   # strip ".json"
            cities.append(city_name)
    return sorted(cities)


def _build_filepath(data_dir, city_name):
    """
    Return the expected JSON filepath for a given city name.
    Private helper function for load_city() and detect_and_load().
    """
    return os.path.join(data_dir, f"{city_name}.json")

# ===================================================== LOADERS =====================================================

def load_network(filepath):
    """
    Read a transit network JSON file and return a raw dictionary with the network data.
    Returns the parsed dictionary, or None if the file cannot be read or is malformed.
    Use of extensions to handle wrong file paths, invalid JSON.
    """
    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}")
        return None

    with open(filepath, encoding="utf-8") as f:  
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON in {filepath}: {e}")
            return None

    if "lignes" not in data:
        print(f"Error: missing 'lignes' key in {filepath}")
        return None

    if "correspondances" not in data:
        print(f"Warning: no 'correspondances' key in {filepath}, assuming none.")
        data["correspondances"] = []

    if "temps_moyen" not in data:
        print(f"Warning: no 'temps_moyen' key in {filepath}, defaulting to 120 seconds.")
        data["temps_moyen"] = 120

    return data


def load_city(city_name, data_dir="data"):
    """
    Load the transit network of a given city by name.

    Returns the raw network dictionary, or None on failure.
    """
    filepath = _build_filepath(data_dir, city_name)
    return load_network(filepath)


def detect_and_load(city_name_or_path, data_dir="data"):
    """
    Accept either a city name or a direct file path and loads the corresponding network.

    Returns:
        ("network", raw_dict)   on success.
        (None, None)            on failure.
    """
    # Treat as a direct path if it ends with .json or contains a path separator
    if city_name_or_path.endswith(".json") or os.sep in city_name_or_path:
        filepath = city_name_or_path
    else:
        filepath = _build_filepath(data_dir, city_name_or_path)

    data = load_network(filepath)
    if data is None:
        return None, None
    return "network", data

# ===================================================== GRAPH BUILDING =====================================================

def build_graph(data):
    """
    Build and return a weighted Graph from a raw network dictionary.

    Edges added:
      - Between every pair of consecutive stations on each line,
        in both directions, weighted by data["temps_moyen"].
        (Uses data["connexions"] if populated, otherwise generates
        the edges automatically from each line's station list.)
      - Between every pair of lines sharing a transfer station
        (correspondance), weighted by the transfer time given
        in data["correspondances"].

    Node identifiers are strings of the form  "<station_name>|<line_id>"
    so that the same physical station on two different lines is
    represented by two distinct nodes, linked by a transfer edge.
    """
    graph = Graph()
    avg_time   = data["temps_moyen"]
    lines      = data["lignes"]
    connexions = data.get("connexions", [])

    # --------------------- Add in-line edges ---------------------

    if connexions:
        # Explicit connexions list provided 
        for conn in connexions:
            src  = f"{conn['de']}|{conn['ligne']}"    # source node
            dst  = f"{conn['vers']}|{conn['ligne']}"  # destination node
            time = conn.get("temps", avg_time)
            graph.add_edge(src, dst, time)
    else:
        # Generate edges automatically from each line's ordered station list
        for line_id, line_data in lines.items():
            stations = line_data["stations"]
            for i in range(len(stations) - 1):
                src = f"{stations[i]}|{line_id}"
                dst = f"{stations[i + 1]}|{line_id}"
                graph.add_edge(src, dst, avg_time)
                graph.add_edge(dst, src, avg_time)   # bidirectional

    # --------------------- Add transfer edges (correspondances) ---------------------

    for transfer in data["correspondances"]:
        station      = transfer["station"]
        lines_served = transfer["lignes"]
        transfer_time = transfer.get("temps", 120)

        # Connect every pair of lines at this station
        for i in range(len(lines_served)):
            for j in range(len(lines_served)):
                if i != j:
                    src = f"{station}|{lines_served[i]}"
                    dst = f"{station}|{lines_served[j]}"
                    graph.add_edge(src, dst, transfer_time)

    return graph


def load_network_into_graph(filepath):
    """
    Convenience function: load a JSON file and immediately build the Graph.

    Returns:
        (graph, raw_data)   on success.
        (None,  None)       on failure.
    """
    data = load_network(filepath)
    if data is None:
        return None, None
    graph = build_graph(data)
    return graph, data


def load_city_into_graph(city_name, data_dir="data"):
    """
    Convenience function: load a city by name and immediately build the Graph.

    Returns:
        (graph, raw_data)   on success.
        (None,  None)       on failure.
    """
    data = load_city(city_name, data_dir)
    if data is None:
        return None, None
    graph = build_graph(data)
    return graph, data
    

# ===================================================== DISPLAY =====================================================

def display_network_summary(data):
    """Print a short summary of a loaded network dictionary."""
    if not data:
        print("No network data to display.")
        return

    city     = data.get("nom", "Unknown")
    lines    = data.get("lignes", {})
    transfers = data.get("correspondances", [])
    avg_time  = data.get("temps_moyen", "?")

    total_stations = sum(len(l["stations"]) for l in lines.values())

    print(f"City           : {city}")
    print(f"Lines          : {len(lines)}  ({', '.join(lines.keys())})")
    print(f"Total stops    : {total_stations}")
    print(f"Transfer pts   : {len(transfers)}")
    print(f"Avg time/stop  : {avg_time} s")


def display_graph_summary(graph):
    """Print a short summary of a built Graph."""
    if graph is None:
        print("No graph to display.")
        return

    nodes = graph.get_all_nodes()
    edge_count = sum(len(graph.get_neighbors(n)) for n in nodes) // 2

    print(f"Graph nodes    : {len(nodes)}")
    print(f"Graph edges    : {edge_count}  (undirected count)")


def list_cities(data_dir="data"):
    """Print all available cities found in the data directory."""
    cities = _list_available_cities(data_dir)
    if not cities:
        print("No cities found.")
        return []
    print("Available cities:")
    for city in cities:
        print(f"  - {city}")
    return cities