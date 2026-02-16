"""
FruitFrenzyAI – Hand Tracking via Mediapipe + OpenCV
Detects index-finger-tip positions and computes a swipe trail.
"""

import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import config as cfg


class HandTracker:
    """Wraps Mediapipe Hands for real-time finger-tip detection."""

    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Open webcam
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Trail history per hand (index 0 and 1)
        self.trails: list[deque] = [
            deque(maxlen=cfg.TRAIL_LENGTH),
            deque(maxlen=cfg.TRAIL_LENGTH),
        ]
        # Smoothed positions
        self._smooth_pos: list[tuple | None] = [None, None]

    # ── public API ──────────────────────────────────────

    def update(self):
        """Capture a frame, run hand detection. Returns the BGR frame (flipped)."""
        success, frame = self.cap.read()
        if not success:
            return None

        frame = cv2.flip(frame, 1)  # mirror
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)
        self._update_trails(frame)
        return frame

    def get_positions(self) -> list[tuple[int, int] | None]:
        """Return smoothed (game-screen x, y) for up to 2 hands."""
        return list(self._smooth_pos)

    def get_trails(self) -> list[list[tuple[int, int]]]:
        """Return the trail (list of recent positions) for each hand."""
        return [list(t) for t in self.trails]

    def get_swipe_speed(self, hand_idx: int = 0) -> float:
        """Pixel-distance between the two most recent trail points."""
        trail = self.trails[hand_idx]
        if len(trail) < 2:
            return 0.0
        p1 = trail[-1]
        p2 = trail[-2]
        return np.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def draw_landmarks(self, frame):
        """Draw hand landmarks on the frame (optional debug visual)."""
        if self.results and self.results.multi_hand_landmarks:
            for hand_lm in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_lm, self.mp_hands.HAND_CONNECTIONS
                )

    def release(self):
        self.cap.release()

    # ── internals ───────────────────────────────────────

    def _update_trails(self, frame):
        h_frame, w_frame = frame.shape[:2]

        # Reset if no hands
        if not self.results or not self.results.multi_hand_landmarks:
            for i in range(2):
                self._smooth_pos[i] = None
            return

        for idx, hand_lm in enumerate(self.results.multi_hand_landmarks[:2]):
            # Index-finger tip = landmark 8
            tip = hand_lm.landmark[8]
            raw_x = int(tip.x * cfg.SCREEN_WIDTH)
            raw_y = int(tip.y * cfg.SCREEN_HEIGHT)

            # Exponential moving average smoothing
            prev = self._smooth_pos[idx]
            if prev is None:
                sx, sy = raw_x, raw_y
            else:
                a = cfg.SMOOTHING_FACTOR
                sx = int(prev[0] * a + raw_x * (1 - a))
                sy = int(prev[1] * a + raw_y * (1 - a))

            self._smooth_pos[idx] = (sx, sy)
            self.trails[idx].append((sx, sy))

        # Clear unused hand slots
        detected = len(self.results.multi_hand_landmarks)
        for i in range(detected, 2):
            self._smooth_pos[i] = None
