import pygame

# --- Screen ---
Tile_Size = 40
Grid_Width = 15
Grid_Height = 15
Screen_Width = 1000
Screen_Height = 800
Status_Bar_Height = 40

# Seed
Global_Seed = None

# Asset paths
TILESET_PATH = "assets/images/tiles/forest/forest_tileset.png"
TILE_SIZE = 16

# Trail
trail_tileset_indices = {
    "vertical": 128,
    "horizontal": 112,

    "up_right": 111,
    "right_up": 147,
    "right_down": 113,
    "down_right": 145,
    "down_left": 147,
    "left_down": 111,
    "left_up": 145,
    "up_left": 113,
}




# --- Colors ---
White = (255, 255, 255)
Black = (0, 0, 0)
Grey = (200, 200, 200)
Light_Grey = (150, 150, 150)
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
    try:
        FONT_BOLD_50 = pygame.font.Font(FONT_BOLD_PATH, 50)
        FONT_BOLD_40 = pygame.font.Font(FONT_BOLD_PATH, 40)
        FONT_BOLD_28 = pygame.font.Font(FONT_BOLD_PATH, 28)
        FONT_REGULAR_26 = pygame.font.Font(FONT_REGULAR_PATH, 26)
        FONT_REGULAR_24 = pygame.font.Font(FONT_REGULAR_PATH, 24)
    except Exception:
        # Fallback to default system font if loading fails
        FONT_BOLD_50 = pygame.font.SysFont(None, 50)
        FONT_BOLD_40 = pygame.font.SysFont(None, 40)
        FONT_BOLD_28 = pygame.font.SysFont(None, 28)
        FONT_REGULAR_26 = pygame.font.SysFont(None, 26)
        FONT_REGULAR_24 = pygame.font.SysFont(None, 24)
