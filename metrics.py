import csv
import os
from datetime import datetime

def Log_Path_Metrics(grid, start, end, path, Agent_Type="Unknown", Noise_Level=0, Max_Depth=None, Success=True):
    # Prepare the folder
    if not os.path.exists("data"):
        os.makedirs("data")
    
    filename = f"data/{Agent_Type.lower()}_metrics.csv"

    walls = sum(row.count(1) for row in grid)
    path_length = len(path) if path else -1  # -1 if no path
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Write headers only if file is new
    write_header = not os.path.exists(filename)

    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        
        if write_header:
            writer.writerow(["Start", "End", "Walls", "Path Length", "Agent Type", "Noise Level", "Max Depth", "Success", "Timestamp"])
        
        writer.writerow([
            start,
            end,
            walls,
            path_length,
            Agent_Type.capitalize(),
            Noise_Level if Noise_Level else "N/A",
            Max_Depth if Max_Depth is not None else "N/A",
            "Yes" if Success else "No",
            timestamp
        ])
