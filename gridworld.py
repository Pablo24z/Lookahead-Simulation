import pygame
import config

class GridWorld:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.start = None
        self.end = None

    def draw(self, screen, tileset, coin_frames, coin_anim_index, player_frames, player_pos, player_direction, player_anim_index):
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

                # If wall, draw bush on top of the correct tile
                if tile_type == 1:
                    bush = tileset[149]
                    scale = int(config.Tile_Size * 0.85)
                    bush = pygame.transform.smoothscale(bush, (scale, scale))
                    x = col * config.Tile_Size + (config.Tile_Size - scale) // 2
                    y = row * config.Tile_Size + (config.Tile_Size - scale) // 2
                    screen.blit(bush, (x, y))


                # Draw coin at end position
                if (row, col) == self.end and coin_frames:
                    index = int(coin_anim_index) % len(coin_frames)
                    frame = coin_frames[index]
                    scale = int(config.Tile_Size * 0.82)
                    frame = pygame.transform.smoothscale(frame, (scale, scale))
                    x = col * config.Tile_Size + (config.Tile_Size - scale) // 2
                    y = row * config.Tile_Size + (config.Tile_Size - scale) // 2 + 2
                    screen.blit(frame, (x, y))

                # Grid line overlay
                rect = pygame.Rect(col * config.Tile_Size, row * config.Tile_Size, config.Tile_Size, config.Tile_Size)
                pygame.draw.rect(screen, config.Light_Grey, rect, 1)

                # Start and End overlays
                # Determine direction based on start and end positions
                if self.start:
                    player_row, player_col = self.start

                    if self.end:
                        end_row, end_col = self.end
                        dx = end_row - player_row
                        dy = end_col - player_col

                        if abs(dx) > abs(dy):
                            facing = "down" if dx > 0 else "up"
                        else:
                            facing = "right" if dy > 0 else "left"
                    else:
                        facing = "down"  # default if no end point

                    if (row, col) == self.start:
                        frame = player_frames[facing][0]  # idle frame
                        scale = int(config.Tile_Size * 0.8)
                        frame = pygame.transform.smoothscale(frame, (scale, scale))
                        px = col * config.Tile_Size + (config.Tile_Size - scale) // 2
                        py = row * config.Tile_Size + (config.Tile_Size - scale) // 2
                        screen.blit(frame, (px, py))



                

    def Toggle_Wall(self, pos):
        row, col = pos
        if self.grid[row][col] == 0:
            self.grid[row][col] = 1
        elif self.grid[row][col] == 1:
            self.grid[row][col] = 0
