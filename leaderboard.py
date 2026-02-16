"""
FruitFrenzyAI – Leaderboard
Persists top scores to a JSON file.
"""

import json
import os
import config as cfg


class Leaderboard:
    """Simple JSON-based high-score tracker."""

    def __init__(self):
        self.file_path = cfg.HIGHSCORE_FILE
        self.scores: list[int] = self._load()

    def add_score(self, score: int):
        self.scores.append(score)
        self.scores.sort(reverse=True)
        self.scores = self.scores[: cfg.MAX_HIGHSCORES]
        self._save()

    def get_scores(self) -> list[int]:
        return list(self.scores)

    def get_high_score(self) -> int:
        return self.scores[0] if self.scores else 0

    def _load(self) -> list[int]:
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
            return sorted(data, reverse=True)[: cfg.MAX_HIGHSCORES]
        except Exception:
            return []

    def _save(self):
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.scores, f)
        except Exception:
            pass
