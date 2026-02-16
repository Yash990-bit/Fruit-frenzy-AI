"""
FruitFrenzyAI – Sound Manager
Generates simple WAV tones programmatically and plays SFX / music.
"""

import os
import struct
import wave
import math
import numpy as np
import pygame
import config as cfg


class SoundManager:
    """Loads (or generates) and plays sound effects."""

    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.assets_dir = cfg.ASSETS_DIR
        os.makedirs(self.assets_dir, exist_ok=True)

        self.sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._generate_sounds()
        self.music_playing = False

    # ── public API ──────────────────────────────────────

    def play(self, name: str):
        snd = self.sounds.get(name)
        if snd:
            snd.play()

    def play_slice(self):
        self.play("slice")

    def play_bomb(self):
        self.play("bomb")

    def play_powerup(self):
        self.play("powerup")

    def play_combo(self):
        self.play("combo")

    def play_gameover(self):
        self.play("gameover")

    def start_music(self):
        """Start looping background music."""
        music_path = os.path.join(self.assets_dir, "bgm.wav")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                self.music_playing = True
            except Exception:
                pass

    def stop_music(self):
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False

    # ── sound generation ────────────────────────────────

    def _generate_sounds(self):
        """Generate simple WAV tones if they don't already exist."""
        defs = {
            "slice":    {"freq": 800,  "dur": 0.1,  "type": "sine",    "vol": 0.5},
            "bomb":     {"freq": 120,  "dur": 0.4,  "type": "noise",   "vol": 0.6},
            "powerup":  {"freq": 1200, "dur": 0.25, "type": "sweep",   "vol": 0.4},
            "combo":    {"freq": 600,  "dur": 0.2,  "type": "arpeggio","vol": 0.45},
            "gameover": {"freq": 300,  "dur": 0.8,  "type": "descend", "vol": 0.5},
        }

        for name, params in defs.items():
            path = os.path.join(self.assets_dir, f"{name}.wav")
            if not os.path.exists(path):
                self._make_wav(path, **params)
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
                self.sounds[name].set_volume(params["vol"])
            except Exception:
                self.sounds[name] = None

        # Background music (longer)
        bgm_path = os.path.join(self.assets_dir, "bgm.wav")
        if not os.path.exists(bgm_path):
            self._make_bgm(bgm_path)

    def _make_wav(self, path, freq, dur, type, vol):
        rate = 44100
        n = int(rate * dur)
        samples = np.zeros(n, dtype=np.float64)

        if type == "sine":
            t = np.linspace(0, dur, n, endpoint=False)
            samples = np.sin(2 * math.pi * freq * t)
            # Quick fade in/out
            fade = min(n // 10, 200)
            samples[:fade] *= np.linspace(0, 1, fade)
            samples[-fade:] *= np.linspace(1, 0, fade)

        elif type == "noise":
            # Low-pass filtered noise for explosion
            samples = np.random.uniform(-1, 1, n)
            # Simple decay
            envelope = np.exp(-np.linspace(0, 5, n))
            samples *= envelope

        elif type == "sweep":
            t = np.linspace(0, dur, n, endpoint=False)
            sweep_freq = freq * (1 + t / dur)
            samples = np.sin(2 * math.pi * sweep_freq * t)
            samples *= np.linspace(1, 0, n)

        elif type == "arpeggio":
            t = np.linspace(0, dur, n, endpoint=False)
            chunk = n // 3
            for i, mult in enumerate([1.0, 1.25, 1.5]):
                start = i * chunk
                end = min(start + chunk, n)
                seg_t = t[start:end] - t[start]
                samples[start:end] = np.sin(2 * math.pi * freq * mult * seg_t)
            samples *= np.linspace(1, 0, n)

        elif type == "descend":
            t = np.linspace(0, dur, n, endpoint=False)
            desc_freq = freq * (1 - 0.5 * t / dur)
            samples = np.sin(2 * math.pi * desc_freq * t)
            samples *= np.linspace(1, 0, n)

        samples = (samples * vol * 32767).astype(np.int16)
        self._write_wav(path, rate, samples)

    def _make_bgm(self, path):
        """Generate a simple looping background track."""
        rate = 44100
        dur = 8.0  # 8-second loop
        n = int(rate * dur)
        t = np.linspace(0, dur, n, endpoint=False)

        # Bass line cycling through notes
        bass_freqs = [110, 130.81, 146.83, 130.81]  # A2 C3 D3 C3
        bass = np.zeros(n)
        seg = n // len(bass_freqs)
        for i, f in enumerate(bass_freqs):
            start = i * seg
            end = min(start + seg, n)
            seg_t = t[start:end]
            bass[start:end] = 0.3 * np.sin(2 * math.pi * f * seg_t)

        # Soft pad
        pad = 0.1 * np.sin(2 * math.pi * 220 * t) + 0.08 * np.sin(2 * math.pi * 330 * t)

        # Rhythm clicks
        click_interval = int(rate * 0.5)
        clicks = np.zeros(n)
        for i in range(0, n, click_interval):
            click_len = min(800, n - i)
            env = np.exp(-np.linspace(0, 10, click_len))
            clicks[i:i + click_len] += 0.15 * env * np.random.uniform(-1, 1, click_len)

        mix = bass + pad + clicks
        mix = np.clip(mix, -1, 1)
        samples = (mix * 0.4 * 32767).astype(np.int16)
        self._write_wav(path, rate, samples)

    @staticmethod
    def _write_wav(path, rate, samples):
        with wave.open(path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes(samples.tobytes())
