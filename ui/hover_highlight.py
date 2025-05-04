import pygame
import config
from utils.game_state import get_grid_position


def draw_hover_highlight(screen, tileset, coin_frames, player_frames, coin_anim_index, controller):
    """
    Draws a translucent overlay on the tile under the mouse cursor.
    Adjusts depending on what mode the user is currently in (Wall/Start/End).
    """
    mouse_pos = pygame.mouse.get_pos()
    tile_size = config.Tile_Size

    pos = get_grid_position(
        mouse_pos,
        config.Screen_Width,
        tile_size,
        controller.grid.width,
        controller.grid.height
    )

    if not pos:
        return

    row, col = pos
    x = col * tile_size
    y = row * tile_size

    # If hovering over a wall and not in wall mode, don’t show highlight
    if controller.grid.grid[row][col] == 1 and controller.click_mode != 0:
        return

    if controller.click_mode == 0:
        # Preview for placing a wall
        bush = tileset[149].copy()
        scale = int(tile_size * 0.85)
        bush = pygame.transform.smoothscale(bush, (scale, scale))
        bush.set_alpha(160)
        screen.blit(bush, (x + (tile_size - scale) //
                    2, y + (tile_size - scale) // 2))

    elif controller.click_mode == 1 and controller.grid.start != (row, col):
        # Preview for placing the player
        player_img = player_frames["down"][0].copy()
        scale = int(tile_size * 0.8)
        player_img = pygame.transform.smoothscale(player_img, (scale, scale))
        player_img.set_alpha(150)
        screen.blit(player_img, (x + (tile_size - scale) //
                    2, y + (tile_size - scale) // 2))

    elif controller.click_mode == 2 and coin_frames:
        # Preview for placing the goal (coin)
        frame = coin_frames[int(coin_anim_index) % len(coin_frames)].copy()
        scale = int(tile_size * 0.65)
        frame = pygame.transform.smoothscale(frame, (scale, scale))
        frame.set_alpha(160)
        screen.blit(frame, (x + (tile_size - scale) //
                    2, y + (tile_size - scale) // 2))
