# Dynamic Pathfinding Agent

A Python Tkinter pathfinding visualizer using A* Search and Greedy Best First Search with dynamic obstacle replanning.

This project visualizes how an agent finds a path from a start node to a goal node in a grid-based environment. The user can generate random obstacles, choose a search algorithm, select a heuristic, and enable dynamic mode where new obstacles appear while the agent is moving.

## Project Overview

The Dynamic Pathfinding Agent is a graphical AI project built with Python and Tkinter.

The grid contains a fixed start position and goal position. The agent searches for a path using either A* Search or Greedy Best First Search. After the path is found, the agent moves along it. If dynamic mode is enabled and a new obstacle blocks the remaining path, the system automatically replans from the agent's current position.

## Features

* Graphical grid-based interface
* Custom row and column size
* Random obstacle generation
* Manual wall placement by clicking cells
* A* Search algorithm
* Greedy Best First Search algorithm
* Manhattan distance heuristic
* Euclidean distance heuristic
* Dynamic obstacle spawning
* Automatic replanning when path is blocked
* Animated agent movement
* Metrics display for:

  * Nodes visited
  * Path cost
  * Execution time

## Color Guide

| Color      | Meaning         |
| ---------- | --------------- |
| Blue       | Start node      |
| Purple     | Goal node       |
| Black      | Obstacle / wall |
| Green      | Final path      |
| Yellow     | Frontier nodes  |
| Light Blue | Visited nodes   |
| Orange     | Moving agent    |
| White      | Empty cell      |

## Algorithms Used

### A* Search

A* uses both the actual path cost and the heuristic estimate:

```text
f(n) = g(n) + h(n)
```

It is more reliable and can find the optimal path when the heuristic is admissible.

### Greedy Best First Search

Greedy Best First Search uses only the heuristic estimate:

```text
f(n) = h(n)
```

It is usually faster in simple maps but does not always guarantee the shortest path.

## Heuristics Used

### Manhattan Distance

Used for grid movement without diagonal moves.

```text
h(n) = |x1 - x2| + |y1 - y2|
```

### Euclidean Distance

Straight-line distance between two cells.

```text
h(n) = sqrt((x1 - x2)^2 + (y1 - y2)^2)
```

## Technologies Used

* Python
* Tkinter
* Heap Queue
* Random module
* Time module

## Project Structure

```text
dynamic-pathfinding-agent/
│
├── app.py
└── README.md
```

## How to Run

1. Make sure Python is installed.

2. Run the application:

```bash
python app.py
```

3. Use the GUI to:

   * Set grid size
   * Generate obstacles
   * Choose A* or GBFS
   * Choose Manhattan or Euclidean heuristic
   * Enable or disable dynamic mode
   * Start the search

## Dynamic Mode

In dynamic mode, new obstacles may appear while the agent is moving. If a new obstacle blocks the remaining path, the system automatically runs the selected search algorithm again from the agent's current position.

This simulates real-world pathfinding where the environment can change while the agent is moving.

## Conclusion

This project shows how informed search algorithms work in a visual environment. A* is more reliable and performs better in complex or dynamic maps, while Greedy Best First Search can be faster in simpler cases but may produce less optimal paths.
