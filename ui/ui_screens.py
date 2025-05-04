import pygame
import config


def draw_start_menu(screen):
    """
    Displays the main start menu with options for selecting agents.
    """
    screen.fill((30, 30, 30))

    title_font = config.FONT_BOLD_50
    button_font = config.FONT_REGULAR_26

    # Title
    title_text = title_font.render("Lookahead Strategy Simulation", True, (255, 255, 255))
    title_y = 120
    screen.blit(title_text, (config.Screen_Width // 2 - title_text.get_width() // 2, title_y))

    underline_y = title_y + title_text.get_height() + 5
    pygame.draw.line(
        screen, (255, 255, 255),
        (config.Screen_Width // 2 - title_text.get_width() // 2, underline_y),
        (config.Screen_Width // 2 + title_text.get_width() // 2, underline_y), 2
    )

    # Buttons for agent selection
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
        button_rect = pygame.Rect(config.Screen_Width // 2 - 250, y, 450, 50)
        is_hovered = button_rect.collidepoint(mouse_pos)
        colour = config.Light_Orange if is_hovered else config.Orange

        pygame.draw.rect(screen, colour, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)

        text = button_font.render(label, True, (0, 0, 0) if is_hovered else (255, 255, 255))
        screen.blit(text, (
            button_rect.centerx - text.get_width() // 2,
            button_rect.centery - text.get_height() // 2
        ))
        button_rects.append((button_rect, label))

    return button_rects


def draw_instructions_screen(screen, agent_key, depth_value, noise_value):
    """
    Displays configuration and controls for the selected agent type.
    """
    screen.fill((30, 30, 30))
    mouse_pos = pygame.mouse.get_pos()
    button_rects = []

    agent_titles = {
        "depth": "Depth-Limited Agent",
        "noise": "Noisy Heuristic Agent",
        "dynamic": "Dynamic Environment Agent"
    }

    agent_controls = {
        "depth": [
            "Press SPACE to switch modes (Wall, Start, End)",
            "Press ENTER to run the algorithm (Default Depth Limit = 15)"
        ],
        "noise": [
            "Press SPACE to switch modes",
            "Press ENTER to run with noisy heuristic (Default Noise Level = 5)"
        ],
        "dynamic": [
            "Press SPACE to switch modes",
            "Press ENTER to run",
            "Press D to trigger a dynamic world change"
        ]
    }

    # Agent title and underline
    title_text = config.FONT_BOLD_40.render(agent_titles[agent_key], True, (255, 255, 255))
    title_y = 100
    screen.blit(title_text, (config.Screen_Width // 2 - title_text.get_width() // 2, title_y))

    underline_y = title_y + title_text.get_height() + 5
    pygame.draw.line(
        screen, (255, 255, 255),
        (config.Screen_Width // 2 - title_text.get_width() // 2, underline_y),
        (config.Screen_Width // 2 + title_text.get_width() // 2, underline_y), 2
    )

    # Instruction lines
    y_offset = underline_y + 40
    for line in agent_controls[agent_key]:
        instr_text = config.FONT_REGULAR_24.render(line, True, (220, 220, 220))
        screen.blit(instr_text, (80, y_offset))
        y_offset += 35

    # Optional parameter sliders
    def draw_param_adjust(label, value, y_pos, key_prefix):
        param_text = config.FONT_REGULAR_24.render(f"{label}: {value}", True, (255, 255, 255))
        screen.blit(param_text, (config.Screen_Width // 2 - param_text.get_width() // 2, y_pos))

        plus_rect = pygame.Rect(config.Screen_Width // 2 + 80, y_pos, 30, 30)
        minus_rect = pygame.Rect(config.Screen_Width // 2 - 110, y_pos, 30, 30)

        for rect, symbol in [(plus_rect, "+"), (minus_rect, "-")]:
            colour = config.Light_Orange if rect.collidepoint(mouse_pos) else config.Orange
            pygame.draw.rect(screen, colour, rect)

            sym_text = config.FONT_REGULAR_26.render(symbol, True, (0, 0, 0))
            screen.blit(sym_text, (
                rect.x + rect.width // 2 - sym_text.get_width() // 2,
                rect.y + rect.height // 2 - sym_text.get_height() // 2
            ))

        button_rects.extend([
            (plus_rect, f"increase_{key_prefix}"),
            (minus_rect, f"decrease_{key_prefix}")
        ])

    if agent_key == "depth":
        draw_param_adjust("Depth", depth_value, y_offset + 20, "depth")

    if agent_key == "noise":
        draw_param_adjust("Noise", noise_value, y_offset + 20, "noise")

    # Simulation setup buttons
    main_button_defs = [
        ("Place Walls Randomly", "random", 360),
        ("Place Walls Manually", "manual", 420),
        ("Main Menu", "menu", 20)
    ]

    for label, action, y in main_button_defs:
        width = 250 if action == "menu" else 400
        x_pos = 30 if action == "menu" else config.Screen_Width // 2 - 200
        button_rect = pygame.Rect(x_pos, y, width, 45 if action != "menu" else 35)
        is_hovered = button_rect.collidepoint(mouse_pos)
        colour = config.Light_Orange if is_hovered else config.Orange

        pygame.draw.rect(screen, colour, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)

        text = config.FONT_REGULAR_26.render(label, True, (0, 0, 0) if is_hovered else (255, 255, 255))
        screen.blit(text, (
            button_rect.centerx - text.get_width() // 2,
            button_rect.centery - text.get_height() // 2
        ))

        button_rects.append((button_rect, action))

    # Benchmark test map buttons
    benchmark_defs = [
        ("Use Benchmark 1 (Easy)", "benchmark1", 480),
        ("Use Benchmark 2 (Medium)", "benchmark2", 540),
        ("Use Benchmark 3 (Hard)", "benchmark3", 600),
    ]

    for label, action, y in benchmark_defs:
        button_rect = pygame.Rect(config.Screen_Width // 2 - 200, y, 400, 45)
        is_hovered = button_rect.collidepoint(mouse_pos)
        colour = config.Light_Orange if is_hovered else config.Orange

        pygame.draw.rect(screen, colour, button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)

        text = config.FONT_REGULAR_26.render(label, True, (0, 0, 0) if is_hovered else (255, 255, 255))
        screen.blit(text, (
            button_rect.centerx - text.get_width() // 2,
            button_rect.centery - text.get_height() // 2
        ))

        button_rects.append((button_rect, action))

    return button_rects
