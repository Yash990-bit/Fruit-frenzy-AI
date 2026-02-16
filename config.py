"""
FruitFrenzyAI – Central Configuration & Constants
"""

# ── Screen ──────────────────────────────────────────────
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "FruitFrenzy AI – Fruit Ninja"

# ── Colors ──────────────────────────────────────────────
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 40, 40)
GREEN = (50, 205, 50)
DARK_GREEN = (0, 128, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 215, 0)
BLUE = (30, 144, 255)
PURPLE = (148, 0, 211)
DARK_RED = (139, 0, 0)
GREY = (128, 128, 128)
DARK_GREY = (50, 50, 50)
LIGHT_BLUE = (135, 206, 250)
PINK = (255, 105, 180)

# Fruit-specific palette
WATERMELON_GREEN = (34, 139, 34)
WATERMELON_RED = (220, 20, 60)
ORANGE_COLOR = (255, 140, 0)
APPLE_RED = (200, 30, 30)
APPLE_GREEN = (100, 200, 50)
BANANA_YELLOW = (255, 225, 53)
GRAPE_PURPLE = (128, 0, 128)
KIWI_GREEN = (118, 171, 47)
MANGO_ORANGE = (255, 179, 71)

# Bomb
BOMB_COLOR = (30, 30, 30)
BOMB_FUSE = (200, 100, 0)
BOMB_FLASH = (255, 50, 50)

# Power-up glows
FIRE_COLOR = (255, 69, 0)
ICE_COLOR = (0, 191, 255)
LIGHTNING_COLOR = (255, 255, 0)

# ── Physics ─────────────────────────────────────────────
GRAVITY = 0.35
FRUIT_RADIUS_MIN = 28
FRUIT_RADIUS_MAX = 42
FRUIT_SPEED_Y_MIN = -13
FRUIT_SPEED_Y_MAX = -9
FRUIT_SPEED_X_MIN = -3
FRUIT_SPEED_X_MAX = 3
FRUIT_ANGULAR_SPEED_MIN = -5
FRUIT_ANGULAR_SPEED_MAX = 5

# ── Spawning ────────────────────────────────────────────
INITIAL_SPAWN_INTERVAL = 1.2          # seconds between spawn batches
MIN_SPAWN_INTERVAL = 0.4
INITIAL_FRUITS_PER_SPAWN = 2
MAX_FRUITS_PER_SPAWN = 6
BOMB_PROBABILITY = 0.12               # chance per spawn slot
POWERUP_PROBABILITY = 0.06

# ── Difficulty ──────────────────────────────────────────
DIFFICULTY_INCREASE_INTERVAL = 30     # seconds
SPAWN_INTERVAL_DECREASE = 0.1
FRUITS_PER_SPAWN_INCREASE = 1
BOMB_PROBABILITY_INCREASE = 0.02

# ── Scoring ─────────────────────────────────────────────
POINTS_PER_FRUIT = 10
BOMB_PENALTY_POINTS = 0               # lives-based instead
COMBO_WINDOW = 0.5                    # seconds for combo chain
COMBO_THRESHOLDS = {3: 2, 5: 3, 8: 5} # count → multiplier
LIGHTNING_BONUS = 50

# ── Lives ───────────────────────────────────────────────
STARTING_LIVES = 3

# ── Power-up durations ──────────────────────────────────
ICE_DURATION = 3.0                    # seconds
FIRE_RADIUS = 120                     # pixels – auto-slice radius

# ── Hand tracking ───────────────────────────────────────
TRAIL_LENGTH = 20                     # points to keep for slice trail
SMOOTHING_FACTOR = 0.4                # EMA smoothing (0 = no smooth, 1 = full smooth)
SLICE_MIN_SPEED = 8                   # minimum pixel-delta to count as a slice move

# ── Particles ───────────────────────────────────────────
PARTICLE_COUNT_SLICE = 15
PARTICLE_COUNT_BOMB = 30
PARTICLE_LIFETIME = 0.6               # seconds
PARTICLE_SPEED_MIN = 2
PARTICLE_SPEED_MAX = 8

# ── Leaderboard ─────────────────────────────────────────
HIGHSCORE_FILE = "highscores.json"
MAX_HIGHSCORES = 5

# ── Asset paths ─────────────────────────────────────────
ASSETS_DIR = "assets"
