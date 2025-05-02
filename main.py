import pygame
import sys
import random
import time
import config
from utils.map_utils import load_map, save_current_grid_to_map
from ui_screens import draw_start_menu, draw_instructions_screen
from tilemap import load_tileset
from gridworld import GridWorld
from config import Tile_Size, Screen_Height, Screen_Width, Grid_Width, Grid_Height
from lookahead import A_Star_Search
from metrics import Log_Path_Metrics


# --- Initialization ---
pygame.init()
config.setup_fonts()   # Important: Initialize fonts AFTER pygame.init()
screen = pygame.display.set_mode((Screen_Width + 400, Screen_Height))
tileset = load_tileset(config.TILESET_PATH, config.TILE_SIZE)
coin_sprite_sheet = pygame.image.load("assets/images/icons/coin/coin_gold.png").convert_alpha()
coin_frames = []
frame_width = coin_sprite_sheet.get_width() // 8  # 8 frames horizontally
frame_height = coin_sprite_sheet.get_height()

for i in range(8):
    frame_surface = coin_sprite_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
    coin_frames.append(frame_surface)


coin_anim_index = 0
coin_anim_speed = 0.1  # tweak for faster/slower spin

# Player sprite loading
player_sheet = pygame.image.load("assets/images/player/player_model.png").convert_alpha()

sheet_width, sheet_height = player_sheet.get_size()
frame_h = sheet_height // 16  # since you confirmed 16 rows
frame_w = 16  # most likely still correct, unless the sheet width says otherwise

#print(f"Frame dimensions: {frame_w} x {frame_h}")

direction_rows = {
    "down": 0,
    "left": 3,
    "right": 2,
    "up": 1
}

sheet_width, sheet_height = player_sheet.get_size()
frame_w, frame_h = 16, 16  # Verified size
frames_per_dir = 4         # 4 frames per direction (columns)

player_frames = {key: [] for key in direction_rows}

for direction, row in direction_rows.items():
    for i in range(frames_per_dir):
        rect = pygame.Rect(i * frame_w, row * frame_h, frame_w, frame_h)
        frame = player_sheet.subsurface(rect)
        player_frames[direction].append(frame)

if rect.right <= sheet_width and rect.bottom <= sheet_height:
    frame = player_sheet.subsurface(rect)
    player_frames[direction].append(frame)
else:
    print(f"Skipping out-of-bounds frame at row {row}, column {i}")


player_direction = "down"
player_anim_index = 0
player_anim_speed = 0.05
player_anim_counter = 0.0

pygame.display.set_caption("Lookahead Strategy Simulation")
clock = pygame.time.Clock()

# --- Global States ---
screen_mode = "menu"
selected_agent = None
depth_value = 15
noise_value = 5
nodes_explored = 0
search_time = 0

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
interpolation_speed = 0.03
agent_start = None
agent_end = None
animation_active = False

# --- Notification States ---
path_notification = None
path_notification_timer = 0
path_notification_colour = (255, 215, 0)

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
    if isinstance(path, list):
        path.clear()
    else:
        path = []



def draw_trail():
    if len(trail_tiles) < 2:
        return

    def get_direction(from_tile, to_tile):
        fr, fc = from_tile
        tr, tc = to_tile
        if fr == tr:
            return "right" if tc > fc else "left"
        elif fc == tc:
            return "down" if tr > fr else "up"
        return None  # Shouldn't happen for valid paths

    for i in range(1, len(trail_tiles) - 1):  # Skip first and last
        before = trail_tiles[i - 1]
        current = trail_tiles[i]
        after = trail_tiles[i + 1]

        dir_from = get_direction(before, current)
        dir_to = get_direction(current, after)

        if dir_from and dir_to:
            if dir_from == dir_to:
                tile_key = "vertical" if dir_from in ("up", "down") else "horizontal"
            else:
                tile_key = f"{dir_from}_{dir_to}"

            tile_index = config.trail_tileset_indices.get(tile_key)
            if tile_index is not None:
                tile = tileset[tile_index]
                r, c = current
                screen.blit(tile, (c * Tile_Size, r * Tile_Size))

    # Draw the first tile based on its direction
    start = trail_tiles[0]
    next_tile = trail_tiles[1]
    dir_start = get_direction(start, next_tile)
    if dir_start:
        key = "vertical" if dir_start in ("up", "down") else "horizontal"
        tile_index = config.trail_tileset_indices.get(key)
        if tile_index:
            screen.blit(tileset[tile_index], (start[1] * Tile_Size, start[0] * Tile_Size))

    # Draw the last tile based on its incoming direction
    end = trail_tiles[-1]
    prev_tile = trail_tiles[-2]
    dir_end = get_direction(prev_tile, end)
    if dir_end:
        key = "vertical" if dir_end in ("up", "down") else "horizontal"
        tile_index = config.trail_tileset_indices.get(key)
        if tile_index:
            screen.blit(tileset[tile_index], (end[1] * Tile_Size, end[0] * Tile_Size))





def draw_agent():
    global player_anim_index, player_anim_counter, player_direction

    if animation_active and agent_start and agent_end:
        # Regular walking logic
        sr, sc = agent_start
        er, ec = agent_end
        row = sr + (er - sr) * interpolation_progress
        col = sc + (ec - sc) * interpolation_progress
        center_x = int(col * Tile_Size + Tile_Size // 2)
        center_y = int(row * Tile_Size + Tile_Size // 2) + 2

        dx, dy = er - sr, ec - sc
        if abs(dx) > abs(dy):
            player_direction = "down" if dx > 0 else "up"
        else:
            player_direction = "right" if dy > 0 else "left"

        frames = player_frames[player_direction]
        frame_index = int(interpolation_progress * len(frames)) % len(frames)
        frame = frames[frame_index]

    elif grid.start and not animation_active:
        # Static player at start or end (idle)
        if hasattr(grid, "trail_tiles") and grid.trail_tiles and grid.trail_tiles[-1] == grid.end:
            # Player at end
            row, col = grid.end
            if len(grid.trail_tiles) >= 2:
                prev = grid.trail_tiles[-2]
                dx = row - prev[0]
                dy = col - prev[1]
                facing = "down" if dx > 0 else "up" if dx < 0 else "right" if dy > 0 else "left"
            else:
                facing = "down"
        else:
            # Player at start
            row, col = grid.start
            if grid.end:
                dx = grid.end[0] - row
                dy = grid.end[1] - col
                facing = "down" if abs(dx) > abs(dy) and dx > 0 else \
                         "up" if abs(dx) > abs(dy) else \
                         "right" if dy > 0 else "left"
            else:
                facing = "down"

        frame = player_frames[facing][0]
        center_x = col * Tile_Size + Tile_Size // 2
        center_y = row * Tile_Size + Tile_Size // 2

    else:
        return  # no player to draw

    scale = int(Tile_Size * 0.8)
    frame = pygame.transform.smoothscale(frame, (scale, scale))
    blit_x = int(center_x - scale // 2)
    blit_y = int(center_y - scale // 2)
    screen.blit(frame, (blit_x, blit_y))





def draw_hover_highlight():
    mouse_pos = pygame.mouse.get_pos()
    pos = get_grid_position(mouse_pos)
    if pos:
        row, col = pos
        if 0 <= row < Grid_Height and 0 <= col < Grid_Width:
            x = col * Tile_Size
            y = row * Tile_Size

            if click_mode == 0:
                bush = tileset[149].copy()
                scale = int(Tile_Size * 0.85)
                bush = pygame.transform.smoothscale(bush, (scale, scale))
                x = col * Tile_Size + (Tile_Size - scale) // 2
                y = row * Tile_Size + (Tile_Size - scale) // 2
                bush.set_alpha(160)
                screen.blit(bush, (x, y))


            elif click_mode == 1 and grid.start != (row, col):  # avoid overlap with real player
                player_img = player_frames["down"][0].copy()  # downward facing
                scale = int(Tile_Size * 0.8)
                player_img = pygame.transform.smoothscale(player_img, (scale, scale))
                player_img.set_alpha(150)

                x = col * Tile_Size + (Tile_Size - scale) // 2
                y = row * Tile_Size + (Tile_Size - scale) // 2
                screen.blit(player_img, (x, y))


            elif click_mode == 2 and coin_frames:
                # Animated opaque coin
                frame = coin_frames[int(coin_anim_index) % len(coin_frames)].copy()
                scale = int(Tile_Size * 0.82)
                frame = pygame.transform.smoothscale(frame, (scale, scale))
                frame.set_alpha(160)
                cx = x + (Tile_Size - scale) // 2
                cy = y + (Tile_Size - scale) // 2
                screen.blit(frame, (cx, cy))


def draw_side_panel():
    panel_rect = pygame.Rect(Screen_Width, 0, 400, Screen_Height)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect)

    entries = [
        ("Agent", selected_agent.capitalize() if selected_agent else "None"),
        ("Walls", str(sum(row.count(1) for row in grid.grid))),
        ("Path Length", str(len(path)) if path else "0"),
        ("Nodes Explored", str(nodes_explored)),
        ("Search Time", f"{search_time:.6f} s"),
    ]

    if selected_agent == "depth":
        entries.append(("Depth Limit", str(depth_value)))

    if selected_agent == "noise":
        entries.append(("Noise Level", str(noise_value)))

    y_offset = 20
    spacing = 40
    for label, value in entries:
        label_text = config.FONT_BOLD_28.render(label + ":", True, (255, 255, 255))
        value_text = config.FONT_REGULAR_24.render(value, True, (200, 200, 200))
        screen.blit(label_text, (Screen_Width + 20, y_offset))
        screen.blit(value_text, (Screen_Width + 20, y_offset + 25))
        y_offset += spacing + 10

    if path_notification and path_notification_timer > 0:
        notif_text = config.FONT_REGULAR_24.render(path_notification, True, path_notification_colour)
        screen.blit(notif_text, (Screen_Width + 20, y_offset + 20))
        y_offset += 60

    instruction_entries = [
        "Controls:",
        "SPACE - Switch Mode",
        "ENTER - Run Simulation"
    ]
    if selected_agent == "dynamic":
        instruction_entries.append("D - Dynamic Update")

    for instruction in instruction_entries:
        instruction_text = config.FONT_REGULAR_24.render(instruction, True, (255, 255, 255))
        screen.blit(instruction_text, (Screen_Width + 20, y_offset))
        y_offset += 30

    # --- Back Button ---
    back_button_rect = pygame.Rect(Screen_Width + 120, Screen_Height - 70, 160, 40)
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = back_button_rect.collidepoint(mouse_pos)
    btn_color = config.Light_Orange if is_hovered else config.Orange

    pygame.draw.rect(screen, btn_color, back_button_rect)
    pygame.draw.rect(screen, (255, 255, 255), back_button_rect, 2)

    back_text = config.FONT_REGULAR_26.render("Back", True, (0, 0, 0) if is_hovered else (255, 255, 255))
    screen.blit(back_text, (
        back_button_rect.centerx - back_text.get_width() // 2,
        back_button_rect.centery - back_text.get_height() // 2
    ))

    return back_button_rect


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
        button_rects = draw_instructions_screen(screen, selected_agent, depth_value, noise_value)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for rect, action in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if action == "increase_depth":
                            depth_value = min(depth_value + 1, 35) # Max depth is 35
                        elif action == "decrease_depth":
                            depth_value = max(depth_value - 1, 5) # Minimum depth is 5
                        elif action == "increase_noise":
                            noise_value = min(noise_value + 1, 10) # Max Noise Level is 10
                        elif action == "decrease_noise":
                            noise_value = max(noise_value - 1, 0) # Minimum Noise Level is 0
                        elif action == "random":
                            grid = GridWorld(Grid_Width, Grid_Height)
                            for _ in range(85):
                                r = random.randint(0, Grid_Height - 1)
                                c = random.randint(0, Grid_Width - 1)
                                grid.grid[r][c] = 1
                            screen_mode = "simulation"
                        elif action == "manual":
                            grid = GridWorld(Grid_Width, Grid_Height)
                            screen_mode = "simulation"
                        elif action == "benchmark":
                            grid = GridWorld(Grid_Width, Grid_Height)
                            loaded_grid, loaded_start, loaded_end = load_map("data/maps/map_easy.json")
                            grid.grid = loaded_grid
                            grid.start = loaded_start
                            grid.end = loaded_end
                            screen_mode = "simulation"
                        elif action == "menu":
                            selected_agent = None
                            screen_mode = "menu"
        continue

    elif screen_mode == "simulation":
        coin_anim_index += coin_anim_speed
        if coin_anim_index >= len(coin_frames):
            coin_anim_index = 0
        screen.fill((30, 30, 30))
        grid.trail_tiles = trail_tiles
        grid.draw(screen, tileset, coin_frames, coin_anim_index, animation_active)
        draw_trail()
        draw_agent()
        back_button_rect = draw_side_panel()
        draw_hover_highlight()
        pygame.display.flip()

        if animation_active:
            interpolation_progress += interpolation_speed
            if interpolation_progress >= 1.0:
                interpolation_progress = 0.0

                # Prevent repeated trail tiles
                if not trail_tiles or trail_tiles[-1] != agent_end:
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
                    start_time = time.perf_counter()
                    if grid.start and grid.end and grid.start != grid.end:
                        log_noise = noise_value if selected_agent == "noise" else None
                        log_depth = depth_value if selected_agent == "depth" else None
                        # Check if start and end are directly adjacent
                        if (abs(grid.start[0] - grid.end[0]) == 1 and grid.start[1] == grid.end[1]) or \
                            (abs(grid.start[1] - grid.end[1]) == 1 and grid.start[0] == grid.end[0]):
                            path_notification = "Too Close!"
                            path_notification_colour = (255, 50, 50)  # Red
                            path_notification_timer = 180
                            Log_Path_Metrics(
                                grid.grid,
                                grid.start,
                                grid.end,
                                None,  # No path possible
                                Agent_Type=selected_agent,
                                Noise_Level=log_noise,
                                Max_Depth=log_depth,
                                Success=False,
                                Nodes_Explored=nodes_explored,
                                Search_Time=search_time
                            )

                        else:
                            if selected_agent == "depth":
                                temp_path, nodes_explored = A_Star_Search(grid.grid, grid.start, grid.end, Noise_Level=None, Max_Depth = depth_value)
                            elif selected_agent == "noise":
                                temp_path, nodes_explored = A_Star_Search(grid.grid, grid.start, grid.end, Noise_Level=noise_value, Max_Depth = None)
                            elif selected_agent == "dynamic":
                                temp_path, nodes_explored = A_Star_Search(grid.grid, grid.start, grid.end, Noise_Level=None, Max_Depth = None)

                            end_time = time.perf_counter()
                            search_time = end_time - start_time
                            if temp_path is not None and len(temp_path) >= 2:
                                # Successful path found
                                path = temp_path
                                trail_tiles.clear()
                                trail_tiles.append(path[0])
                                current_step = 0
                                agent_start = path[0]
                                agent_end = path[1]
                                interpolation_progress = 0.0
                                animation_active = True
                                path_notification = "Path Found!"
                                path_notification_colour = (0, 255, 0)  # Green
                                path_notification_timer = 180
                                Log_Path_Metrics(grid.grid, grid.start, grid.end, path, Agent_Type=selected_agent, Noise_Level=log_noise, Max_Depth=log_depth, Success=True, Nodes_Explored=nodes_explored, Search_Time=search_time)

                            else:
                                # Path not found
                                if selected_agent == "depth":
                                    path_notification = "Path Blocked (Due to Depth Limit!)"
                                else:
                                    path_notification = "No Path Found!"
                                path_notification_colour = (255, 50, 50)
                                path_notification_timer = 180
                                Log_Path_Metrics(grid.grid, grid.start, grid.end, path, Agent_Type=selected_agent, Noise_Level=log_noise, Max_Depth=log_depth, Success=False, Nodes_Explored=nodes_explored, Search_Time=search_time)

                    else:
                        path_notification = "Invalid Start/End!"
                        path_notification_colour = (255, 50, 50)
                        path_notification_timer = 180
                elif event.key == pygame.K_d and selected_agent == "dynamic":
                    for _ in range(10):
                        r = random.randint(0, Grid_Height - 1)
                        c = random.randint(0, Grid_Width - 1)
                        if (r, c) != grid.start and (r, c) != grid.end:
                            grid.grid[r][c] = 1
                elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    from utils.map_utils import save_current_grid_to_map
                    save_current_grid_to_map(grid.grid, "data/maps/map_easy.json", grid.start, grid.end)

                    clear_path()
                    trail_tiles.clear()
                    animation_active = False
                    nodes_explored = 0
                    search_time = 0
                    path = []

                    if grid.start and grid.end:
                        start_time = time.perf_counter()
                        temp_path, nodes_explored = A_Star_Search(grid.grid, grid.start, grid.end)
                        end_time = time.perf_counter()
                        search_time = end_time - start_time

                        if temp_path is not None and len(temp_path) >= 2:
                            path = temp_path
                            trail_tiles.clear()
                            trail_tiles.append(path[0])
                            current_step = 0
                            agent_start = path[0]
                            agent_end = path[1]
                            interpolation_progress = 0.0
                            animation_active = True

                            path_notification = "New Path Found!"
                            path_notification_colour = (0, 255, 0)
                            path_notification_timer = 180
                        else:
                            path_notification = "No Path After Update"
                            path_notification_colour = (255, 50, 50)
                            path_notification_timer = 180
                    else:
                        path_notification = "Environment Updated!"
                        path_notification_colour = (100, 200, 255)
                        path_notification_timer = 180



            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if event.button == 1:  # Left-click
                    mouse_held = True
                    if back_button_rect.collidepoint(mouse_pos):
                        screen_mode = "instructions"
                        trail_tiles.clear()
                        path.clear()
                        animation_active = False
                        agent_start = None
                        agent_end = None
                        current_step = 0
                        interpolation_progress = 0.0
                        path_notification = None
                        path_notification_timer = 0
                        nodes_explored = 0
                        search_time = 0
                elif event.button == 3:  # Right-click
                    mouse_right_held = True
                pos = get_grid_position(pygame.mouse.get_pos())
                if pos:
                    if click_mode == 0:
                        grid.Toggle_Wall(pos)
                        clear_path()
                        trail_tiles.clear()
                        animation_active = False
                        nodes_explored = 0
                        search_time = 0
                        last_dragged_tile = pos
                    elif click_mode == 1:
                        if grid.grid[pos[0]][pos[1]] == 0 and pos != grid.end:
                            grid.start = pos
                            clear_path()
                            trail_tiles.clear()
                            animation_active = False
                            nodes_explored = 0
                            search_time = 0
                    elif click_mode == 2:
                        if grid.grid[pos[0]][pos[1]] == 0 and pos != grid.start:
                            grid.end = pos
                            clear_path()
                            trail_tiles.clear()
                            animation_active = False
                            search_time = 0
                            nodes_explored = 0

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


    #print("FPS:", clock.get_fps())
    clock.tick(120)

pygame.quit()
sys.exit()
