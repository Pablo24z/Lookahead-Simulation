import pygame
import config

def get_clean_trail(trail):
    cleaned = []
    prev = None
    for tile in trail:
        if tile != prev:
            cleaned.append(tile)
            prev = tile
    return cleaned

class GridWorld:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.start = None
        self.end = None


    def draw(self, screen, tileset, coin_frames, coin_anim_index, player_frames, player_pos, player_direction, player_anim_index, animation_active):
        for row in range(self.height):
            for col in range(self.width):
                tile_type = self.grid[row][col]

                # Select base tile (always draw appropriate grass)
                if row == 0 and col == 0:
                    base_tile = tileset[1]  # top-left corner
                elif row == 0 and col == self.width - 1:
                    base_tile = tileset[2]  # top-right corner
                elif row == self.height - 1 and col == 0:
                    base_tile = tileset[18]  # bottom-left corner
                elif row == self.height - 1 and col == self.width - 1:
                    base_tile = tileset[19]  # bottom-right corner
                elif row == 0:
                    base_tile = tileset[39]  # top edge
                elif row == self.height - 1:
                    base_tile = tileset[5]  # bottom edge
                elif col == 0:
                    base_tile = tileset[23]  # left edge
                elif col == self.width - 1:
                    base_tile = tileset[21]  # right edge
                else:
                    base_tile = tileset[3]   # center grass

                # Draw base grass tile
                screen.blit(base_tile, (col * config.Tile_Size, row * config.Tile_Size))

                # Define tile indices for straight and corner stepping stones
                stepping_stone_tiles = {
                    "up": 128,
                    "down": 128,
                    "left": 112,
                    "right": 112,
                    ("left", "up"): 145,
                    ("up", "left"): 113,
                    ("right", "up"): 147,
                    ("up", "right"): 111,
                    ("left", "down"): 111,
                    ("down", "left"): 111,
                    ("right", "down"): 113,
                    ("down", "right"): 145,
                    }


                # If wall, draw bush on top of the correct tile
                if tile_type == 1:
                    bush = tileset[149]
                    scale = int(config.Tile_Size * 0.85)
                    bush = pygame.transform.smoothscale(bush, (scale, scale))
                    x = col * config.Tile_Size + (config.Tile_Size - scale) // 2
                    y = row * config.Tile_Size + (config.Tile_Size - scale) // 2
                    screen.blit(bush, (x, y))


                # Draw coin at end position
                if (row, col) == self.end and coin_frames and (animation_active or not hasattr(self, "trail_tiles") or self.end not in self.trail_tiles):
                    index = int(coin_anim_index) % len(coin_frames)
                    frame = coin_frames[index]
                    scale = int(config.Tile_Size * 0.82)
                    frame = pygame.transform.smoothscale(frame, (scale, scale))
                    x = col * config.Tile_Size + (config.Tile_Size - scale) // 2
                    y = row * config.Tile_Size + (config.Tile_Size - scale) // 2 + 2
                    screen.blit(frame, (x, y))

                # --- Draw player model at start point if idle ---
                if self.start and not animation_active and (not hasattr(self, "trail_tiles") or self.start not in self.trail_tiles):
                    if self.end:
                        dx = self.end[0] - self.start[0]
                        dy = self.end[1] - self.start[1]
                        if abs(dx) > abs(dy):
                            facing = "down" if dx > 0 else "up"
                        else:
                            facing = "right" if dy > 0 else "left"
                    else:
                        facing = "down"

                    frame = player_frames[facing][0]
                    scale = int(config.Tile_Size * 0.8)
                    frame = pygame.transform.smoothscale(frame, (scale, scale))
                    px = self.start[1] * config.Tile_Size + (config.Tile_Size - scale) // 2
                    py = self.start[0] * config.Tile_Size + (config.Tile_Size - scale) // 2
                    screen.blit(frame, (px, py))


                # --- Draw player model at end point if animation just ended ---
                if self.end and not animation_active and hasattr(self, "trail_tiles") and self.trail_tiles:
                    if self.trail_tiles[-1] == self.end:
                        # Draw stepping stone under player
                        tile_index = 128  # default vertical stepping stone (adjust if needed)
                        stone = tileset[tile_index]
                        screen.blit(stone, (self.end[1] * config.Tile_Size, self.end[0] * config.Tile_Size))

                        # Draw player facing from second-to-last tile
                        if len(self.trail_tiles) >= 2:
                            prev = self.trail_tiles[-2]
                            dx = self.end[0] - prev[0]
                            dy = self.end[1] - prev[1]
                            if abs(dx) > abs(dy):
                                facing = "down" if dx > 0 else "up"
                            else:
                                facing = "right" if dy > 0 else "left"
                        else:
                            facing = "down"

                        frame = player_frames[facing][0]
                        scale = int(config.Tile_Size * 0.8)
                        frame = pygame.transform.smoothscale(frame, (scale, scale))
                        px = self.end[1] * config.Tile_Size + (config.Tile_Size - scale) // 2
                        py = self.end[0] * config.Tile_Size + (config.Tile_Size - scale) // 2
                        screen.blit(frame, (px, py))


                # Grid line overlay
                rect = pygame.Rect(col * config.Tile_Size, row * config.Tile_Size, config.Tile_Size, config.Tile_Size)
                pygame.draw.rect(screen, config.Light_Grey, rect, 1)

                # Draw stepping stones for cleaned trail
                if hasattr(self, "trail_tiles"):
                    trail = get_clean_trail(self.trail_tiles)

                    for i in range(1, len(trail) - 1):
                        prev = trail[i - 1]
                        curr = trail[i]
                        next = trail[i + 1]

                        dr1, dc1 = curr[0] - prev[0], curr[1] - prev[1]
                        dr2, dc2 = next[0] - curr[0], next[1] - curr[1]

                        dir_map = {(0, -1): "left", (0, 1): "right", (-1, 0): "up", (1, 0): "down"}

                        dir_from = dir_map.get((dr1, dc1))
                        dir_to = dir_map.get((dr2, dc2))

                        if dir_from and dir_to:
                            if dir_from == dir_to:
                                tile_index = stepping_stone_tiles[dir_from]
                            else:
                                tile_index = stepping_stone_tiles.get((dir_from, dir_to))
                            
                            if tile_index is not None and (curr != self.end or animation_active):

                                stone = tileset[tile_index]
                                screen.blit(stone, (curr[1] * config.Tile_Size, curr[0] * config.Tile_Size))


                    # Optionally draw stepping stone at start
                    if trail:
                        start_pos = trail[0]
                        tile_index = stepping_stone_tiles.get("down")  # default start direction
                        if tile_index is not None:
                            stone = tileset[tile_index]
                            screen.blit(stone, (start_pos[1] * config.Tile_Size, start_pos[0] * config.Tile_Size))





                

    def Toggle_Wall(self, pos):
        row, col = pos
        if self.grid[row][col] == 0:
            self.grid[row][col] = 1
        elif self.grid[row][col] == 1:
            self.grid[row][col] = 0
