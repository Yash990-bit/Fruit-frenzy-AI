"""
FruitFrenzyAI – Fruit System
Handles fruit spawning, physics, drawing, and slice detection.
"""

import random
import math
import time
import pygame
import numpy as np
import config as cfg


# ── Fruit type definitions ──────────────────────────────
FRUIT_TYPES = [
    {"name": "watermelon", "color": cfg.WATERMELON_GREEN, "inner": cfg.WATERMELON_RED, "points": 10},
    {"name": "orange",     "color": cfg.ORANGE_COLOR,     "inner": cfg.YELLOW,         "points": 10},
    {"name": "apple",      "color": cfg.APPLE_RED,        "inner": cfg.WHITE,           "points": 10},
    {"name": "grape",      "color": cfg.GRAPE_PURPLE,     "inner": cfg.PINK,            "points": 15},
    {"name": "kiwi",       "color": cfg.KIWI_GREEN,       "inner": cfg.WHITE,           "points": 10},
    {"name": "mango",      "color": cfg.MANGO_ORANGE,     "inner": cfg.YELLOW,          "points": 15},
    {"name": "banana",     "color": cfg.BANANA_YELLOW,    "inner": cfg.WHITE,           "points": 10},
]


class Fruit:
    """A single fruit in the game world."""

    def __init__(self, x: float | None = None):
        ftype = random.choice(FRUIT_TYPES)
        self.name = ftype["name"]
        self.color = ftype["color"]
        self.inner_color = ftype["inner"]
        self.points = ftype["points"]

        self.radius = random.randint(cfg.FRUIT_RADIUS_MIN, cfg.FRUIT_RADIUS_MAX)
        self.x = x if x is not None else random.randint(
            self.radius + 40, cfg.SCREEN_WIDTH - self.radius - 40
        )
        self.y = cfg.SCREEN_HEIGHT + self.radius + 10
        self.vx = random.uniform(cfg.FRUIT_SPEED_X_MIN, cfg.FRUIT_SPEED_X_MAX)
        self.vy = random.uniform(cfg.FRUIT_SPEED_Y_MIN, cfg.FRUIT_SPEED_Y_MAX)
        self.angle = 0.0
        self.angular_vel = random.uniform(
            cfg.FRUIT_ANGULAR_SPEED_MIN, cfg.FRUIT_ANGULAR_SPEED_MAX
        )
        self.sliced = False
        self.alive = True

        # Post-slice halves
        self.half_offset_x = 0.0
        self.half_timer = 0.0

    def update(self, dt: float, slow_factor: float = 1.0):
        factor = slow_factor
        self.vy += cfg.GRAVITY * factor
        self.x += self.vx * factor
        self.y += self.vy * factor
        self.angle += self.angular_vel * factor

        if self.sliced:
            self.half_timer += dt
            self.half_offset_x += 2.0 * factor
            if self.half_timer > 1.0:
                self.alive = False

        # Off-screen removal
        if self.y > cfg.SCREEN_HEIGHT + self.radius + 50 and not self.sliced:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        ix, iy = int(self.x), int(self.y)
        r = self.radius

        if not self.sliced:
            # Outer circle
            pygame.draw.circle(surface, self.color, (ix, iy), r)
            # Inner circle (flesh)
            pygame.draw.circle(surface, self.inner_color, (ix, iy), int(r * 0.65))
            # Shine highlight
            shine_x = ix - int(r * 0.3)
            shine_y = iy - int(r * 0.3)
            pygame.draw.circle(surface, (255, 255, 255), (shine_x, shine_y), int(r * 0.18))
            # Leaf on top
            leaf_pts = [
                (ix, iy - r),
                (ix - 6, iy - r - 12),
                (ix + 6, iy - r - 8),
            ]
            pygame.draw.polygon(surface, cfg.DARK_GREEN, leaf_pts)
        else:
            # Draw two halves separating
            off = int(self.half_offset_x)
            alpha = max(0, 255 - int(self.half_timer * 300))

            # Left half
            left_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(left_surf, (*self.color, alpha), (r, r), r)
            pygame.draw.rect(left_surf, (0, 0, 0, 0), (r, 0, r, r * 2))
            # Inner
            pygame.draw.circle(left_surf, (*self.inner_color, alpha), (r, r), int(r * 0.65))
            pygame.draw.rect(left_surf, (0, 0, 0, 0), (r, 0, r, r * 2))
            surface.blit(left_surf, (ix - r - off, iy - r))

            # Right half
            right_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(right_surf, (*self.color, alpha), (r, r), r)
            pygame.draw.rect(right_surf, (0, 0, 0, 0), (0, 0, r, r * 2))
            pygame.draw.circle(right_surf, (*self.inner_color, alpha), (r, r), int(r * 0.65))
            pygame.draw.rect(right_surf, (0, 0, 0, 0), (0, 0, r, r * 2))
            surface.blit(right_surf, (ix - r + off, iy - r))

    def check_slice(self, trail: list[tuple[int, int]]) -> bool:
        """Check if the hand trail line segments intersect this fruit."""
        if self.sliced or len(trail) < 2:
            return False
        cx, cy, r = self.x, self.y, self.radius
        for i in range(len(trail) - 1):
            if _segment_circle_intersect(trail[i], trail[i + 1], cx, cy, r):
                return True
        return False

    def slice(self):
        self.sliced = True
        self.vy = min(self.vy, -2)


# ── Fruit Manager ───────────────────────────────────────

class FruitManager:
    """Spawns and manages all active fruits."""

    def __init__(self):
        self.fruits: list[Fruit] = []
        self.spawn_timer = 0.0
        self.spawn_interval = cfg.INITIAL_SPAWN_INTERVAL
        self.fruits_per_spawn = cfg.INITIAL_FRUITS_PER_SPAWN

    def update(self, dt: float, slow_factor: float = 1.0):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._spawn_batch()

        for f in self.fruits:
            f.update(dt, slow_factor)
        self.fruits = [f for f in self.fruits if f.alive]

    def draw(self, surface: pygame.Surface):
        for f in self.fruits:
            f.draw(surface)

    def increase_difficulty(self):
        self.spawn_interval = max(
            cfg.MIN_SPAWN_INTERVAL,
            self.spawn_interval - cfg.SPAWN_INTERVAL_DECREASE,
        )
        self.fruits_per_spawn = min(
            cfg.MAX_FRUITS_PER_SPAWN,
            self.fruits_per_spawn + cfg.FRUITS_PER_SPAWN_INCREASE,
        )

    def _spawn_batch(self):
        count = random.randint(
            max(1, self.fruits_per_spawn - 1), self.fruits_per_spawn
        )
        margin = 80
        positions = random.sample(
            range(margin, cfg.SCREEN_WIDTH - margin, 60),
            min(count, (cfg.SCREEN_WIDTH - 2 * margin) // 60),
        )
        for x in positions:
            self.fruits.append(Fruit(x))


# ── Geometry helper ─────────────────────────────────────

def _segment_circle_intersect(
    p1: tuple, p2: tuple, cx: float, cy: float, r: float
) -> bool:
    """Does line segment p1→p2 intersect circle (cx, cy, r)?"""
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
