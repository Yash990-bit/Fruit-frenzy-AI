"""
FruitFrenzyAI – Combo Tracking System
Tracks rapid successive slices for combo multipliers.
"""

import time
import config as cfg


class ComboTracker:
    """Tracks fruits sliced within a short time window for combo bonuses."""

    def __init__(self):
        self.timestamps: list[float] = []
        self.combo_count = 0
        self.multiplier = 1
        self.display_timer = 0.0   # how long to show combo popup

    def register_slice(self):
        """Call when a fruit is sliced."""
        now = time.time()
        self.timestamps.append(now)
        # Prune old timestamps outside the combo window
        self.timestamps = [
            t for t in self.timestamps if now - t <= cfg.COMBO_WINDOW
        ]
        self.combo_count = len(self.timestamps)
        self._update_multiplier()
        if self.combo_count >= 3:
            self.display_timer = 1.5  # show combo popup for 1.5s

    def update(self, dt: float):
        now = time.time()
        self.timestamps = [
            t for t in self.timestamps if now - t <= cfg.COMBO_WINDOW
        ]
        self.combo_count = len(self.timestamps)
        self._update_multiplier()
        if self.display_timer > 0:
            self.display_timer -= dt

    def get_multiplier(self) -> int:
        return self.multiplier

    def get_combo_count(self) -> int:
        return self.combo_count

    def should_show_popup(self) -> bool:
        return self.display_timer > 0 and self.combo_count >= 3

    def reset(self):
        self.timestamps.clear()
        self.combo_count = 0
        self.multiplier = 1
        self.display_timer = 0.0

    def _update_multiplier(self):
        self.multiplier = 1
        for threshold, mult in sorted(cfg.COMBO_THRESHOLDS.items()):
            if self.combo_count >= threshold:
                self.multiplier = mult
