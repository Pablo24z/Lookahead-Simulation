# Lookahead Strategy Simulation

## Overview

This project is a Python-based simulation tool designed to explore how lookahead strategies perform in dynamic grid environments. The simulation allows a user to select between different agent types, each employing a different lookahead method to find paths from a start to an end position across a customizable grid. The tool is particularly useful for studying decision-making under uncertainty, pathfinding efficiency, and the limitations of different search strategies.

## Features

- **Multiple Agents**:
  - **Depth-Limited Lookahead**: Explores to a maximum depth limit.
  - **Noisy Heuristic Lookahead**: Adds noise to the heuristic to simulate real-world uncertainty.
  - **Dynamic Environment Lookahead**: Handles grid updates in real-time.

- **Grid Editing**:
  - Manual or random placement of walls.
  - Set custom start and end points.

- **Pathfinding Metrics**:
  - Nodes explored.
  - Path length.
  - Search time (measured precisely in microseconds).

- **Data Logging**:
  - Results are logged in a clean directory structure.
  - Separate folders for each agent type (`depth`, `noise`, `dynamic`) under `data/metrics/`.
  - Old metric files are automatically archived for historical comparison.

- **User Interface**:
  - Intuitive mouse and keyboard controls.
  - Visual feedback with clear color coding.
  - Animated path traversal after successful searches.

- **Performance Considerations**:
  - Efficiently handles grids of moderate size.
  - Updates and redraws handled at 120 FPS for smoothness.

## Controls

- `SPACE`: Switch between Wall/Start/End placement mode.
- `ENTER`: Run the selected pathfinding simulation.
- `D`: Trigger a dynamic environment update (only available for Dynamic Lookahead agent).
- `Left Click`: Place walls, start, or end points.
- `Right Click`: Remove walls.

## Installation

1. Ensure you have Python 3.8+ installed.
2. Install required libraries:
```bash
pip install pygame
```
3. Run the simulation:
```bash
python main.py
```

## Folder Structure

```
assets/fonts/             # Font resources
config.py                 # Color schemes, font setup
main.py                   # Main execution file
lookahead.py              # A* Search algorithm with optional depth/noise
metrics.py                # Data logging and management
ui_screens.py             # Start and instruction screen handling
gridworld.py              # Grid management
README.md                 # This file
data/metrics/             # Output folders for metric logs
```

## Academic Focus

This project aims to:
- Provide empirical insight into how limited lookahead depth and heuristic noise affect search efficiency.
- Allow users to simulate dynamic environments where obstacles can appear mid-search.
- Generate reproducible metrics for analysis, supporting research on decision-making algorithms.

The tool is crafted with careful emphasis on:
- Correctness of the search implementations.
- Robust data collection.
- Smooth and responsive user interaction.
- Professional project organization.

## Future Enhancements

- Visual upgrades (e.g., sprite-based rendering for walls/start/end tiles).
- Smarter dynamic updates with probability-based wall placements.
- Agent personality visualization based on strategy.

---


**Author**: Joseph Adeyeye (21355389) - Manchester Metropolitan University

**Last Updated**: April 2025

