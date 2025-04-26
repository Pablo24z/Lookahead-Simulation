import pygame

# --- Screen ---
Tile_Size = 40
Grid_Width = 15
Grid_Height = 15
Screen_Width = 1000
Screen_Height = 800

# --- Colors ---
White = (255, 255, 255)
Black = (0, 0, 0)
Grey = (200, 200, 200)
Green = (0, 255, 0)
Red = (255, 0, 0)
Blue = (50, 100, 255)
Orange = (249, 168, 37)
Light_Orange = (255, 204, 77)
Background_Color = (30, 30, 30)

# --- Font paths ---
FONT_BOLD_PATH = "assets/fonts/RobotoMono-Bold.ttf"
FONT_REGULAR_PATH = "assets/fonts/RobotoMono-Regular.ttf"

# --- Fonts (initially empty) ---
FONT_BOLD_50 = None
FONT_BOLD_40 = None
FONT_BOLD_28 = None
FONT_REGULAR_26 = None
FONT_REGULAR_24 = None

# --- Setup function to initialize fonts AFTER pygame.init() ---
def setup_fonts():
    global FONT_BOLD_50, FONT_BOLD_40, FONT_BOLD_28, FONT_REGULAR_26, FONT_REGULAR_24
    FONT_BOLD_50 = pygame.font.Font(FONT_BOLD_PATH, 50)
    FONT_BOLD_40 = pygame.font.Font(FONT_BOLD_PATH, 40)
    FONT_BOLD_28 = pygame.font.Font(FONT_BOLD_PATH, 28)
    FONT_REGULAR_26 = pygame.font.Font(FONT_REGULAR_PATH, 26)
    FONT_REGULAR_24 = pygame.font.Font(FONT_REGULAR_PATH, 24)
