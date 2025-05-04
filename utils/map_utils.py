import json
import os


def load_full_map(filepath):
    """
    Loads a complete benchmark map from a JSON file.

    Expected structure in the JSON:
    {
        "grid": List of lists of integers (0 = empty, 1 = wall),
        "start": [row, col],
        "end": [row, col]
    }

    Args:
        filepath (str): Path to the .json map file

    Returns:
        dict: A dictionary with 'grid', 'start', and 'end' keys

    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValueError: If any of the required keys are missing
    """
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Map file not found: {filepath}")

    with open(filepath, "r") as f:
        data = json.load(f)

    required_keys = ("grid", "start", "end")
    if not all(key in data for key in required_keys):
        raise ValueError(
            f"Map file is missing required keys {required_keys}: {filepath}")

    return data
