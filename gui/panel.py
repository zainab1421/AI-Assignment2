import pygame
from gui.grid_renderer import (
    C_BG, C_PANEL_BG, C_TEXT, C_ACCENT, C_EMPTY, C_WALL,
    C_START, C_GOAL, C_FRONTIER, C_EXPANDED, C_PATH, C_AGENT
)

C_BTN      = (49, 50, 68)
C_BTN_HOV  = (69, 71, 90)
C_BTN_ACT  = (166, 227, 161)
C_YELLOW   = (249, 226, 175)
C_RED      = (243, 139, 168)


class Button:
    def __init__(self, rect, label, toggle=False, active_color=None):
        self.rect         = pygame.Rect(rect)
        self.label        = label
        self.toggle       = toggle
        self.on           = False
        self.active_color = active_color or C_BTN_ACT

    def draw(self, surface, font):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if self.toggle and self.on:
            bg = self.active_color
            fg = (24, 24, 37)
        elif hovered:
            bg = C_BTN_HOV
            fg = C_TEXT
        else:
            bg = C_BTN
            fg = C_TEXT
        pygame.draw.rect(surface, bg, self.rect, border_radius=5)
        pygame.draw.rect(surface, C_ACCENT, self.rect, 1, border_radius=5)
        t = font.render(self.label, True, fg)
        surface.blit(t, t.get_rect(center=self.rect.center))

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            if self.toggle:
                self.on = not self.on
            return True
        return False


class Cycler:
    def __init__(self, rect, options, prefix=""):
        self.rect    = pygame.Rect(rect)
        self.options = options
        self.idx     = 0
        self.prefix  = prefix

    @property
    def value(self):
        return self.options[self.idx]

    def next(self):
        self.idx = (self.idx + 1) % len(self.options)

    def draw(self, surface, font):
        pygame.draw.rect(surface, C_BTN, self.rect, border_radius=5)
        pygame.draw.rect(surface, C_ACCENT, self.rect, 1, border_radius=5)
        t = font.render(f"{self.prefix}{self.value}", True, C_YELLOW)
        surface.blit(t, t.get_rect(center=self.rect.center))

    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.next()
            return True
        return False


class Slider:
    def __init__(self, rect, label, min_val, max_val, value, step=1, fmt=None):
        self.rect    = pygame.Rect(rect)
        self.label   = label
        self.min_val = min_val
        self.max_val = max_val
        self.value   = value
        self.step    = step
        self.fmt     = fmt or (lambda v: str(v))
        self.dragging = False

    def _val_to_x(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + ratio * self.rect.width)

    def draw(self, surface, font):
        track_y = self.rect.centery
        pygame.draw.line(surface, C_BTN,
                         (self.rect.x, track_y),
                         (self.rect.right, track_y), 4)
        kx = self._val_to_x()
        pygame.draw.circle(surface, C_ACCENT, (kx, track_y), 7)
        lbl = font.render(f"{self.label}: {self.fmt(self.value)}", True, C_TEXT)
        surface.blit(lbl, (self.rect.x, self.rect.y - 16))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            knob_x = self._val_to_x()
            if abs(event.pos[0] - knob_x) < 10 and abs(event.pos[1] - self.rect.centery) < 10:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            ratio = (event.pos[0] - self.rect.x) / self.rect.width
            ratio = max(0.0, min(1.0, ratio))
            raw   = self.min_val + ratio * (self.max_val - self.min_val)
            steps = round((raw - self.min_val) / self.step)
            self.value = round(self.min_val + steps * self.step, 4)
            self.value = max(self.min_val, min(self.max_val, self.value))


class ControlPanel:
    PANEL_W = 220

    def __init__(self, screen_h, grid_h):
        self.screen_h = screen_h
        self.grid_h   = grid_h
        self.font     = None
        self.font_sm  = None

        x  = 8
        bw = self.PANEL_W - 16
        bh = 28

        def btn(y, label, toggle=False, ac=None):
            return Button((x, y, bw, bh), label, toggle, ac)

        def cyc(y, opts, pre, w=None):
            return Cycler((x, y, w or bw, bh), opts, pre)

        def sld(y, label, lo, hi, val, step=1, fmt=None):
            return Slider((x + 4, y + 18, bw - 8, 8), label, lo, hi, val, step, fmt)

        y = 10
        self.btn_run   = btn(y,      "▶  Run Search");        y += bh + 6
        self.btn_anim  = btn(y,      "⚡ Animate Agent");      y += bh + 6
        self.btn_new   = btn(y,      "⊞  New Grid");          y += bh + 6
        self.btn_clear = btn(y,      "✕  Clear Path");        y += bh + 6
        self.btn_reset = btn(y,      "↺  Reset Walls");       y += bh + 6
        self.btn_dyn   = btn(y,      "Dynamic: OFF", toggle=True, ac=C_BTN_ACT); y += bh + 10

        self.cyc_algo  = cyc(y,  ["A*", "GBFS"],               "Algo: ");       y += bh + 6
        self.cyc_heur  = cyc(y,  ["Manhattan", "Euclidean"],   "H: ");          y += bh + 6
        self.cyc_draw  = cyc(y,  ["Wall", "Erase", "Start", "Goal"], "Draw: "); y += bh + 16

        self.sld_rows  = sld(y,  "Rows",    8,  25, 15);   y += 46
        self.sld_cols  = sld(y,  "Cols",   10,  35, 20);   y += 46
        self.sld_dens  = sld(y,  "Density", 0.05, 0.55, 0.28, 0.05,
                             fmt=lambda v: f"{v:.0%}");     y += 46
        self.sld_spawn = sld(y,  "Spawn %", 0.05, 0.40, 0.15, 0.05,
                             fmt=lambda v: f"{v:.0%}");     y += 46
        self.sld_speed = sld(y,  "Speed",   1, 20, 8,
                             fmt=lambda v: f"{v} fps");     y += 46

        self.metrics_y = y + 10

        self.all_btns    = [self.btn_run, self.btn_anim, self.btn_new,
                            self.btn_clear, self.btn_reset, self.btn_dyn]
        self.all_cyclers = [self.cyc_algo, self.cyc_heur, self.cyc_draw]
        self.all_sliders = [self.sld_rows, self.sld_cols, self.sld_dens,
                            self.sld_spawn, self.sld_speed]

    def _ensure_fonts(self):
        if self.font is None:
            self.font    = pygame.font.SysFont("Segoe UI", 13, bold=True)
            self.font_sm = pygame.font.SysFont("Segoe UI", 11)

    def draw(self, surface, panel_x, metrics: dict):
        self._ensure_fonts()
        panel_rect = pygame.Rect(panel_x, 0, self.PANEL_W, self.screen_h)
        pygame.draw.rect(surface, C_PANEL_BG, panel_rect)
        pygame.draw.line(surface, C_ACCENT, (panel_x, 0), (panel_x, self.screen_h), 1)

        for w in self.all_btns + self.all_cyclers + self.all_sliders:
            if w.rect.x < panel_x:
                w.rect.x += panel_x
                if hasattr(w, 'rect') and isinstance(w, Slider):
                    w.rect.x += panel_x

        for b in self.all_btns:    b.draw(surface, self.font)
        for c in self.all_cyclers: c.draw(surface, self.font)
        for s in self.all_sliders: s.draw(surface, self.font_sm)

        self.btn_dyn.label = "Dynamic: ON" if self.btn_dyn.on else "Dynamic: OFF"

        my = self.metrics_y + panel_x * 0
        mx = panel_x + 8
        my_abs = self.metrics_y
        pygame.draw.line(surface, C_ACCENT, (panel_x + 4, my_abs - 4),
                         (panel_x + self.PANEL_W - 4, my_abs - 4), 1)
        rows_metrics = [
            ("Nodes Expanded", str(metrics.get("nodes", 0))),
            ("Path Cost",      str(metrics.get("cost", 0))),
            ("Time",           f"{metrics.get('time_ms', 0.0):.1f} ms"),
            ("Re-plans",       str(metrics.get("replans", 0))),
            ("Status",         metrics.get("status", "Ready")),
        ]
        y = my_abs
        for label, val in rows_metrics:
            lbl = self.font_sm.render(label + ":", True, C_ACCENT)
            surface.blit(lbl, (mx, y))
            v   = self.font_sm.render(val, True, C_TEXT)
            surface.blit(v,   (mx, y + 14))
            y  += 34

    def handle_click(self, pos, panel_x):
        for b in self.all_btns:
            if b.handle_click(pos):
                return b
        for c in self.all_cyclers:
            if c.handle_click(pos):
                return c
        return None

    def handle_event(self, event, panel_x):
        for s in self.all_sliders:
            s.handle_event(event)
