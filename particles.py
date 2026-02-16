"""
FruitFrenzyAI – Particle / Visual Effects System
Juice splashes, bomb explosions, slice trails, screen shake.
"""

import random
import math
import pygame
import config as cfg


class Particle:
    """A single particle (juice drop, spark, etc.)."""

    __slots__ = ("x", "y", "vx", "vy", "color", "size", "lifetime", "age", "alive")

    def __init__(self, x, y, color, speed_range=(2, 8), size_range=(3, 7), lifetime=0.6):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(1, 3)
        self.color = color
        self.size = random.uniform(*size_range)
        self.lifetime = lifetime
        self.age = 0.0
        self.alive = True

    def update(self, dt: float):
        self.age += dt
        if self.age >= self.lifetime:
            self.alive = False
            return
        self.vy += cfg.GRAVITY * 0.5
        self.x += self.vx
        self.y += self.vy
        # Shrink as it ages
        progress = self.age / self.lifetime
        self.size = max(0.5, self.size * (1 - progress * 0.03))

    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        alpha = max(0, int(255 * (1 - self.age / self.lifetime)))
        s = max(1, int(self.size))
        p_surf = pygame.Surface((s * 2, s * 2), pygame.SRCALPHA)
        col = (*self.color[:3], alpha) if len(self.color) == 3 else (*self.color[:3], alpha)
        pygame.draw.circle(p_surf, col, (s, s), s)
        surface.blit(p_surf, (int(self.x) - s, int(self.y) - s))


class ParticleSystem:
    """Manages all active particles."""

    def __init__(self):
        self.particles: list[Particle] = []

    def emit(self, x, y, color, count=15, speed_range=(2, 8), lifetime=0.6):
        for _ in range(count):
            self.particles.append(
                Particle(x, y, color, speed_range=speed_range, lifetime=lifetime)
            )

    def emit_slice(self, x, y, color):
        """Emit juice particles for a fruit slice."""
        self.emit(x, y, color, count=cfg.PARTICLE_COUNT_SLICE, lifetime=cfg.PARTICLE_LIFETIME)

    def emit_bomb(self, x, y):
        """Emit explosion particles for a bomb."""
        self.emit(
            x, y, cfg.BOMB_FLASH,
            count=cfg.PARTICLE_COUNT_BOMB,
            speed_range=(4, 12),
            lifetime=0.8,
        )
        # Secondary sparks
        self.emit(x, y, cfg.YELLOW, count=10, speed_range=(3, 9), lifetime=0.5)

    def emit_powerup(self, x, y, color):
        """Emit sparkle particles for a power-up."""
        self.emit(x, y, color, count=20, speed_range=(3, 10), lifetime=0.7)
        self.emit(x, y, cfg.WHITE, count=8, speed_range=(2, 6), lifetime=0.4)

    def update(self, dt: float):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface: pygame.Surface):
        for p in self.particles:
            p.draw(surface)


class SliceTrail:
    """Renders a glowing trail following the hand position."""

    def __init__(self):
        self.glow_color = (200, 230, 255)

    def draw(self, surface: pygame.Surface, trail: list[tuple[int, int]]):
        if len(trail) < 2:
            return
        n = len(trail)
        for i in range(1, n):
            progress = i / n
            alpha = int(255 * progress)
            width = max(1, int(3 + 5 * progress))
            color = (*self.glow_color, alpha)

            # Glow layer
            glow_surf = pygame.Surface(
                (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            pygame.draw.line(glow_surf, (*self.glow_color, alpha // 3), trail[i - 1], trail[i], width + 4)
            pygame.draw.line(glow_surf, color, trail[i - 1], trail[i], width)
            surface.blit(glow_surf, (0, 0))

        # Bright tip
        if trail:
            tip = trail[-1]
            pygame.draw.circle(surface, cfg.WHITE, tip, 6)
            glow = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*self.glow_color, 100), (12, 12), 12)
            surface.blit(glow, (tip[0] - 12, tip[1] - 12))


class ScreenShake:
    """Applies a screen-shake offset."""

    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.timer = 0.0

    def trigger(self, intensity=10.0, duration=0.3):
        self.intensity = intensity
        self.duration = duration
        self.timer = 0.0

    def update(self, dt: float) -> tuple[int, int]:
        if self.timer >= self.duration:
            return (0, 0)
        self.timer += dt
        progress = 1 - self.timer / self.duration
        offset_x = int(random.uniform(-1, 1) * self.intensity * progress)
        offset_y = int(random.uniform(-1, 1) * self.intensity * progress)
        return (offset_x, offset_y)
