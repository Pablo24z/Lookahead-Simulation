import json
import os

def save_current_grid_to_map(grid_data, filepath, start=None, end=None):
    """
    Saves the current grid layout to a JSON file for benchmarking purposes.

    Args:
        grid_data (List[List[int]]): 2D grid of walls (0 = empty, 1 = wall)
        filepath (str): Path to save JSON map
        start (tuple[int, int] | None): Optional start tile (row, col)
        end (tuple[int, int] | None): Optional end tile (row, col)
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    data = {
        "grid": grid_data,
        "start": list(start) if start else None,
        "end": list(end) if end else None
    }

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

    print(f"[✓] Map saved to {filepath}")


def load_map(filename):
    """Load a map file containing grid, start, and end points."""
    with open(filename, "r") as f:
        data = json.load(f)
        return data["grid"], tuple(data.get("start", ())), tuple(data.get("end", ()))

