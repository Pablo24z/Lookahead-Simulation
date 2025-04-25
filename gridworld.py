import pygame

#Grid Constants
Status_Bar_Height = 40
Tile_Size = 40
Grid_Width = 15
Grid_Height = 15
Screen_Width = 1000
Screen_Height = 800

#Colours

White = (255, 255, 255)
Black = (0, 0, 0)
Grey = (200, 200, 200)
Green = (0, 255, 0)
Red = (255, 0, 0)
Blue = (50, 100, 255)


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
                rect = pygame.Rect(col * Tile_Size, row * Tile_Size, Tile_Size, Tile_Size)

                if self.grid[row][col] == 1:
                    pygame.draw.rect(screen, Black, rect)
                elif (row, col) == self.start:
                    pygame.draw.rect(screen, Green, rect)
                elif (row, col) == self.end:
                    pygame.draw.rect(screen, Red, rect)
                else:
                    pygame.draw.rect(screen, White, rect)
                
                pygame.draw.rect(screen, Grey, rect, 1)
                


    def Toggle_Wall(self, pos):
        row, col = pos
        if self.grid[row][col] == 0:
            self.grid[row][col] = 1
        elif self.grid[row][col] == 1:
            self.grid[row][col] = 0