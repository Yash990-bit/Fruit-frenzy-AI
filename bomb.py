"""
FruitFrenzyAI – Bomb System
Bombs that penalise the player when sliced.
"""

import random
import math
import pygame
import config as cfg


class Bomb:
    """A bomb object – slicing it costs a life."""

    def __init__(self, x: float | None = None):
        self.radius = random.randint(24, 34)
        self.x = x if x is not None else random.randint(
            self.radius + 50, cfg.SCREEN_WIDTH - self.radius - 50
        )
        self.y = cfg.SCREEN_HEIGHT + self.radius + 10
        self.vx = random.uniform(cfg.FRUIT_SPEED_X_MIN, cfg.FRUIT_SPEED_X_MAX)
        self.vy = random.uniform(cfg.FRUIT_SPEED_Y_MIN, cfg.FRUIT_SPEED_Y_MAX)
        self.angle = 0.0
        self.angular_vel = random.uniform(-3, 3)
        self.sliced = False
        self.alive = True
        self.flash_timer = 0.0

        # Fuse spark animation
        self._spark_angle = 0.0

    def update(self, dt: float, slow_factor: float = 1.0):
        factor = slow_factor
        self.vy += cfg.GRAVITY * factor
        self.x += self.vx * factor
        self.y += self.vy * factor
        self.angle += self.angular_vel * factor
        self._spark_angle += 8 * dt

        if self.sliced:
            self.flash_timer += dt
            if self.flash_timer > 0.5:
                self.alive = False

        if self.y > cfg.SCREEN_HEIGHT + self.radius + 50 and not self.sliced:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        ix, iy = int(self.x), int(self.y)
        r = self.radius

        if not self.sliced:
            # Body
            pygame.draw.circle(surface, cfg.BOMB_COLOR, (ix, iy), r)
            pygame.draw.circle(surface, (60, 60, 60), (ix, iy), r, 2)

            # Skull / X symbol
            pygame.draw.line(surface, cfg.RED, (ix - 7, iy - 7), (ix + 7, iy + 7), 3)
            pygame.draw.line(surface, cfg.RED, (ix + 7, iy - 7), (ix - 7, iy + 7), 3)

            # Fuse
            fuse_x = ix + int(r * 0.5)
            fuse_y = iy - r
            pygame.draw.line(surface, cfg.BOMB_FUSE, (ix, iy - r + 4), (fuse_x, fuse_y - 10), 3)

            # Spark at fuse tip
            spark_size = int(4 + 2 * math.sin(self._spark_angle))
            pygame.draw.circle(surface, cfg.YELLOW, (fuse_x, fuse_y - 10), spark_size)
            pygame.draw.circle(surface, cfg.WHITE, (fuse_x, fuse_y - 10), max(1, spark_size - 2))
        else:
            # Explosion flash
            alpha = max(0, 255 - int(self.flash_timer * 600))
            flash_r = int(r * (1 + self.flash_timer * 4))
            flash_surf = pygame.Surface((flash_r * 2, flash_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                flash_surf, (*cfg.BOMB_FLASH, alpha), (flash_r, flash_r), flash_r
            )
            surface.blit(flash_surf, (ix - flash_r, iy - flash_r))

    def check_slice(self, trail: list[tuple[int, int]]) -> bool:
        if self.sliced or len(trail) < 2:
            return False
        for i in range(len(trail) - 1):
            if _seg_circle(trail[i], trail[i + 1], self.x, self.y, self.radius):
                return True
        return False

    def slice(self):
        self.sliced = True


class BombManager:
    """Manages bomb spawning alongside fruits."""

    def __init__(self):
        self.bombs: list[Bomb] = []
        self.bomb_probability = cfg.BOMB_PROBABILITY

    def try_spawn(self):
        """Call once per fruit spawn batch. Randomly adds a bomb."""
        if random.random() < self.bomb_probability:
            self.bombs.append(Bomb())

    def update(self, dt: float, slow_factor: float = 1.0):
        for b in self.bombs:
            b.update(dt, slow_factor)
        self.bombs = [b for b in self.bombs if b.alive]

    def draw(self, surface: pygame.Surface):
        for b in self.bombs:
            b.draw(surface)

    def increase_difficulty(self):
        self.bomb_probability = min(
            0.35, self.bomb_probability + cfg.BOMB_PROBABILITY_INCREASE
        )


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
