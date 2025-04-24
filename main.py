import pygame
import sys
from gridworld import GridWorld, Tile_Size, Screen_Height, Screen_Width, Grid_Width, Grid_Height
from lookahead import A_Star_Search
from metrics import Log_Path_Metrics


#initialise pygame
pygame.init()
screen = pygame.display.set_mode((Screen_Width, Screen_Height))
pygame.display.set_caption("Lookahead Strategy Simulation")
clock = pygame.time.Clock()

#create gridworld instance
grid = GridWorld(Grid_Width, Grid_Height)

#mouse modes: 0 = wall, 1 = start, 2 = end
click_mode = 0
path = []
modes = ["Wall", "Start", "End"]

font = pygame.font.SysFont(None, 24)

def get_Grid_Pos(mouse_pos):
    x, y = mouse_pos
    row = y // Tile_Size
    col = x // Tile_Size
    if 0 <= row < Grid_Height and 0 <= col < Grid_Width:
        return row, col
    return None


def draw_Mode_Text():
    pygame.draw.rect(screen, (230, 230, 230), (0, Tile_Size * Grid_Height, Screen_Width, 40))  # Status bar
    mode_text = font.render(f"Click Mode: {modes[click_mode]}", True, (0, 0, 0))
    help_text = font.render("SPACE = Switch mode | ENTER = Run path | ESC = Quit", True, (0, 0, 0))
    screen.blit(mode_text, (10, Tile_Size * Grid_Height + 5))
    screen.blit(help_text, (200, Tile_Size * Grid_Height + 5))

mouse_held = False
Last_Dragged_Tile = None

#main loop
running = True
while running:
    screen.fill((255, 255, 255))
    grid.draw(screen)
    draw_Mode_Text()
    #draw path
    if path:
        for cell in path:
            row, col = cell
            rect = pygame.Rect(col * Tile_Size, row * Tile_Size, Tile_Size, Tile_Size)
            pygame.draw.rect(screen, (50, 100, 255), rect) #blue path colour
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                click_mode = (click_mode + 1) % 3 #toggles between the modes
            elif event.key == pygame.K_RETURN:
                if grid.start and grid.end:
                    depth_limit = None
                    Noise_Level = 10
                    path = A_Star_Search(grid.grid, grid.start, grid.end, depth_limit = depth_limit, Noise_Level= Noise_Level)
                    Log_Path_Metrics(grid.grid, grid.start, grid.end, path)
                    if not path:
                        print("No Path can be Found. (Likely due to lookahead limit)")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_held = True
            pos = get_Grid_Pos(pygame.mouse.get_pos())
            if pos:
                if click_mode == 0:
                    grid.Toggle_Wall(pos)
                    path = []
                    Last_Dragged_Tile = pos
                elif click_mode == 1:
                    grid.start = pos
                    path = []
                elif click_mode == 2:
                    grid.end = pos
                    path = []

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False
            Last_Dragged_Tile = None

    if mouse_held and click_mode == 0:
        pos = get_Grid_Pos(pygame.mouse.get_pos())
        if pos and pos != Last_Dragged_Tile:
            grid.Toggle_Wall(pos)
            path = []
            Last_Dragged_Tile = pos

    clock.tick(60)
pygame.quit()
sys.exit()