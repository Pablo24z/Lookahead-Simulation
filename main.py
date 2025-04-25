import pygame
import sys
import random
from gridworld import GridWorld, Tile_Size, Screen_Height, Screen_Width, Grid_Width, Grid_Height
from lookahead import A_Star_Search
from metrics import Log_Path_Metrics


#initialise pygame
pygame.init()
Screen_Mode = "Menu" #other modes: "instructions", "simulation"
Sim_Mode = None
Selected_Agent = None
screen = pygame.display.set_mode((Screen_Width, Screen_Height))
pygame.display.set_caption("Lookahead Strategy Simulation")
clock = pygame.time.Clock()

#create gridworld instance
grid = GridWorld(Grid_Width, Grid_Height)

#mouse modes: 0 = wall, 1 = start, 2 = end
click_mode = 0
path = []
modes = ["Wall", "Start", "End"]

font = pygame.font.SysFont(None, 24)

def get_Grid_Pos(mouse_pos):
    x, y = mouse_pos
    row = y // Tile_Size
    col = x // Tile_Size
    if 0 <= row < Grid_Height and 0 <= col < Grid_Width:
        return row, col
    return None


def draw_Mode_Text():
    pygame.draw.rect(screen, (230, 230, 230), (0, Tile_Size * Grid_Height, Screen_Width, 40))  # Status bar
    mode_text = font.render(f"Click Mode: {modes[click_mode]}", True, (0, 0, 0))
    help_text = font.render("SPACE = Switch mode | ENTER = Run path | ESC = Quit", True, (0, 0, 0))
    screen.blit(mode_text, (10, Tile_Size * Grid_Height + 5))
    screen.blit(help_text, (200, Tile_Size * Grid_Height + 5))

mouse_held = False
Last_Dragged_Tile = None

def draw_Start_Menu():
    screen.fill((30, 30, 30)) #Dark Background
    Title_Font = pygame.font.Font("assets/fonts/RobotoMono-Bold.ttf", 50)
    Button_Font = pygame.font.Font("assets/fonts/RobotoMono-Regular.ttf", 26)

    #Title - Main Menu
    Title_Text = Title_Font.render("Lookahead Strategy Simulation", True, (255, 255, 255))
    screen.blit(Title_Text, (Screen_Width // 2 - Title_Text.get_width() // 2, 80))


    #Buttons
    Buttons = [
        ("Depth-Limited Agent", "depth", 180),
        ("Noisy Heuristic Agent", "noise", 240),
        ("Dynamic Environment Agent", "dynamic", 300),
    ]


    Button_Rects = []

    for Label, _, y in Buttons:
        rect = pygame.Rect(Screen_Width // 2 - 250, y, 450, 50)
        Button_Colour = (249, 168, 37) # yellow-orange
        pygame.draw.rect(screen, Button_Colour, rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2) #white border
        text = Button_Font.render(Label, True, (255, 255, 255))
        screen.blit(text, (rect.x + rect.width // 2 - text.get_width() // 2, rect.y + rect.height // 2 - text.get_height() //2 ))
        Button_Rects.append((rect, Label))

    return Button_Rects


def draw_Instructions_Screen(agent):
    screen.fill((30, 30, 30))
    title_font = pygame.font.Font("assets/fonts/RobotoMono-Bold.ttf", 40)
    text_font = pygame.font.Font("assets/fonts/RobotoMono-Regular.ttf", 24)

    agent_titles = {
        "depth": "Depth-Limited Agent",
        "noise": "Noisy Heuristic Agent",
        "dynamic": "Dynamic Environment Agent"
    }

    # Title
    title_text = agent_titles.get(agent, "Instructions")
    title_y = 70
    title = title_font.render(title_text, True, (255, 255, 255))
    screen.blit(title, (Screen_Width // 2 - title.get_width() // 2, title_y))

    # Agent-specific instructions
    agent_controls = {
        "depth": [
            "Press SPACE to switch modes (Wall, Start, End)",
            "Press ENTER to run the algorithm",
        ],
        "noise": [
            "Press SPACE to switch modes",
            "Press ENTER to run with noisy heuristic (Noise Level = 5)",
        ],
        "dynamic": [
            "Press SPACE to switch modes",
            "Press ENTER to run",
            "Press D to trigger a dynamic world change",
        ]
    }

    lines = agent_controls.get(agent, [])
    for i, line in enumerate(lines):
        text = text_font.render(line, True, (220, 220, 220))
        screen.blit(text, (80, 120 + i * 35))

    # Buttons
    button_font = pygame.font.Font("assets/fonts/RobotoMono-Regular.ttf", 26)
    buttons = [
        ("Place Walls Randomly", "random", 360),
        ("Place Walls Manually", "manual", 420),
        ("Main Menu", "menu", 20)  # Top left back button
    ]

    button_rects = []
    for label, action, y in buttons:
        rect = pygame.Rect(Screen_Width // 2 - 200, y, 400, 45) if action != "menu" else pygame.Rect(30, y, 250, 35)
        pygame.draw.rect(screen, (249, 168, 37), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2) #white border
        text = button_font.render(label, True, (255, 255, 255))
        screen.blit(text, (
            rect.x + rect.width // 2 - text.get_width() // 2,
            rect.y + rect.height // 2 - text.get_height() // 2
        ))
        button_rects.append((rect, action))

    return button_rects


#main loop
running = True
while running:
    if Screen_Mode == "Menu":
        Button_Rects = draw_Start_Menu()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for rect, Label in Button_Rects:
                    if rect.collidepoint(mouse_pos):
                        if Label == "Depth-Limited Agent":
                            Selected_Agent = "depth"
                            Screen_Mode = "instructions"
                        elif Label == "Noisy Heuristic Agent":
                            Selected_Agent = "noise"
                            Screen_Mode = "instructions"
                        elif Label == "Dynamic Environment Agent":
                            Selected_Agent = "dynamic"
                            Screen_Mode = "instructions"
        continue # Skip running sim logic if still in menu
    
    

    if Screen_Mode == "instructions":
        Button_Rects = draw_Instructions_Screen(Selected_Agent)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for rect, action in Button_Rects:
                    if rect.collidepoint(mouse_pos):
                        if action == "random":
                            print(f"{Selected_Agent} agent — random walls selected.")
                            grid = GridWorld(Grid_Width, Grid_Height)
                            for _ in range(85):
                                r = random.randint(0, Grid_Height - 1)
                                c = random.randint(0, Grid_Width - 1)
                                grid.grid[r][c] = 1
                            Screen_Mode = "simulation"
                        elif action == "manual":
                            print(f"{Selected_Agent} agent — manual wall placement selected.")
                            grid = GridWorld(Grid_Width, Grid_Height)
                            Screen_Mode = "simulation"
                        elif action == "menu":
                            Selected_Agent = None
                            Screen_Mode = "Menu"
        continue





    if Screen_Mode == "simulation":
        screen.fill((30, 30, 30)) # dark gray
        grid.draw(screen)
        draw_Mode_Text()


        if path:
            for cell in path:
                row, col = cell
                rect = pygame.Rect(col * Tile_Size, row * Tile_Size, Tile_Size, Tile_Size)
                pygame.draw.rect(screen, (50, 100, 255), rect)
        
        pygame.display.flip()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    click_mode = (click_mode + 1) % 3 #toggles between the modes


                elif event.key == pygame.K_RETURN:
                    if grid.start and grid.end:
                        depth_limit = None
                        Noise_Level = 5
                        path = A_Star_Search(grid.grid, grid.start, grid.end, depth_limit = depth_limit, Noise_Level= Noise_Level)
                        Log_Path_Metrics(grid.grid, grid.start, grid.end, path, Noise_Level = Noise_Level)
                        if not path:
                            print("No Path can be Found. (Likely due to lookahead limit)")



                elif event.key == pygame.K_d:
                    print("Dynamic Event triggered: The World Shifts!")
                    for _ in range(10):
                        r = random.randint(0, Grid_Height - 1)
                        c = random.randint(0, Grid_Width - 1)
                        if (r, c) != grid.start and (r, c) != grid.end:
                            grid.grid[r][c] = 1 # Adds a wall

                    path = A_Star_Search(grid.grid, grid.start, grid.end)
                    Log_Path_Metrics(grid.grid, grid.start, grid.end, path, Noise_Level = 0)
                    if not path:
                        print("No Path can be Found after the world shift!")


            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_held = True
                pos = get_Grid_Pos(pygame.mouse.get_pos())
                if pos:
                    if click_mode == 0:
                        grid.Toggle_Wall(pos)
                        path = []
                        Last_Dragged_Tile = pos
                    elif click_mode == 1:
                        grid.start = pos
                        path = []
                    elif click_mode == 2:
                        grid.end = pos
                        path = []

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_held = False
                Last_Dragged_Tile = None

        if mouse_held and click_mode == 0:
            pos = get_Grid_Pos(pygame.mouse.get_pos())
            if pos and pos != Last_Dragged_Tile:
                grid.Toggle_Wall(pos)
                path = []
                Last_Dragged_Tile = pos

    clock.tick(60)
pygame.quit()
sys.exit()