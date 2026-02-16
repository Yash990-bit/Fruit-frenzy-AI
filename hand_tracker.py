"""
FruitFrenzyAI – Hand Tracking via Mediapipe Tasks API + OpenCV
Detects index-finger-tip positions and computes a swipe trail.
Compatible with mediapipe >= 0.10.9 (Tasks API).
"""

import os
import urllib.request
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    RunningMode,
)
from collections import deque
import config as cfg

# Model URL (Google-hosted, ~12 MB)
_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
_MODEL_PATH = os.path.join(cfg.ASSETS_DIR, "hand_landmarker.task")


def _ensure_model():
    """Download the hand-landmarker model if it doesn't exist locally."""
    os.makedirs(cfg.ASSETS_DIR, exist_ok=True)
    if not os.path.exists(_MODEL_PATH):
        print("⏳ Downloading hand-landmarker model (~12 MB)…")
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        print("✅ Model downloaded.")


class HandTracker:
    """Wraps Mediapipe HandLandmarker (Tasks API) for real-time finger-tip detection."""

    def __init__(self):
        _ensure_model()

        # Build options for VIDEO (frame-by-frame) mode
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=_MODEL_PATH),
            running_mode=RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        self._frame_ts = 0  # monotonic timestamp in ms for VIDEO mode

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

        # Store latest result
        self._result = None

    # ── public API ──────────────────────────────────────

    def update(self):
        """Capture a frame, run hand detection. Returns the BGR frame (flipped)."""
        success, frame = self.cap.read()
        if not success:
            return None

        frame = cv2.flip(frame, 1)  # mirror
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to mediapipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        # Detect (VIDEO mode needs a monotonic timestamp in ms)
        self._frame_ts += 33  # ~30 fps step
        self._result = self.landmarker.detect_for_video(mp_image, self._frame_ts)

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
        """Draw hand landmarks on the frame (optional debug overlay)."""
        if self._result and self._result.hand_landmarks:
            h, w = frame.shape[:2]
            for hand_lm in self._result.hand_landmarks:
                for lm in hand_lm:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)

    def release(self):
        self.cap.release()
        self.landmarker.close()

    # ── internals ───────────────────────────────────────

    def _update_trails(self, frame):
        # Reset if no hands
        if not self._result or not self._result.hand_landmarks:
            for i in range(2):
                self._smooth_pos[i] = None
            return

        for idx, hand_lm in enumerate(self._result.hand_landmarks[:2]):
            # Index-finger tip = landmark 8
            tip = hand_lm[8]
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
        detected = len(self._result.hand_landmarks)
        for i in range(detected, 2):
            self._smooth_pos[i] = None
