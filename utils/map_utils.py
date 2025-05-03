import json
import os

def load_full_map(filepath):
    """
    Load a full benchmark map from a JSON file, including:
    - grid layout (2D list)
    - start position (row, col)
    - end position (row, col)

    Returns:
        dict with keys: "grid", "start", "end"
    """
    with open(filepath, "r") as f:
        return json.load(f)
