import os
import csv
import shutil
from datetime import datetime

# Track cleared files to avoid re-archiving during the same session
cleared_files = set()

def Log_Path_Metrics(grid, start, end, path, Agent_Type="Unknown", Noise_Level=None, Max_Depth=None, Success=False, Nodes_Explored=None, Search_Time=None):
    """Logs simulation metrics to a CSV file, auto-archiving old files based on modification date."""

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    # --- Folder setup ---
    base_folder = os.path.join("data", "metrics", Agent_Type.lower())
    archive_folder = os.path.join(base_folder, "archive")
    os.makedirs(base_folder, exist_ok=True)
    os.makedirs(archive_folder, exist_ok=True)

    filename = os.path.join(base_folder, f"{today_str}_{Agent_Type.lower()}_metrics.csv")

    # --- Archive file if needed ---
    if filename not in cleared_files:
        if os.path.exists(filename):
            modified_time = datetime.fromtimestamp(os.path.getmtime(filename))
            if modified_time.date() != now.date():
                archived_name = os.path.join(
                    archive_folder,
                    f"{modified_time.strftime('%Y-%m-%d_%H-%M-%S')}_{Agent_Type.lower()}_metrics.csv"
                )
                shutil.move(filename, archived_name)
                # After archiving, don't log to the moved file
                cleared_files.discard(filename)

        # Now mark this day's file as cleared
        cleared_files.add(filename)


    # --- Data preparation ---
    walls = sum(row.count(1) for row in grid)
    path_length = len(path) if path else -1
    search_time_micro = int(Search_Time * 1_000_000) if Search_Time is not None else "N/A"

    row_data = {
        "Timestamp": timestamp_str,
        "Start": start,
        "End": end,
        "Walls": walls,
        "Path Length": path_length,
        "Agent Type": Agent_Type.capitalize(),
        "Noise Level": Noise_Level if Noise_Level is not None else "N/A",
        "Max Depth": Max_Depth if Max_Depth is not None else "N/A",
        "Success": "Yes" if Success else "No",
        "Nodes Explored": Nodes_Explored if Nodes_Explored is not None else "N/A",
        "Search Time (μs)": search_time_micro
    }

    # --- Write data to CSV ---
    with open(filename, mode="a", newline="", encoding="utf-8") as csvfile:
        fieldnames = list(row_data.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if os.path.getsize(filename) == 0:
            writer.writeheader()

        writer.writerow(row_data)
