import pygame
import config

def load_tileset(path, tile_size):
    """
    Loads and slices a tileset image into individual tiles, scaled to match
    the in-game tile size defined in config.

    Args:
        path (str): Path to the tileset image (e.g. a sprite sheet)
        tile_size (int): Original width and height of each tile in the image

    Returns:
        List[pygame.Surface]: List of scaled tile surfaces
    """
    # Load image with alpha transparency and optimise for blitting
    image = pygame.image.load(path).convert_alpha()
    tiles = []

    # Determine number of tiles across and down
    tiles_x = image.get_width() // tile_size
    tiles_y = image.get_height() // tile_size

    # Extract and scale each tile
    for row in range(tiles_y):
        for col in range(tiles_x):
            rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
            tile_surface = image.subsurface(rect)

            # Scale to match game’s visual grid size (e.g. 40x40)
            scaled_tile = pygame.transform.scale(tile_surface, (config.Tile_Size, config.Tile_Size))
            tiles.append(scaled_tile)

    return tiles
