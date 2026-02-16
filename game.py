"""
FruitFrenzyAI – Game Engine
Main loop, state management, collision handling, difficulty scaling.
"""

import time
import cv2
import pygame
import numpy as np
import config as cfg

from hand_tracker import HandTracker
from fruit import FruitManager
from bomb import BombManager
from powerups import PowerUpManager, PowerUpType
from particles import ParticleSystem, SliceTrail, ScreenShake
from combo import ComboTracker
from hud import HUD
from sound_manager import SoundManager
from leaderboard import Leaderboard


class GameState:
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class Game:
    """Core game engine – ties every sub-system together."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(cfg.GAME_TITLE)
        self.clock = pygame.time.Clock()

        # Sub-systems
        self.hand_tracker = HandTracker()
        self.fruit_mgr = FruitManager()
        self.bomb_mgr = BombManager()
        self.powerup_mgr = PowerUpManager()
        self.particles = ParticleSystem()
        self.slice_trail = SliceTrail()
        self.screen_shake = ScreenShake()
        self.combo = ComboTracker()
        self.hud = HUD()
        self.sound = SoundManager()
        self.leaderboard = Leaderboard()

        # Game state
        self.state = GameState.MENU
        self.score = 0
        self.lives = cfg.STARTING_LIVES
        self.elapsed = 0.0          # play time in seconds
        self.difficulty_timer = 0.0
        self.slow_factor = 1.0      # 1.0 = normal, <1 = slow-mo (ice)
        self.ice_timer = 0.0
        self.powerup_text = ""
        self.powerup_text_timer = 0.0
        self.menu_pulse = 0.0       # for pulsing menu text
        self.hand_detected_start = False

        # Spawn timer synchronisation
        self._last_spawn_check = 0.0

    # ── Main loop ───────────────────────────────────────

    def run(self):
        self.sound.start_music()
        running = True

        while running:
            dt = self.clock.tick(cfg.FPS) / 1000.0
            dt = min(dt, 0.05)  # cap to avoid spiral-of-death

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self._handle_key(event.key)

            # Webcam
            frame = self.hand_tracker.update()
            if frame is None:
                continue

            # Render webcam as background
            cam_surface = self._frame_to_surface(frame)
            self.screen.blit(cam_surface, (0, 0))

            # Dim background slightly for better contrast
            dim = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 70))
            self.screen.blit(dim, (0, 0))

            # State dispatch
            if self.state == GameState.MENU:
                self._update_menu(dt)
            elif self.state == GameState.PLAYING:
                self._update_playing(dt)
            elif self.state == GameState.PAUSED:
                self.hud.draw_pause(self.screen)
            elif self.state == GameState.GAME_OVER:
                self._update_game_over(dt)

            pygame.display.flip()

        self._cleanup()

    # ── State updates ───────────────────────────────────

    def _update_menu(self, dt: float):
        self.menu_pulse += dt
        self.hud.draw_start_screen(self.screen, self.menu_pulse)

        # Detect hand to start
        positions = self.hand_tracker.get_positions()
        if any(p is not None for p in positions):
            if not self.hand_detected_start:
                self.hand_detected_start = True
            else:
                self._start_game()

    def _update_playing(self, dt: float):
        self.elapsed += dt
        self.difficulty_timer += dt

        # Difficulty ramp
        if self.difficulty_timer >= cfg.DIFFICULTY_INCREASE_INTERVAL:
            self.difficulty_timer = 0.0
            self.fruit_mgr.increase_difficulty()
            self.bomb_mgr.increase_difficulty()

        # Ice slow-motion
        if self.ice_timer > 0:
            self.ice_timer -= dt
            self.slow_factor = 0.4
        else:
            self.slow_factor = 1.0

        # Spawn bombs / power-ups alongside fruit batches
        prev_count = len(self.fruit_mgr.fruits)
        self.fruit_mgr.update(dt, self.slow_factor)
        if len(self.fruit_mgr.fruits) > prev_count:
            # A batch was just spawned
            self.bomb_mgr.try_spawn()
            self.powerup_mgr.try_spawn()

        self.bomb_mgr.update(dt, self.slow_factor)
        self.powerup_mgr.update(dt, self.slow_factor)
        self.particles.update(dt)
        self.combo.update(dt)

        # Shake offset
        shake = self.screen_shake.update(dt)

        # Hand collision detection
        positions = self.hand_tracker.get_positions()
        trails = self.hand_tracker.get_trails()

        for hand_idx in range(2):
            trail = trails[hand_idx]
            if not trail or len(trail) < 2:
                continue
            speed = self.hand_tracker.get_swipe_speed(hand_idx)
            if speed < cfg.SLICE_MIN_SPEED:
                continue

            # Check fruits
            for fruit in self.fruit_mgr.fruits:
                if fruit.check_slice(trail):
                    fruit.slice()
                    self.combo.register_slice()
                    mult = self.combo.get_multiplier()
                    pts = fruit.points * mult
                    self.score += pts
                    self.particles.emit_slice(fruit.x, fruit.y, fruit.color)
                    self.sound.play_slice()
                    if self.combo.get_combo_count() >= 3:
                        self.sound.play_combo()

            # Check bombs
            for bomb in self.bomb_mgr.bombs:
                if bomb.check_slice(trail):
                    bomb.slice()
                    self.lives -= 1
                    self.particles.emit_bomb(bomb.x, bomb.y)
                    self.screen_shake.trigger(15, 0.4)
                    self.sound.play_bomb()
                    if self.lives <= 0:
                        self._game_over()
                        return

            # Check power-ups
            for pu in self.powerup_mgr.powerups:
                if pu.check_slice(trail):
                    pu.slice()
                    self._activate_powerup(pu)

            # Fire power-up auto-slice
            if self.slow_factor < 1.0:
                pass  # Ice active – no fire overlap needed

        # ── Draw everything ─────────────────────────────
        render_surf = pygame.Surface(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
        )

        self.fruit_mgr.draw(render_surf)
        self.bomb_mgr.draw(render_surf)
        self.powerup_mgr.draw(render_surf)
        self.particles.draw(render_surf)

        # Slice trails for each hand
        for hand_idx in range(2):
            trail = trails[hand_idx]
            if trail:
                self.slice_trail.draw(render_surf, trail)

        # Apply shake
        self.screen.blit(render_surf, shake)

        # HUD (not affected by shake)
        self.hud.draw_score(self.screen, self.score)
        self.hud.draw_lives(self.screen, self.lives)
        self.hud.draw_timer(self.screen, self.elapsed)
        self.hud.draw_combo(
            self.screen,
            self.combo.get_combo_count(),
            self.combo.get_multiplier(),
            self.combo.display_timer,
        )
        if self.powerup_text_timer > 0:
            self.powerup_text_timer -= dt
            self.hud.draw_powerup_text(self.screen, self.powerup_text, self.powerup_text_timer)

        # Ice tint overlay
        if self.ice_timer > 0:
            ice_overlay = pygame.Surface(
                (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
            )
            ice_overlay.fill((100, 180, 255, 30))
            self.screen.blit(ice_overlay, (0, 0))

    def _update_game_over(self, dt: float):
        self.menu_pulse += dt
        self.hud.draw_game_over(
            self.screen, self.score,
            self.leaderboard.get_scores(), self.menu_pulse,
        )
        # Allow restart via hand
        positions = self.hand_tracker.get_positions()
        if any(p is not None for p in positions):
            if not self.hand_detected_start:
                self.hand_detected_start = True
            # Require re-raise after brief delay
        else:
            self.hand_detected_start = False

    # ── Actions ─────────────────────────────────────────

    def _start_game(self):
        self.state = GameState.PLAYING
        self.score = 0
        self.lives = cfg.STARTING_LIVES
        self.elapsed = 0.0
        self.difficulty_timer = 0.0
        self.slow_factor = 1.0
        self.ice_timer = 0.0
        self.powerup_text = ""
        self.powerup_text_timer = 0.0
        self.hand_detected_start = False
        self.fruit_mgr = FruitManager()
        self.bomb_mgr = BombManager()
        self.powerup_mgr = PowerUpManager()
        self.particles = ParticleSystem()
        self.combo.reset()

    def _game_over(self):
        self.state = GameState.GAME_OVER
        self.leaderboard.add_score(self.score)
        self.sound.play_gameover()
        self.hand_detected_start = False
        self.menu_pulse = 0.0

    def _activate_powerup(self, pu):
        self.sound.play_powerup()
        self.particles.emit_powerup(pu.x, pu.y, pu.color)

        if pu.ptype == PowerUpType.FIRE:
            # Auto-slice all nearby fruits
            for fruit in self.fruit_mgr.fruits:
                if not fruit.sliced:
                    dx = fruit.x - pu.x
                    dy = fruit.y - pu.y
                    if (dx * dx + dy * dy) <= cfg.FIRE_RADIUS ** 2:
                        fruit.slice()
                        self.combo.register_slice()
                        self.score += fruit.points * self.combo.get_multiplier()
                        self.particles.emit_slice(fruit.x, fruit.y, cfg.FIRE_COLOR)
            self.powerup_text = "🔥 FIRE – Auto Slice!"
            self.powerup_text_timer = 2.0

        elif pu.ptype == PowerUpType.ICE:
            self.ice_timer = cfg.ICE_DURATION
            self.powerup_text = "❄️ ICE – Slow Motion!"
            self.powerup_text_timer = 2.0

        elif pu.ptype == PowerUpType.LIGHTNING:
            self.score += cfg.LIGHTNING_BONUS
            self.screen_shake.trigger(8, 0.2)
            self.powerup_text = "⚡ LIGHTNING – +50 Bonus!"
            self.powerup_text_timer = 2.0

    # ── Input ───────────────────────────────────────────

    def _handle_key(self, key) -> bool:
        """Returns False to quit, True to continue."""
        if key == pygame.K_ESCAPE:
            if self.state == GameState.PLAYING:
                self.state = GameState.PAUSED
            elif self.state == GameState.PAUSED:
                self.state = GameState.PLAYING
            elif self.state == GameState.GAME_OVER:
                return False  # quit
        elif key == pygame.K_SPACE:
            if self.state == GameState.MENU:
                self._start_game()
            elif self.state == GameState.GAME_OVER:
                self._start_game()
        return True

    # ── Helpers ─────────────────────────────────────────

    @staticmethod
    def _frame_to_surface(frame) -> pygame.Surface:
        """Convert an OpenCV BGR frame to a Pygame surface scaled to the screen."""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame_rgb.shape[:2]
        surface = pygame.surfarray.make_surface(
            np.transpose(frame_rgb, (1, 0, 2))
        )
        return pygame.transform.scale(surface, (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))

    def _cleanup(self):
        self.sound.stop_music()
        self.hand_tracker.release()
        pygame.quit()
