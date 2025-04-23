import csv
import os
from datetime import datetime

def Log_Path_Metrics(grid, start, end, path):
    Wall_Count = sum(row.count(1) for row in grid)
    Grid_Size = len(grid) * len(grid[0])
    Success = path is not None
    Path_Length = len(path) if path else 0
    Time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #Printing to terminal

    print(f"[{Time}] Run Summary:")
    print(f"  Grid size: {Grid_Size} tiles")
    print(f"  Walls: {Wall_Count}")
    print(f"  Start: {start}, End: {end}")
    print(f"  Success: {Success}")
    print(f"  Path length: {Path_Length}")

    File_Path = "data/Metrics_Log.csv"
    File_Exists = os.path.isfile(File_Path)

    #saving to csv file
    with open("data/Metrics_Log.csv", mode="a", newline="") as f:
        writer = csv.writer(f)
        if not File_Exists:
             writer.writerow(["Timestamp", " GridSize", " WallCount", " Start", " End", " Success", " PathLength"])
        writer.writerow([Time , Grid_Size, Wall_Count, start, end, Success, Path_Length])