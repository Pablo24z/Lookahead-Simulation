# Lookahead Strategy Simulation

## Overview

This Python-based simulation platform has been designed to analyse how different lookahead agents perform when navigating a grid world under varying conditions — including uncertainty, constraints, and dynamic updates. The tool offers a hands-on visual interface and thorough logging system, making it ideal for academic experimentation and demonstration.

It was built with a strong emphasis on reproducibility, clarity of logic, and high-quality visualisation of agent behaviour. The interface allows users to interactively test and compare the performance of several decision-making strategies, all in real time.

## Key Features

### Multiple Agent Strategies

- **Depth-Limited Agent**: Explores only up to a defined depth — useful for modelling cognitive limitations.
- **Noisy Heuristic Agent**: Adds probabilistic variation to the heuristic, simulating uncertainty and imperfect perception.
- **Dynamic Agent**: Designed to handle real-time changes in the environment, rerouting if the world is altered mid-search.

### Interactive Grid Editor

- Draw and remove walls manually, or place them randomly.
- Define custom start and end tiles.
- Live feedback when tiles are invalid (e.g. too close, blocked).

### In-Depth Metrics Logging

- Path length.
- Nodes explored.
- Time taken (measured precisely in microseconds).
- Success status and seed tracking.
- All results stored cleanly under `data/metrics/{agent}/...`.

Benchmark runs are also supported and stored separately for controlled testing.

### Simulation Visuals

- Live animation of the agent traversing its discovered path.
- Smooth path transitions using interpolation.
- Hover previews for wall, start, and goal placement.
- Status panel showing real-time values (agent type, wall count, path length, etc.).
- Colour-coded notifications that now intelligently reflect dynamic updates.

### Graphical Metrics Visualiser

- **Built-in GUI tool** (`visualiser.py`) to explore logged results.
- Compare agents on metrics like path length, success rate, and nodes explored.
- Automatically export graphs and summaries to PDF for academic reporting.
- Manual button now available to open the PDF immediately after export.

## Controls

| Key / Action       | Function                                          |
|--------------------|---------------------------------------------------|
| `SPACE`            | Toggle between Wall, Start, and End modes         |
| `ENTER`            | Run the simulation for the current agent          |
| `D`                | Trigger a dynamic environment update *(Dynamic Agent only)* |
| Left Click         | Place wall/start/end depending on active mode     |
| Right Click        | Remove wall at clicked location                   |
| Click "Back"       | Return to the agent configuration screen          |

## Running the Project

1. **Install Requirements**  
   You'll need Python 3.8 or higher and the following libraries:
   ```bash
   pip install pygame seaborn matplotlib pandas tqdm
   ```

2. **Launch the Simulation**
   ```bash
   python main.py
   ```

3. **Run Benchmarks**
   To automate a batch of simulation runs:
   ```bash
   python run_benchmarks.py --agent depth --benchmark easy --runs 5
   ```

4. **Launch the Metrics Visualiser**
   ```bash
   python visualiser.py
   ```

## Folder Structure (Updated)

```
src/

  main.py                     # Main simulation entry point
  config.py                   # Constants for layout, colours, fonts
  simulation_controller.py    # Central logic + animation manager
  lookahead.py                # A* search with optional noise and depth limit
  metrics.py                  # CSV + benchmarking logger
  run_benchmarks.py           # CLI-based benchmark runner
  visualiser.py               # Tkinter GUI for metric comparison and PDF export

  gridworld.py                # Grid data structure + draw logic
  tilemap.py                  # Tileset loader and slicer

  ui/
    draw_agent.py
    draw_trail.py
    draw_side_panel.py
    hover_highlight.py
    ui_screens.py

  utils/
    game_state.py
    map_utils.py

  data/
    maps/                   # Benchmark maps (.json)
    metrics/                # All run logs (auto-structured)
    assets/                     # Sprites + fonts
```

## Academic Intent

This simulation has been crafted to:

- Evaluate how imperfect or constrained planning affects agent performance.
- Support experimental analysis through tightly controlled benchmark testing.
- Offer clean visual output and real-time interactivity suitable for both demonstrations and deeper exploration.

The code is thoroughly modular to support future extensions, such as learning agents, adaptive noise, or probabilistic obstacle generation.

## Future Considerations

- Smarter wall generation with configurable density distributions.
- Visual overlays for explored nodes and frontiers.
- Extension into probabilistic planning domains (e.g. partially observable maps).
- Modular support for reinforcement learning baselines.

**Author**: Joseph Adeyeye (21355389)
**Institution**: Manchester Metropolitan University