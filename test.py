import pygame

pygame.init()
image = pygame.image.load("assets/images/icons/coin/coin_gold.png")
tiles_per_row = image.get_width() // 16
print("Tiles per row:", tiles_per_row)
