from collections import deque
import heapq

# penalty when switching lines at the same station
TRANSFER_TIME = 120


# ======================================== Search algorithms ========================================

def bfs(graph, start, end):
    """
    BFS - Breadth First Search algorithm
    from the course: uses white/grey/black colors + a queue (FIFO)
    finds the path with the fewest stops (ignores travel time)
    """
    # initialize all stations as unvisited (white)
    color = dict()
    for station in graph:
        color[station] = 'white'

    color[start] = 'grey'
    queue = [[start]]   # queue of full paths, not just stations

    while queue:
        path = queue.pop(0)         # FIFO: take the first path
        current = path[-1]

        if current == end:
            return path             # found the destination

        for neighbor, travel_time, line in graph[current]:
            if color[neighbor] == 'white':
                color[neighbor] = 'grey'
                queue.append(path + [neighbor])

        color[current] = 'black'    # done with this station

    return None  # no path found

def dfs(graph, start, end):
    """
    DFS - Depth First Search algorithm
    from the course: uses white/grey/black colors + a stack (LIFO)
    explores one full branch before trying another
    """ 
    # initialize all stations as unvisited (white)
    color = dict()
    for station in graph:
        color[station] = 'white'

    color[start] = 'grey'
    path = [start]
    stack = [start]

    while stack:
        current = stack[-1]  # peek at top of stack (LIFO)

        # find unvisited neighbors
        white_neighbors = [
            neighbor for neighbor, travel_time, line in graph[current]
            if color[neighbor] == 'white'
        ]

        if white_neighbors:
            # go deeper into the first unvisited neighbor
            next_station = white_neighbors[0]
            color[next_station] = 'grey'
            path.append(next_station)
            stack.append(next_station)

            if next_station == end:
                return path          # found the destination

        else:
            # dead end, backtrack
            stack.pop()
            color[current] = 'black'

    return None  # no path found


def dijkstra(graph, start, end):
    """
    DIJKSTRA algorithm for shortest path in a weighted graph
    from the course: always picks the nearest unvisited vertex
    adds TRANSFER_TIME (120s) when switching lines
    uses a priority queue (heap) to always pop the smallest cost
    """
    if start not in graph or end not in graph:
        return None, None

    # heap entry: (elapsed time, station, line we're on, steps so far)
    heap = [(0, start, None, [])]

    # tracks the best known time for each (station, line) pair
    # same idea as marking vertices as visited in the course table
    visited = {}

    while heap:
        elapsed, station, current_line, steps = heapq.heappop(heap)

        # skip if already visited (like the X in the course table)
        state = (station, current_line)
        if state in visited:
            continue
        visited[state] = elapsed

        # label this step (board / continue / transfer / alight)
        if not steps:
            step = {"station": station, "line": None, "action": "board"}
        elif current_line is not None and current_line != steps[-1]["line"]:
            step = {"station": station, "line": current_line, "action": "transfer"}
        else:
            step = {"station": station, "line": current_line, "action": "continue"}

        steps = steps + [step]

        # destination reached — same as stopping when we visit the target
        if station == end:
            steps[-1]["action"] = "alight"
            return elapsed, steps

        # update neighbors — same as filling the Dijkstra table in the course
        for neighbor, travel_time, line in graph[station]:
            penalty = TRANSFER_TIME if (current_line and line != current_line) else 0
            new_time = elapsed + travel_time + penalty

            if (neighbor, line) not in visited:
                heapq.heappush(heap, (new_time, neighbor, line, steps))

    return None, None  # no path found


# ======================================== DISPLAY ========================================

def format_route(steps, total_time):
    """
    Prints the route taken in a readable way
    """
    if steps is None:
        print("No route found.")
        return

    print("\n" + "-" * 45)

    for step in steps:
        station = step["station"]
        line    = step["line"]
        action  = step["action"]

        if action == "board":
            print(f"  Board at {station}")
        elif action == "continue":
            print(f"  Continue through {station}  (line {line})")
        elif action == "transfer":
            print(f"  Change at {station} -> line {line}  (+2 min)")
        elif action == "alight":
            print(f"  Alight at {station}  (line {line})")

    mins = total_time // 60
    secs = total_time % 60
    print(f"\n  Total time: {mins} min {secs} sec")
    print("-" * 45 + "\n")


# ======================================== CONNECTIVITY CHECK ========================================

def is_connected(graph):
    """Check if the graph is fully connected using BFS."""
    if not graph:
        return True

    # pick any station as starting point
    start = next(iter(graph))

    color = dict()
    for station in graph:
        color[station] = 'white'

    color[start] = 'grey'
    queue = deque([start])

    while queue:
        station = queue.popleft()
        for neighbor, travel_time, line in graph.get(station, []):
            if color[neighbor] == 'white':
                color[neighbor] = 'grey'
                queue.append(neighbor)
        color[station] = 'black'

    # if every station turned black, the network is fully connected
    return all(c == 'black' for c in color.values())


# ======================================== TRANSFER STATIONS ========================================


def find_transfer_stations(graph):
    """Identify stations that serve multiple lines, which are potential transfer points."""
    transfers = {}

    for station, neighbors in graph.items():
        lines = set(line for neighbor, travel_time, line in neighbors)
        if len(lines) > 1:
            transfers[station] = lines

    return transfers