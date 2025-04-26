import pygame
import sys
import random
from ui_screens import draw_start_menu, draw_instructions_screen
from gridworld import GridWorld, Tile_Size, Screen_Height, Screen_Width, Grid_Width, Grid_Height
from lookahead import A_Star_Search
from metrics import Log_Path_Metrics

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((Screen_Width + 200, Screen_Height))
pygame.display.set_caption("Lookahead Strategy Simulation")
clock = pygame.time.Clock()

# --- Global States ---
screen_mode = "menu"
selected_agent = None

# --- Grid and Interaction States ---
grid = GridWorld(Grid_Width, Grid_Height)
click_mode = 0
click_modes = ["Wall", "Start", "End"]
path = []
mouse_held = False
mouse_right_held = False
last_dragged_tile = None

# --- Animation States ---
trail_tiles = []
current_step = 0
interpolation_progress = 0.0
interpolation_speed = 0.05
agent_start = None
agent_end = None
animation_active = False

# --- Fonts ---
default_font = pygame.font.SysFont("RobotoMono", 24)
title_font = pygame.font.SysFont("RobotoMono", 28, bold=True)

# --- Notification States ---
path_notification = None
path_notification_timer = 0

# --- Helper Functions ---
def get_grid_position(mouse_pos):
    x, y = mouse_pos
    if x >= Screen_Width:
        return None
    row = y // Tile_Size
    col = x // Tile_Size
    if 0 <= row < Grid_Height and 0 <= col < Grid_Width:
        return row, col
    return None

def clear_path():
    global path
    if path:
        path.clear()
    else:
        path = []

def draw_mode_status_bar():
    pygame.draw.rect(screen, (230, 230, 230), (0, Tile_Size * Grid_Height, Screen_Width + 200, 40))
    mode_text = default_font.render(f"Click Mode: {click_modes[click_mode]}", True, (0, 0, 0))
    help_text = default_font.render("SPACE: Switch | ENTER: Run | D: Dynamic", True, (0, 0, 0))
    screen.blit(mode_text, (10, Tile_Size * Grid_Height + 5))
    screen.blit(help_text, (300, Tile_Size * Grid_Height + 5))

def draw_grid():
    for row in range(Grid_Height):
        for col in range(Grid_Width):
            rect = pygame.Rect(col * Tile_Size, row * Tile_Size, Tile_Size, Tile_Size)
            color = (40, 40, 40) if grid.grid[row][col] == 1 else (240, 240, 240)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            if (row, col) == grid.start:
                pygame.draw.circle(screen, (0, 200, 100), rect.center, Tile_Size // 3)
            elif (row, col) == grid.end:
                pygame.draw.rect(screen, (200, 50, 50), rect.inflate(-Tile_Size // 3, -Tile_Size // 3))

def draw_trail():
    for i, (row, col) in enumerate(trail_tiles):
        rect = pygame.Rect(col * Tile_Size, row * Tile_Size, Tile_Size, Tile_Size)
        color = (50, 150, 255 - min(i * 8, 200))
        pygame.draw.rect(screen, color, rect)

def draw_agent():
    if animation_active and agent_start and agent_end:
        sr, sc = agent_start
        er, ec = agent_end
        row = sr + (er - sr) * interpolation_progress
        col = sc + (ec - sc) * interpolation_progress
        center_x = int(col * Tile_Size + Tile_Size // 2)
        center_y = int(row * Tile_Size + Tile_Size // 2)
        pygame.draw.circle(screen, (0, 255, 255), (center_x, center_y), Tile_Size // 4)


def draw_hover_highlight():
    mouse_pos = pygame.mouse.get_pos()
    pos = get_grid_position(mouse_pos)
    if pos:
        row, col = pos
        if 0 <= row < Grid_Height and 0 <= col < Grid_Width:
            hover_rect = pygame.Rect(col * Tile_Size, row * Tile_Size, Tile_Size, Tile_Size)
            s = pygame.Surface((Tile_Size, Tile_Size), pygame.SRCALPHA)  # Alpha surface
            # Dynamically change hover color depending on click_mode
            if click_mode == 0:  # Wall mode
                s.fill((255, 255, 0, 60))  # Soft yellow
            elif click_mode == 1:  # Start point
                s.fill((0, 255, 0, 60))    # Soft green
            elif click_mode == 2:  # End point
                s.fill((255, 0, 0, 60))    # Soft red

            screen.blit(s, hover_rect.topleft)




# --- Update draw_side_panel function ---
def draw_side_panel():
    panel_rect = pygame.Rect(Screen_Width, 0, 200, Screen_Height)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect)
    entries = [
        ("Agent", selected_agent.capitalize() if selected_agent else "None"),
        ("Walls", str(sum(row.count(1) for row in grid.grid))),
        ("Path Length", str(len(path)) if path else "0"),
        ("Noise", "5" if selected_agent == "noise" else "0"),
    ]
    y_offset = 20
    spacing = 40
    for label, value in entries:
        label_text = title_font.render(label + ":", True, (255, 255, 255))
        value_text = default_font.render(value, True, (200, 200, 200))
        screen.blit(label_text, (Screen_Width + 20, y_offset))
        screen.blit(value_text, (Screen_Width + 20, y_offset + 25))
        y_offset += spacing + 10
    if path_notification and path_notification_timer > 0:
        notif_text = default_font.render(path_notification, True, (255, 215, 0))
        screen.blit(notif_text, (Screen_Width + 20, y_offset + 20))


# --- Main Loop ---
running = True
while running:
    if screen_mode == "menu":
        button_rects = draw_start_menu(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for rect, label in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if "Depth-Limited" in label:
                            selected_agent = "depth"
                        elif "Noisy Heuristic" in label:
                            selected_agent = "noise"
                        elif "Dynamic Environment" in label:
                            selected_agent = "dynamic"
                        screen_mode = "instructions"
        continue
    elif screen_mode == "instructions":
        button_rects = draw_instructions_screen(screen, selected_agent)
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
        draw_grid()
        draw_trail()
        draw_agent()
        draw_mode_status_bar()
        draw_side_panel()
        draw_hover_highlight()
        pygame.display.flip()

        if animation_active:
            interpolation_progress += interpolation_speed
            if interpolation_progress >= 1.0:
                interpolation_progress = 0.0
                trail_tiles.append(agent_end)
                current_step += 1
                if current_step < len(path) - 1:
                    agent_start = path[current_step]
                    agent_end = path[current_step + 1]
                else:
                    animation_active = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    click_mode = (click_mode + 1) % 3
                elif event.key == pygame.K_RETURN:
                    if grid.start and grid.end and grid.start != grid.end:
                        temp_path = A_Star_Search(grid.grid, grid.start, grid.end, Noise_Level=5)
                        if temp_path is not None and len(temp_path) >= 2:
                            path = temp_path  # Only set the path if it's valid!
                            trail_tiles.clear()
                            trail_tiles.append(path[0])
                            current_step = 0
                            agent_start = path[0]
                            agent_end = path[1]
                            interpolation_progress = 0.0
                            animation_active = True
                            path_notification = "Path Found!"
                            path_notification_timer = 180
                            Log_Path_Metrics(grid.grid, grid.start, grid.end, path, Noise_Level=5)
                        else:
                            path_notification = "No Path Found"
                            path_notification_timer = 180
                    else:
                        path_notification = "Invalid Start/End!"
                        path_notification_timer = 180
                elif event.key == pygame.K_d and selected_agent == "dynamic":
                    for _ in range(10):
                        r = random.randint(0, Grid_Height - 1)
                        c = random.randint(0, Grid_Width - 1)
                        if (r, c) != grid.start and (r, c) != grid.end:
                            grid.grid[r][c] = 1
                    clear_path()
                    trail_tiles.clear()
                    animation_active = False
                    path = A_Star_Search(grid.grid, grid.start, grid.end)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left-click
                    mouse_held = True
                elif event.button == 3:  # Right-click
                    mouse_right_held = True
                pos = get_grid_position(pygame.mouse.get_pos())
                if pos:
                    if click_mode == 0:
                        grid.Toggle_Wall(pos)
                        clear_path()
                        trail_tiles.clear()
                        animation_active = False
                        last_dragged_tile = pos
                    elif click_mode == 1:
                        if grid.grid[pos[0]][pos[1]] == 0 and pos != grid.end:
                            grid.start = pos
                            clear_path()
                            trail_tiles.clear()
                            animation_active = False
                    elif click_mode == 2:
                        if grid.grid[pos[0]][pos[1]] == 0 and pos != grid.start:
                            grid.end = pos
                            clear_path()
                            trail_tiles.clear()
                            animation_active = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_held = False
                elif event.button == 3:
                    mouse_right_held = False
                last_dragged_tile = None


        if (mouse_held or mouse_right_held) and click_mode == 0:
            pos = get_grid_position(pygame.mouse.get_pos())
            if pos and pos != last_dragged_tile:
                if mouse_held and grid.grid[pos[0]][pos[1]] == 0:
                    grid.grid[pos[0]][pos[1]] = 1  # Place wall
                    clear_path()
                    trail_tiles.clear()
                    animation_active = False
                elif mouse_right_held and grid.grid[pos[0]][pos[1]] == 1:
                    grid.grid[pos[0]][pos[1]] = 0  # Remove wall
                    clear_path()
                    trail_tiles.clear()
                    animation_active = False
                last_dragged_tile = pos



    clock.tick(120)

pygame.quit()
sys.exit()
