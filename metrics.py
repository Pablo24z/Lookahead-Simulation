import os
import csv
import shutil
import config
from datetime import datetime

# Keep track of which files have already been checked for archiving
cleared_files = set()


def Log_Path_Metrics(
    grid,
    start,
    end,
    path,
    Agent_Type="Unknown",
    Noise_Level=None,
    Max_Depth=None,
    Success=False,
    Nodes_Explored=None,
    Search_Time=None,
    is_benchmark=False,
    benchmark_name=None,
    seed=None
):
    """
    Logs all simulation results into a metrics CSV file. Supports both regular and benchmark modes.

    If a benchmark is active, the data is saved under a fixed file for that map/agent.
    Otherwise, logs are grouped by date and archived daily.
    """
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")

    agent_folder = f"{config.DATA_DIR}/metrics/{Agent_Type.lower()}"

    if is_benchmark:
        if not benchmark_name:
            raise ValueError(
                "Must provide benchmark_name when is_benchmark=True")

        filename = f"{benchmark_name}_{Agent_Type.lower()}_metrics.csv"
        filepath = os.path.join(agent_folder, "benchmark_data", filename)
        graph_folder = os.path.join(agent_folder, "benchmark_data", "graphs")

    else:
        filepath = os.path.join(
            agent_folder, f"{today_str}_{Agent_Type.lower()}_metrics.temp.csv")
        archive_folder = os.path.join(agent_folder, "archive")
        os.makedirs(archive_folder, exist_ok=True)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Auto-archive yesterday’s log (only for non-benchmark runs)
    if not is_benchmark and filepath not in cleared_files:
        if os.path.exists(filepath):
            modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if modified_time.date() != now.date():
                archived_name = os.path.join(
                    archive_folder,
                    f"{modified_time.strftime('%Y-%m-%d_%H-%M-%S')}_{Agent_Type.lower()}_metrics.temp.csv"
                )
                shutil.move(filepath, archived_name)
                cleared_files.discard(filepath)
        cleared_files.add(filepath)

    # Count walls and compute path stats
    walls = sum(row.count(1) for row in grid)
    path_length = len(path) if path else -1
    search_time_micro = int(
        Search_Time * 1_000_000) if Search_Time is not None else "N/A"

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
        "Search Time (μs)": search_time_micro,
        "Seed": seed if seed is not None else "N/A"
    }

    # Append row to CSV; add header if it's a new file
    with open(filepath, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=row_data.keys())

        if os.path.getsize(filepath) == 0:
            writer.writeheader()

        writer.writerow(row_data)
