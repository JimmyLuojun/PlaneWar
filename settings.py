# /Users/junluo/Desktop/PlaneWar/settings.py
import pygame
import os

# --- Base Directory ---
# Assumes the script is run from the PlaneWar directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Gets the directory where settings.py is
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
IMG_DIR = os.path.join(MEDIA_DIR, 'images')
SND_DIR = os.path.join(MEDIA_DIR, 'sounds')

# --- Screen Dimensions ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
FPS = 60 # Frames per second

# --- File Paths ---
PLAYER_IMG_PATH = os.path.join(IMG_DIR, "player.png")
ENEMY1_IMG_PATH = os.path.join(IMG_DIR, "Enemy1.png")
ENEMY_BOSS_IMG_PATH = os.path.join(IMG_DIR, "Enemy_Boss.png")
POWERUP_DOUBLESHOT_IMG_PATH = os.path.join(IMG_DIR, "powerup_doubleshot.png")
POWERUP_SHIELD_IMG_PATH = os.path.join(IMG_DIR, "powerup_shield.png")
POWERUP_BOMB_IMG_PATH = os.path.join(IMG_DIR, "powerup_bomb.png")

SHOOT_SOUND_PATH = os.path.join(SND_DIR, "shoot.wav")
ENEMY_EXPLODE_SOUND_PATH = os.path.join(SND_DIR, "explode.wav")
BOSS_EXPLODE_SOUND_PATH = os.path.join(SND_DIR, "big_explosion.wav")
POWERUP_PICKUP_SOUND_PATH = os.path.join(SND_DIR, "small_powerup.wav")
WIN_SOUND_PATH = os.path.join(SND_DIR, "win.wav")
LOSE_SOUND_PATH = os.path.join(SND_DIR, "lose.wav")
BOSS_INTRO_SOUND_PATH = os.path.join(SND_DIR, "boss_intro.mp3")
BOSS_HIT_SOUND_PATH = os.path.join(SND_DIR, "boss_hit.mp3")
BGM_PATH = os.path.join(SND_DIR, "Dynamedion GbR - 危险_SQ.flac") # Corrected path assumption
SHIELD_UP_SOUND_PATH = os.path.join(SND_DIR, "shield_up.mp3")
SHIELD_DOWN_SOUND_PATH = os.path.join(SND_DIR, "shield_down.mp3")
BOMB_SOUND_PATH = os.path.join(SND_DIR, "bomb_explode.wav")
BOSS_SHOOT_SOUND_PATH = os.path.join(SND_DIR, "boss_shoot.wav")

# --- Sprite Dimensions ---
PLAYER_WIDTH = 55
PLAYER_HEIGHT = 45
ENEMY1_WIDTH = 45
ENEMY1_HEIGHT = 35
ENEMY_BOSS_WIDTH = 120
ENEMY_BOSS_HEIGHT = 90
POWERUP_WIDTH = 40
POWERUP_HEIGHT = 40
BULLET_WIDTH = 5
BULLET_HEIGHT = 12
ENEMY_BULLET_WIDTH = 8
ENEMY_BULLET_HEIGHT = 15

# --- Game Constants ---
ENEMY_SPAWN_INTERVAL = 45 # Ticks between enemy spawns (lower is faster)
BULLET_SPEED = 10
ENEMY_MIN_SPEED_Y = 2
ENEMY_MAX_SPEED_Y = 5
ENEMY_MIN_SPEED_X = -2
ENEMY_MAX_SPEED_X = 2
BOSS_SPAWN_SCORE = 30 # Score required to spawn the boss
STARTUP_GRACE_PERIOD = 1500 # Milliseconds of invulnerability at start
PLAYER_SHOOT_DELAY = 150 # Milliseconds between player shots
POWERUP_SPAWN_INTERVAL = 8000 # Milliseconds between powerup spawns
POWERUP_DURATION = 5000 # Milliseconds double shot lasts
SHIELD_DURATION = 7000 # Milliseconds shield lasts
POWERUP_SPEED_Y = 3
BOMB_KEY = pygame.K_b # Key to press for using a bomb
ENEMY_BULLET_SPEED_Y = 6
BOSS_ENTRY_Y = 100 # Y-coordinate the boss stops descending at
BOSS_SPEED_X = 3
BOSS_SHOOT_DELAY = 1500 # Milliseconds between boss shots
BOSS_MAX_HEALTH = 50

# --- PowerUp Types ---
POWERUP_TYPES = ['double_shot', 'shield', 'bomb']
POWERUP_IMAGES = { # Associate types with paths for easier loading
    'double_shot': POWERUP_DOUBLESHOT_IMG_PATH,
    'shield': POWERUP_SHIELD_IMG_PATH,
    'bomb': POWERUP_BOMB_IMG_PATH
}
POWERUP_FALLBACK_COLORS = { # Fallback colors if images fail
    'double_shot': (0, 0, 255), # BLUE
    'shield': (0, 255, 255), # CYAN
    'bomb': (255, 165, 0) # ORANGE
}

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GREY = (128, 128, 128)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
ENEMY_BULLET_COLOR = RED
SHIELD_VISUAL_COLOR = (*CYAN, 100) # Tuple unpacking to add alpha

# --- Font Sizes ---
FONT_SIZE_LARGE = 60
FONT_SIZE_SCORE = 36
FONT_SIZE_SMALL = 24

# --- Mixer Settings ---
MIXER_FREQUENCY = 44100
MIXER_SIZE = -16
MIXER_CHANNELS = 2
MIXER_BUFFER = 512

# --- Sound Volumes ---
# (Values from 0.0 to 1.0)
PLAYER_SHOOT_VOLUME = 0.25
ENEMY_EXPLODE_VOLUME = 0.4
BOSS_EXPLODE_VOLUME = 0.6
POWERUP_PICKUP_VOLUME = 0.5
WIN_VOLUME = 0.7
LOSE_VOLUME = 0.7
BOSS_INTRO_VOLUME = 0.6
BOSS_HIT_VOLUME = 0.5
SHIELD_UP_VOLUME = 0.5
SHIELD_DOWN_VOLUME = 0.5
BOMB_VOLUME = 0.7
BOSS_SHOOT_VOLUME = 0.5
BGM_VOLUME = 0.3