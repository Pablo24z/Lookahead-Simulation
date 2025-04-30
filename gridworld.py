import pygame
import config

class GridWorld:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.start = None
        self.end = None

    def draw(self, screen, tileset, coin_frames, coin_anim_index):
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
                    screen.blit(tileset[149], (col * config.Tile_Size, row * config.Tile_Size))
                    
                    if (row, col) == self.end:
                        raw_coin = coin_frames[int(coin_anim_index)]
                        
                        # Scale to ~60–70% of tile size
                        coin_size = int(config.Tile_Size * 0.6)
                        scaled_coin = pygame.transform.scale(raw_coin, (coin_size, coin_size))

                        # Center the coin in the tile
                        center_x = col * config.Tile_Size + (config.Tile_Size - coin_size) // 2
                        center_y = row * config.Tile_Size + (config.Tile_Size - coin_size) // 2
                        screen.blit(scaled_coin, (center_x, center_y))





                # Grid line overlay
                rect = pygame.Rect(col * config.Tile_Size, row * config.Tile_Size, config.Tile_Size, config.Tile_Size)
                pygame.draw.rect(screen, config.Light_Grey, rect, 1)



                # Start and End overlays
                if (row, col) == self.start:
                    pygame.draw.rect(screen, (0, 255, 0), rect, 3)  # Green border
                elif (row, col) == self.end:
                    pygame.draw.rect(screen, (255, 0, 0), rect, 3)  # Red border

    def Toggle_Wall(self, pos):
        row, col = pos
        if self.grid[row][col] == 0:
            self.grid[row][col] = 1
        elif self.grid[row][col] == 1:
            self.grid[row][col] = 0
