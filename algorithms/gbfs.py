import heapq
from utils.grid import get_neighbors, reconstruct_path


def gbfs(grid, start, goal, heuristic, rows, cols):
    open_heap = []
    heapq.heappush(open_heap, (heuristic(start, goal), start))

    came_from = {start: None}
    visited   = {start}
    expanded  = set()
    frontier  = {start}

    nodes_exp = 0

    while open_heap:
        _, current = heapq.heappop(open_heap)

        expanded.add(current)
        frontier.discard(current)
        nodes_exp += 1

        if current == goal:
            path = reconstruct_path(came_from, goal)
            return path, frontier, expanded, nodes_exp, len(path) - 1

        for neighbor in get_neighbors(grid, current, rows, cols):
            if neighbor not in visited:
                visited.add(neighbor)
                frontier.add(neighbor)
                came_from[neighbor] = current
                heapq.heappush(open_heap, (heuristic(neighbor, goal), neighbor))

    return None, frontier, expanded, nodes_exp, 0
