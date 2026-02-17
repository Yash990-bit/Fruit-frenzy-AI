"""
FruitFrenzyAI – HUD & Menu Screens (Enhanced)
Renders score, lives, combos, power-up statuses, frenzy mode, and menu/game-over screens.
Supports single and multiplayer layouts.
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

    def draw_score(self, surface: pygame.Surface, score_p1: int, score_p2: int = 0):
        # P1 Score (Left)
        color_p1 = cfg.P1_COLOR if cfg.MULTIPLAYER else cfg.WHITE
        txt_p1 = self.font_medium.render(f"P1: {score_p1}" if cfg.MULTIPLAYER else f"Score: {score_p1}", True, color_p1)
        # Shadow
        shadow_p1 = self.font_medium.render(f"P1: {score_p1}" if cfg.MULTIPLAYER else f"Score: {score_p1}", True, cfg.BLACK)
        surface.blit(shadow_p1, (22, 17))
        surface.blit(txt_p1, (20, 15))

        # P2 Score (Right) - only if multiplayer
        if cfg.MULTIPLAYER:
            txt_p2 = self.font_medium.render(f"P2: {score_p2}", True, cfg.P2_COLOR)
            shadow_p2 = self.font_medium.render(f"P2: {score_p2}", True, cfg.BLACK)
            x_p2 = cfg.SCREEN_WIDTH - txt_p2.get_width() - 20
            surface.blit(shadow_p2, (x_p2 + 2, 17))
            surface.blit(txt_p2, (x_p2, 15))

    def draw_lives(self, surface: pygame.Surface, lives: int, shield_active: bool):
        # Center-top or right-top depending on layout
        x_start = cfg.SCREEN_WIDTH - 150 if cfg.MULTIPLAYER else cfg.SCREEN_WIDTH - 40
        y_pos = 28
        
        # Shield icon
        if shield_active:
            pygame.draw.circle(surface, cfg.SHIELD_COLOR, (x_start - (lives * 35) - 20, y_pos), 12)
            pygame.draw.circle(surface, cfg.WHITE, (x_start - (lives * 35) - 20, y_pos), 12, 2)
            txt = self.font_small.render("S", True, cfg.WHITE)
            surface.blit(txt, (x_start - (lives * 35) - 28, y_pos - 12))

        for i in range(lives):
            x = x_start - i * 35
            # Heart shape
            pygame.draw.circle(surface, cfg.RED, (x - 6, y_pos), 9)
            pygame.draw.circle(surface, cfg.RED, (x + 6, y_pos), 9)
            pygame.draw.polygon(surface, cfg.RED, [
                (x - 14, y_pos + 4), (x, y_pos + 20), (x + 14, y_pos + 4)
            ])

    def draw_status_icons(self, surface: pygame.Surface, magnet_active: bool, ice_active: bool):
        """Draw icons for active power-ups."""
        y = 70
        x = 20
        
        if magnet_active:
            # Magnet icon
            pygame.draw.circle(surface, cfg.MAGNET_COLOR, (x + 20, y), 18)
            pygame.draw.circle(surface, cfg.WHITE, (x + 20, y), 18, 2)
            txt = self.font_small.render("M", True, cfg.WHITE)
            surface.blit(txt, (x + 12, y - 12))
            x += 50

        if ice_active:
             # Ice icon
            pygame.draw.circle(surface, cfg.ICE_COLOR, (x + 20, y), 18)
            pygame.draw.circle(surface, cfg.WHITE, (x + 20, y), 18, 2)
            txt = self.font_small.render("I", True, cfg.WHITE)
            surface.blit(txt, (x + 16, y - 12))

    def draw_combo(self, surface: pygame.Surface, combo_count: int, multiplier: int, timer: float, player_idx: int = 0):
        if combo_count < 3 or timer <= 0:
            return
        alpha = min(255, int(timer * 300))
        scale = 1.0 + 0.1 * math.sin(timer * 10)

        color = cfg.YELLOW
        if cfg.MULTIPLAYER:
            color = cfg.P1_COLOR if player_idx == 0 else cfg.P2_COLOR

        text = f"COMBO x{multiplier}!"
        combo_surf = self.font_combo.render(text, True, color)
        
        # Scale
        w, h = combo_surf.get_size()
        sw, sh = int(w * scale), int(h * scale)
        combo_surf = pygame.transform.scale(combo_surf, (sw, sh))

        # Create alpha surface
        final = pygame.Surface((sw, sh), pygame.SRCALPHA)
        final.blit(combo_surf, (0, 0))
        final.set_alpha(alpha)

        # Position based on player? or just center for simplicity
        # If multiplayer, maybe offset slightly left/right? 
        # For now, keep center but color-coded.
        x = cfg.SCREEN_WIDTH // 2 - sw // 2
        y = cfg.SCREEN_HEIGHT // 2 - sh // 2 - 60
        if cfg.MULTIPLAYER:
            x += -100 if player_idx == 0 else 100
            
        surface.blit(final, (x, y))

    def draw_frenzy_bar(self, surface: pygame.Surface, frenzy_timer: float, duration: float):
        if frenzy_timer <= 0:
            return
            
        # Draw "FRENZY!" banner
        banner_height = 60
        y = cfg.SCREEN_HEIGHT - banner_height - 20
        
        # Pulsing background
        alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.01))
        bg = pygame.Surface((cfg.SCREEN_WIDTH, banner_height), pygame.SRCALPHA)
        bg.fill((255, 100, 0, alpha))
        surface.blit(bg, (0, y))
        
        # Text
        txt = self.font_large.render("🔥 FRENZY MODE! 🔥", True, cfg.YELLOW)
        surface.blit(txt, (cfg.SCREEN_WIDTH // 2 - txt.get_width() // 2, y + 5))
        
        # Progress bar
        bar_width = cfg.SCREEN_WIDTH * 0.6
        progress = frenzy_timer / duration
        pygame.draw.rect(surface, cfg.DARK_GREY, (cfg.SCREEN_WIDTH//2 - bar_width//2, y - 10, bar_width, 8))
        pygame.draw.rect(surface, cfg.ORANGE, (cfg.SCREEN_WIDTH//2 - bar_width//2, y - 10, bar_width * progress, 8))

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
        if cfg.MULTIPLAYER:
            instructions.append("🎮  2 Players: Hand 1 = P1, Hand 2 = P2")
            
        for i, line in enumerate(instructions):
            txt = self.font_small.render(line, True, cfg.WHITE)
            surface.blit(txt, (cx - txt.get_width() // 2, 380 + i * 35))

        # Press space hint
        hint = self.font_small.render("or press SPACE to start", True, cfg.GREY)
        surface.blit(hint, (cx - hint.get_width() // 2, 580))

    def draw_game_over(self, surface: pygame.Surface, score_p1: int, score_p2: int, high_scores: list[int], pulse: float):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        cx = cfg.SCREEN_WIDTH // 2

        # Game Over title
        title = self.font_title.render("GAME OVER", True, cfg.RED)
        surface.blit(title, (cx - title.get_width() // 2, 80))

        # Score
        if cfg.MULTIPLAYER:
             # Winner
            if score_p1 > score_p2:
                w_txt = "Player 1 Wins!"
                w_col = cfg.P1_COLOR
            elif score_p2 > score_p1:
                w_txt = "Player 2 Wins!"
                w_col = cfg.P2_COLOR
            else:
                w_txt = "It's a Draw!"
                w_col = cfg.YELLOW
            
            winner = self.font_large.render(w_txt, True, w_col)
            surface.blit(winner, (cx - winner.get_width() // 2, 160))
            
            s1 = self.font_medium.render(f"P1: {score_p1}", True, cfg.P1_COLOR)
            s2 = self.font_medium.render(f"P2: {score_p2}", True, cfg.P2_COLOR)
            surface.blit(s1, (cx - 150, 220))
            surface.blit(s2, (cx + 50, 220))
            
        else:
            score_txt = self.font_large.render(f"Score: {score_p1}", True, cfg.YELLOW)
            surface.blit(score_txt, (cx - score_txt.get_width() // 2, 180))

        # High scores
        hs_label = self.font_medium.render("High Scores", True, cfg.WHITE)
        surface.blit(hs_label, (cx - hs_label.get_width() // 2, 280))

        for i, hs in enumerate(high_scores[:5]):
            color = cfg.YELLOW if (hs == score_p1 or (cfg.MULTIPLAYER and hs == score_p2)) else cfg.WHITE
            txt = self.font_small.render(f"{i + 1}.  {hs}", True, color)
            surface.blit(txt, (cx - txt.get_width() // 2, 325 + i * 30))

        # Restart hint
        alpha = int(128 + 127 * math.sin(pulse * 3))
        restart = self.font_subtitle.render("Press SPACE or raise hand to play again", True, cfg.WHITE)
        restart.set_alpha(alpha)
        surface.blit(restart, (cx - restart.get_width() // 2, 500))

        esc = self.font_small.render("ESC to quit", True, cfg.GREY)
        surface.blit(esc, (cx - esc.get_width() // 2, 550))

    def draw_pause(self, surface: pygame.Surface):
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        cx = cfg.SCREEN_WIDTH // 2
        txt = self.font_title.render("PAUSED", True, cfg.WHITE)
        surface.blit(txt, (cx - txt.get_width() // 2, 230))

        hint = self.font_subtitle.render("Press ESC to resume", True, cfg.GREY)
        surface.blit(hint, (cx - hint.get_width() // 2, 330))
