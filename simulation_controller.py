import pygame
import time
import random
import os
import config

from gridworld import GridWorld
from lookahead import A_Star_Search
from config import Grid_Width, Grid_Height, Global_Seed
from metrics import Log_Path_Metrics
from utils.map_utils import load_full_map


class SimulationController:
    def __init__(self):
        # Agent and configuration
        self.selected_agent = None
        self.depth_value = 15
        self.noise_value = 5

        # Pathfinding results
        self.path = []
        self.success = False
        self.search_time = 0
        self.nodes_explored = 0

        # Grid setup
        self.grid = GridWorld(Grid_Width, Grid_Height)

        # Animation state
        self.trail_tiles = []
        self.agent_start = None
        self.agent_end = None
        self.path_step = 0
        self.interpolation_progress = 0.0
        self.interpolation_speed = 0.03
        self.animation_active = False

        # Interaction state
        self.click_mode = 0
        self.click_modes = ["Wall", "Start", "End"]
        self.mouse_held = False
        self.mouse_right_held = False
        self.last_dragged_tile = None

        # Dynamic world tracking
        self.dynamic_update_occurred = False

        # Benchmarking
        self.is_benchmark_run = False
        self.benchmark_name = None

        # Notification state
        self.path_notification = None
        self.path_notification_colour = (255, 215, 0)
        self.path_notification_timer = 0

        # Seeding
        if Global_Seed is not None:
            random.seed(Global_Seed)

    def set_agent(self, agent_type: str):
        self.selected_agent = agent_type

    def set_depth(self, value: int):
        self.depth_value = max(5, min(value, 35))

    def set_noise(self, value: int):
        self.noise_value = max(0, min(value, 15))

    def handle_mouse_input(self, mouse_pos, button):
        """
        Handles left/right mouse clicks for wall placement and start/end configuration.
        """
        from config import Tile_Size, Grid_Width, Grid_Height, Screen_Width

        x, y = mouse_pos
        if x >= Screen_Width:
            return

        row = y // Tile_Size
        col = x // Tile_Size
        if not (0 <= row < Grid_Height and 0 <= col < Grid_Width):
            return

        pos = (row, col)

        if button == 1:
            self.mouse_held = True
            self.last_dragged_tile = pos

            if self.click_mode == 0:
                self.grid.Toggle_Wall(pos)
                self.reset_path()
            elif self.click_mode == 1:
                if self.grid.grid[row][col] == 0 and pos != self.grid.end:
                    self.grid.start = pos
                    self.reset_path()
            elif self.click_mode == 2:
                if self.grid.grid[row][col] == 0 and pos != self.grid.start:
                    self.grid.end = pos
                    self.reset_path()

        elif button == 3:
            self.mouse_right_held = True
            self.last_dragged_tile = pos

    def handle_mouse_drag(self, mouse_pos):
        """
        Handles drag behaviour for adding/removing walls.
        """
        from config import Tile_Size, Grid_Width, Grid_Height, Screen_Width

        x, y = mouse_pos
        if x >= Screen_Width:
            return

        row = y // Tile_Size
        col = x // Tile_Size
        if not (0 <= row < Grid_Height and 0 <= col < Grid_Width):
            return

        pos = (row, col)
        if pos == self.last_dragged_tile:
            return

        if self.mouse_held and self.click_mode == 0 and self.grid.grid[row][col] == 0:
            self.grid.grid[row][col] = 1
            self.reset_path()

        elif self.mouse_right_held and self.click_mode == 0 and self.grid.grid[row][col] == 1:
            self.grid.grid[row][col] = 0
            self.reset_path()

        self.last_dragged_tile = pos

    def handle_key_input(self, key):
        """
        Handles keyboard interaction for switching modes or running simulation.
        """
        import pygame
        from config import Grid_Height, Grid_Width

        if key == pygame.K_SPACE:
            self.click_mode = (self.click_mode + 1) % len(self.click_modes)

        elif key == pygame.K_RETURN:
            self.run_simulation()

        elif key == pygame.K_d and self.selected_agent == "dynamic":
            self.dynamic_update_occurred = True

            for _ in range(10):
                r = random.randint(0, Grid_Height - 1)
                c = random.randint(0, Grid_Width - 1)
                if (r, c) != self.grid.start and (r, c) != self.grid.end:
                    self.reset_path()
                    self.grid.grid[r][c] = 1

            self.path_notification = "Environment Updated!"
            self.path_notification_colour = (255, 204, 77)
            self.path_notification_timer = 180

            if self.grid.start and self.grid.end and self.grid.start != self.grid.end:
                if abs(self.grid.start[0] - self.grid.end[0]) + abs(self.grid.start[1] - self.grid.end[1]) == 1:
                    self.path_notification = "Too Close!"
                    self.path_notification_colour = (255, 50, 50)
                    self.path_notification_timer = 180
                    return
                self.run_simulation()

    def update_animation_step(self):
        """
        Moves the agent along the path using interpolation.
        """
        if self.animation_active:
            self.interpolation_progress += self.interpolation_speed
            if self.interpolation_progress >= 1.0:
                self.interpolation_progress = 0.0
                if not self.trail_tiles or self.trail_tiles[-1] != self.agent_end:
                    self.trail_tiles.append(self.agent_end)
                self.path_step += 1
                if self.path_step < len(self.path) - 1:
                    self.agent_start = self.path[self.path_step]
                    self.agent_end = self.path[self.path_step + 1]
                else:
                    self.animation_active = False

    def update_notification_timer(self):
        """
        Gradually decreases the display time for notifications.
        """
        if self.path_notification_timer > 0:
            self.path_notification_timer -= 1

    def clear_simulation_notifications(self):
        """
        Resets all pathfinding and notification-related state.
        """
        self.reset_path()
        self.path_notification = None
        self.path_notification_timer = 0

    def reset_manual_grid(self):
        """
        Re-initialises a clean grid for manual wall placement.
        """
        self.grid = GridWorld(Grid_Width, Grid_Height)
        self.reset_path()

    def reset_path(self):
        """
        Clears pathfinding results and animation state.
        """
        self.path.clear()
        self.trail_tiles.clear()
        self.animation_active = False
        self.agent_start = None
        self.agent_end = None
        self.path_step = 0
        self.interpolation_progress = 0.0
        self.search_time = 0
        self.nodes_explored = 0

    def trigger_random_walls(self, count=85):
        """
        Randomly populates the grid with a specified number of walls.
        """
        self.grid = GridWorld(Grid_Width, Grid_Height)
        for _ in range(count):
            r = random.randint(0, Grid_Height - 1)
            c = random.randint(0, Grid_Width - 1)
            self.grid.grid[r][c] = 1

    def load_benchmark_map(self, name: str):
        """
        Loads a saved grid configuration from a benchmark file.
        """
        path = f"{config.DATA_DIR}/maps/map_{name}.json"
        data = load_full_map(path)
        loaded_grid = data["grid"]
        rows = len(loaded_grid)
        cols = len(loaded_grid[0])
        self.grid = GridWorld(cols, rows)
        self.grid.grid = loaded_grid
        self.grid.start = tuple(data["start"]) if data["start"] else None
        self.grid.end = tuple(data["end"]) if data["end"] else None
        self.is_benchmark_run = True
        self.benchmark_name = name

    def run_simulation(self):
        """
        Runs A* simulation and updates internal state + notification feedback.
        """
        self.path_notification_timer = 0

        if not self.grid.start or not self.grid.end or self.grid.start == self.grid.end:
            self.path_notification = "Invalid Start/End!"
            self.path_notification_colour = (255, 50, 50)
            self.path_notification_timer = 600
            return

        if abs(self.grid.start[0] - self.grid.end[0]) + abs(self.grid.start[1] - self.grid.end[1]) == 1:
            self.path_notification = "Too Close!"
            self.path_notification_colour = (255, 50, 50)
            self.path_notification_timer = 600
            return

        log_noise = self.noise_value if self.selected_agent == "noise" else None
        log_depth = self.depth_value if self.selected_agent == "depth" else None

        start_time = time.perf_counter()
        if self.selected_agent == "depth":
            temp_path, explored = A_Star_Search(
                self.grid.grid, self.grid.start, self.grid.end, Max_Depth=self.depth_value)
        elif self.selected_agent == "noise":
            temp_path, explored = A_Star_Search(
                self.grid.grid, self.grid.start, self.grid.end, Noise_Level=self.noise_value)
        elif self.selected_agent == "dynamic":
            temp_path, explored = A_Star_Search(
                self.grid.grid, self.grid.start, self.grid.end)
        else:
            temp_path, explored = None, 0
        end_time = time.perf_counter()

        self.search_time = end_time - start_time
        self.nodes_explored = explored
        self.success = temp_path is not None and len(temp_path) >= 2

        if self.success:
            self.path = temp_path
            self.trail_tiles = [self.path[0]]
            self.path_step = 0
            self.agent_start = self.path[0]
            self.agent_end = self.path[1]
            self.interpolation_progress = 0.0
            self.animation_active = True

            if self.selected_agent == "dynamic" and self.dynamic_update_occurred:
                self.path_notification = "Path Found After Update!"
            else:
                self.path_notification = "Path Found!"
            self.path_notification_colour = (0, 255, 0)
            self.path_notification_timer = 600

        else:
            self.path = []
            if self.selected_agent == "dynamic" and self.dynamic_update_occurred:
                self.path_notification = "No Path After Update"
            elif self.selected_agent == "depth":
                self.path_notification = "Path Blocked!"
            else:
                self.path_notification = "No Path Found!"
            self.path_notification_colour = (255, 50, 50)
            self.path_notification_timer = 600

        self.dynamic_update_occurred = False

        Log_Path_Metrics(
            grid=self.grid.grid,
            start=self.grid.start,
            end=self.grid.end,
            path=self.path if self.success else None,
            Agent_Type=self.selected_agent,
            Noise_Level=log_noise,
            Max_Depth=log_depth,
            Success=self.success,
            Nodes_Explored=self.nodes_explored,
            Search_Time=self.search_time,
            is_benchmark=self.is_benchmark_run,
            benchmark_name=self.benchmark_name if self.is_benchmark_run else None
        )
