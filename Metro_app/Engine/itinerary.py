def format_time(seconds):
    """
    Convert a number of seconds into a readable format.
    """

    if seconds is None:
        return "unknown time"

    if not isinstance(seconds, int) or seconds < 0:
        return "invalid time"

    minutes = seconds // 60
    remaining_seconds = seconds % 60

    if minutes == 0:
        return f"{remaining_seconds} seconds"

    if remaining_seconds == 0:
        if minutes == 1:
            return "1 minute"
        return f"{minutes} minutes"

    if minutes == 1:
        return f"1 minute {remaining_seconds} seconds"

    return f"{minutes} minutes {remaining_seconds} seconds"


def is_valid_path(path):
    """
    Check if the path has the correct format.

    A valid path must be a list of dictionaries.
    Each dictionary must contain:
    - "station"
    - "line"
    """

    if not isinstance(path, list):
        return False

    if len(path) == 0:
        return True

    for step in path:
        if not isinstance(step, dict):
            return False

        if "station" not in step or "line" not in step:
            return False

        if not isinstance(step["station"], str):
            return False

        if not isinstance(step["line"], str):
            return False

    return True


def create_itinerary_steps(path):
    """
    Convert a calculated path into readable itinerary instructions.

    Example output:
    [
        "Board at Argentine station, line 1",
        "Continue through Charles de Gaulle - Étoile station",
        "Transfer at Charles de Gaulle - Étoile station, take line 2",
        "Continue through Ternes station",
        "Alight at Monceau station, line 2"
    ]
    """

    steps = []

    if not is_valid_path(path):
        return ["Invalid path format."]

    if len(path) == 0:
        return ["No route found."]

    if len(path) == 1:
        station = path[0]["station"]
        line = path[0]["line"]
        return [f"You are already at {station} station, line {line}."]

    start_station = path[0]["station"]
    start_line = path[0]["line"]

    end_station = path[-1]["station"]
    end_line = path[-1]["line"]

    steps.append(f"Board at {start_station} station, line {start_line}")

    previous_station = path[0]["station"]
    previous_line = path[0]["line"]

    for i in range(1, len(path)):
        current_station = path[i]["station"]
        current_line = path[i]["line"]

        is_last_station = i == len(path) - 1

        if current_station == previous_station and current_line != previous_line:
            steps.append(
                f"Transfer at {current_station} station, take line {current_line}"
            )

        elif not is_last_station:
            steps.append(f"Continue through {current_station} station")

        previous_station = current_station
        previous_line = current_line

    steps.append(f"Alight at {end_station} station, line {end_line}")

    return steps


def display_itinerary(path, total_time):
    """
    Display the itinerary in the console.

    Parameters:
    - path: list of dictionaries with station and line
    - total_time: total travel time in seconds
    """

    steps = create_itinerary_steps(path)

    print()
    print("========== ITINERARY ==========")

    for step in steps:
        print(step)

    if is_valid_path(path) and len(path) > 1:
        print(f"Estimated total time: {format_time(total_time)}")

    print("===============================")
    print()


def get_itinerary_as_text(path, total_time):
    """
    Return the itinerary as a string instead of printing it.

    This can be useful for the interface module.
    """

    steps = create_itinerary_steps(path)
    result = []

    result.append("========== ITINERARY ==========")

    for step in steps:
        result.append(step)

    if is_valid_path(path) and len(path) > 1:
        result.append(f"Estimated total time: {format_time(total_time)}")

    result.append("===============================")

    return "\n".join(result)


def test_itinerary():
    """
    Test function using the example from the project subject.
    """

    test_path = [
        {"station": "Argentine", "line": "1"},
        {"station": "Charles de Gaulle - Étoile", "line": "1"},
        {"station": "Charles de Gaulle - Étoile", "line": "2"},
        {"station": "Ternes", "line": "2"},
        {"station": "Courcelles", "line": "2"},
        {"station": "Monceau", "line": "2"},
    ]

    test_time = 570

    display_itinerary(test_path, test_time)


if __name__ == "__main__":
    test_itinerary()