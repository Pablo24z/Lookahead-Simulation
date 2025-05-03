import pygame
import config

def draw_start_menu(screen):
    screen.fill((30, 30, 30))

    title_font = config.FONT_BOLD_50
    button_font = config.FONT_REGULAR_26

    title_text = title_font.render("Lookahead Strategy Simulation", True, (255, 255, 255))
    title_y = 120
    screen.blit(title_text, (config.Screen_Width // 2 - title_text.get_width() // 2, title_y))

    underline_y = title_y + title_text.get_height() + 5
    pygame.draw.line(screen, (255, 255, 255),
                     (config.Screen_Width // 2 - title_text.get_width() // 2, underline_y),
                     (config.Screen_Width // 2 + title_text.get_width() // 2, underline_y), 2)

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
        btn_rect = pygame.Rect(config.Screen_Width // 2 - 250, y, 450, 50)
        is_hovered = btn_rect.collidepoint(mouse_pos)
        btn_color = config.Light_Orange if is_hovered else config.Orange

        pygame.draw.rect(screen, btn_color, btn_rect)
        pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2)

        text = button_font.render(label, True, (0, 0, 0) if is_hovered else (255, 255, 255))
        screen.blit(text, (
            btn_rect.x + btn_rect.width // 2 - text.get_width() // 2,
            btn_rect.y + btn_rect.height // 2 - text.get_height() // 2
        ))
        button_rects.append((btn_rect, label))

    return button_rects

# Updated draw_instructions_screen

def draw_instructions_screen(screen, agent_key, depth_value, noise_value):
    screen.fill((30, 30, 30))

    agent_titles = {
        "depth": "Depth-Limited Agent",
        "noise": "Noisy Heuristic Agent",
        "dynamic": "Dynamic Environment Agent"
    }
    agent_controls = {
        "depth": ["Press SPACE to switch modes (Wall, Start, End)", "Press ENTER to run the algorithm (Default Depth Limit = 15)"],
        "noise": ["Press SPACE to switch modes", "Press ENTER to run with noisy heuristic (Default Noise Level = 5)"],
        "dynamic": ["Press SPACE to switch modes", "Press ENTER to run", "Press D to trigger a dynamic world change"]
    }

    # --- Title ---
    title_text = config.FONT_BOLD_40.render(agent_titles[agent_key], True, (255, 255, 255))
    title_y = 100
    screen.blit(title_text, (config.Screen_Width // 2 - title_text.get_width() // 2, title_y))

    # --- Underline ---
    underline_y = title_y + title_text.get_height() + 5
    pygame.draw.line(screen, (255, 255, 255),
                     (config.Screen_Width // 2 - title_text.get_width() // 2, underline_y),
                     (config.Screen_Width // 2 + title_text.get_width() // 2, underline_y), 2)

    # --- Controls Text ---
    y_offset = underline_y + 40
    for line in agent_controls[agent_key]:
        instruction = config.FONT_REGULAR_24.render(line, True, (220, 220, 220))
        screen.blit(instruction, (80, y_offset))
        y_offset += 35

    mouse_pos = pygame.mouse.get_pos()
    button_rects = []

    # --- Depth Value (only for Depth Agent) ---
    if agent_key == "depth":
        depth_text = config.FONT_REGULAR_24.render(f"Depth: {depth_value}", True, (255, 255, 255))
        screen.blit(depth_text, (config.Screen_Width // 2 - depth_text.get_width() // 2, y_offset + 20))

        # + Button
        plus_rect = pygame.Rect(config.Screen_Width // 2 + 80, y_offset + 20, 30, 30)
        pygame.draw.rect(screen, config.Light_Orange if plus_rect.collidepoint(mouse_pos) else config.Orange, plus_rect)
        plus_symbol = config.FONT_REGULAR_26.render("+", True, (0, 0, 0))
        screen.blit(plus_symbol, (plus_rect.x + plus_rect.width // 2 - plus_symbol.get_width() // 2, plus_rect.y + plus_rect.height // 2 - plus_symbol.get_height() // 2))

        # - Button
        minus_rect = pygame.Rect(config.Screen_Width // 2 - 110, y_offset + 20, 30, 30)
        pygame.draw.rect(screen, config.Light_Orange if minus_rect.collidepoint(mouse_pos) else config.Orange, minus_rect)
        minus_symbol = config.FONT_REGULAR_26.render("-", True, (0, 0, 0))
        screen.blit(minus_symbol, (minus_rect.x + minus_rect.width // 2 - minus_symbol.get_width() // 2, minus_rect.y + minus_rect.height // 2 - minus_symbol.get_height() // 2))

        button_rects.append((plus_rect, "increase_depth"))
        button_rects.append((minus_rect, "decrease_depth"))

    if agent_key == "noise":
        noise_text = config.FONT_REGULAR_24.render(f"Noise: {noise_value}", True, (255, 255, 255))
        screen.blit(noise_text, (config.Screen_Width // 2 - noise_text.get_width() // 2, y_offset + 20))

        # + Button
        plus_rect = pygame.Rect(config.Screen_Width // 2 + 80, y_offset + 20, 30, 30)
        pygame.draw.rect(screen, config.Light_Orange if plus_rect.collidepoint(mouse_pos) else config.Orange, plus_rect)
        plus_symbol = config.FONT_REGULAR_26.render("+", True, (0, 0, 0))
        screen.blit(plus_symbol, (plus_rect.x + plus_rect.width // 2 - plus_symbol.get_width() // 2, plus_rect.y + plus_rect.height // 2 - plus_symbol.get_height() // 2))

        # - Button
        minus_rect = pygame.Rect(config.Screen_Width // 2 - 110, y_offset + 20, 30, 30)
        pygame.draw.rect(screen, config.Light_Orange if minus_rect.collidepoint(mouse_pos) else config.Orange, minus_rect)
        minus_symbol = config.FONT_REGULAR_26.render("-", True, (0, 0, 0))
        screen.blit(minus_symbol, (minus_rect.x + minus_rect.width // 2 - minus_symbol.get_width() // 2, minus_rect.y + minus_rect.height // 2 - minus_symbol.get_height() // 2))

        button_rects.append((plus_rect, "increase_noise"))
        button_rects.append((minus_rect, "decrease_noise"))


    # --- Main Buttons ---
    button_defs = [
        ("Place Walls Randomly", "random", 360),
        ("Place Walls Manually", "manual", 420),
        ("Main Menu", "menu", 20)
    ]

    for label, action, y in button_defs:
        if action == "menu":
            btn_rect = pygame.Rect(30, y, 250, 35)
        else:
            btn_rect = pygame.Rect(config.Screen_Width // 2 - 200, y, 400, 45)

        is_hovered = btn_rect.collidepoint(mouse_pos)
        btn_color = config.Light_Orange if is_hovered else config.Orange

        pygame.draw.rect(screen, btn_color, btn_rect)
        pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2)

        text = config.FONT_REGULAR_26.render(label, True, (0, 0, 0) if is_hovered else (255, 255, 255))
        screen.blit(text, (
            btn_rect.x + btn_rect.width // 2 - text.get_width() // 2,
            btn_rect.y + btn_rect.height // 2 - text.get_height() // 2
        ))
        button_rects.append((btn_rect, action))

    # --- Benchmark Map Buttons ---
    benchmark_defs = [
        ("Use Benchmark 1 (Easy)", "benchmark1", 480),
        ("Use Benchmark 2 (Medium)", "benchmark2", 540),
        ("Use Benchmark 3 (Hard)", "benchmark3", 600),
    ]

    for label, action, y in benchmark_defs:
        btn_rect = pygame.Rect(config.Screen_Width // 2 - 200, y, 400, 45)
        is_hovered = btn_rect.collidepoint(mouse_pos)
        btn_color = config.Light_Orange if is_hovered else config.Orange

        pygame.draw.rect(screen, btn_color, btn_rect)
        pygame.draw.rect(screen, (255, 255, 255), btn_rect, 2)

        text = config.FONT_REGULAR_26.render(label, True, (0, 0, 0) if is_hovered else (255, 255, 255))
        screen.blit(text, (
            btn_rect.x + btn_rect.width // 2 - text.get_width() // 2,
            btn_rect.y + btn_rect.height // 2 - text.get_height() // 2
        ))
        button_rects.append((btn_rect, action))



    return button_rects
