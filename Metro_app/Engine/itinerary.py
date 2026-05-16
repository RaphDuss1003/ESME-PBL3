def format_time(seconds):
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


def split_station_and_line(value):
    if not isinstance(value, str):
        return value, None

    if "|" in value:
        station, line = value.rsplit("|", 1)  # split from the right to separate station and line
        return station, line

    return value, None


def normalize_step(step, next_step=None):
    if not isinstance(step, dict):
        return None

    station = step.get("station")
    line = step.get("line")
    action = step.get("action")

    station_name, line_from_station = split_station_and_line(station)

    if line is None:
        line = line_from_station  # use the line stored inside "Station|Line"

    if line is None and next_step is not None and isinstance(next_step, dict):
        next_line = next_step.get("line")
        next_station = next_step.get("station")

        if next_line is None:
            _, next_line = split_station_and_line(next_station)  # infer line from next station

        line = next_line  # first board step usually needs this

    return {
        "station": station_name,
        "line": line,
        "action": action
    }


def is_valid_steps(steps):
    if steps is None:
        return False

    if not isinstance(steps, list):
        return False

    for step in steps:
        if not isinstance(step, dict):
            return False

        if "station" not in step:
            return False

    return True


def create_itinerary_steps(steps):
    if not is_valid_steps(steps):
        return ["No route found."]

    if len(steps) == 0:
        return ["No route found."]

    if len(steps) == 1:
        only_step = normalize_step(steps[0])
        station = only_step["station"]
        line = only_step["line"]

        if line is None:
            return [f"You are already at {station} station."]
        return [f"You are already at {station} station, line {line}."]

    itinerary = []

    for i in range(len(steps)):
        current = steps[i]
        next_step = steps[i + 1] if i + 1 < len(steps) else None  # avoid index error at the end

        clean_step = normalize_step(current, next_step)

        station = clean_step["station"]
        line = clean_step["line"]
        action = clean_step["action"]

        if action == "board":
            if line is None:
                itinerary.append(f"Board at {station} station")
            else:
                itinerary.append(f"Board at {station} station, line {line}")

        elif action == "continue":
            itinerary.append(f"Continue through {station} station")

        elif action == "transfer":
            if line is None:
                itinerary.append(f"Transfer at {station} station")
            else:
                itinerary.append(f"Transfer at {station} station, take line {line}")

        elif action == "alight":
            if line is None:
                itinerary.append(f"Alight at {station} station")
            else:
                itinerary.append(f"Alight at {station} station, line {line}")

        else:
            if i == 0:
                itinerary.append(f"Board at {station} station, line {line}")
            elif i == len(steps) - 1:
                itinerary.append(f"Alight at {station} station, line {line}")
            else:
                itinerary.append(f"Continue through {station} station")

    return itinerary


def display_itinerary(steps, total_time):
    itinerary = create_itinerary_steps(steps)

    print()
    print("========== ITINERARY ==========")

    for instruction in itinerary:
        print(instruction)

    if is_valid_steps(steps) and len(steps) > 1:
        print(f"Estimated total time: {format_time(total_time)}")

    print("===============================")
    print()


def get_itinerary_as_text(steps, total_time):
    itinerary = create_itinerary_steps(steps)

    result = []
    result.append("========== ITINERARY ==========")

    for instruction in itinerary:
        result.append(instruction)

    if is_valid_steps(steps) and len(steps) > 1:
        result.append(f"Estimated total time: {format_time(total_time)}")

    result.append("===============================")

    return "\n".join(result)


def test_itinerary():
    test_steps = [
        {"station": "Argentine", "line": None, "action": "board"},
        {"station": "Charles de Gaulle - Étoile", "line": "1", "action": "continue"},
        {"station": "Charles de Gaulle - Étoile", "line": "2", "action": "transfer"},
        {"station": "Ternes", "line": "2", "action": "continue"},
        {"station": "Courcelles", "line": "2", "action": "continue"},
        {"station": "Monceau", "line": "2", "action": "alight"},
    ]

    test_time = 570
    display_itinerary(test_steps, test_time)


if __name__ == "__main__":
    test_itinerary()