class Graph:
    """
    Weighted directed graph using an adjacency list.

    Each node is a string of the form "StationName|LineId"

    Each entry in the adjacency list is a tuple:
        (neighbor: str, weight: int, line: str)

    This structure is chosen over an adjacency matrix because transit networks are sparse 
    (each station has very few neighbors relative to the total number of nodes), so a list uses far less memory and
    iterating over neighbors is faster.

    Use of dunder methods allows the graph to be used with familiar syntax in algorithms.py like:
    - "node in graph" to check existence
    - "for node in graph" to iterate over nodes
    - "graph[node]" to get neighbors of a node
    """

    def __init__(self):
        # Dictionary formated as:{ node: [(neighbor, time, line), ...] }
        self.adjacency = {}

    # ==================== Core operations ====================

    def add_node(self, node):
        """Add a node to the graph if it does not already exist."""
        if node not in self.adjacency:
            self.adjacency[node] = []

    def add_edge(self, src, dst, time, line=None):
        """
        Add a directed weighted edge from source (departure) to destination (arrival).

        The line is inferred from the src node identifier ("Station|Line")
        if not explicitly provided — this covers in-line edges.
        For transfer edges the line stored is the destination line,
        which is what the algorithms need when deciding whether a
        line change has occurred.

        Both src and dst nodes are created automatically if missing.
        """
        self.add_node(src)
        self.add_node(dst)

        # infer line from src node identifier if not given
        if line is None:
            line = dst.split("|")[-1] if "|" in src else None # using dst means the stored line is the new line the traveller boards when there is transfer

        # avoid duplicate edges
        if (dst, time, line) not in self.adjacency[src]:
            self.adjacency[src].append((dst, time, line))

    # ==================== Getters ====================

    def get_all_nodes(self):
        """Return the list of all node identifiers in the graph."""
        return list(self.adjacency.keys())

    def get_neighbors(self, node):
        """
        Return the neighbor list of a node: [(neighbor, time, line), ...]
        Returns an empty list if the node does not exist.
        """
        return self.adjacency.get(node, [])

    def __contains__(self, node):
        """Support 'node in graph' checks used by algorithms.py."""
        return node in self.adjacency

    def __iter__(self):
        """Support 'for node in graph' iteration used by algorithms.py."""
        return iter(self.adjacency)

    def __getitem__(self, node):
        """Support 'graph[node]' access used by algorithms.py."""
        return self.adjacency[node]

    def get(self, node, default=None):
        """Support 'graph.get(node, default)' used by is_connected()."""
        return self.adjacency.get(node, default)

    def items(self):
        """Support 'graph.items()' used by find_transfer_stations()."""
        return self.adjacency.items()

    # ==================== Display ====================

    def __repr__(self):
        return f"Graph({len(self.adjacency)} nodes)"