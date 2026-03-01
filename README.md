# Dynamic Pathfinding Agent — AI 2002 Assignment 2 (Q6)

A grid-based pathfinding visualiser built with **Pygame** that implements A\* and Greedy Best-First Search with real-time dynamic obstacle re-planning.

## Features

- A\* Search and Greedy Best-First Search (GBFS)
- Manhattan and Euclidean heuristics (toggle in GUI)
- Color-coded frontier (yellow) vs expanded (blue) nodes
- Dynamic obstacle mode with configurable spawn probability
- Interactive map editor — click/drag to draw or erase walls
- Place Start and Goal anywhere via right-click menu
- Real-time metrics dashboard (nodes expanded, path cost, time)
- Adjustable grid size and obstacle density
- Step-by-step animation with variable speed

## Project Structure

```
pathfinding_agent/
├── main.py                  # Entry point
├── requirements.txt
├── README.md
├── algorithms/
│   ├── __init__.py
│   ├── astar.py             # A* Search implementation
│   └── gbfs.py              # Greedy Best-First Search implementation
├── gui/
│   ├── __init__.py
│   ├── app.py               # Main Pygame application loop
│   ├── grid_renderer.py     # Grid drawing, colors, cell states
│   └── panel.py             # Control panel buttons and metrics
└── utils/
    ├── __init__.py
    ├── grid.py              # Grid generation and helpers
    └── heuristics.py        # Manhattan and Euclidean heuristics
```

## Installation

```bash
pip install -r requirements.txt
```

> **macOS users:** If pygame fails to build from source, install SDL2 first:
> ```bash
> brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf
> pip install pygame
> ```

## Running

```bash
python main.py
```

## Controls

| Action | Control |
|--------|---------|
| Draw wall | Left-click / drag |
| Erase wall | Right-click on wall |
| Run search | `R` key or **Run** button |
| Animate agent | `A` key or **Animate** button |
| New random grid | `N` key or **New Grid** button |
| Clear path | `C` key or **Clear** button |
| Reset all walls | **Reset** button |
| Toggle Dynamic Mode | `D` key or **Dynamic** button |
| Quit | `ESC` |

## GUI Layout

- **Top panel:** Algorithm selector, Heuristic selector, Draw mode
- **Bottom panel:** Metrics (nodes expanded, path cost, time ms, re-plans)
- **Right panel:** Buttons and sliders for grid size, density, spawn probability, animation speed
- **Grid:** Color-coded cells

## Cell Colors

| Color | Meaning |
|-------|---------|
| Dark grey | Empty cell |
| Light grey | Wall / obstacle |
| Yellow | Frontier (in priority queue) |
| Blue | Expanded (closed set) |
| Teal/Green | Final path |
| Bright green | Start node |
| Pink/Red | Goal node |
| Purple star | Agent current position |

## Algorithm Details

### A\* Search
Uses `f(n) = g(n) + h(n)`. Guarantees optimal path when heuristic is admissible. Uses an Expanded List (closed set) — nodes are only closed when popped, allowing re-opening if a cheaper path is found.

### Greedy Best-First Search
Uses `f(n) = h(n)` only. Fast but not guaranteed to find the optimal path. Uses a Strict Visited List — nodes are marked visited immediately when discovered.

## Dynamic Mode

When enabled, new walls spawn randomly during agent animation with a configurable probability (default 15%). If a new wall blocks the current planned path, the agent immediately re-plans from its current position using the selected algorithm.
