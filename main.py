# /Users/junluo/Desktop/PlaneWar/main.py
import pygame
import random
import os
import sys # For error handling during init

# Import game settings and classes from other modules
from settings import * # Import all constants
from player import Player
from bullet import Bullet, EnemyBullet
from enemy import Enemy, EnemyBoss
from powerup import PowerUp

# --- Helper Function for Image Loading and Scaling ---
def load_and_scale_image(path, width, height, colorkey=None):
    """Loads an image, scales it, handles potential errors, and sets colorkey."""
    if not os.path.exists(path):
        print(f"错误: 文件未找到 {path}. 使用备用方块.")
        fallback_surface = pygame.Surface((width, height))
        fallback_surface.fill((200, 50, 50)) # Distinct error color
        pygame.draw.rect(fallback_surface, WHITE, fallback_surface.get_rect(), 1)
        return fallback_surface
    try:
        image_full_size = pygame.image.load(path).convert_alpha()
        scaled_image = pygame.transform.scale(image_full_size, (width, height))
        if colorkey is not None:
            if colorkey == -1: # Use top-left pixel color as colorkey
                colorkey = scaled_image.get_at((0,0))
            scaled_image.set_colorkey(colorkey, pygame.RLEACCEL)
        print(f"成功加载并缩放图片: {os.path.basename(path)}")
        return scaled_image
    except pygame.error as e:
        print(f"警告: 无法加载或处理图片 {path}: {e}. 使用备用方块.")
        fallback_surface = pygame.Surface((width, height))
        # Random fallback color to distinguish different failed loads
        fallback_surface.fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
        pygame.draw.rect(fallback_surface, WHITE, fallback_surface.get_rect(), 1)
        return fallback_surface

# --- Helper Function for Sound Loading ---
def load_sound(path, volume):
    """Loads a sound file, sets its volume, and handles errors."""
    if not pygame.mixer: # Check if mixer initialized successfully
        return None
    if not path or not os.path.exists(path):
        print(f"警告: 音效文件未找到或路径无效: {path}")
        return None
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        print(f"成功加载音效: {os.path.basename(path)} (音量: {volume:.2f})")
        return sound
    except pygame.error as e:
        print(f"警告: 无法加载音效 {path}: {e}")
        return None


# --- Initialize Pygame and Mixer ---
try:
    pygame.init()
    pygame.mixer.init(frequency=MIXER_FREQUENCY, size=MIXER_SIZE, channels=MIXER_CHANNELS, buffer=MIXER_BUFFER)
    print("Pygame 和 混音器 初始化成功")
except pygame.error as e:
    print(f"严重错误: 无法初始化Pygame或混音器: {e}")
    pygame.quit()
    sys.exit()

# --- Create Screen and Clock ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("飞机大战 - 模块化")
clock = pygame.time.Clock()

# --- Load Fonts ---
try:
    font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
    font_score = pygame.font.Font(None, FONT_SIZE_SCORE)
    # font_small = pygame.font.Font(None, FONT_SIZE_SMALL) # Uncomment if needed
except Exception as e:
    print(f"警告: 无法加载默认字体: {e}. 使用系统备用字体.")
    font_large = pygame.font.SysFont(pygame.font.get_default_font(), FONT_SIZE_LARGE)
    font_score = pygame.font.SysFont(pygame.font.get_default_font(), FONT_SIZE_SCORE)
    # font_small = pygame.font.SysFont(pygame.font.get_default_font(), FONT_SIZE_SMALL)

# --- Load Assets (Images and Sounds) ---
print("\n--- 加载资源 ---")
# Images
player_img = load_and_scale_image(PLAYER_IMG_PATH, PLAYER_WIDTH, PLAYER_HEIGHT)
enemy1_img = load_and_scale_image(ENEMY1_IMG_PATH, ENEMY1_WIDTH, ENEMY1_HEIGHT)
boss_img = load_and_scale_image(ENEMY_BOSS_IMG_PATH, ENEMY_BOSS_WIDTH, ENEMY_BOSS_HEIGHT)

# Load powerup images into a dictionary
powerup_images = {}
for type, path in POWERUP_IMAGES.items():
     powerup_images[type] = load_and_scale_image(path, POWERUP_WIDTH, POWERUP_HEIGHT)

# Sounds
player_shoot_snd = load_sound(SHOOT_SOUND_PATH, PLAYER_SHOOT_VOLUME)
enemy_explode_snd = load_sound(ENEMY_EXPLODE_SOUND_PATH, ENEMY_EXPLODE_VOLUME)
boss_explode_snd = load_sound(BOSS_EXPLODE_SOUND_PATH, BOSS_EXPLODE_VOLUME)
powerup_pickup_snd = load_sound(POWERUP_PICKUP_SOUND_PATH, POWERUP_PICKUP_VOLUME)
game_win_snd = load_sound(WIN_SOUND_PATH, WIN_VOLUME)
player_lose_snd = load_sound(LOSE_SOUND_PATH, LOSE_VOLUME)
boss_intro_snd = load_sound(BOSS_INTRO_SOUND_PATH, BOSS_INTRO_VOLUME)
boss_hit_snd = load_sound(BOSS_HIT_SOUND_PATH, BOSS_HIT_VOLUME)
shield_up_snd = load_sound(SHIELD_UP_SOUND_PATH, SHIELD_UP_VOLUME)
shield_down_snd = load_sound(SHIELD_DOWN_SOUND_PATH, SHIELD_DOWN_VOLUME)
bomb_snd = load_sound(BOMB_SOUND_PATH, BOMB_VOLUME)
boss_shoot_snd = load_sound(BOSS_SHOOT_SOUND_PATH, BOSS_SHOOT_VOLUME)
print("--- 资源加载完成 ---\n")

# --- Load Background Music ---
bgm_loaded = False
if pygame.mixer:
    if os.path.exists(BGM_PATH):
        try:
            pygame.mixer.music.load(BGM_PATH)
            pygame.mixer.music.set_volume(BGM_VOLUME)
            bgm_loaded = True
            print(f"成功加载背景音乐: {os.path.basename(BGM_PATH)}")
        except pygame.error as e:
            print(f"警告: 无法加载背景音乐 {BGM_PATH}: {e}")
    else:
        print(f"错误: 背景音乐文件未找到 {BGM_PATH}")

# --- Create Sprite Groups ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()      # Regular enemies
bullets = pygame.sprite.Group()      # Player bullets
boss_group = pygame.sprite.GroupSingle() # For the single boss
powerups = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group() # Bullets fired by enemies (boss)

# --- Create Player Instance ---
# Pass loaded assets (image, sounds) to the player constructor
player = Player(player_img=player_img,
                shoot_sound=player_shoot_snd,
                shield_up_sound=shield_up_snd,
                shield_down_sound=shield_down_snd,
                powerup_sound=powerup_pickup_snd,
                bomb_sound=bomb_snd)
all_sprites.add(player)

# --- Game Variables ---
score = 0
game_over = False
player_won = False
enemy_spawn_timer = 0 # Ticks since last enemy spawn
powerup_last_spawn_time = pygame.time.get_ticks()
start_time = pygame.time.get_ticks() # For grace period
boss_active = False
boss_instance = None # To hold the current boss sprite

# --- Start Background Music ---
if bgm_loaded and pygame.mixer:
    try:
        pygame.mixer.music.play(loops=-1)
        print("开始播放背景音乐")
    except pygame.error as e:
        print(f"警告: 无法播放背景音乐: {e}")

# --- Game Loop ---
running = True
while running:
    # --- Timing ---
    delta_time = clock.tick(FPS) / 1000.0 # Time since last frame in seconds (optional, not used here yet)

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == BOMB_KEY and not game_over:
                # Pass the group of enemies to the bomb function
                score_increase = player.use_bomb(enemies)
                score += score_increase # Add score from bombed enemies

    # --- Game Logic Update ---
    if not game_over:
        # Update all sprites (player movement, enemy movement, bullet movement, powerup movement)
        all_sprites.update()

        # Player Shooting (Mouse or Space)
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        if keys[pygame.K_SPACE] or mouse_buttons[0]:
            new_player_bullets = player.shoot() # Player.shoot now returns bullets
            for bullet in new_player_bullets:
                all_sprites.add(bullet)
                bullets.add(bullet)

        # Boss Logic (Update and Shooting)
        if boss_active and boss_instance:
            # Boss update returns any new bullets it fired
            new_boss_bullets = boss_instance.update() # Boss update is called via all_sprites.update(), redundant? No, need return value
            # Let's adjust: Boss update should happen via all_sprites.update()
            # We need a different way to get the bullets. Let's check if the boss exists and call its update separately IF we need return value.
            # OR: Modify EnemyBoss.shoot() to directly add to groups passed in __init__ (less ideal)
            # OR: Modify EnemyBoss.update() to store fired bullets in an attribute, check it here.

            # Let's stick to the original pattern where EnemyBoss.update handles its own timer and shooting.
            # The issue was how to get the bullets. Let's refine EnemyBoss.shoot to return the bullet
            # and EnemyBoss.update to call shoot and return the result.

            # Re-evaluating: all_sprites.update() already calls boss_instance.update().
            # The current enemy.py has boss.update() return new bullets. So this works:
            if boss_instance in boss_group: # Check if boss still exists before updating
               new_enemy_bullets = boss_instance.update() # Call update AGAIN to get bullets? No, that's wrong.
               # The boss's update within all_sprites.update() ALREADY handles movement and *deciding* to shoot.
               # The shoot method itself should add bullets to groups. Let's refactor enemy.py

               # --- Refactor Decision ---
               # Modify EnemyBoss.__init__ to accept sprite groups.
               # Modify EnemyBoss.shoot to add bullets directly to groups.
               # Remove bullet return value from EnemyBoss.update and EnemyBoss.shoot.
               # See updated enemy.py below this main.py block for this change.

               # Now, the boss shooting is handled entirely within its update method via all_sprites.update()

        # Enemy Spawning (Only if Boss is NOT active)
        if not boss_active:
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= ENEMY_SPAWN_INTERVAL:
                enemy = Enemy(enemy1_img) # Pass loaded image
                all_sprites.add(enemy)
                enemies.add(enemy)
                enemy_spawn_timer = 0 # Reset timer

        # Boss Spawning Trigger
        if not boss_group and not boss_active and score >= BOSS_SPAWN_SCORE:
             # --- Refactor: Pass groups to Boss ---
             boss_instance = EnemyBoss(boss_img, boss_shoot_snd, all_sprites, enemy_bullets)
             all_sprites.add(boss_instance)
             boss_group.add(boss_instance) # GroupSingle automatically manages the single boss
             boss_active = True
             enemy_spawn_timer = -9999 # Stop regular enemy spawns
             print("Boss Incoming!")
             if boss_intro_snd: boss_intro_snd.play()
             # Stop regular enemies from spawning immediately
             # Optionally, kill existing enemies:
             # for enemy in enemies:
             #     enemy.kill()

        # Powerup Spawning
        now = pygame.time.get_ticks()
        if now - powerup_last_spawn_time > POWERUP_SPAWN_INTERVAL:
            powerup_last_spawn_time = now
            powerup = PowerUp(powerup_images) # Pass loaded image dictionary
            all_sprites.add(powerup)
            powerups.add(powerup)
            print(f"生成道具: {powerup.type}")

        # --- Collision Detection ---
        # Player Bullets vs Enemies
        enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True) # Kill both
        for hit_enemy in enemy_hits:
            score += 1
            if enemy_explode_snd: enemy_explode_snd.play()
            # Add explosion effect here later if desired

        # Player Bullets vs Boss
        if boss_active and boss_instance:
            # Use spritecollide with the single boss instance
            bullets_hitting_boss = pygame.sprite.spritecollide(boss_instance, bullets, True) # Kill bullets
            if bullets_hitting_boss:
                if boss_hit_snd: boss_hit_snd.play()
                boss_instance.health -= len(bullets_hitting_boss)
                print(f"Boss health: {boss_instance.health}/{boss_instance.max_health}")
                if boss_instance.health <= 0:
                    if pygame.mixer: pygame.mixer.music.stop() # Stop BGM immediately
                    if boss_explode_snd: boss_explode_snd.play()
                    # Optional: Add visual explosion effect for boss
                    boss_instance.kill() # Remove boss sprite
                    score += 50 # Bonus score for defeating boss
                    print("Boss Defeated! YOU WIN!")
                    game_over = True
                    player_won = True
                    boss_active = False
                    boss_instance = None # Clear reference
                    # Wait briefly before win sound/fadeout
                    pygame.time.wait(500)
                    if game_win_snd: game_win_snd.play()
                    # Fade out music if it wasn't stopped (e.g., if win sound is short)
                    # if pygame.mixer: pygame.mixer.music.fadeout(1500)

        # Player vs Powerups
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True) # Kill powerup on collect
        for hit_powerup in powerup_hits:
            player.activate_powerup(hit_powerup.type) # Player handles activation logic

        # --- Player Collision Checks (Enemies, Boss, Enemy Bullets) ---
        # Only check collisions after the grace period
        now = pygame.time.get_ticks()
        if now - start_time > STARTUP_GRACE_PERIOD:
            # Check only if player is alive and not shielded
            if player.alive() and not player.shield_active:
                # Player vs Normal Enemies
                player_enemy_hits = pygame.sprite.spritecollide(player, enemies, True) # Kill enemy on collision
                if player_enemy_hits:
                    print("玩家被普通敌机击中！游戏结束！")
                    if player_lose_snd: player_lose_snd.play()
                    player.kill() # Remove player sprite

                # Player vs Boss Body (only if boss exists)
                if boss_active and boss_instance:
                     # Use collide_rect for pixel-perfect collision (or mask if needed)
                    if pygame.sprite.collide_rect(player, boss_instance): # Can change to collide_mask later
                        print("玩家撞到Boss！游戏结束！")
                        if player_lose_snd: player_lose_snd.play()
                        player.kill()

                # Player vs Enemy Bullets
                enemy_bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True) # Kill bullet on collision
                if enemy_bullet_hits:
                    print("玩家被Boss子弹击中！游戏结束！")
                    if player_lose_snd: player_lose_snd.play()
                    player.kill()

                # Check if player was killed in this frame
                if not player.alive():
                    game_over = True
                    player_won = False
                    if pygame.mixer: pygame.mixer.music.fadeout(1000) # Fade out BGM on loss


    # --- Drawing ---
    screen.fill(BLACK) # Clear screen
    all_sprites.draw(screen) # Draw all sprites

    # Draw UI Elements
    score_text_surface = font_score.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text_surface, (10, 10))
    bomb_text_surface = font_score.render(f"Bombs: {player.bomb_count}", True, ORANGE)
    screen.blit(bomb_text_surface, (10, 50)) # Position below score

    # Draw Boss Health Bar (if boss active)
    if boss_active and boss_instance:
        boss_instance.draw_health_bar(screen)

    # Draw Game Over / Win Screen
    if game_over:
        # Optional: Dim the background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA) # Surface with alpha
        overlay.fill((0, 0, 0, 180)) # Black overlay with 180/255 transparency
        screen.blit(overlay, (0, 0))

        # Display message
        if player_won:
            end_text_str = "YOU WIN!"
            end_text_color = GREEN
        else:
            end_text_str = "GAME OVER"
            end_text_color = RED
        end_text = font_large.render(end_text_str, True, end_text_color)
        text_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(end_text, text_rect)
        # Add "Press R to Restart" later if needed

    # --- Update Display ---
    pygame.display.flip() # Show the newly drawn frame

# --- Game End ---
print("游戏结束!")
pygame.quit()
sys.exit() # Ensure clean exit