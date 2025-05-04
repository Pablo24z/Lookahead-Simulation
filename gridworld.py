import pygame
import config

def get_clean_trail(trail):
    """
    Removes consecutive duplicate tiles from a trail.
    Useful for visual clarity if the same tile is added repeatedly.
    """
    cleaned = []
    previous = None
    for tile in trail:
        if tile != previous:
            cleaned.append(tile)
            previous = tile
    return cleaned


class GridWorld:
    def __init__(self, width, height):
        """
        Initialises a new grid-based environment.

        Args:
            width (int): Number of columns
            height (int): Number of rows
        """
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]  # 0 = empty, 1 = wall
        self.start = None
        self.end = None

    def draw(self, screen, tileset, coin_frames, coin_anim_index, animation_active):
        """
        Draws the current state of the grid on the screen.

        Includes:
        - Terrain base tiles
        - Walls (bushes)
        - Coin on the endpoint
        - Grid lines

        Args:
            screen (Surface): The Pygame display surface
            tileset (list): List of tile images
            coin_frames (list): Animated coin images
            coin_anim_index (float): Current animation frame index
            animation_active (bool): Whether the agent is currently moving
        """
        for row in range(self.height):
            for col in range(self.width):
                tile_type = self.grid[row][col]

                # Determine base tile type based on location
                if row == 0 and col == 0:
                    base_tile = tileset[1]  # Top-left corner
                elif row == 0 and col == self.width - 1:
                    base_tile = tileset[2]  # Top-right corner
                elif row == self.height - 1 and col == 0:
                    base_tile = tileset[18]  # Bottom-left corner
                elif row == self.height - 1 and col == self.width - 1:
                    base_tile = tileset[19]  # Bottom-right corner
                elif row == 0:
                    base_tile = tileset[39]  # Top edge
                elif row == self.height - 1:
                    base_tile = tileset[5]  # Bottom edge
                elif col == 0:
                    base_tile = tileset[23]  # Left edge
                elif col == self.width - 1:
                    base_tile = tileset[21]  # Right edge
                else:
                    base_tile = tileset[3]  # Default middle tile

                screen.blit(base_tile, (col * config.Tile_Size, row * config.Tile_Size))

                # Draw bush (wall) if applicable
                if tile_type == 1:
                    bush = tileset[149]
                    scale = int(config.Tile_Size * 0.85)
                    bush = pygame.transform.smoothscale(bush, (scale, scale))
                    x = col * config.Tile_Size + (config.Tile_Size - scale) // 2
                    y = row * config.Tile_Size + (config.Tile_Size - scale) // 2
                    screen.blit(bush, (x, y))

                # Draw coin if at end tile and still active
                if (row, col) == self.end and coin_frames:
                    should_draw = (
                        animation_active or
                        not hasattr(self, "trail_tiles") or
                        self.end not in self.trail_tiles
                    )
                    if should_draw:
                        frame_index = int(coin_anim_index) % len(coin_frames)
                        frame = coin_frames[frame_index]
                        scale = int(config.Tile_Size * 0.65)
                        frame = pygame.transform.smoothscale(frame, (scale, scale))
                        x = col * config.Tile_Size + (config.Tile_Size - scale) // 2
                        y = row * config.Tile_Size + (config.Tile_Size - scale) // 2
                        screen.blit(frame, (x, y))

                # Draw grid overlay
                rect = pygame.Rect(
                    col * config.Tile_Size,
                    row * config.Tile_Size,
                    config.Tile_Size,
                    config.Tile_Size
                )
                pygame.draw.rect(screen, config.Light_Grey, rect, 1)

    def Toggle_Wall(self, pos):
        """
        Toggles a tile between being a wall and empty space.

        Args:
            pos (tuple): (row, col) of the tile to toggle
        """
        row, col = pos
        self.grid[row][col] = 1 if self.grid[row][col] == 0 else 0
