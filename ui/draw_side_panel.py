import pygame
import config


def draw_side_panel(screen, controller):
    """
    Draws the right-hand information and control panel on the right side of the screen.
    Displays agent info, statistics, current mode, controls, and a back button.
    """

    # Define and draw the panel background
    panel_rect = pygame.Rect(config.Screen_Width, 0, 400, config.Screen_Height)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect)

    # Display key statistics about the simulation state
    entries = [
        ("Agent", controller.selected_agent.capitalize() if controller.selected_agent else "None"),
        ("Walls", str(sum(row.count(1) for row in controller.grid.grid))),
        ("Path Length", str(len(controller.path)) if controller.path else "0"),
        ("Nodes Explored", str(controller.nodes_explored)),
        ("Search Time", f"{controller.search_time:.6f} s"),
    ]

    # Add relevant parameter depending on agent type
    if controller.selected_agent == "depth":
        entries.append(("Depth Limit", str(controller.depth_value)))
    elif controller.selected_agent == "noise":
        entries.append(("Noise Level", str(controller.noise_value)))

    # Draw each label-value pair
    y_offset = 20
    spacing = 40
    for label, value in entries:
        label_text = config.FONT_BOLD_28.render(f"{label}:", True, config.White)
        value_text = config.FONT_REGULAR_24.render(value, True, config.Light_Grey)
        screen.blit(label_text, (config.Screen_Width + 20, y_offset))
        screen.blit(value_text, (config.Screen_Width + 20, y_offset + 25))
        y_offset += spacing + 10

    # Show a notification message if one is active
    if controller.path_notification and controller.path_notification_timer > 0:
        notif_text = config.FONT_REGULAR_24.render(controller.path_notification, True, controller.path_notification_colour)
        screen.blit(notif_text, (config.Screen_Width + 20, y_offset + 20))
        y_offset += 60

    # Display keyboard instructions for user interaction
    mode_name = {0: "Wall", 1: "Start", 2: "End"}.get(controller.click_mode, "Unknown")
    instructions = [
        f"Click Mode: {mode_name}",
        "SPACE - Switch Mode",
        "ENTER - Run Simulation"
    ]
    if controller.selected_agent == "dynamic":
        instructions.append("D - Dynamic Update")

    for line in instructions:
        text = config.FONT_REGULAR_24.render(line, True, config.White)
        screen.blit(text, (config.Screen_Width + 20, y_offset))
        y_offset += 30

    # Draw the back button at the bottom
    back_button_rect = pygame.Rect(config.Screen_Width + 120, config.Screen_Height - 70, 160, 40)
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = back_button_rect.collidepoint(mouse_pos)
    btn_colour = config.Light_Orange if is_hovered else config.Orange

    pygame.draw.rect(screen, btn_colour, back_button_rect)
    pygame.draw.rect(screen, config.White, back_button_rect, 2)

    back_text = config.FONT_REGULAR_26.render("Back", True, (0, 0, 0) if is_hovered else config.White)
    screen.blit(back_text, (
        back_button_rect.centerx - back_text.get_width() // 2,
        back_button_rect.centery - back_text.get_height() // 2
    ))

    return back_button_rect
