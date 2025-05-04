import heapq
import random

def heuristics(a, b, Noise_Level=0):
    """
    Calculates the estimated cost between two tiles using Manhattan Distance.

    Optionally introduces controlled noise to simulate an imperfect heuristic.

    Args:
        a (tuple[int, int]): First tile position (row, col)
        b (tuple[int, int]): Second tile position (row, col)
        Noise_Level (int | float): Amount of noise to apply (0 = none)

    Returns:
        float: Heuristic estimate of distance from a to b
    """
    base = abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    if Noise_Level and Noise_Level > 0:
        noise_factor = 1 + random.uniform(-Noise_Level / 10, Noise_Level / 10)
        return base * noise_factor

    return base


def get_Neighbours(pos, grid):
    """
    Returns valid neighbouring tiles that are not walls.

    Args:
        pos (tuple[int, int]): Current tile position
        grid (List[List[int]]): The environment grid (0 = empty, 1 = wall)

    Returns:
        List[tuple[int, int]]: List of accessible neighbour coordinates
    """
    neighbours = []
    row, col = pos
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            if grid[r][c] != 1:
                neighbours.append((r, c))

    return neighbours


def A_Star_Search(grid, start, end, Noise_Level=0, Max_Depth=None):
    """
    Runs A* search with optional noise and depth limit.

    Simulates lookahead planning by optionally cutting off early using Max_Depth.
    Supports imperfect heuristic guidance via the Noise_Level parameter.

    Args:
        grid (List[List[int]]): The map grid (0 = walkable, 1 = wall)
        start (tuple[int, int]): Starting tile
        end (tuple[int, int]): Goal tile
        Noise_Level (int, optional): Adds randomness to the heuristic
        Max_Depth (int, optional): Maximum nodes allowed to be expanded

    Returns:
        tuple[List[tuple[int, int]], int]: The final path (if any) and number of nodes explored
    """
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}  # Tracks where we came from
    g_score = {start: 0}  # Cost from start to current
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
            return None, explored_count

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path, explored_count

        for neighbour in get_Neighbours(current, grid):
            new_cost = g_score[current] + 1  # Assume all moves cost 1

            if neighbour not in g_score or new_cost < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = new_cost
                total_estimate = new_cost + heuristics(neighbour, end, Noise_Level=Noise_Level)
                f_score[neighbour] = total_estimate
                heapq.heappush(open_set, (total_estimate, neighbour))

    return None, explored_count  # No path found
