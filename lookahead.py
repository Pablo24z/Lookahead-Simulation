import heapq
import random

def heuristics(a, b, Noise_Level=0):
    """Manhattan Distance"""
    Base = abs(a[0] - b[0]) + abs(a[1] - b[1])
    if Noise_Level > 0:
        Noise_Factor = 1 + random.uniform(-Noise_Level / 10, Noise_Level / 10)
        return Base * Noise_Factor
    return Base


def get_Neighbours(pos, grid):
    neighbours = []
    row, col = pos
    Directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] #to go up, down, left and right

    for dr, dc in Directions:
        r, c = row + dr, col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            if grid[r][c] != 1: # not a wall
                neighbours.append((r, c))
    return neighbours

def A_Star_Search(grid, start, end, depth_limit=None, Noise_Level=0):
    explored_count = 0
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristics(start, end, Noise_Level=Noise_Level)}

    while open_set:
        _, current = heapq.heappop(open_set)

        explored_count += 1
        if depth_limit is not None and explored_count > depth_limit:
            return None #Simulates lookahead failure

        if current == end:
            #reconstructs path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        
        for neighbour in get_Neighbours(current, grid):
            tentative_g = g_score[current] + 1
            if neighbour not in g_score or tentative_g < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = tentative_g
                f_score[neighbour] = tentative_g + heuristics(neighbour, end, Noise_Level=Noise_Level)
                heapq.heappush(open_set, (f_score[neighbour], neighbour))

    return None