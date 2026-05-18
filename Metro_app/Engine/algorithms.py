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
    color = {station: 'white' for station in graph.get_all_nodes()}

    color[start] = 'grey'
    queue = [[start]]   # queue of full paths, not just stations

    while queue:
        path = queue.pop(0)         # FIFO: take the first path
        current = path[-1]

        if current == end:
            return path             # found the destination

        for neighbor, travel_time, line in graph.get_neighbors(current):
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
    color = {station: 'white' for station in graph.get_all_nodes()}

    color[start] = 'grey'
    path = [start]
    stack = [start]

    while stack:
        current = stack[-1]  # peek at top of stack (LIFO)

        # find unvisited neighbors
        white_neighbors = [
            neighbor for neighbor, travel_time, line in graph.get_neighbors(current)
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

    Heap entry: (elapsed_time, tie_breaker, station, line, steps)
    The tie_breaker counter prevents Python from trying to compare
    the `steps` list of dicts when two entries share the same elapsed time,
    which would raise a TypeError.
    """
    if start not in graph or end not in graph:
        return None, None

    _counter = 0  # tie-breaker: simple integer, always unique, always comparable
    # added _counter in 2nd position so heapq never reaches the steps list when
    # two entries share the same elapsed time (dicts are not comparable with <)

    # FIX bug 1: extract the real line from "Station|Line" before entering the loop
    start_line = start.split("|")[-1] if "|" in start else None  # fix bug 1: line is known immediately, no None ambiguity

    # FIX bug 1: build the board step HERE (before the loop) so it never gets confused with a transfer
    # previously the board step was built inside the loop at pop time, where current_line was None
    # -> that caused None != real_line to be True -> wrongly labelled as "transfer"
    initial_step = {"station": start.split("|")[0], "line": start_line, "action": "board"}  # fix bug 1: board step created at push time with the correct line
    heap = [(0, _counter, start, start_line, [initial_step])]  # (elapsed, tie-breaker, station, line, steps)

    # tracks the best known time for each (station, line) pair
    # same idea as marking vertices as visited in the course table
    visited = {}

    while heap:
        elapsed, _, station, current_line, steps = heapq.heappop(heap)  # _ discards the tie-breaker, we don't need it after the pop

        # skip if already visited (like the X in the course table)
        state = (station, current_line)
        if state in visited:
            continue
        visited[state] = elapsed

        # destination reached — relabel the last step as "alight"
        if station == end:
            final_steps = steps[:-1] + [{**steps[-1], "action": "alight"}]  # fix: copy the last step dict and override only "action"
            return elapsed, final_steps

        # FIX bugs 2 & 3: build the next step at PUSH time, not pop time
        # this way we know exactly which line and station we're moving TO
        for neighbor, travel_time, line in graph.get_neighbors(station):
            if (neighbor, line) in visited:
                continue

            penalty = TRANSFER_TIME if (current_line and line != current_line) else 0
            new_time = elapsed + travel_time + penalty

            # physical station name = everything before the "|" in the node id
            neighbor_station = neighbor.split("|")[0] if "|" in neighbor else neighbor  # fix bug 3: extract clean name to compare physical locations

            # FIX bug 3: transfer is detected HERE by checking same physical station + different line
            # previously it was detected at pop time, one hop too late
            # FIX bug 2: "line" here is the NEW line (destination), not current_line (old line)
            same_physical_station = (neighbor_station == station.split("|")[0])  # True only for transfer edges (Station|LineA -> Station|LineB)
            if current_line and line != current_line and same_physical_station:
                # we are crossing a transfer edge -> announce the NEW line
                action = "transfer"  # fix bug 3: labelled at the right station, fix bug 2: correct line stored below
            else:
                action = "continue"

            next_step = {"station": neighbor_station, "line": line, "action": action}  # fix bug 2: "line" is the NEW line, not the old one

            _counter += 1  # increment before each push so every entry gets a unique tie-breaker
            heapq.heappush(heap, (new_time, _counter, neighbor, line, steps + [next_step]))  # _counter in 2nd position, same as the initial heap entry

    return None, None  # no path found


# ======================================== CONNECTIVITY CHECK ========================================

def is_connected(graph):
    """Check if the graph is fully connected using BFS."""
    nodes = graph.get_all_nodes()
    if not nodes:
        return True

    # pick any station as starting point
    start = nodes[0]

    color = {station: 'white' for station in nodes}
    color[start] = 'grey'
    queue = deque([start])

    while queue:
        station = queue.popleft()
        for neighbor, travel_time, line in graph.get_neighbors(station):
            if color[neighbor] == 'white':
                color[neighbor] = 'grey'
                queue.append(neighbor)
        color[station] = 'black'

    # if every station turned black, the network is fully connected
    return all(c == 'black' for c in color.values())


# ======================================== TRANSFER STATIONS ========================================

def find_transfer_stations(graph):
    """
    Identifies stations that serve multiple lines, which are potential transfer points.
    We don't use it because in our itinerary we detect transfers per-route inside the Dijkstra method.
    """
    transfers = {}

    for station in graph.get_all_nodes():
        lines = set(line for neighbor, travel_time, line in graph.get_neighbors(station))
        if len(lines) > 1:
            transfers[station] = lines

    return transfers