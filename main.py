import pygame
import sys
import random
import os

import config
from tilemap import load_tileset
from simulation_controller import SimulationController

# UI drawing modules
from ui.ui_screens import draw_start_menu, draw_instructions_screen
from ui.draw_agent import draw_agent
from ui.draw_trail import draw_trail
from ui.hover_highlight import draw_hover_highlight
from ui.draw_side_panel import draw_side_panel

# Pygame setup
pygame.init()
config.setup_fonts()
screen = pygame.display.set_mode(
    (config.Screen_Width + 400, config.Screen_Height))
pygame.display.set_caption("Lookahead Strategy Simulation")
clock = pygame.time.Clock()

# Load and scale environment tiles
tileset = load_tileset(config.TILESET_PATH, config.TILESET_TILE_SIZE)

# Load animated coin frames (8 frames, 32x32 each)
coin_sheet = pygame.image.load(
    f"{config.ASSETS_DIR}/images/icons/coin/coin_gold.png").convert_alpha()
coin_frames = [coin_sheet.subsurface(
    pygame.Rect(i * 32, 0, 32, 32)) for i in range(8)]
coin_anim_index = 0
coin_anim_speed = 0.1

# Load player directional animations
player_sheet = pygame.image.load(
    f"{config.ASSETS_DIR}/images/player/player_model.png").convert_alpha()
direction_rows = {"down": 0, "left": 3, "right": 2, "up": 1}
player_frames = {
    direction: [player_sheet.subsurface(pygame.Rect(
        i * 16, row * 16, 16, 16)) for i in range(4)]
    for direction, row in direction_rows.items()
}

# Controller to manage game logic
controller = SimulationController()
screen_mode = "menu"

# Main game loop
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
                        controller.set_agent(
                            "depth" if "Depth" in label else
                            "noise" if "Noisy" in label else
                            "dynamic"
                        )
                        screen_mode = "instructions"
        continue

    elif screen_mode == "instructions":
        button_rects = draw_instructions_screen(
            screen,
            controller.selected_agent,
            controller.depth_value,
            controller.noise_value
        )
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for rect, action in button_rects:
                    if rect.collidepoint(mouse_pos):
                        if action == "increase_depth":
                            controller.set_depth(controller.depth_value + 1)
                        elif action == "decrease_depth":
                            controller.set_depth(controller.depth_value - 1)
                        elif action == "increase_noise":
                            controller.set_noise(controller.noise_value + 1)
                        elif action == "decrease_noise":
                            controller.set_noise(controller.noise_value - 1)
                        elif action == "random":
                            controller.clear_simulation_notifications()
                            controller.trigger_random_walls()
                            screen_mode = "simulation"
                        elif action == "manual":
                            controller.clear_simulation_notifications()
                            controller.reset_manual_grid()
                            screen_mode = "simulation"
                        elif action.startswith("benchmark"):
                            key = action.replace("benchmark", "")
                            name = {"1": "easy", "2": "medium",
                                    "3": "true_maze"}.get(key, "easy")
                            controller.clear_simulation_notifications()
                            controller.load_benchmark_map(name)
                            screen_mode = "simulation"
                        elif action == "menu":
                            controller.set_agent(None)
                            screen_mode = "menu"
        continue

    elif screen_mode == "simulation":
        # Update coin animation
        coin_anim_index = (coin_anim_index +
                           coin_anim_speed) % len(coin_frames)
        controller.update_notification_timer()
        screen.fill(config.Background_Color)

        # Draw grid, trail, agent, UI, and hover effects
        controller.grid.trail_tiles = controller.trail_tiles
        controller.grid.draw(screen, tileset, coin_frames,
                             coin_anim_index, controller.animation_active)
        draw_trail(screen, tileset, controller.trail_tiles)
        draw_agent(screen, player_frames, controller)
        back_button_rect = draw_side_panel(screen, controller)
        draw_hover_highlight(screen, tileset, coin_frames,
                             player_frames, coin_anim_index, controller)

        pygame.display.flip()

        # Advance pathfinding animation frame
        if controller.animation_active:
            controller.update_animation_step()

        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                controller.handle_key_input(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):  # Left or right click
                    mouse_pos = pygame.mouse.get_pos()
                    if back_button_rect and back_button_rect.collidepoint(mouse_pos):
                        controller.clear_simulation_notifications()
                        screen_mode = "instructions"
                    else:
                        controller.handle_mouse_input(mouse_pos, event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    controller.mouse_held = False
                elif event.button == 3:
                    controller.mouse_right_held = False
                controller.last_dragged_tile = None

        if controller.mouse_held or controller.mouse_right_held:
            controller.handle_mouse_drag(pygame.mouse.get_pos())

    clock.tick(120)

pygame.quit()
sys.exit()
