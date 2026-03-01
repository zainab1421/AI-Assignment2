import pygame
import random
import time

from algorithms         import ALGORITHMS
from utils.grid         import make_random_grid, make_empty_grid, WALL, EMPTY
from utils.heuristics   import HEURISTICS
from gui.grid_renderer  import GridRenderer, C_BG, C_PANEL_BG, C_TEXT, C_ACCENT, C_FRONTIER
from gui.panel          import ControlPanel, Button, Cycler

CELL = 34


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Dynamic Pathfinding Agent — AI 2002")

        self.rows  = 15
        self.cols  = 20
        self.start = (0, 0)
        self.goal  = (self.rows - 1, self.cols - 1)
        self.grid  = make_random_grid(self.rows, self.cols, 0.28, self.start, self.goal)

        self.path      = []
        self.frontier  = set()
        self.expanded  = set()
        self.agent_step = 0
        self.animating  = False
        self.last_step  = 0
        self.metrics    = {"nodes": 0, "cost": 0, "time_ms": 0.0, "replans": 0, "status": "Ready"}

        self.panel_w    = ControlPanel.PANEL_W
        self._rebuild_screen()

        self.renderer   = GridRenderer(CELL)
        self.panel      = ControlPanel(self.screen_h, self.rows * CELL)
        self._shift_panel_widgets()

        self.mouse_held = False
        self.clock      = pygame.time.Clock()
        self.font_top   = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.font_sm    = pygame.font.SysFont("Segoe UI", 11)

    def _rebuild_screen(self):
        self.grid_w  = self.cols * CELL
        self.grid_h  = self.rows * CELL
        self.top_bar = 32
        self.screen_w = self.grid_w + self.panel_w
        self.screen_h = self.grid_h + self.top_bar
        self.surface  = pygame.display.set_mode((self.screen_w, self.screen_h))

    def _shift_panel_widgets(self):
        panel_x = self.grid_w
        for w in (self.panel.all_btns + self.panel.all_cyclers + self.panel.all_sliders):
            w.rect.x = panel_x + 8

    def _heuristic(self):
        return HEURISTICS[self.panel.cyc_heur.value]

    def _algo(self):
        return ALGORITHMS[self.panel.cyc_algo.value]

    def do_search(self, start=None):
        s = start or self.start
        t0 = time.time()
        path, frontier, expanded, nexp, cost = self._algo()(
            self.grid, s, self.goal, self._heuristic(), self.rows, self.cols
        )
        elapsed = (time.time() - t0) * 1000
        self.frontier = frontier
        self.expanded = expanded
        self.metrics["nodes"]   = nexp
        self.metrics["time_ms"] = elapsed
        if path:
            self.path = path
            self.metrics["cost"]   = cost
            self.metrics["status"] = (
                f"{self.panel.cyc_algo.value}+{self.panel.cyc_heur.value} | "
                f"Cost {cost} | {nexp} nodes"
            )
        else:
            self.path = []
            self.metrics["status"] = "No path found!"
        return path

    def do_new_grid(self):
        self.rows  = int(self.panel.sld_rows.value)
        self.cols  = int(self.panel.sld_cols.value)
        self.start = (0, 0)
        self.goal  = (self.rows - 1, self.cols - 1)
        self.grid  = make_random_grid(self.rows, self.cols,
                                      self.panel.sld_dens.value, self.start, self.goal)
        self._clear_state()
        self._rebuild_screen()
        self._shift_panel_widgets()
        self.panel.screen_h = self.screen_h
        self.metrics["status"] = "New grid generated"

    def _clear_state(self):
        self.path      = []
        self.frontier  = set()
        self.expanded  = set()
        self.agent_step = 0
        self.animating  = False
        self.metrics["replans"] = 0
        self.metrics["nodes"]   = 0
        self.metrics["cost"]    = 0
        self.metrics["time_ms"] = 0.0

    def _cell_at(self, mx, my):
        gy = my - self.top_bar
        c  = mx // CELL
        r  = gy // CELL
        if 0 <= r < self.rows and 0 <= c < self.cols and mx < self.grid_w:
            return (r, c)
        return None

    def _apply_draw(self, cell):
        mode = self.panel.cyc_draw.value
        if mode == "Wall"  and cell not in (self.start, self.goal):
            self.grid[cell[0]][cell[1]] = WALL
            self.path = []; self.frontier = set(); self.expanded = set()
        elif mode == "Erase" and cell not in (self.start, self.goal):
            self.grid[cell[0]][cell[1]] = EMPTY
        elif mode == "Start":
            self.start = cell
            self.path = []; self.frontier = set(); self.expanded = set()
        elif mode == "Goal":
            self.goal = cell
            self.path = []; self.frontier = set(); self.expanded = set()

    def _try_spawn_obstacle(self):
        prob = self.panel.sld_spawn.value
        if random.random() > prob:
            return
        cur = self.path[self.agent_step] if self.agent_step < len(self.path) else None
        cands = [
            (r, c) for r in range(self.rows) for c in range(self.cols)
            if self.grid[r][c] == EMPTY
            and (r, c) not in (self.start, self.goal)
            and (r, c) != cur
        ]
        if not cands:
            return
        nw = random.choice(cands)
        self.grid[nw[0]][nw[1]] = WALL
        remaining = set(self.path[self.agent_step + 1:])
        if nw in remaining:
            self.metrics["status"] = "Obstacle! Re-planning..."
            new_start = self.path[self.agent_step]
            res = self.do_search(start=new_start)
            if res:
                self.agent_step = 0
                self.metrics["replans"] += 1
                self.metrics["status"] = (
                    f"Re-planned #{self.metrics['replans']} | "
                    f"Cost {self.metrics['cost']}"
                )
            else:
                self.animating = False
                self.metrics["status"] = "No path after obstacle!"

    def _draw(self):
        self.surface.fill(C_BG)

        pygame.draw.rect(self.surface, (24, 24, 37), (0, 0, self.grid_w, self.top_bar))
        pygame.draw.line(self.surface, C_ACCENT,
                         (0, self.top_bar), (self.grid_w, self.top_bar), 1)
        status_t = self.font_top.render(self.metrics["status"], True, C_FRONTIER)
        self.surface.blit(status_t, (8, 8))

        self.renderer.draw(
            self.surface, self.grid, self.rows, self.cols,
            self.start, self.goal,
            self.frontier, self.expanded,
            self.path, self.agent_step,
            offset_y=self.top_bar
        )

        legend_y = self.grid_h + self.top_bar - 16
        self.renderer.draw_legend(self.surface, 4, legend_y)

        self.panel.draw(self.surface, self.grid_w, self.metrics)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            fps = max(1, int(self.panel.sld_speed.value))
            self.clock.tick(fps * 10)
            now = pygame.time.get_ticks()

            step_ms = 1000 // max(1, fps)
            if self.animating and self.path and now - self.last_step > step_ms:
                self.last_step = now
                if self.agent_step < len(self.path):
                    if self.panel.btn_dyn.on and self.agent_step < len(self.path) - 1:
                        self._try_spawn_obstacle()
                    if self.animating:
                        self.agent_step += 1
                else:
                    self.animating = False
                    self.metrics["status"] = "Agent reached Goal! ✓"

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.panel.handle_event(event, self.grid_w)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    cell = self._cell_at(*pos)

                    if cell and pos[0] < self.grid_w:
                        self.mouse_held = True
                        self._apply_draw(cell)
                    else:
                        clicked = self.panel.handle_click(pos, self.grid_w)
                        if clicked is self.panel.btn_run:
                            self.animating = False
                            self.agent_step = 0
                            self.do_search()
                        elif clicked is self.panel.btn_anim:
                            self.do_search()
                            self.agent_step = 0
                            self.animating  = bool(self.path)
                            self.last_step  = now
                        elif clicked is self.panel.btn_new:
                            self.do_new_grid()
                        elif clicked is self.panel.btn_clear:
                            self._clear_state()
                            self.metrics["status"] = "Cleared"
                        elif clicked is self.panel.btn_reset:
                            self.grid = make_empty_grid(self.rows, self.cols)
                            self._clear_state()
                            self.metrics["status"] = "All walls removed"

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_held = False

                elif event.type == pygame.MOUSEMOTION and self.mouse_held:
                    cell = self._cell_at(*event.pos)
                    if cell and event.pos[0] < self.grid_w:
                        self._apply_draw(cell)

                elif event.type == pygame.KEYDOWN:
                    k = event.key
                    if   k == pygame.K_r:      self.animating=False; self.agent_step=0; self.do_search()
                    elif k == pygame.K_a:      self.do_search(); self.agent_step=0; self.animating=bool(self.path); self.last_step=now
                    elif k == pygame.K_n:      self.do_new_grid()
                    elif k == pygame.K_c:      self._clear_state(); self.metrics["status"]="Cleared"
                    elif k == pygame.K_d:      self.panel.btn_dyn.on = not self.panel.btn_dyn.on
                    elif k == pygame.K_ESCAPE: running = False

            self._draw()

        pygame.quit()
