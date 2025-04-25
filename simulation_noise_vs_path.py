from lookahead import A_Star_Search
from gridworld import GridWorld, Grid_Height, Grid_Width
import random

random.seed(42) #ensures reproducible random walls across runs


Start = (0, 0)
End = (Grid_Height - 1, Grid_Width - 1)

#loop the noise levels
for Noise in range(0, 11): #loops 0 - 10
    Success_Count = 0
    Total_Cost = 0

    for _ in range(10): #10 trails per noise level
        grid = GridWorld(Grid_Width, Grid_Height)

        for _ in range(85):
            r = random.randint(0, Grid_Height - 1)
            c = random.randint(0, Grid_Width - 1)
            grid.grid[r][c] = 1


        grid.start = Start
        grid.end = End

        path = A_Star_Search(grid.grid, Start, End, Noise_Level=Noise)
        if path:
            Success_Count += 1
            Total_Cost += len(path)

    Average_Cost = Total_Cost / Success_Count if Success_Count > 0 else 0
    print(f"Noise: {Noise}, Successes: {Success_Count}, Average Path Cost: {Average_Cost:.2f}")
