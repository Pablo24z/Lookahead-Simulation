def get_grid_position(mouse_pos, screen_width, tile_size, grid_width, grid_height):
    """
    Converts the mouse's pixel position into a grid (row, col) position.

    Returns:
        (row, col) tuple if within grid bounds, otherwise None.
    """
    x, y = mouse_pos
    if x >= screen_width:
        return None

    row = y // tile_size
    col = x // tile_size

    if 0 <= row < grid_height and 0 <= col < grid_width:
        return row, col

    return None


def clear_path(path_ref):
    """
    Clears a path list in-place. Only affects mutable list objects.
    """
    if isinstance(path_ref, list):
        path_ref.clear()

    return path_ref
