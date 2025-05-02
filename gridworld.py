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


    def draw(self, screen, tileset, coin_frames, coin_anim_index, animation_active):
        for row in range(self.height):
            for col in range(self.width):
                tile_type = self.grid[row][col]

                # Select appropriate base grass tile
                if row == 0 and col == 0:
                    base_tile = tileset[1]
                elif row == 0 and col == self.width - 1:
                    base_tile = tileset[2]
                elif row == self.height - 1 and col == 0:
                    base_tile = tileset[18]
                elif row == self.height - 1 and col == self.width - 1:
                    base_tile = tileset[19]
                elif row == 0:
                    base_tile = tileset[39]
                elif row == self.height - 1:
                    base_tile = tileset[5]
                elif col == 0:
                    base_tile = tileset[23]
                elif col == self.width - 1:
                    base_tile = tileset[21]
                else:
                    base_tile = tileset[3]

                # Draw base tile
                screen.blit(base_tile, (col * config.Tile_Size, row * config.Tile_Size))

                # Draw bushes (walls)
                if tile_type == 1:
                    bush = tileset[149]
                    scale = int(config.Tile_Size * 0.85)
                    bush = pygame.transform.smoothscale(bush, (scale, scale))
                    x = col * config.Tile_Size + (config.Tile_Size - scale) // 2
                    y = row * config.Tile_Size + (config.Tile_Size - scale) // 2
                    screen.blit(bush, (x, y))

                # Draw coin at end
                if (row, col) == self.end and coin_frames and (
                    animation_active or not hasattr(self, "trail_tiles") or self.end not in self.trail_tiles
                ):
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





                

    def Toggle_Wall(self, pos):
        row, col = pos
        if self.grid[row][col] == 0:
            self.grid[row][col] = 1
        elif self.grid[row][col] == 1:
            self.grid[row][col] = 0
