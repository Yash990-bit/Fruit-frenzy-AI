"""
FruitFrenzyAI – HUD & Menu Screens
Renders score, lives, combos, and menu/game-over screens.
"""

import math
import pygame
import config as cfg


class HUD:
    """Heads-up display for in-game UI."""

    def __init__(self):
        pygame.font.init()
        self.font_large = pygame.font.SysFont("Arial", 48, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 22)
        self.font_combo = pygame.font.SysFont("Arial", 56, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 28)

    # ── In-game HUD ─────────────────────────────────────

    def draw_score(self, surface: pygame.Surface, score: int):
        txt = self.font_medium.render(f"Score: {score}", True, cfg.WHITE)
        # Shadow
        shadow = self.font_medium.render(f"Score: {score}", True, cfg.BLACK)
        surface.blit(shadow, (22, 17))
        surface.blit(txt, (20, 15))

    def draw_lives(self, surface: pygame.Surface, lives: int):
        x_start = cfg.SCREEN_WIDTH - 40
        for i in range(lives):
            x = x_start - i * 35
            # Heart shape
            pygame.draw.circle(surface, cfg.RED, (x - 6, 28), 9)
            pygame.draw.circle(surface, cfg.RED, (x + 6, 28), 9)
            pygame.draw.polygon(surface, cfg.RED, [
                (x - 14, 32), (x, 48), (x + 14, 32)
            ])

    def draw_combo(self, surface: pygame.Surface, combo_count: int, multiplier: int, timer: float):
        if combo_count < 3 or timer <= 0:
            return
        alpha = min(255, int(timer * 300))
        scale = 1.0 + 0.1 * math.sin(timer * 10)

        text = f"COMBO x{multiplier}!"
        combo_surf = self.font_combo.render(text, True, cfg.YELLOW)
        # Scale
        w, h = combo_surf.get_size()
        sw, sh = int(w * scale), int(h * scale)
        combo_surf = pygame.transform.scale(combo_surf, (sw, sh))

        # Create alpha surface
        final = pygame.Surface((sw, sh), pygame.SRCALPHA)
        final.blit(combo_surf, (0, 0))
        final.set_alpha(alpha)

        x = cfg.SCREEN_WIDTH // 2 - sw // 2
        y = cfg.SCREEN_HEIGHT // 2 - sh // 2 - 60
        surface.blit(final, (x, y))

    def draw_powerup_text(self, surface: pygame.Surface, text: str, timer: float):
        if timer <= 0:
            return
        alpha = min(255, int(timer * 400))
        txt = self.font_medium.render(text, True, cfg.LIGHT_BLUE)
        txt.set_alpha(alpha)
        x = cfg.SCREEN_WIDTH // 2 - txt.get_width() // 2
        surface.blit(txt, (x, cfg.SCREEN_HEIGHT // 2 + 20))

    def draw_timer(self, surface: pygame.Surface, elapsed: float):
        mins = int(elapsed) // 60
        secs = int(elapsed) % 60
        txt = self.font_small.render(f"{mins:02d}:{secs:02d}", True, cfg.WHITE)
        shadow = self.font_small.render(f"{mins:02d}:{secs:02d}", True, cfg.BLACK)
        surface.blit(shadow, (cfg.SCREEN_WIDTH // 2 - txt.get_width() // 2 + 1, 16))
        surface.blit(txt, (cfg.SCREEN_WIDTH // 2 - txt.get_width() // 2, 15))

    # ── Menu Screens ────────────────────────────────────

    def draw_start_screen(self, surface: pygame.Surface, pulse: float):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.font_title.render("FRUIT FRENZY", True, cfg.YELLOW)
        shadow = self.font_title.render("FRUIT FRENZY", True, cfg.DARK_RED)
        cx = cfg.SCREEN_WIDTH // 2
        surface.blit(shadow, (cx - title.get_width() // 2 + 3, 123))
        surface.blit(title, (cx - title.get_width() // 2, 120))

        # AI subtitle
        sub = self.font_medium.render("AI Hand-Controlled", True, cfg.LIGHT_BLUE)
        surface.blit(sub, (cx - sub.get_width() // 2, 195))

        # Pulsing start text
        alpha = int(128 + 127 * math.sin(pulse * 3))
        start_txt = self.font_subtitle.render("✋  Raise your hand to start  ✋", True, cfg.WHITE)
        start_txt.set_alpha(alpha)
        surface.blit(start_txt, (cx - start_txt.get_width() // 2, 300))

        # Instructions
        instructions = [
            "🍉  Swipe to slice fruits",
            "💣  Avoid bombs!",
            "⚡  Collect power-ups for bonuses",
            "🔥  Chain slices for combos",
        ]
        for i, line in enumerate(instructions):
            txt = self.font_small.render(line, True, cfg.WHITE)
            surface.blit(txt, (cx - txt.get_width() // 2, 380 + i * 35))

        # Press space hint
        hint = self.font_small.render("or press SPACE to start", True, cfg.GREY)
        surface.blit(hint, (cx - hint.get_width() // 2, 540))

    def draw_game_over(self, surface: pygame.Surface, score: int, high_scores: list[int], pulse: float):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        cx = cfg.SCREEN_WIDTH // 2

        # Game Over title
        title = self.font_title.render("GAME OVER", True, cfg.RED)
        surface.blit(title, (cx - title.get_width() // 2, 80))

        # Score
        score_txt = self.font_large.render(f"Score: {score}", True, cfg.YELLOW)
        surface.blit(score_txt, (cx - score_txt.get_width() // 2, 180))

        # High scores
        hs_label = self.font_medium.render("High Scores", True, cfg.WHITE)
        surface.blit(hs_label, (cx - hs_label.get_width() // 2, 250))

        for i, hs in enumerate(high_scores[:5]):
            color = cfg.YELLOW if hs == score else cfg.WHITE
            txt = self.font_small.render(f"{i + 1}.  {hs}", True, color)
            surface.blit(txt, (cx - txt.get_width() // 2, 295 + i * 30))

        # Restart hint
        alpha = int(128 + 127 * math.sin(pulse * 3))
        restart = self.font_subtitle.render("Press SPACE or raise hand to play again", True, cfg.WHITE)
        restart.set_alpha(alpha)
        surface.blit(restart, (cx - restart.get_width() // 2, 480))

        esc = self.font_small.render("ESC to quit", True, cfg.GREY)
        surface.blit(esc, (cx - esc.get_width() // 2, 540))

    def draw_pause(self, surface: pygame.Surface):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        cx = cfg.SCREEN_WIDTH // 2
        txt = self.font_title.render("PAUSED", True, cfg.WHITE)
        surface.blit(txt, (cx - txt.get_width() // 2, 230))

        hint = self.font_subtitle.render("Press ESC to resume", True, cfg.GREY)
        surface.blit(hint, (cx - hint.get_width() // 2, 330))
