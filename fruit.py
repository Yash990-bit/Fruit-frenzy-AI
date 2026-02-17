"""
FruitFrenzyAI – Fruit System (Enhanced Sprites)
Detailed per-type fruit rendering with gradient fills, stems, seeds, and cross-sections.
"""

import random
import math
import pygame
import numpy as np
import config as cfg


# ── Fruit type definitions ──────────────────────────────
FRUIT_TYPES = [
    {"name": "watermelon", "color": cfg.WATERMELON_GREEN, "inner": cfg.WATERMELON_RED, "points": 10},
    {"name": "orange",     "color": cfg.ORANGE_COLOR,     "inner": (255, 200, 80),      "points": 10},
    {"name": "apple",      "color": cfg.APPLE_RED,        "inner": (255, 255, 220),      "points": 10},
    {"name": "grape",      "color": cfg.GRAPE_PURPLE,     "inner": (200, 130, 220),      "points": 15},
    {"name": "kiwi",       "color": cfg.KIWI_GREEN,       "inner": (180, 220, 100),      "points": 10},
    {"name": "mango",      "color": cfg.MANGO_ORANGE,     "inner": (255, 220, 100),      "points": 15},
    {"name": "banana",     "color": cfg.BANANA_YELLOW,    "inner": (255, 255, 220),      "points": 10},
]


def _draw_gradient_circle(surface, center, radius, color_outer, color_inner):
    """Draw a radial gradient circle."""
    for i in range(radius, 0, -1):
        t = 1 - (i / radius)
        r = int(color_outer[0] + (color_inner[0] - color_outer[0]) * t)
        g = int(color_outer[1] + (color_inner[1] - color_outer[1]) * t)
        b = int(color_outer[2] + (color_inner[2] - color_outer[2]) * t)
        pygame.draw.circle(surface, (r, g, b), center, i)


def _create_fruit_surface(name, radius, color, inner_color):
    """Pre-render a detailed fruit sprite surface."""
    size = radius * 2 + 20
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    r = radius

    if name == "watermelon":
        # Dark green base with stripes
        darker = (20, 100, 20)
        _draw_gradient_circle(surf, (cx, cy), r, darker, color)
        # Stripes
        for i in range(-r, r, 12):
            stripe_color = (15, 80, 15)
            start_y = cy + i
            length = int(math.sqrt(max(0, r * r - i * i)))
            if length > 5:
                pygame.draw.line(surf, stripe_color,
                                 (cx - length + 5, start_y), (cx + length - 5, start_y), 3)
        # Shine
        shine_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(shine_surf, (255, 255, 255, 50),
                            (cx - r // 2, cy - r + 4, r // 2, r // 2))
        surf.blit(shine_surf, (0, 0))

    elif name == "orange":
        _draw_gradient_circle(surf, (cx, cy), r, (200, 100, 0), color)
        # Dimples (texture)
        for _ in range(12):
            dx = random.randint(-r + 8, r - 8)
            dy = random.randint(-r + 8, r - 8)
            if dx * dx + dy * dy < (r - 8) ** 2:
                pygame.draw.circle(surf, (230, 130, 0), (cx + dx, cy + dy), 2)
        # Navel
        pygame.draw.circle(surf, (180, 90, 0), (cx, cy + r - 8), 4)
        # Shine
        pygame.draw.ellipse(surf, (255, 255, 200, 70),
                            (cx - r // 3, cy - r + 5, r // 2, r // 3))
        # Leaf + stem
        pygame.draw.line(surf, (100, 60, 20), (cx, cy - r + 2), (cx, cy - r - 6), 3)
        leaf_pts = [(cx + 2, cy - r - 4), (cx + 12, cy - r - 12), (cx + 6, cy - r - 2)]
        pygame.draw.polygon(surf, cfg.DARK_GREEN, leaf_pts)

    elif name == "apple":
        # Apple shape (slightly wider)
        _draw_gradient_circle(surf, (cx, cy + 2), r, (150, 10, 10), color)
        # Blush highlight
        pygame.draw.circle(surf, (240, 60, 60), (cx - r // 4, cy - r // 4), r // 3)
        # Shine
        shine = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(shine, (255, 255, 255, 80),
                            (cx - r // 2 - 2, cy - r + 6, r // 2, r // 3))
        surf.blit(shine, (0, 0))
        # Stem
        pygame.draw.line(surf, (100, 60, 20), (cx, cy - r + 2), (cx + 2, cy - r - 10), 3)
        # Leaf
        leaf_pts = [(cx + 3, cy - r - 6), (cx + 15, cy - r - 14), (cx + 10, cy - r - 4)]
        pygame.draw.polygon(surf, (50, 180, 50), leaf_pts)
        # Small indent at top
        pygame.draw.arc(surf, (130, 10, 10), (cx - 6, cy - r - 2, 12, 8), 0, math.pi, 2)

    elif name == "grape":
        # Cluster of small circles
        grape_positions = [
            (0, -r // 2), (-r // 3, -r // 4), (r // 3, -r // 4),
            (-r // 2, r // 6), (0, r // 6), (r // 2, r // 6),
            (-r // 3, r // 2), (r // 3, r // 2), (0, r // 2 + r // 4),
        ]
        grape_r = r // 3 + 2
        for gx, gy in grape_positions:
            _draw_gradient_circle(surf, (cx + gx, cy + gy), grape_r,
                                  (80, 0, 80), color)
            # Tiny shine on each grape
            pygame.draw.circle(surf, (200, 150, 220, 120),
                               (cx + gx - grape_r // 3, cy + gy - grape_r // 3),
                               grape_r // 4)
        # Stem
        pygame.draw.line(surf, (100, 70, 30), (cx, cy - r // 2 - grape_r),
                         (cx, cy - r // 2 - grape_r - 12), 3)
        leaf = [(cx, cy - r // 2 - grape_r - 8),
                (cx + 14, cy - r // 2 - grape_r - 16),
                (cx + 8, cy - r // 2 - grape_r - 4)]
        pygame.draw.polygon(surf, (50, 160, 50), leaf)

    elif name == "kiwi":
        # Brown fuzzy exterior
        _draw_gradient_circle(surf, (cx, cy), r, (120, 90, 40), (160, 130, 60))
        # Fuzzy texture dots
        for _ in range(20):
            dx = random.randint(-r + 5, r - 5)
            dy = random.randint(-r + 5, r - 5)
            if dx * dx + dy * dy < (r - 5) ** 2:
                pygame.draw.circle(surf, (100, 75, 30), (cx + dx, cy + dy), 1)
        # Shine
        pygame.draw.ellipse(surf, (200, 180, 120, 60),
                            (cx - r // 3, cy - r + 5, r // 2, r // 3))
        # Small dimples at ends
        pygame.draw.circle(surf, (90, 60, 25), (cx, cy - r + 4), 3)
        pygame.draw.circle(surf, (90, 60, 25), (cx, cy + r - 4), 3)

    elif name == "mango":
        # Oval mango shape
        mango_rect = (cx - r, cy - int(r * 0.75), r * 2, int(r * 1.5))
        # Draw elongated shape
        _draw_gradient_circle(surf, (cx, cy), r, (200, 100, 0), color)
        # Red-orange blush on the side
        blush = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(blush, (220, 60, 30, 60), (cx + r // 3, cy - r // 4), r // 2)
        surf.blit(blush, (0, 0))
        # Shine
        pygame.draw.ellipse(surf, (255, 255, 200, 70),
                            (cx - r // 2, cy - r + 5, r // 2, r // 3))
        # Stem
        pygame.draw.line(surf, (100, 70, 20), (cx, cy - r + 2), (cx + 3, cy - r - 8), 3)

    elif name == "banana":
        # Curved banana shape using arc
        banana_color = color
        # Draw a thick curved shape
        arc_rect = (cx - r - 5, cy - r, r * 2 + 10, r * 2)
        pygame.draw.arc(surf, banana_color, arc_rect, 0.3, math.pi - 0.3, r // 2 + 8)
        # Tips
        tip_l = (cx - r + 5, cy - int(r * 0.25))
        tip_r = (cx + r - 5, cy - int(r * 0.25))
        pygame.draw.circle(surf, (180, 160, 30), tip_l, 5)
        pygame.draw.circle(surf, (140, 120, 20), tip_r, 5)
        # Brown end spots
        pygame.draw.circle(surf, (120, 90, 20), tip_l, 3)
        pygame.draw.circle(surf, (120, 90, 20), tip_r, 3)
        # Highlight along curve
        highlight_rect = (cx - r + 10, cy - r + 5, r * 2 - 20, r * 2 - 10)
        pygame.draw.arc(surf, (255, 245, 120), highlight_rect, 0.5, math.pi - 0.5, 3)

    return surf


def _create_slice_surface(name, radius, color, inner_color, is_left=True):
    """Pre-render a sliced half surface with cross-section detail."""
    size = radius * 2 + 20
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    r = radius

    # Outer rind
    pygame.draw.circle(surf, color, (cx, cy), r)
    # Inner flesh
    pygame.draw.circle(surf, inner_color, (cx, cy), int(r * 0.8))

    # Per-fruit cross-section details
    if name == "watermelon":
        # Seeds
        for _ in range(8):
            sx = cx + random.randint(-int(r * 0.5), int(r * 0.5))
            sy = cy + random.randint(-int(r * 0.5), int(r * 0.5))
            if (sx - cx) ** 2 + (sy - cy) ** 2 < (r * 0.6) ** 2:
                pygame.draw.ellipse(surf, (30, 30, 30), (sx - 2, sy - 1, 5, 3))

    elif name == "orange":
        # Segments
        for i in range(8):
            angle = i * (math.pi * 2 / 8)
            ex = cx + int(r * 0.7 * math.cos(angle))
            ey = cy + int(r * 0.7 * math.sin(angle))
            pygame.draw.line(surf, (255, 180, 50), (cx, cy), (ex, ey), 2)

    elif name == "apple":
        # Core / star pattern
        for i in range(5):
            angle = i * (math.pi * 2 / 5) - math.pi / 2
            sx = cx + int(r * 0.25 * math.cos(angle))
            sy = cy + int(r * 0.25 * math.sin(angle))
            pygame.draw.circle(surf, (160, 120, 80), (sx, sy), 3)
        pygame.draw.circle(surf, (200, 180, 140), (cx, cy), 6)

    elif name == "kiwi":
        # White center + radial lines + seeds
        pygame.draw.circle(surf, (230, 240, 200), (cx, cy), int(r * 0.2))
        for i in range(16):
            angle = i * (math.pi * 2 / 16)
            ex = cx + int(r * 0.65 * math.cos(angle))
            ey = cy + int(r * 0.65 * math.sin(angle))
            pygame.draw.line(surf, (200, 230, 150), (cx, cy), (ex, ey), 1)
        # Tiny black seeds
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(r * 0.3, r * 0.6)
            sx = cx + int(dist * math.cos(angle))
            sy = cy + int(dist * math.sin(angle))
            pygame.draw.circle(surf, (20, 20, 20), (sx, sy), 1)

    elif name == "grape":
        pygame.draw.circle(surf, (200, 150, 220), (cx, cy), int(r * 0.5))
        pygame.draw.circle(surf, (180, 120, 200), (cx, cy), int(r * 0.2))

    elif name == "mango":
        # Pit in center
        pygame.draw.ellipse(surf, (200, 170, 80), (cx - r // 3, cy - r // 4, r * 2 // 3, r // 2))
        pygame.draw.ellipse(surf, (180, 150, 60), (cx - r // 4, cy - r // 6, r // 2, r // 3))

    elif name == "banana":
        # Simple creamy interior
        pygame.draw.circle(surf, (255, 255, 230), (cx, cy), int(r * 0.6))

    # Mask to half
    mask_rect = (cx if is_left else 0, 0, size // 2, size)
    pygame.draw.rect(surf, (0, 0, 0, 0), mask_rect)

    return surf


class Fruit:
    """A single fruit in the game world with detailed sprite rendering."""

    # Cache for pre-rendered sprites
    _sprite_cache: dict[str, dict[int, pygame.Surface]] = {}
    _slice_cache: dict[str, dict[int, tuple[pygame.Surface, pygame.Surface]]] = {}

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

        # Pre-render sprite
        self._sprite = self._get_sprite()
        self._left_half, self._right_half = self._get_slice_sprites()

    def _get_sprite(self) -> pygame.Surface:
        key = self.name
        if key not in Fruit._sprite_cache:
            Fruit._sprite_cache[key] = {}
        cache = Fruit._sprite_cache[key]
        if self.radius not in cache:
            cache[self.radius] = _create_fruit_surface(
                self.name, self.radius, self.color, self.inner_color
            )
        return cache[self.radius]

    def _get_slice_sprites(self) -> tuple[pygame.Surface, pygame.Surface]:
        key = self.name
        if key not in Fruit._slice_cache:
            Fruit._slice_cache[key] = {}
        cache = Fruit._slice_cache[key]
        if self.radius not in cache:
            left = _create_slice_surface(self.name, self.radius, self.color, self.inner_color, True)
            right = _create_slice_surface(self.name, self.radius, self.color, self.inner_color, False)
            cache[self.radius] = (left, right)
        return cache[self.radius]

    def update(self, dt: float, slow_factor: float = 1.0, magnet_pos=None, magnet_active=False):
        factor = slow_factor
        
        # Magnet attraction
        if magnet_active and magnet_pos and not self.sliced:
            dx = magnet_pos[0] - self.x
            dy = magnet_pos[1] - self.y
            dist = max(1, math.sqrt(dx * dx + dy * dy))
            force = cfg.MAGNET_STRENGTH / max(1, dist / 100)
            self.vx += (dx / dist) * force * factor
            self.vy += (dy / dist) * force * factor
        
        self.vy += cfg.GRAVITY * factor
        self.x += self.vx * factor
        self.y += self.vy * factor
        self.angle += self.angular_vel * factor

        if self.sliced:
            self.half_timer += dt
            self.half_offset_x += 2.5 * factor
            if self.half_timer > 1.0:
                self.alive = False

        if self.y > cfg.SCREEN_HEIGHT + self.radius + 50 and not self.sliced:
            self.alive = False

    def draw(self, surface: pygame.Surface):
        if not self.sliced:
            # Rotate the pre-rendered sprite
            rotated = pygame.transform.rotate(self._sprite, self.angle)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(rotated, rect)
        else:
            off = int(self.half_offset_x)
            alpha = max(0, 255 - int(self.half_timer * 300))

            # Left half
            left = self._left_half.copy()
            left.set_alpha(alpha)
            left_rot = pygame.transform.rotate(left, self.angle + self.half_timer * 30)
            rect_l = left_rot.get_rect(center=(int(self.x) - off, int(self.y)))
            surface.blit(left_rot, rect_l)

            # Right half
            right = self._right_half.copy()
            right.set_alpha(alpha)
            right_rot = pygame.transform.rotate(right, self.angle - self.half_timer * 30)
            rect_r = right_rot.get_rect(center=(int(self.x) + off, int(self.y)))
            surface.blit(right_rot, rect_r)

    def check_slice(self, trail: list[tuple[int, int]]) -> bool:
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


class GiantFruit(Fruit):
    """A massive fruit that requires multiple slices to destroy."""

    def __init__(self, x=None):
        super().__init__(x)
        # Override properties for boss
        self.radius = random.randint(100, 120)
        self.points = 100
        self.max_health = 10
        self.health = self.max_health
        self.vx *= 0.6  # Slower horizontal movement
        self.vy = random.uniform(-14, -10) # Heavy/High toss
        
        self.hit_cooldown = 0.0
        self.scale_pulse = 0.0

        # Clear standard cache for this unique giant instance to avoid memory bloat with random radii
        # Actually, Fruit._get_sprite uses radius as key. Unique large radii are fine.
        # Force re-generation with current radius
        self._sprite = self._get_sprite()
        
        # Pre-calc slices for final death
        # We don't pre-calc slices for every hit, only death split
        self._left_half, self._right_half = self._get_slice_sprites()

    def update(self, dt: float, slow_factor: float = 1.0, magnet_pos=None, magnet_active=False):
        super().update(dt, slow_factor, magnet_pos, magnet_active)
        
        if self.hit_cooldown > 0:
            self.hit_cooldown -= dt

        # Pulse effect when alive
        if not self.sliced:
            self.scale_pulse += dt * 5
            
    def check_slice(self, trail: list[tuple[int, int]]) -> bool:
        if self.hit_cooldown > 0:
            return False
        return super().check_slice(trail)

    def slice(self):
        """Take damage. Only split if health <= 0."""
        self.health -= 1
        self.hit_cooldown = 0.15 # Small delay so one swipe = 1 hit usually
        
        if self.health <= 0:
            self.sliced = True
            self.vy = min(self.vy, -2)
        else:
            # Not dead yet – just took a hit
            # Push it slightly up to juggle it?
            self.vy -= 2
            self.vx += random.uniform(-1, 1)


# ── Fruit Manager ───────────────────────────────────────

class FruitManager:
    """Spawns and manages all active fruits."""

    def __init__(self):
        self.fruits: list[Fruit] = []
        self.spawn_timer = 0.0
        self.spawn_interval = cfg.INITIAL_SPAWN_INTERVAL
        self.fruits_per_spawn = cfg.INITIAL_FRUITS_PER_SPAWN

    def update(self, dt: float, slow_factor: float = 1.0, magnet_pos=None, magnet_active=False):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            self._spawn_batch()

        for f in self.fruits:
            f.update(dt, slow_factor, magnet_pos, magnet_active)
        self.fruits = [f for f in self.fruits if f.alive]

    def draw(self, surface: pygame.Surface):
        for f in self.fruits:
            f.draw(surface)
            
            # Draw health bar for Giant Fruit
            if isinstance(f, GiantFruit) and not f.sliced:
                # Simple bar above fruit
                bar_w = 100
                bar_h = 10
                bx = f.x - bar_w // 2
                by = f.y - f.radius - 20
                pct = f.health / f.max_health
                pygame.draw.rect(surface, (50, 50, 50), (bx, by, bar_w, bar_h))
                pygame.draw.rect(surface, (255, 50, 50), (bx, by, bar_w * pct, bar_h))
                pygame.draw.rect(surface, (255, 255, 255), (bx, by, bar_w, bar_h), 1)

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
        # Chance for Giant Fruit (1%)
        if random.random() < 0.01:
            self.fruits.append(GiantFruit())
            return # Skip normal batch if boss spawns

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

    def frenzy_spawn(self):
        """Spawn a large burst of fruits for Frenzy mode."""
        margin = 60
        count = cfg.FRENZY_FRUITS_PER_SPAWN
        positions = random.sample(
            range(margin, cfg.SCREEN_WIDTH - margin, 50),
            min(count, (cfg.SCREEN_WIDTH - 2 * margin) // 50),
        )
        for x in positions:
            self.fruits.append(Fruit(x))


# ── Geometry helper ─────────────────────────────────────

def _segment_circle_intersect(
    p1: tuple, p2: tuple, cx: float, cy: float, r: float
) -> bool:
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
