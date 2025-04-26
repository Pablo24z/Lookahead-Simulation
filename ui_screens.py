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

def draw_instructions_screen(screen, agent_key):
    screen.fill((30, 30, 30))

    title_font = config.FONT_BOLD_40
    text_font = config.FONT_REGULAR_24
    button_font = config.FONT_REGULAR_26

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
    screen.blit(title_text, (config.Screen_Width // 2 - title_text.get_width() // 2, title_y))

    underline_y = title_y + title_text.get_height() + 5
    pygame.draw.line(screen, (255, 255, 255),
                     (config.Screen_Width // 2 - title_text.get_width() // 2, underline_y),
                     (config.Screen_Width // 2 + title_text.get_width() // 2, underline_y), 2)

    for i, line in enumerate(agent_controls[agent_key]):
        instruction = text_font.render(line, True, (220, 220, 220))
        screen.blit(instruction, (80, underline_y + 40 + i * 35))

    mouse_pos = pygame.mouse.get_pos()
    button_rects = []

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

        text = button_font.render(label, True, (0, 0, 0) if is_hovered else (255, 255, 255))
        screen.blit(text, (
            btn_rect.x + btn_rect.width // 2 - text.get_width() // 2,
            btn_rect.y + btn_rect.height // 2 - text.get_height() // 2
        ))
        button_rects.append((btn_rect, action))

    return button_rects
