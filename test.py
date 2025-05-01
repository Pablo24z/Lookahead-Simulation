import pygame

pygame.init()
player_sheet = pygame.image.load("assets/images/player/Unarmed_Walk_full.png")
sheet_width, sheet_height = player_sheet.get_size()
frame_h = sheet_height // 16  # since you confirmed 16 rows
frame_w = 16  # most likely still correct, unless the sheet width says otherwise

print(f"Frame dimensions: {frame_w} x {frame_h}")


