# /Users/junluo/Desktop/PlaneWar/main.py
import pygame
import random
import os
import sys
import time
import json  # <--- Import json

# Import game settings and classes from other modules
# Make sure settings.py defines necessary paths (IMG_DIR, SND_DIR, FONT_DIR, LEVELS_DIR)
# and constants (colors, speeds, volumes, etc.)
from settings import *
from player import Player
from bullet import Bullet, EnemyBullet
from enemy import Enemy, EnemyBoss # Ensure enemy.py is updated for speed ranges
from powerup import PowerUp

# --- Define the path to the levels directory (Using path from settings.py) ---
# Ensure LEVELS_DIR is defined correctly in settings.py
# Example: LEVELS_DIR = os.path.join(BASE_DIR, 'levels')

# --- Helper Functions (load_and_scale_image, load_sound, load_high_score, save_high_score) ---
def load_and_scale_image(path, width, height, colorkey=None):
    """Loads, scales, handles errors, and sets transparency for an image."""
    if not path or not os.path.exists(path):
        print(f"Error: Image file not found or path invalid: {path}. Using fallback.")
        fallback = pygame.Surface((width, height))
        fallback.fill((200, 50, 50)); pygame.draw.rect(fallback, WHITE, fallback.get_rect(), 1)
        return fallback
    try:
        image = pygame.image.load(path).convert_alpha()
        scaled_image = pygame.transform.scale(image, (width, height))
        if colorkey is not None:
            if colorkey == -1: colorkey = scaled_image.get_at((0, 0))
            scaled_image.set_colorkey(colorkey, pygame.RLEACCEL)
        # print(f"Successfully loaded and scaled: {os.path.basename(path)}")
        return scaled_image
    except pygame.error as e:
        print(f"Warning: Failed to load/process image {path}: {e}. Using fallback.")
        fallback = pygame.Surface((width, height))
        fallback.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
        pygame.draw.rect(fallback, WHITE, fallback.get_rect(), 1)
        return fallback

def load_sound(path, volume):
    """Loads a sound file, sets volume, and handles errors."""
    if not pygame.mixer or not pygame.mixer.get_init():
        print("Mixer not initialized, cannot load sound.")
        return None
    if not path or not os.path.exists(path):
        print(f"Warning: Sound file not found or path invalid: {path}")
        return None
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        # print(f"Successfully loaded sound: {os.path.basename(path)}")
        return sound
    except pygame.error as e:
        print(f"Warning: Failed to load sound {path}: {e}")
        return None

def load_high_score(filepath):
    """Loads the high score from a file, returning 0 on error or if file not found."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                score_str = f.read().strip()
            # Ensure string is not empty before converting
            return int(score_str) if score_str else 0
        else:
            print(f"Info: High score file not found: {filepath}. Returning 0.")
            return 0
    except (IOError, ValueError, Exception) as e:
        print(f"Warning: Error loading high score from {filepath}: {e}. Returning 0.")
        return 0

def save_high_score(filepath, score):
    """Saves the high score to a file."""
    try:
        with open(filepath, 'w') as f:
            f.write(str(score))
        print(f"Saved new high score {score} to '{os.path.basename(filepath)}'.")
    except (IOError, Exception) as e:
        print(f"Error: Failed to save high score to {filepath}: {e}")

# --- NEW FUNCTION: Load level data ---
def load_level_data(levels_directory):
    """Loads all .json files from the specified directory and sorts them by level number."""
    if not os.path.isdir(levels_directory):
        print(f"Error: Levels directory not found: {levels_directory}")
        return []
    try:
        level_files = [f for f in os.listdir(levels_directory) if f.endswith('.json')]
    except OSError as e:
        print(f"Error accessing levels directory {levels_directory}: {e}")
        return []

    loaded_levels = []
    print(f"--- Loading Levels from: {levels_directory} ---")
    if not level_files:
        print("Warning: No .json level files found in the 'levels' directory!")
        return []

    for filename in level_files:
        filepath = os.path.join(levels_directory, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                level_data = json.load(f)
            # Basic validation
            if 'level_number' in level_data and isinstance(level_data['level_number'], int):
                loaded_levels.append(level_data)
                print(f"  Successfully loaded: {filename} (Level {level_data['level_number']})")
            else:
                print(f"  Warning: Skipping file {filename} - missing 'level_number' or not an integer.")
        except json.JSONDecodeError as e:
            print(f"  Error: Failed to parse JSON file {filename}: {e}")
        except IOError as e:
            print(f"  Error: Failed to read file {filename}: {e}")
        except Exception as e:
            print(f"  Unknown error loading level {filename}: {e}")

    # Sort levels based on 'level_number' found in the JSON data
    loaded_levels.sort(key=lambda lvl: lvl.get('level_number', float('inf')))

    print(f"--- Level loading complete. Loaded {len(loaded_levels)} valid levels. ---")
    return loaded_levels

# --- Screen Display Functions ---
def show_start_screen(screen_surf, clock_obj, title_font, score_font, high_score):
    """Displays the start screen and waits for player input."""
    if not title_font or not score_font:
        print("Error: Invalid fonts passed to show_start_screen.")
        # Attempt fallback if possible, otherwise exit might be necessary
        title_font = title_font or pygame.font.SysFont(None, FONT_SIZE_TITLE)
        score_font = score_font or pygame.font.SysFont(None, FONT_SIZE_SCORE)
        if not title_font or not score_font: # Still failed
             pygame.quit(); sys.exit("Critical font error in show_start_screen.")

    screen_surf.fill(BLACK)
    try:
        # Title
        title_text = title_font.render("飞机大战", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen_surf.blit(title_text, title_rect)
        # High Score
        high_score_text = score_font.render(f"历史最高分: {high_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen_surf.blit(high_score_text, high_score_rect)
        # Prompt
        prompt_text = score_font.render("按任意键开始游戏", True, YELLOW)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4))
        screen_surf.blit(prompt_text, prompt_rect)
    except Exception as e:
        print(f"Error rendering start screen text: {e}")
        # Minimal fallback text
        try:
            fallback_font = pygame.font.SysFont(None, 50)
            err_text = fallback_font.render("Press Key To Start", True, RED)
            err_rect = err_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen_surf.blit(err_text, err_rect)
        except Exception as fallback_e:
            print(f"Error rendering fallback start screen text: {fallback_e}")

    pygame.display.flip()
    # Wait for key press
    waiting = True
    while waiting:
        clock_obj.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def show_end_screen(screen_surf, clock_obj, fonts, game_result, final_score):
    """Displays the game over/win screen and waits for player choice."""
    font_large = fonts.get('large') or pygame.font.SysFont(None, FONT_SIZE_LARGE)
    font_score = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE)

    # Semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen_surf.blit(overlay, (0, 0))

    # Main Result Text
    end_text_str = "YOU WIN!" if game_result == 'WIN' else "GAME OVER"
    end_text_color = GREEN if game_result == 'WIN' else RED
    try:
        end_text = font_large.render(end_text_str, True, end_text_color)
        text_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 1 // 3))
        screen_surf.blit(end_text, text_rect)
        # Final Score Text
        score_text_surf = font_score.render(f"Final Score: {final_score}", True, WHITE)
        score_rect = score_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen_surf.blit(score_text_surf, score_rect)
        # Prompt Text
        prompt_text_surf = font_score.render("按 [R] 重新开始 , 按 [Q] 退出", True, YELLOW)
        prompt_rect = prompt_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
        screen_surf.blit(prompt_text_surf, prompt_rect)
    except Exception as e:
        print(f"Error rendering end screen text: {e}")

    pygame.display.flip()
    # Wait for R or Q
    waiting = True
    while waiting:
        clock_obj.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    print("Player chose REPLAY.")
                    return 'REPLAY'
                if event.key == pygame.K_q:
                    print("Player chose QUIT.")
                    return 'QUIT'

def show_level_start_screen(screen_surf, clock_obj, font, level_number):
    """Displays the level transition screen."""
    if not font: font = pygame.font.SysFont(None, FONT_SIZE_LARGE) # Fallback
    screen_surf.fill(BLACK)
    try:
        level_text = font.render(f"Level {level_number}", True, WHITE)
        text_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen_surf.blit(level_text, text_rect)
    except Exception as e:
        print(f"Error rendering level start screen text: {e}")
    pygame.display.flip()
    pygame.time.wait(1500) # Pause for 1.5 seconds

# --- REFACTORED Game Logic Function (run_game) ---
def run_game(screen_surf, clock_obj, fonts, images, sounds, level_data):
    """
    Runs a single level. Spawns enemies, then boss after a delay if specified.
    Level ends when boss is defeated or player dies.
    """
    level_num = level_data.get('level_number', '?')
    print(f"\n--- Starting Level {level_num} ---")

    # --- Get Level Configuration ---
    is_boss_level = level_data.get('is_boss_level', False) # Does this level HAVE a boss?
    enemy_types = level_data.get('enemy_types', ['enemy1'])
    spawn_interval = level_data.get('spawn_interval', ENEMY_SPAWN_INTERVAL)
    max_on_screen = level_data.get('max_on_screen', MAX_ONSCREEN_ENEMIES)
    enemy_speed_y_range = level_data.get('enemy_speed_y_range')
    enemy_speed_x_range = level_data.get('enemy_speed_x_range')
    powerup_interval = level_data.get('powerup_interval', POWERUP_SPAWN_INTERVAL)
    # *** 新增：获取 Boss 延迟时间 ***
    boss_appear_delay_seconds = level_data.get('boss_appear_delay_seconds', 99999) # Default to very long delay if not set

    # --- Resources ---
    font_score = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    player_img = images.get('player')
    boss_img = images.get('boss')
    powerup_images = images.get('powerups', {})
    available_enemy_images = [img for etype in enemy_types if (img := images.get(etype))]
    # ... (获取声音资源代码不变) ...
    sounds = sounds # Pass the whole dict for simplicity below


    # --- Initialize Level State ---
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()     # Regular enemies
    bullets = pygame.sprite.Group()     # Player bullets
    enemy_bullets = pygame.sprite.Group() # Boss bullets
    powerups = pygame.sprite.Group()
    boss_group = pygame.sprite.GroupSingle() # For the single boss

    if not player_img: sys.exit("Player image not loaded, cannot start game.")
    player = Player(player_img, sounds.get('player_shoot'), sounds.get('shield_up'), sounds.get('shield_down'), sounds.get('powerup_pickup'), sounds.get('bomb'))
    all_sprites.add(player)

    game_over_local = False # Player died this level
    level_passed = False    # Player met level objective (now only boss defeat)
    boss_active = False     # Boss is currently on screen and active
    boss_spawned = False    # Has the boss instance been created?
    boss_defeated = False   # Has the boss been defeated?
    boss_instance = None

    enemy_spawn_timer = 0
    powerup_last_spawn_time = pygame.time.get_ticks()
    level_start_time = pygame.time.get_ticks()

    # --- Level Game Loop ---
    running_this_level = True
    while running_this_level:
        delta_time = clock_obj.tick(FPS) / 1000.0
        now = pygame.time.get_ticks() # Get current time once per frame

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT', player.score # Return current score on quit
            if event.type == pygame.KEYDOWN:
                if event.key == BOMB_KEY and not game_over_local:
                    killed_by_bomb = player.use_bomb(enemies)
                    player.score += killed_by_bomb # Add score for bomb kills

        # --- Game Logic Update ---
        if not game_over_local and not level_passed:
            all_sprites.update()

            # Player Shooting
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            if keys[pygame.K_SPACE] or mouse_buttons[0]:
                new_player_bullets = player.shoot()
                for bullet in new_player_bullets:
                    all_sprites.add(bullet)
                    bullets.add(bullet)


            # --- *** 修改后的 Boss 生成逻辑 *** ---
            # Check if it's a boss level, if boss hasn't been spawned yet, and if delay time is reached
            if is_boss_level and not boss_spawned: # Check if spawn attempted
                elapsed_seconds = (now - level_start_time) / 1000
                if elapsed_seconds >= boss_appear_delay_seconds:
                    print(f"Boss appear delay reached ({boss_appear_delay_seconds}s). Spawning Boss!")
                    if not boss_img:
                        print(f"Error: Boss image missing for boss level {level_num}. Failing level.")
                        game_over_local = True # Treat as failure if boss can't spawn
                    else:
                        boss_instance = EnemyBoss(boss_img, sounds.get('boss_shoot'), all_sprites, enemy_bullets)
                        all_sprites.add(boss_instance)
                        boss_group.add(boss_instance)
                        boss_active = True   # Boss is now active
                        boss_spawned = True # Mark as spawned so we don't try again
                        print("Boss Incoming!")
                        if sounds.get('boss_intro'):
                            try: sounds.get('boss_intro').play()
                            except pygame.error as e: print(f"Warning: Could not play boss intro sound: {e}")

            # --- *** 修改后的普通小兵生成逻辑 *** ---
            # Spawn regular enemies based on interval and count limit.
            # This runs independently of the boss state (before and during boss fight).
            if available_enemy_images: # Only spawn if types are defined
                enemy_spawn_timer += 1
                if enemy_spawn_timer >= spawn_interval and len(enemies) < max_on_screen:
                    enemy_spawn_timer = 0
                    chosen_img = random.choice(available_enemy_images)
                    enemy = Enemy(chosen_img, speed_y_range=enemy_speed_y_range, speed_x_range=enemy_speed_x_range)
                    all_sprites.add(enemy)
                    enemies.add(enemy)

            # --- Powerup Spawning (代码不变) ---
            if now - powerup_last_spawn_time > powerup_interval:
                powerup_last_spawn_time = now
                if powerup_images: # Check if powerup images were loaded
                    powerup = PowerUp(powerup_images)
                    all_sprites.add(powerup)
                    powerups.add(powerup)

            # --- Collisions ---
            # ... (碰撞检测代码基本不变, 确保 Boss 击败逻辑设置 level_passed) ...
            # Player Bullets vs Enemies
            enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for _ in enemy_hits:
                player.score += 1
                if sounds.get('enemy_explode'):
                    try: sounds.get('enemy_explode').play()
                    except pygame.error as e: print(f"Warning: Could not play enemy explode sound: {e}")

            # Player Bullets vs Boss
            if boss_active and boss_instance:
                bullets_hitting_boss = pygame.sprite.spritecollide(boss_instance, bullets, True)
                if bullets_hitting_boss:
                    if sounds.get('boss_hit'):
                        try: sounds.get('boss_hit').play()
                        except pygame.error as e: print(f"Warning: Could not play boss hit sound: {e}")
                    boss_instance.health -= len(bullets_hitting_boss)
                    if boss_instance.health <= 0:
                        # --- Boss Defeated ---
                        if sounds.get('boss_explode'):
                            try: sounds.get('boss_explode').play()
                            except pygame.error as e: print(f"Warning: Could not play boss explode sound: {e}")
                        if sounds.get('game_win'): # Play win sound immediately
                            try: sounds.get('game_win').play()
                            except pygame.error as e: print(f"Warning: Could not play game win sound: {e}")

                        boss_instance.kill()
                        player.score += 50
                        print("Boss Defeated!")
                        boss_defeated = True
                        boss_active = False
                        boss_instance = None
                        # *** 关卡通过条件 ***
                        level_passed = True # Level passed ONLY when boss is defeated

            # Player vs Powerups
            # ... (不变) ...
            powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit_powerup in powerup_hits:
                player.activate_powerup(hit_powerup.type)


            # --- Player Death Check ---
            # ... (不变, 但现在只会在 boss 关卡发生) ...
            if now - level_start_time > STARTUP_GRACE_PERIOD:
                if player.alive() and not player.shield_active:
                    player_enemy_hits = pygame.sprite.spritecollide(player, enemies, True) # Kill enemy on collision
                    player_boss_collision = boss_active and boss_instance and pygame.sprite.collide_rect(player, boss_instance)
                    enemy_bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True) # Kill bullet

                    if player_enemy_hits or player_boss_collision or enemy_bullet_hits:
                        reason = "Enemy" if player_enemy_hits else ("Boss Collision" if player_boss_collision else "Boss Bullet")
                        print(f"Player hit by {reason}! Level Failed!")
                        if sounds.get('player_lose'):
                            try: sounds.get('player_lose').play()
                            except pygame.error as e: print(f"Warning: Could not play player lose sound: {e}")
                        player.kill()
                        game_over_local = True


            # --- Level Completion Check (REMOVED Time Check) ---
            # Level now only completes if level_passed is set (by defeating boss)

        # --- Drawing ---
        screen_surf.fill(BLACK)
        all_sprites.draw(screen_surf)
        # ... (UI 绘制代码不变, 但时间显示部分可以移除了) ...
        try:
            score_text = font_score.render(f"Score: {player.score}", True, WHITE)
            screen_surf.blit(score_text, (10, 10))
            bomb_text = font_score.render(f"Bombs: {player.bomb_count}", True, ORANGE)
            screen_surf.blit(bomb_text, (10, 40))
            level_text_surf = font_score.render(f"Level: {level_num}", True, WHITE)
            screen_surf.blit(level_text_surf, (SCREEN_WIDTH - level_text_surf.get_width() - 10, 10))
            # Time display removed as levels are no longer timed
        except Exception as e:
            print(f"Error rendering UI: {e}")


        # Boss Health Bar
        if boss_active and boss_instance:
            boss_instance.draw_health_bar(screen_surf)

        # --- Check Level End Condition ---
        if game_over_local or level_passed:
            running_this_level = False

        pygame.display.flip()

    # --- Level Loop Ended ---
    result = 'PASSED' if level_passed else ('FAILED' if game_over_local else 'QUIT')
    print(f"--- Level {level_num} Ended. Result: {result}, Score: {player.score} ---")
    time.sleep(1.0)
    return result, player.score

# ==============================================================================
# --- Main Application Entry Point ---
# ==============================================================================
def main():
    """Initializes Pygame, loads all assets, and runs the main game loop."""
    print("--- Pygame Initialization ---")
    try:
        pygame.init()
        if pygame.mixer and not pygame.mixer.get_init():
            print("Initializing Mixer...")
            pygame.mixer.init(frequency=MIXER_FREQUENCY, size=MIXER_SIZE, channels=MIXER_CHANNELS, buffer=MIXER_BUFFER)
            print("Pygame Mixer Initialized Successfully")
        elif not pygame.mixer:
            print("Warning: Mixer module not available. No sound will be played.")
    except pygame.error as e:
        print(f"ERROR: Pygame/Mixer Initialization Failed: {e}")
        sys.exit(1) # Exit with error code

    # --- Setup Screen & Clock ---
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("飞机大战 - 多关卡版")
        clock = pygame.time.Clock()
    except pygame.error as e:
        print(f"ERROR: Failed to set up screen: {e}")
        pygame.quit()
        sys.exit(1)

    # --- Load Fonts ---
    fonts = {}
    print("\n--- Loading Fonts ---")
    try:
        # Try loading the specified font
        if UI_FONT_PATH and os.path.exists(UI_FONT_PATH):
            fonts['title'] = pygame.font.Font(UI_FONT_PATH, FONT_SIZE_TITLE)
            fonts['large'] = pygame.font.Font(UI_FONT_PATH, FONT_SIZE_LARGE)
            fonts['score'] = pygame.font.Font(UI_FONT_PATH, FONT_SIZE_SCORE)
            print(f"Successfully loaded font: {os.path.basename(UI_FONT_PATH)}")
        else:
            # If path doesn't exist or isn't set, force fallback
            raise FileNotFoundError("Custom font not found or path not set.")
    except Exception as e:
        # Fallback to system font
        print(f"Warning: Failed to load custom font ({e}). Using system default.")
        try:
            fonts['title'] = pygame.font.SysFont(None, FONT_SIZE_TITLE)
            fonts['large'] = pygame.font.SysFont(None, FONT_SIZE_LARGE)
            fonts['score'] = pygame.font.SysFont(None, FONT_SIZE_SCORE)
            print("Loaded system default font.")
        except Exception as e_sys:
            # If even system font fails, it's critical
            print(f"CRITICAL ERROR: Failed to load any fonts: {e_sys}")
            pygame.quit()
            sys.exit("Font Loading Error")

    # --- Load General Assets (Images & Sounds) ---
    images = {}
    sounds = {}
    music_paths = {} # Store paths to level-specific music files
    print("\n--- Loading General Assets ---")
    try:
        # Load Player Image
        images['player'] = load_and_scale_image(PLAYER_IMG_PATH, PLAYER_WIDTH, PLAYER_HEIGHT)
        if not images['player']: raise ValueError("Failed to load essential player image.")

        # Load Enemy Images (Add more keys as needed based on settings.py)
        enemy_image_configs = {
            'enemy1': (ENEMY1_IMG_PATH, ENEMY1_WIDTH, ENEMY1_HEIGHT),
            'enemy2': (ENEMY2_IMG_PATH, ENEMY2_WIDTH, ENEMY2_HEIGHT),
            'enemy3': (ENEMY3_IMG_PATH, ENEMY3_WIDTH, ENEMY3_HEIGHT),
            'enemy4': (ENEMY4_IMG_PATH, ENEMY4_WIDTH, ENEMY4_HEIGHT),
            'boss':   (ENEMY_BOSS_IMG_PATH, ENEMY_BOSS_WIDTH, ENEMY_BOSS_HEIGHT),
        }
        for key, (path, w, h) in enemy_image_configs.items():
             images[key] = load_and_scale_image(path, w, h)
             # Optionally check if essential images loaded: if key == 'boss' and not images[key]: raise ...

        # Load Powerup Images
        images['powerups'] = {}
        for type_key, path in POWERUP_IMAGES.items():
            img = load_and_scale_image(path, POWERUP_WIDTH, POWERUP_HEIGHT)
            if img: images['powerups'][type_key] = img
            else: print(f"Warning: Failed to load powerup image for type '{type_key}'")

        # Load Sound Effects
        sound_configs = {
            'player_shoot': (SHOOT_SOUND_PATH, PLAYER_SHOOT_VOLUME),
            'enemy_explode': (ENEMY_EXPLODE_SOUND_PATH, ENEMY_EXPLODE_VOLUME),
            'boss_explode': (BOSS_EXPLODE_SOUND_PATH, BOSS_EXPLODE_VOLUME),
            'powerup_pickup': (POWERUP_PICKUP_SOUND_PATH, POWERUP_PICKUP_VOLUME),
            'game_win': (WIN_SOUND_PATH, WIN_VOLUME),
            'player_lose': (LOSE_SOUND_PATH, LOSE_VOLUME),
            'boss_intro': (BOSS_INTRO_SOUND_PATH, BOSS_INTRO_VOLUME),
            'boss_hit': (BOSS_HIT_SOUND_PATH, BOSS_HIT_VOLUME),
            'shield_up': (SHIELD_UP_SOUND_PATH, SHIELD_UP_VOLUME),
            'shield_down': (SHIELD_DOWN_SOUND_PATH, SHIELD_DOWN_VOLUME),
            'bomb': (BOMB_SOUND_PATH, BOMB_VOLUME),
            'boss_shoot': (BOSS_SHOOT_SOUND_PATH, BOSS_SHOOT_VOLUME),
        }
        for key, (path, vol) in sound_configs.items():
            snd = load_sound(path, vol)
            if snd: sounds[key] = snd
            # No warning here as load_sound already prints warnings

        print("--- General Assets Loaded ---")

    except Exception as e:
        print(f"CRITICAL ERROR during asset loading: {e}")
        pygame.quit()
        sys.exit("Asset Loading Error")

    # --- Load Level Data ---
    LEVELS = load_level_data(LEVELS_DIR)
    if not LEVELS:
        print("CRITICAL ERROR: No level data found or loaded. Exiting.")
        pygame.quit()
        sys.exit("Level Data Error")

    # --- Prepare Music Paths (after loading LEVELS) ---
    print("\n--- Checking Level Music Paths ---")
    for level_cfg in LEVELS:
        level_num = level_cfg.get('level_number')
        music_filename = level_cfg.get('music') # e.g., "level1.ogg" or null
        if level_num is not None and music_filename:
            full_music_path = os.path.join(SND_DIR, music_filename)
            if os.path.exists(full_music_path):
                music_paths[level_num] = full_music_path
                print(f"  Found music for Level {level_num}: {music_filename}")
            else:
                print(f"  Warning: Music file '{music_filename}' for Level {level_num} not found.")

    # --- Load High Score ---
    high_score = load_high_score(HIGH_SCORE_FILE_PATH)
    print(f"\n--- High Score Loaded: {high_score} ---")

    # --- Application State Machine ---
    app_running = True
    game_state = 'START_SCREEN'
    current_level_index = 0
    final_score_this_run = 0
    current_music_path = None # Track the path of the music currently playing

    # --- Main Game Loop ---
    while app_running:

        # --- State: START_SCREEN ---
        if game_state == 'START_SCREEN':
            # Stop music before showing start screen
            if pygame.mixer and pygame.mixer.music.get_busy():
                 pygame.mixer.music.stop()
            current_music_path = None
            # Show screen and wait for key press
            show_start_screen(screen, clock, fonts.get('title'), fonts.get('score'), high_score)
            # Reset for new game attempt
            current_level_index = 0
            final_score_this_run = 0
            game_state = 'LEVEL_START' # Proceed to first level prep

        # --- State: LEVEL_START ---
        elif game_state == 'LEVEL_START':
            if current_level_index < len(LEVELS):
                level_data = LEVELS[current_level_index]
                level_num = level_data.get('level_number', current_level_index + 1)

                # --- Handle Music for the Level ---
                track_to_play = music_paths.get(level_num) # Specific track for this level?
                if not track_to_play:
                    # No specific track, try default BGM
                    default_bgm = Default_BGM_PATH # Use constant directly
                    if default_bgm and os.path.exists(default_bgm):
                         track_to_play = default_bgm
                    # else: print(f"Level {level_num}: No specific or default music.")

                # Play if track found and different from current
                if track_to_play and track_to_play != current_music_path:
                    if pygame.mixer and pygame.mixer.get_init():
                        print(f"Playing music: {os.path.basename(track_to_play)}")
                        try:
                            pygame.mixer.music.load(track_to_play)
                            pygame.mixer.music.set_volume(BGM_VOLUME)
                            pygame.mixer.music.play(loops=-1)
                            current_music_path = track_to_play
                        except pygame.error as e:
                            print(f"Error playing music '{track_to_play}': {e}")
                            current_music_path = None
                # Stop if no track for this level but music was playing
                elif not track_to_play and current_music_path:
                     if pygame.mixer and pygame.mixer.get_init():
                         pygame.mixer.music.stop()
                     current_music_path = None
                # --- End Music Handling ---

                # Show transition screen
                show_level_start_screen(screen, clock, fonts.get('large'), level_num)
                game_state = 'RUNNING_LEVEL' # Start playing the level
            else:
                # All levels completed successfully
                game_state = 'GAME_WON'

        # --- State: RUNNING_LEVEL ---
        elif game_state == 'RUNNING_LEVEL':
            level_data = LEVELS[current_level_index]
            # Run the actual level gameplay
            level_result, score_at_level_end = run_game(screen, clock, fonts, images, sounds, level_data)
            final_score_this_run = score_at_level_end # Record score achieved in this run

            # Process level outcome
            if level_result == 'PASSED':
                current_level_index += 1 # Move to next level index
                # Check if that was the last level
                game_state = 'LEVEL_START' if current_level_index < len(LEVELS) else 'GAME_WON'
            elif level_result == 'FAILED':
                game_state = 'GAME_OVER' # Player lost
            elif level_result == 'QUIT':
                app_running = False # Player quit mid-game

        # --- State: GAME_WON ---
        elif game_state == 'GAME_WON':
            print("Congratulations! You beat all levels!")
            game_result_for_screen = 'WIN' # Set result for end screen
            game_state = 'END_SCREEN'

        # --- State: GAME_OVER ---
        elif game_state == 'GAME_OVER':
            print("Game Over!")
            game_result_for_screen = 'LOSE' # Set result for end screen
            game_state = 'END_SCREEN'

        # --- State: END_SCREEN ---
        elif game_state == 'END_SCREEN':
            # Stop music before showing end screen
            if pygame.mixer and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            current_music_path = None

            # Check & Save High Score
            if final_score_this_run > high_score:
                print(f"New High Score: {final_score_this_run}")
                save_high_score(HIGH_SCORE_FILE_PATH, final_score_this_run)
                high_score = final_score_this_run # Update score shown on start screen if replaying

            # Show End Screen and get player choice
            player_choice = show_end_screen(screen, clock, fonts, game_result_for_screen, final_score_this_run)
            if player_choice == 'QUIT':
                app_running = False
            elif player_choice == 'REPLAY':
                game_state = 'START_SCREEN' # Loop back to start

    # --- Game Exit ---
    print("Exiting PlaneWar.")
    pygame.quit()
    sys.exit()

# --- Script Execution Guard ---
if __name__ == '__main__':
    main()