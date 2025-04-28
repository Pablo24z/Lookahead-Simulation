import heapq
import random

def heuristics(a, b, Noise_Level=0):
    """Manhattan Distance with optional noise"""
    base = abs(a[0] - b[0]) + abs(a[1] - b[1])
    if Noise_Level is not None and Noise_Level > 0:
        noise_factor = 1 + random.uniform(-Noise_Level / 10, Noise_Level / 10)
        return base * noise_factor
    return base


def get_Neighbours(pos, grid):
    """Returns valid neighbours (not walls)"""
    neighbours = []
    row, col = pos
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            if grid[r][c] != 1:  # Not a wall
                neighbours.append((r, c))
    return neighbours

def A_Star_Search(grid, start, end, Noise_Level=0, Max_Depth=None):
    """A* Search with optional noise and depth limit"""
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristics(start, end, Noise_Level=Noise_Level)}

    explored_count = 0
    closed_set = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current in closed_set:
            continue
        closed_set.add(current)

        explored_count += 1
        if Max_Depth is not None and explored_count > Max_Depth:
            return None, explored_count  # Simulates lookahead failure

        if current == end:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, explored_count

        for neighbour in get_Neighbours(current, grid):
            tentative_g = g_score[current] + 1
            if neighbour not in g_score or tentative_g < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = tentative_g
                f_score[neighbour] = tentative_g + heuristics(neighbour, end, Noise_Level=Noise_Level)
                heapq.heappush(open_set, (f_score[neighbour], neighbour))

    return None, explored_count
