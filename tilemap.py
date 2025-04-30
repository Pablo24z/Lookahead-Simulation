import pygame
import config

def load_tileset(path, tile_size):
    image = pygame.image.load(path).convert_alpha()
    tiles = []
    sheet_width = image.get_width() // tile_size
    sheet_height = image.get_height() // tile_size

    for y in range(sheet_height):
        for x in range(sheet_width):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            tile = image.subsurface(rect)

            # Scale the 16x16 tile to match in-game Tile_Size (e.g. 40x40)
            tile = pygame.transform.scale(tile, (config.Tile_Size, config.Tile_Size))
            tiles.append(tile)

    return tiles
