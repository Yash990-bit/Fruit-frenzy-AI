"""
FruitFrenzyAI – Power-Up System
Special fruits: Fire, Ice, Lightning, Magnet, Shield.
"""

import random
import math
import pygame
import config as cfg


class PowerUpType:
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    MAGNET = "magnet"
    SHIELD = "shield"


POWERUP_DEFS = {
    PowerUpType.FIRE: {
        "color": cfg.FIRE_COLOR,
        "glow": (255, 120, 30),
        "label": "F",
        "desc": "Auto-Slice!",
    },
    PowerUpType.ICE: {
        "color": cfg.ICE_COLOR,
        "glow": (100, 200, 255),
        "label": "I",
        "desc": "Slow Motion!",
    },
    PowerUpType.LIGHTNING: {
        "color": cfg.LIGHTNING_COLOR,
        "glow": (255, 255, 150),
        "label": "Z",
        "desc": "+50 Bonus!",
    },
    PowerUpType.MAGNET: {
        "color": cfg.MAGNET_COLOR,
        "glow": (200, 100, 255),
        "label": "M",
        "desc": "Magnet!",
    },
    PowerUpType.SHIELD: {
        "color": cfg.SHIELD_COLOR,
        "glow": (80, 255, 220),
        "label": "S",
        "desc": "Shield!",
    },
}


class PowerUp:
    """A special power-up fruit."""

    def __init__(self, x: float | None = None, ptype: str | None = None):
        self.ptype = ptype or random.choice(list(POWERUP_DEFS.keys()))
        defn = POWERUP_DEFS[self.ptype]
        self.color = defn["color"]
        self.glow_color = defn["glow"]
        self.label = defn["label"]
        self.desc = defn["desc"]

        self.radius = random.randint(30, 40)
        self.x = x if x is not None else random.randint(
            self.radius + 60, cfg.SCREEN_WIDTH - self.radius - 60
        )
        self.y = cfg.SCREEN_HEIGHT + self.radius + 10
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(cfg.FRUIT_SPEED_Y_MIN, cfg.FRUIT_SPEED_Y_MAX)
        self.angle = 0.0
        self.angular_vel = random.uniform(-4, 4)

        self.sliced = False
        self.alive = True
        self._pulse = 0.0

    def update(self, dt: float, slow_factor: float = 1.0):
        self.vy += cfg.GRAVITY * slow_factor
        self.x += self.vx * slow_factor
        self.y += self.vy * slow_factor
        self.angle += self.angular_vel * slow_factor
        self._pulse += dt * 6

        if self.sliced:
            self.alive = False

        if self.y > cfg.SCREEN_HEIGHT + self.radius + 50 and not self.sliced:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        ix, iy = int(self.x), int(self.y)
        r = self.radius

        # Pulsating glow
        glow_r = int(r * (1.3 + 0.2 * math.sin(self._pulse)))
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf, (*self.glow_color, 60), (glow_r, glow_r), glow_r
        )
        surface.blit(glow_surf, (ix - glow_r, iy - glow_r))

        # Main body
        pygame.draw.circle(surface, self.color, (ix, iy), r)
        pygame.draw.circle(surface, cfg.WHITE, (ix, iy), r, 2)

        # Inner pattern based on type
        if self.ptype == PowerUpType.FIRE:
            # Flame tongues
            for i in range(5):
                a = self.angle + i * 72
                flame_len = r * 0.6 + r * 0.15 * math.sin(self._pulse + i)
                ex = ix + int(flame_len * math.cos(math.radians(a)))
                ey = iy + int(flame_len * math.sin(math.radians(a)))
                pygame.draw.line(surface, cfg.YELLOW, (ix, iy), (ex, ey), 3)
            pygame.draw.circle(surface, cfg.YELLOW, (ix, iy), int(r * 0.3))

        elif self.ptype == PowerUpType.ICE:
            # Snowflake arms
            for i in range(6):
                a = self.angle + i * 60
                ex = ix + int(r * 0.6 * math.cos(math.radians(a)))
                ey = iy + int(r * 0.6 * math.sin(math.radians(a)))
                pygame.draw.line(surface, cfg.WHITE, (ix, iy), (ex, ey), 2)
                # Branch
                bx = ix + int(r * 0.35 * math.cos(math.radians(a)))
                by = iy + int(r * 0.35 * math.sin(math.radians(a)))
                bx2 = bx + int(r * 0.2 * math.cos(math.radians(a + 45)))
                by2 = by + int(r * 0.2 * math.sin(math.radians(a + 45)))
                pygame.draw.line(surface, cfg.WHITE, (bx, by), (bx2, by2), 1)

        elif self.ptype == PowerUpType.LIGHTNING:
            # Bolt shape
            points = [
                (ix - 5, iy - int(r * 0.5)),
                (ix + 2, iy - 3),
                (ix - 2, iy - 3),
                (ix + 5, iy + int(r * 0.5)),
                (ix - 1, iy + 3),
                (ix + 1, iy + 3),
            ]
            pygame.draw.polygon(surface, cfg.WHITE, points)

        elif self.ptype == PowerUpType.MAGNET:
            # U-magnet shape
            pygame.draw.arc(surface, cfg.WHITE,
                            (ix - int(r * 0.4), iy - int(r * 0.2), int(r * 0.8), int(r * 0.6)),
                            math.pi, 2 * math.pi, 3)
            pygame.draw.line(surface, cfg.RED,
                             (ix - int(r * 0.4), iy + int(r * 0.1)),
                             (ix - int(r * 0.4), iy - int(r * 0.3)), 4)
            pygame.draw.line(surface, cfg.BLUE,
                             (ix + int(r * 0.4), iy + int(r * 0.1)),
                             (ix + int(r * 0.4), iy - int(r * 0.3)), 4)

        elif self.ptype == PowerUpType.SHIELD:
            # Shield emblem
            shield_pts = [
                (ix, iy - int(r * 0.45)),
                (ix - int(r * 0.35), iy - int(r * 0.2)),
                (ix - int(r * 0.3), iy + int(r * 0.15)),
                (ix, iy + int(r * 0.45)),
                (ix + int(r * 0.3), iy + int(r * 0.15)),
                (ix + int(r * 0.35), iy - int(r * 0.2)),
            ]
            pygame.draw.polygon(surface, cfg.WHITE, shield_pts, 2)
            pygame.draw.polygon(surface, (*cfg.WHITE, 60), shield_pts)

        # Label letter
        font = pygame.font.SysFont("Arial", int(r * 0.45), bold=True)
        txt = font.render(self.label, True, cfg.WHITE)
        surface.blit(txt, (ix - txt.get_width() // 2, iy + int(r * 0.35)))

    def check_slice(self, trail: list[tuple[int, int]]) -> bool:
        if self.sliced or len(trail) < 2:
            return False
        for i in range(len(trail) - 1):
            if _seg_circle(trail[i], trail[i + 1], self.x, self.y, self.radius):
                return True
        return False

    def slice(self):
        self.sliced = True


class PowerUpManager:
    """Spawns and manages power-ups."""

    def __init__(self):
        self.powerups: list[PowerUp] = []
        self.probability = cfg.POWERUP_PROBABILITY

    def try_spawn(self):
        if random.random() < self.probability:
            self.powerups.append(PowerUp())

    def update(self, dt: float, slow_factor: float = 1.0):
        for p in self.powerups:
            p.update(dt, slow_factor)
        self.powerups = [p for p in self.powerups if p.alive]

    def draw(self, surface: pygame.Surface):
        for p in self.powerups:
            p.draw(surface)


# ── geometry ────────────────────────────────────────────

def _seg_circle(p1, p2, cx, cy, r) -> bool:
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    fx, fy = p1[0] - cx, p1[1] - cy
    a = dx * dx + dy * dy
    if a == 0:
        return (fx * fx + fy * fy) <= r * r
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - r * r
    disc = b * b - 4 * a * c
    if disc < 0:
        return False
    disc = math.sqrt(disc)
    t1 = (-b - disc) / (2 * a)
    t2 = (-b + disc) / (2 * a)
    return (0 <= t1 <= 1) or (0 <= t2 <= 1) or (t1 < 0 and t2 > 1)
