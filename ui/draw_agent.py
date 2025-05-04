import pygame
import config


def draw_agent(screen, player_frames, controller):
    """
    Responsible for drawing the agent (player character) on the grid.
    Depending on the current animation state, it either shows a moving animation
    or a static frame facing the appropriate direction.
    """

    # Handle Animated Movement
    if controller.animation_active and controller.agent_start and controller.agent_end:
        # Calculate interpolated position between start and end
        sr, sc = controller.agent_start
        er, ec = controller.agent_end
        row = sr + (er - sr) * controller.interpolation_progress
        col = sc + (ec - sc) * controller.interpolation_progress

        # Centre the image on the tile
        center_x = int(col * config.Tile_Size + config.Tile_Size // 2)
        center_y = int(row * config.Tile_Size + config.Tile_Size // 2) + 2  # Offset for visual balance

        # Determine direction of movement
        dx, dy = er - sr, ec - sc
        direction = "down" if dx > 0 else "up" if dx < 0 else "right" if dy > 0 else "left"

        # Select correct animation frame
        frames = player_frames[direction]
        frame_index = int(controller.interpolation_progress * len(frames)) % len(frames)
        frame = frames[frame_index]

    # Handle Static Idle
    elif controller.grid.start and not controller.animation_active:
        # If player has reached the endpoint, determine final facing direction
        if hasattr(controller.grid, "trail_tiles") and controller.grid.trail_tiles and controller.grid.trail_tiles[-1] == controller.grid.end:
            row, col = controller.grid.end
            facing = "down"  # Default
            if len(controller.grid.trail_tiles) >= 2:
                prev = controller.grid.trail_tiles[-2]
                dx = row - prev[0]
                dy = col - prev[1]
                facing = "down" if dx > 0 else "up" if dx < 0 else "right" if dy > 0 else "left"

        else:
            # If path not completed, determine facing direction from start to end
            row, col = controller.grid.start
            if not controller.grid.end:
                facing = "down"  # Default if no end is placed
            else:
                dx = controller.grid.end[0] - row
                dy = controller.grid.end[1] - col
                if abs(dx) > abs(dy):
                    facing = "down" if dx > 0 else "up"
                else:
                    facing = "right" if dy > 0 else "left"

        frame = player_frames[facing][0]
        center_x = col * config.Tile_Size + config.Tile_Size // 2
        center_y = row * config.Tile_Size + config.Tile_Size // 2

    else:
        return  # No agent to draw

    # Final Blitting
    scale = int(config.Tile_Size * 0.8)
    frame = pygame.transform.smoothscale(frame, (scale, scale))
    screen.blit(frame, (int(center_x - scale // 2), int(center_y - scale // 2)))
