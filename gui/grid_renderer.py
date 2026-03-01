import pygame

C_BG         = (30,  30,  46)
C_EMPTY      = (49,  50,  68)
C_WALL       = (88,  91, 112)
C_GRID_LINE  = (24,  24,  37)
C_START      = (166, 227, 161)
C_GOAL       = (243, 139, 168)
C_FRONTIER   = (249, 226, 175)
C_EXPANDED   = (137, 180, 250)
C_PATH       = (148, 226, 213)
C_AGENT      = (203, 166, 247)
C_TEXT       = (205, 214, 244)
C_ACCENT     = (137, 220, 235)
C_PANEL_BG   = (24,  24,  37)


class GridRenderer:
    def __init__(self, cell_size: int = 34):
        self.cell_size = cell_size

    def draw(self, surface, grid, rows, cols,
             start, goal,
             frontier: set, expanded: set,
             path: list, agent_step: int,
             offset_y: int = 0):

        cs   = self.cell_size
        path_set = set(path)
        agent_pos = path[agent_step] if path and 0 <= agent_step < len(path) else None

        for r in range(rows):
            for c in range(cols):
                cell = (r, c)
                x1 = c * cs + 1
                y1 = r * cs + offset_y + 1
                rect = (x1, y1, cs - 2, cs - 2)

                if grid[r][c] == 1:
                    color = C_WALL
                elif cell == start:
                    color = C_START
                elif cell == goal:
                    color = C_GOAL
                elif cell == agent_pos:
                    color = C_AGENT
                elif cell in path_set:
                    color = C_PATH
                elif cell in expanded:
                    color = C_EXPANDED
                elif cell in frontier:
                    color = C_FRONTIER
                else:
                    color = C_EMPTY

                pygame.draw.rect(surface, color, rect, border_radius=3)

                lbl = None
                if   cell == start:     lbl, fc = "S", C_BG
                elif cell == goal:      lbl, fc = "G", C_BG
                elif cell == agent_pos: lbl, fc = "A", C_BG

                if lbl:
                    font = pygame.font.SysFont("Segoe UI", max(10, cs // 3), bold=True)
                    t = font.render(lbl, True, fc)
                    cx = x1 + (cs - 2) // 2
                    cy = y1 + (cs - 2) // 2
                    surface.blit(t, t.get_rect(center=(cx, cy)))

    def draw_legend(self, surface, x, y):
        font = pygame.font.SysFont("Segoe UI", 12)
        items = [
            (C_START,    "Start"),
            (C_GOAL,     "Goal"),
            (C_WALL,     "Wall"),
            (C_FRONTIER, "Frontier"),
            (C_EXPANDED, "Expanded"),
            (C_PATH,     "Path"),
            (C_AGENT,    "Agent"),
        ]
        ox = x
        for color, label in items:
            pygame.draw.rect(surface, color, (ox, y, 12, 12), border_radius=2)
            t = font.render(label, True, C_TEXT)
            surface.blit(t, (ox + 15, y))
            ox += t.get_width() + 28
