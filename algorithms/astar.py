import heapq
from utils.grid import get_neighbors, reconstruct_path


def astar(grid, start, goal, heuristic, rows, cols):
    open_heap = []
    heapq.heappush(open_heap, (heuristic(start, goal), 0, start))

    came_from  = {start: None}
    g_score    = {start: 0}
    expanded   = set()
    frontier   = {start}

    nodes_exp  = 0

    while open_heap:
        f, g, current = heapq.heappop(open_heap)

        if current in expanded:
            continue

        expanded.add(current)
        frontier.discard(current)
        nodes_exp += 1

        if current == goal:
            path = reconstruct_path(came_from, goal)
            return path, frontier, expanded, nodes_exp, len(path) - 1

        for neighbor in get_neighbors(grid, current, rows, cols):
            if neighbor in expanded:
                continue
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor]   = tentative_g
                f_score             = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f_score, tentative_g, neighbor))
                frontier.add(neighbor)

    return None, frontier, expanded, nodes_exp, 0
