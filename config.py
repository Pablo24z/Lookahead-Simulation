import logging
import pygame
import os

# Resolve the working directory so relative paths always work, even when called from outside the src folder
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SRC_DIR, "data")
ASSETS_DIR = os.path.join(SRC_DIR, "assets")
METRICS_DIR = os.path.join(DATA_DIR, "metrics")


logger = logging.getLogger(__name__)

logger.debug(
    f"Config file loaded from {SRC_DIR}.\n"
    f"Assets directory: {ASSETS_DIR}.\n"
    f"Data directory: {DATA_DIR}.\n"
    f"Metrics directory: {METRICS_DIR}.\n"
    f"Current working directory: {os.getcwd()}.\n"
)

# Grid and display settings
Tile_Size = 40             # In-game tile size (scaled from sprite)
Grid_Width = 15            # Number of columns
Grid_Height = 15           # Number of rows
Screen_Width = 1000        # Width of the game window
Screen_Height = 800        # Height of the game window

# Reproducibility
Global_Seed = None         # Set this to fix randomness for repeatable results

# File paths for assets
TILESET_TILE_SIZE = 16     # Raw sprite size in tileset (usually 16x16)
TILESET_PATH = f"{ASSETS_DIR}/images/tiles/forest/forest_tileset.png"

FONT_BOLD_PATH = f"{ASSETS_DIR}/fonts/RobotoMono-Bold.ttf"
FONT_REGULAR_PATH = f"{ASSETS_DIR}/fonts/RobotoMono-Regular.ttf"

# Trail tile indices for path visuals
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

# Colour definitions (RGB)
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

# Font references (set during initialisation)
FONT_BOLD_50 = None
FONT_BOLD_40 = None
FONT_BOLD_28 = None
FONT_REGULAR_26 = None
FONT_REGULAR_24 = None


def setup_fonts():
    """
    Loads font assets after pygame is initialised.
    Falls back to default system fonts if loading fails.
    """
    global FONT_BOLD_50, FONT_BOLD_40, FONT_BOLD_28, FONT_REGULAR_26, FONT_REGULAR_24
    try:
        FONT_BOLD_50 = pygame.font.Font(FONT_BOLD_PATH, 50)
        FONT_BOLD_40 = pygame.font.Font(FONT_BOLD_PATH, 40)
        FONT_BOLD_28 = pygame.font.Font(FONT_BOLD_PATH, 28)
        FONT_REGULAR_26 = pygame.font.Font(FONT_REGULAR_PATH, 26)
        FONT_REGULAR_24 = pygame.font.Font(FONT_REGULAR_PATH, 24)
    except Exception:
        FONT_BOLD_50 = pygame.font.SysFont(None, 50)
        FONT_BOLD_40 = pygame.font.SysFont(None, 40)
        FONT_BOLD_28 = pygame.font.SysFont(None, 28)
        FONT_REGULAR_26 = pygame.font.SysFont(None, 26)
        FONT_REGULAR_24 = pygame.font.SysFont(None, 24)
