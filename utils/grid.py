import random


EMPTY = 0
WALL  = 1


def make_empty_grid(rows, cols):
    return [[EMPTY] * cols for _ in range(rows)]


def make_random_grid(rows, cols, density, start, goal, seed=None):
    if seed is not None:
        random.seed(seed)
    grid = make_empty_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in (start, goal):
                if random.random() < density:
                    grid[r][c] = WALL
    return grid


def in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols


def is_passable(grid, r, c):
    return grid[r][c] == EMPTY


NEIGHBORS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def get_neighbors(grid, cell, rows, cols):
    r, c = cell
    result = []
    for dr, dc in NEIGHBORS:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc, rows, cols) and is_passable(grid, nr, nc):
            result.append((nr, nc))
    return result


def reconstruct_path(came_from, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    return path[::-1]
