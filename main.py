import pygame
import sys
import random
from gridworld import GridWorld, Tile_Size, Screen_Height, Screen_Width, Grid_Width, Grid_Height
from lookahead import A_Star_Search
from metrics import Log_Path_Metrics

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((Screen_Width, Screen_Height))
pygame.display.set_caption("Lookahead Strategy Simulation")
clock = pygame.time.Clock()

# Modes and state tracking
screen_mode = "menu"
simulation_mode = None
selected_agent = None

# Grid and interaction
grid = GridWorld(Grid_Width, Grid_Height)
click_mode = 0
path = []
click_modes = ["Wall", "Start", "End"]
mouse_held = False
last_dragged_tile = None

# Animation state
agent_position = None
animation_index = 0
animation_active = False
animation_speed = 10
trail_tiles = []

# Fonts
default_font = pygame.font.SysFont(None, 24)


def get_grid_position(mouse_pos):
    x, y = mouse_pos
    row = y // Tile_Size
    col = x // Tile_Size
    if 0 <= row < Grid_Height and 0 <= col < Grid_Width:
        return row, col
    return None


def draw_mode_status_bar():
    pygame.draw.rect(screen, (230, 230, 230), (0, Tile_Size * Grid_Height, Screen_Width, 40))
    mode_text = default_font.render(f"Click Mode: {click_modes[click_mode]}", True, (0, 0, 0))
    help_text = default_font.render("SPACE = Switch mode | ENTER = Run path | D = Dynamic Event", True, (0, 0, 0))
    screen.blit(mode_text, (10, Tile_Size * Grid_Height + 5))
    screen.blit(help_text, (200, Tile_Size * Grid_Height + 5))


def draw_simulation_grid():
    for row in range(Grid_Height):
        for col in range(Grid_Width):
            cell_value = grid.grid[row][col]
            rect = pygame.Rect(col * Tile_Size, row * Tile_Size, Tile_Size, Tile_Size)

            if cell_value == 1:
                pygame.draw.rect(screen, (40, 40, 40), rect)
            else:
                pygame.draw.rect(screen, (240, 240, 240), rect)

            pygame.draw.rect(screen, (200, 200, 200), rect, 1)

            if (row, col) == grid.start:
                pygame.draw.circle(screen, (0, 200, 100), rect.center, Tile_Size // 3)
            elif (row, col) == grid.end:
                pygame.draw.rect(screen, (200, 50, 50), rect.inflate(-Tile_Size // 3, -Tile_Size // 3))


def draw_trail(trail):
    for i, (row, col) in enumerate(trail):
        rect = pygame.Rect(col * Tile_Size, row * Tile_Size, Tile_Size, Tile_Size)
        color = (50, 150, 255 - min(i * 8, 200))
        pygame.draw.rect(screen, color, rect)


def draw_agent_icon():
    if animation_active and agent_position:
        row, col = agent_position
        center = (col * Tile_Size + Tile_Size // 2, row * Tile_Size + Tile_Size // 2)
        pygame.draw.circle(screen, (0, 255, 255), center, Tile_Size // 4)


def draw_start_menu():
    screen.fill((30, 30, 30))
    title_font = pygame.font.Font("assets/fonts/RobotoMono-Bold.ttf", 50)
    button_font = pygame.font.Font("assets/fonts/RobotoMono-Regular.ttf", 26)

    title_text = title_font.render("Lookahead Strategy Simulation", True, (255, 255, 255))
    title_y = 120
    screen.blit(title_text, (Screen_Width // 2 - title_text.get_width() // 2, title_y))

    underline_y = title_y + title_text.get_height() + 5
    pygame.draw.line(screen, (255, 255, 255),
                     (Screen_Width // 2 - title_text.get_width() // 2, underline_y),
                     (Screen_Width // 2 + title_text.get_width() // 2, underline_y), 2)

    button_y_start = 250
    button_spacing = 70
    button_specs = [
        ("Depth-Limited Agent", "depth", button_y_start),
        ("Noisy Heuristic Agent", "noise", button_y_start + button_spacing * 2),
        ("Dynamic Environment Agent", "dynamic", button_y_start + button_spacing * 4),
    ]

    mouse_pos = pygame.mouse.get_pos()
    button_rects = []

    for label, agent_key, y in button_specs:
        btn_rect = pygame.Rect(Screen_Width // 2 - 250, y, 450, 50)
        is_hovered = btn_rect.collidepoint(mouse_pos)
        btn_color = (255, 204, 77) if is_hovered else (249, 168, 37)

        pygame.draw.rect(screen, btn_color, btn_rect)
        pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2)
        text = button_font.render(label, True, (0, 0, 0) if is_hovered else (255, 255, 255))
        screen.blit(text, (
            btn_rect.x + btn_rect.width // 2 - text.get_width() // 2,
            btn_rect.y + btn_rect.height // 2 - text.get_height() // 2
        ))
        button_rects.append((btn_rect, label))

    return button_rects


def draw_instructions_screen(agent_key):
    screen.fill((30, 30, 30))
    title_font = pygame.font.Font("assets/fonts/RobotoMono-Bold.ttf", 40)
    text_font = pygame.font.Font("assets/fonts/RobotoMono-Regular.ttf", 24)

    agent_titles = {
        "depth": "Depth-Limited Agent",
        "noise": "Noisy Heuristic Agent",
        "dynamic": "Dynamic Environment Agent"
    }
    agent_controls = {
        "depth": ["Press SPACE to switch modes (Wall, Start, End)", "Press ENTER to run the algorithm"],
        "noise": ["Press SPACE to switch modes", "Press ENTER to run with noisy heuristic (Noise Level = 5)"],
        "dynamic": ["Press SPACE to switch modes", "Press ENTER to run", "Press D to trigger a dynamic world change"]
    }

    title_text = title_font.render(agent_titles[agent_key], True, (255, 255, 255))
    title_y = 100
    screen.blit(title_text, (Screen_Width // 2 - title_text.get_width() // 2, title_y))

    underline_y = title_y + title_text.get_height() + 5
    pygame.draw.line(screen, (255, 255, 255),
                     (Screen_Width // 2 - title_text.get_width() // 2, underline_y),
                     (Screen_Width // 2 + title_text.get_width() // 2, underline_y), 2)

    for i, line in enumerate(agent_controls[agent_key]):
        instruction = text_font.render(line, True, (220, 220, 220))
        screen.blit(instruction, (80, underline_y + 40 + i * 35))

    button_font = pygame.font.Font("assets/fonts/RobotoMono-Regular.ttf", 26)
    button_defs = [
        ("Place Walls Randomly", "random", 360),
        ("Place Walls Manually", "manual", 420),
        ("Main Menu", "menu", 20)
    ]

    mouse_pos = pygame.mouse.get_pos()
    button_rects = []

    for label, action, y in button_defs:
        btn_rect = pygame.Rect(Screen_Width // 2 - 200, y, 400, 45) if action != "menu" else pygame.Rect(30, y, 250, 35)
        is_hovered = btn_rect.collidepoint(mouse_pos)
        btn_color = (255, 204, 77) if is_hovered else (249, 168, 37)

        pygame.draw.rect(screen, btn_color, btn_rect)
        pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2)
        text = button_font.render(label, True, (0, 0, 0) if is_hovered else (255, 255, 255))
        screen.blit(text, (
            btn_rect.x + btn_rect.width // 2 - text.get_width() // 2,
            btn_rect.y + btn_rect.height // 2 - text.get_height() // 2
        ))
        button_rects.append((btn_rect, action))

    return button_rects





# Main loop
running = True
frame_counter = 0  # New frame counter for controlling animation speed!

while running:
    if screen_mode == "menu":
        button_rects = draw_start_menu()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for rect, label in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if label == "Depth-Limited Agent":
                            selected_agent = "depth"
                        elif label == "Noisy Heuristic Agent":
                            selected_agent = "noise"
                        elif label == "Dynamic Environment Agent":
                            selected_agent = "dynamic"
                        screen_mode = "instructions"
        continue

    elif screen_mode == "instructions":
        button_rects = draw_instructions_screen(selected_agent)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for rect, action in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if action == "random":
                            grid = GridWorld(Grid_Width, Grid_Height)
                            for _ in range(85):
                                r = random.randint(0, Grid_Height - 1)
                                c = random.randint(0, Grid_Width - 1)
                                grid.grid[r][c] = 1
                            screen_mode = "simulation"
                        elif action == "manual":
                            grid = GridWorld(Grid_Width, Grid_Height)
                            screen_mode = "simulation"
                        elif action == "menu":
                            selected_agent = None
                            screen_mode = "menu"
        continue

    elif screen_mode == "simulation":
        screen.fill((30, 30, 30))
        draw_simulation_grid()
        if trail_tiles:
            draw_trail(trail_tiles)
        draw_agent_icon()
        draw_mode_status_bar()
        pygame.display.flip()

        # Agent walking animation control
        frame_counter += 1
        if animation_active and frame_counter >= animation_speed:
            frame_counter = 0
            if animation_index < len(path):
                agent_position = path[animation_index]
                trail_tiles.append(agent_position)
                animation_index += 1
            else:
                animation_active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    click_mode = (click_mode + 1) % 3

                elif event.key == pygame.K_RETURN:
                    if grid.start and grid.end:
                        # Clear previous path
                        trail_tiles = []
                        animation_index = 0
                        agent_position = None
                        animation_active = False

                        depth_limit = None
                        noise_level = 5
                        path = A_Star_Search(grid.grid, grid.start, grid.end, Noise_Level=noise_level)

                        if path:
                            animation_active = True
                            Log_Path_Metrics(grid.grid, grid.start, grid.end, path, Noise_Level=noise_level)
                        else:
                            print("Path Could Not be Found!")

                elif event.key == pygame.K_d and selected_agent == "dynamic":
                    for _ in range(10):
                        r = random.randint(0, Grid_Height - 1)
                        c = random.randint(0, Grid_Width - 1)
                        if (r, c) != grid.start and (r, c) != grid.end:
                            grid.grid[r][c] = 1

                    # After world changes, re-run pathfinding
                    trail_tiles = []
                    animation_index = 0
                    agent_position = None
                    animation_active = False

                    path = A_Star_Search(grid.grid, grid.start, grid.end)
                    if path:
                        animation_active = True
                    else:
                        print("No Path can be Found after world shift!")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_held = True
                pos = get_grid_position(pygame.mouse.get_pos())
                if pos:
                    if click_mode == 0:
                        grid.Toggle_Wall(pos)
                        path = []
                        animation_active = False
                        trail_tiles = []
                        last_dragged_tile = pos
                    elif click_mode == 1:
                        grid.start = pos
                        path = []
                        animation_active = False
                        trail_tiles = []
                    elif click_mode == 2:
                        grid.end = pos
                        path = []
                        animation_active = False
                        trail_tiles = []

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_held = False
                last_dragged_tile = None

        if mouse_held and click_mode == 0:
            pos = get_grid_position(pygame.mouse.get_pos())
            if pos and pos != last_dragged_tile:
                grid.Toggle_Wall(pos)
                path = []
                animation_active = False
                trail_tiles = []
                last_dragged_tile = pos

    clock.tick(60)

pygame.quit()
sys.exit()

