import config


def draw_trail(screen, tileset, trail_tiles):
    """
    Draws the agent's trail on the grid, connecting each tile using directional pieces.
    Only works if there are at least 2 tiles in the trail.
    """

    if len(trail_tiles) < 2:
        return

    def get_direction(from_tile, to_tile):
        """
        Determines the direction of movement between two tiles.
        Assumes no diagonal paths.
        """
        fr, fc = from_tile
        tr, tc = to_tile
        if fr == tr:
            return "right" if tc > fc else "left"
        elif fc == tc:
            return "down" if tr > fr else "up"
        return None  # Diagonal movement not supported

    # Draw the middle part of the trail
    for i in range(1, len(trail_tiles) - 1):
        before = trail_tiles[i - 1]
        current = trail_tiles[i]
        after = trail_tiles[i + 1]

        dir_from = get_direction(before, current)
        dir_to = get_direction(current, after)

        if dir_from and dir_to:
            if dir_from == dir_to:
                tile_key = "vertical" if dir_from in ("up", "down") else "horizontal"
            else:
                tile_key = f"{dir_from}_{dir_to}"

            tile_index = config.trail_tileset_indices.get(tile_key)
            if tile_index is not None:
                row, col = current
                screen.blit(tileset[tile_index], (col * config.Tile_Size, row * config.Tile_Size))

    # Draw the start of the trail
    start = trail_tiles[0]
    next_tile = trail_tiles[1]
    dir_start = get_direction(start, next_tile)
    if dir_start:
        tile_key = "vertical" if dir_start in ("up", "down") else "horizontal"
        tile_index = config.trail_tileset_indices.get(tile_key)
        if tile_index is not None:
            screen.blit(tileset[tile_index], (start[1] * config.Tile_Size, start[0] * config.Tile_Size))

    # Draw the end of the trail
    end = trail_tiles[-1]
    prev_tile = trail_tiles[-2]
    dir_end = get_direction(prev_tile, end)
    if dir_end:
        tile_key = "vertical" if dir_end in ("up", "down") else "horizontal"
        tile_index = config.trail_tileset_indices.get(tile_key)
        if tile_index is not None:
            screen.blit(tileset[tile_index], (end[1] * config.Tile_Size, end[0] * config.Tile_Size))
