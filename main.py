import tkinter as tk
from tkinter import messagebox
import random
import time
import heapq

# ------------------ DEFAULTS ------------------
ROWS = 20
COLS = 20
CELL_SIZE = 30

COLOR_EMPTY = "white"
COLOR_WALL = "black"
COLOR_START = "blue"
COLOR_GOAL = "purple"
COLOR_PATH = "green"
COLOR_FRONTIER = "yellow"     # nodes in priority queue
COLOR_VISITED = "lightblue"   # nodes expanded/explored
COLOR_AGENT = "orange"

# ------------------ GRID DATA ------------------
grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

start = (0, 0)                # FIXED Start (does NOT move)
goal = (ROWS - 1, COLS - 1)    # FIXED Goal

final_path = []

frontier_nodes = set()
visited_nodes = set()

search_running = False
search_state = None

# ------------------ DYNAMIC MODE ------------------
dynamic_mode_var = None       # created after root
spawn_probability_var = None  # created after root

agent_position = None
agent_moving = False

# This is the key fix:
# search_start changes during replanning, but 'start' stays fixed.
search_start = start

# ------------------ TKINTER UI ------------------
root = tk.Tk()
root.title("Dynamic Pathfinding Agent")

top_bar = tk.Frame(root)
top_bar.pack(pady=5)

metrics_bar = tk.Frame(root)
metrics_bar.pack(pady=5)

canvas = tk.Canvas(root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE)
canvas.pack()

nodes_visited_var = tk.IntVar(value=0)
path_cost_var = tk.IntVar(value=0)
time_ms_var = tk.StringVar(value="0 ms")

algorithm_var = tk.StringVar(value="A*")
heuristic_var = tk.StringVar(value="Manhattan")

# Dynamic vars now that root exists
dynamic_mode_var = tk.BooleanVar(value=False)
spawn_probability_var = tk.StringVar(value="0.05")

# ------------------ METRICS UI ------------------
tk.Label(metrics_bar, text="Nodes Visited:").pack(side="left", padx=5)
tk.Label(metrics_bar, textvariable=nodes_visited_var).pack(side="left", padx=5)

tk.Label(metrics_bar, text="Path Cost:").pack(side="left", padx=5)
tk.Label(metrics_bar, textvariable=path_cost_var).pack(side="left", padx=5)

tk.Label(metrics_bar, text="Execution Time:").pack(side="left", padx=5)
tk.Label(metrics_bar, textvariable=time_ms_var).pack(side="left", padx=5)

# ------------------ HELPERS ------------------
def clear_path():
    global final_path
    final_path = []

def clear_search_colors():
    frontier_nodes.clear()
    visited_nodes.clear()

def reset_metrics():
    """Reset metrics and stop agent movement."""
    global agent_position, agent_moving, search_start

    agent_moving = False
    agent_position = None
    search_start = start

    nodes_visited_var.set(0)
    path_cost_var.set(0)
    time_ms_var.set("0 ms")

    clear_path()
    clear_search_colors()
    draw_grid()

def cell_color(r, c):
    cell = (r, c)

    # Priority order:
    # Start, Goal, Wall, Agent, Path, Visited, Frontier, Empty
    if cell == start:
        return COLOR_START
    if cell == goal:
        return COLOR_GOAL
    if grid[r][c] == 1:
        return COLOR_WALL
    if agent_position == cell:
        return COLOR_AGENT
    if cell in final_path:
        return COLOR_PATH
    if cell in visited_nodes:
        return COLOR_VISITED
    if cell in frontier_nodes:
        return COLOR_FRONTIER
    return COLOR_EMPTY

def draw_grid():
    canvas.delete("all")
    for r in range(ROWS):
        for c in range(COLS):
            x1 = c * CELL_SIZE
            y1 = r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="black",
                fill=cell_color(r, c)
            )

# ------------------ STEP 1: DYNAMIC GRID SIZING ------------------
def create_grid():
    """Creates a new grid using user-defined rows and columns."""
    global ROWS, COLS, grid, start, goal, final_path, agent_position, agent_moving, search_start

    try:
        new_rows = int(rows_entry.get())
        new_cols = int(cols_entry.get())

        if new_rows < 5 or new_cols < 5:
            messagebox.showwarning("Invalid Size", "Rows and Cols must be at least 5.")
            return
        if new_rows > 50 or new_cols > 50:
            messagebox.showwarning("Too Large", "Max allowed size is 50 x 50 (for performance).")
            return
    except ValueError:
        messagebox.showwarning("Invalid Input", "Rows and Cols must be integers.")
        return

    ROWS = new_rows
    COLS = new_cols

    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]

    start = (0, 0)
    goal = (ROWS - 1, COLS - 1)

    # reset agent and replanning start
    agent_position = None
    agent_moving = False
    search_start = start

    final_path = []
    clear_search_colors()
    reset_metrics()

    canvas.config(width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE)
    draw_grid()

# ------------------ MAP GEN + CLICK EDIT (WALLS ONLY) ------------------
def on_click(event):
    col = event.x // CELL_SIZE
    row = event.y // CELL_SIZE

    if 0 <= row < ROWS and 0 <= col < COLS:
        if (row, col) == start or (row, col) == goal:
            return

        grid[row][col] = 1 if grid[row][col] == 0 else 0
        reset_metrics()

def generate_random_map():
    text = density_entry.get().strip()
    density = int(text) if text != "" else 30
    probability = density / 100.0

    for r in range(ROWS):
        for c in range(COLS):
            if (r, c) == start or (r, c) == goal:
                grid[r][c] = 0
            else:
                grid[r][c] = 1 if random.random() < probability else 0

    reset_metrics()

# ------------------ SEARCH HELPERS ------------------
def get_neighbors(r, c):
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == 0:
            neighbors.append((nr, nc))
    return neighbors

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def euclidean(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

def heuristic(a, b):
    return manhattan(a, b) if heuristic_var.get() == "Manhattan" else euclidean(a, b)

def reconstruct_path(parent, current):
    path = [current]
    while current in parent:
        current = parent[current]
        path.append(current)
    path.reverse()
    return path

# ------------------ A* (USES search_start) ------------------
def a_star_init():
    clear_search_colors()

    open_heap = []
    g_score = {search_start: 0}
    parent = {}

    start_f = heuristic(search_start, goal)
    heapq.heappush(open_heap, (start_f, search_start))
    frontier_nodes.add(search_start)

    return {
        "open_heap": open_heap,
        "g_score": g_score,
        "parent": parent,
        "nodes_expanded": 0
    }

def a_star_step():
    global search_running, search_state, final_path

    if not search_running or search_state is None:
        return

    open_heap = search_state["open_heap"]
    g_score = search_state["g_score"]
    parent = search_state["parent"]

    if not open_heap:
        search_running = False
        nodes_visited_var.set(search_state["nodes_expanded"])
        t1 = time.perf_counter()
        time_ms_var.set(f"{(t1 - search_state['t0']) * 1000.0:.2f} ms")
        messagebox.showwarning("No Path", "No path found from Start to Goal.")
        return

    _, current = heapq.heappop(open_heap)

    if current in frontier_nodes:
        frontier_nodes.remove(current)

    if current in visited_nodes:
        root.after(1, a_star_step)
        return

    visited_nodes.add(current)
    search_state["nodes_expanded"] += 1
    nodes_visited_var.set(search_state["nodes_expanded"])

    if current == goal:
        search_running = False
        final_path = reconstruct_path(parent, current)
        path_cost_var.set(len(final_path) - 1)
        t1 = time.perf_counter()
        time_ms_var.set(f"{(t1 - search_state['t0']) * 1000.0:.2f} ms")
        draw_grid()
        agent_start_movement()
        return

    for nb in get_neighbors(current[0], current[1]):
        tentative_g = g_score[current] + 1
        if nb not in g_score or tentative_g < g_score[nb]:
            g_score[nb] = tentative_g
            parent[nb] = current
            f_nb = tentative_g + heuristic(nb, goal)
            heapq.heappush(open_heap, (f_nb, nb))
            if nb not in visited_nodes:
                frontier_nodes.add(nb)

    draw_grid()
    root.after(10, a_star_step)

# ------------------ GBFS (USES search_start) ------------------
def gbfs_init():
    clear_search_colors()

    open_heap = []
    parent = {}

    start_h = heuristic(search_start, goal)
    heapq.heappush(open_heap, (start_h, search_start))
    frontier_nodes.add(search_start)

    return {
        "open_heap": open_heap,
        "parent": parent,
        "nodes_expanded": 0
    }

def gbfs_step():
    global search_running, search_state, final_path

    if not search_running or search_state is None:
        return

    open_heap = search_state["open_heap"]
    parent = search_state["parent"]

    if not open_heap:
        search_running = False
        nodes_visited_var.set(search_state["nodes_expanded"])
        t1 = time.perf_counter()
        time_ms_var.set(f"{(t1 - search_state['t0']) * 1000.0:.2f} ms")
        messagebox.showwarning("No Path", "No path found (GBFS).")
        return

    _, current = heapq.heappop(open_heap)

    if current in frontier_nodes:
        frontier_nodes.remove(current)

    if current in visited_nodes:
        root.after(1, gbfs_step)
        return

    visited_nodes.add(current)
    search_state["nodes_expanded"] += 1
    nodes_visited_var.set(search_state["nodes_expanded"])

    if current == goal:
        search_running = False
        final_path = reconstruct_path(parent, current)
        path_cost_var.set(len(final_path) - 1)
        t1 = time.perf_counter()
        time_ms_var.set(f"{(t1 - search_state['t0']) * 1000.0:.2f} ms")
        draw_grid()
        agent_start_movement()
        return

    for nb in get_neighbors(current[0], current[1]):
        if nb not in visited_nodes and nb not in parent:
            parent[nb] = current
        if nb not in visited_nodes:
            heapq.heappush(open_heap, (heuristic(nb, goal), nb))
            frontier_nodes.add(nb)

    draw_grid()
    root.after(10, gbfs_step)

# ------------------ DYNAMIC SPAWN + MOVEMENT + REPLAN ------------------
def spawn_obstacles():
    """Spawn obstacles with probability during movement (avoid start, goal, agent)."""
    if not dynamic_mode_var.get():
        return

    try:
        prob = float(spawn_probability_var.get())
    except:
        prob = 0.05

    for r in range(ROWS):
        for c in range(COLS):
            if (r, c) in [start, goal, agent_position]:
                continue
            if grid[r][c] == 0 and random.random() < prob:
                grid[r][c] = 1

def agent_start_movement():
    global agent_position, agent_moving, search_start
    agent_position = start
    search_start = start
    agent_moving = True
    root.after(300, move_agent_step)

def move_agent_step():
    global agent_position, final_path, search_start, agent_moving

    if not agent_moving:
        return

    if not final_path:
        agent_moving = False
        return

    if len(final_path) > 1:
        final_path.pop(0)
        agent_position = final_path[0]

        # update ONLY replanning start
        search_start = agent_position

        spawn_obstacles()

        # if remaining path blocked -> replan
        for cell in final_path:
            if grid[cell[0]][cell[1]] == 1:
                replan_from_current()
                return

        draw_grid()
        root.after(150, move_agent_step)
    else:
        agent_moving = False
        messagebox.showinfo("Success", "Agent reached Goal!")

def replan_from_current():
    global search_running, search_state, final_path

    clear_search_colors()
    final_path = []

    selected_algorithm = algorithm_var.get()
    t0 = time.perf_counter()

    if selected_algorithm == "A*":
        search_state = a_star_init()
        search_state["t0"] = t0
        search_running = True
        a_star_step()
    else:
        search_state = gbfs_init()
        search_state["t0"] = t0
        search_running = True
        gbfs_step()

# ------------------ START SEARCH ------------------
def start_search():
    global search_running, search_state, agent_moving, agent_position, search_start

    # stop anything running
    search_running = False
    search_state = None

    agent_moving = False
    agent_position = None
    search_start = start

    reset_metrics()
    clear_path()
    clear_search_colors()
    draw_grid()

    t0 = time.perf_counter()

    if algorithm_var.get() == "A*":
        search_state = a_star_init()
        search_state["t0"] = t0
        search_running = True
        a_star_step()
    else:
        search_state = gbfs_init()
        search_state["t0"] = t0
        search_running = True
        gbfs_step()

# ------------------ TOP BAR UI ------------------
tk.Label(top_bar, text="Rows:").pack(side="left", padx=5)
rows_entry = tk.Entry(top_bar, width=4)
rows_entry.insert(0, str(ROWS))
rows_entry.pack(side="left", padx=2)

tk.Label(top_bar, text="Cols:").pack(side="left", padx=5)
cols_entry = tk.Entry(top_bar, width=4)
cols_entry.insert(0, str(COLS))
cols_entry.pack(side="left", padx=2)

tk.Button(top_bar, text="Create Grid", command=create_grid).pack(side="left", padx=8)

tk.Label(top_bar, text="Obstacle Density (%):").pack(side="left", padx=5)
density_entry = tk.Entry(top_bar, width=5)
density_entry.insert(0, "20")
density_entry.pack(side="left", padx=5)

tk.Button(top_bar, text="Generate Random Map", command=generate_random_map).pack(side="left", padx=5)

tk.Label(top_bar, text="Algorithm:").pack(side="left", padx=5)
tk.OptionMenu(top_bar, algorithm_var, "A*", "GBFS").pack(side="left", padx=5)

tk.Label(top_bar, text="Heuristic:").pack(side="left", padx=5)
tk.OptionMenu(top_bar, heuristic_var, "Manhattan", "Euclidean").pack(side="left", padx=5)

tk.Checkbutton(top_bar, text="Dynamic Mode", variable=dynamic_mode_var).pack(side="left", padx=5)
tk.Label(top_bar, text="Spawn Prob:").pack(side="left", padx=5)
tk.Entry(top_bar, width=5, textvariable=spawn_probability_var).pack(side="left", padx=5)

tk.Button(top_bar, text="Start Search", command=start_search).pack(side="left", padx=5)
tk.Button(top_bar, text="Reset Metrics", command=reset_metrics).pack(side="left", padx=5)

# ------------------ EVENTS ------------------
canvas.bind("<Button-1>", on_click)

draw_grid()
root.mainloop()