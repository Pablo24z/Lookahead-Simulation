import pygame
import config


class GridWorld:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.start = None
        self.end = None

    def draw(self, screen):
        for row in range(self.height):
            for col in range(self.width):
                rect = pygame.Rect(col * config.Tile_Size, row * config.Tile_Size, config.Tile_Size, config.Tile_Size)

                if self.grid[row][col] == 1:
                    pygame.draw.rect(screen, config.Black, rect)
                elif (row, col) == self.start:
                    pygame.draw.rect(screen, config.Green, rect)
                elif (row, col) == self.end:
                    pygame.draw.rect(screen, config.Red, rect)
                else:
                    pygame.draw.rect(screen, config.White, rect)

                pygame.draw.rect(screen, config.Grey, rect, 1)

    def Toggle_Wall(self, pos):
        row, col = pos
        if self.grid[row][col] == 0:
            self.grid[row][col] = 1
        elif self.grid[row][col] == 1:
            self.grid[row][col] = 0
