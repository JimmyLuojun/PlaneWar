# /Users/junluo/Desktop/PlaneWar/enemy.py
import pygame
import random
from settings import *
from bullet import EnemyBullet # Import EnemyBullet for the Boss

class Enemy(pygame.sprite.Sprite):
    # ... (Enemy class remains the same as above) ...
    def __init__(self, enemy_img):
        super().__init__()
        self.image = enemy_img # Use the image passed from main
        self.rect = self.image.get_rect()

        # Initial position off-screen (top)
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)

        # Random vertical and horizontal speed
        self.speedy = random.randint(ENEMY_MIN_SPEED_Y, ENEMY_MAX_SPEED_Y)
        # Ensure speedx is not zero
        self.speedx = random.choice([i for i in range(ENEMY_MIN_SPEED_X, ENEMY_MAX_SPEED_X + 1) if i != 0])

    def update(self):
        """ Move the enemy down and bounce horizontally. """
        self.rect.y += self.speedy
        self.rect.x += self.speedx

        # Bounce off the sides
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.speedx = -self.speedx
            # Clamp position to prevent getting stuck off-screen
            if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
            if self.rect.left < 0: self.rect.left = 0

        # Kill if it moves off the bottom of the screen
        if self.rect.top > SCREEN_HEIGHT + 10: # Add a small buffer
            self.kill()


class EnemyBoss(pygame.sprite.Sprite):
    """ Represents the Boss enemy. """
    # --- MODIFIED: Accept sprite groups ---
    def __init__(self, boss_img, shoot_sound, all_sprites_group, enemy_bullets_group):
        super().__init__()
        self.image_orig = boss_img
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = -20

        self.entry_speedy = 1
        self.entry_y = BOSS_ENTRY_Y
        self.speedx = BOSS_SPEED_X
        self.entered = False

        self.max_health = BOSS_MAX_HEALTH
        self.health = self.max_health

        self.shoot_delay = BOSS_SHOOT_DELAY
        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_sound = shoot_sound

        # --- MODIFIED: Store group references ---
        self.all_sprites = all_sprites_group
        self.enemy_bullets = enemy_bullets_group

    def update(self):
        """ Handles Boss entry, movement, and shooting checks. """
        now = pygame.time.get_ticks()

        if not self.entered:
            if self.rect.centery < self.entry_y:
                self.rect.y += self.entry_speedy
            else:
                self.entered = True
                self.last_shot_time = now
                print("Boss entry complete. Engaging!")
        else:
            self.rect.x += self.speedx
            if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
                self.speedx = -self.speedx
                self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))

            # Shooting Logic - Check timer and call shoot
            if now - self.last_shot_time > self.shoot_delay:
                self.shoot() # Call the shoot method directly
                self.last_shot_time = now # Reset timer

        # --- MODIFIED: No return value needed ---

    def shoot(self):
        """ Creates enemy bullet(s) and adds them to groups. """
        # --- MODIFIED: No return value, adds directly to groups ---
        print("Boss shooting!")
        bullet_spawn_x = self.rect.centerx
        bullet_spawn_y = self.rect.bottom

        enemy_bullet = EnemyBullet(bullet_spawn_x, bullet_spawn_y)
        # --- MODIFIED: Add to groups passed during init ---
        self.all_sprites.add(enemy_bullet)
        self.enemy_bullets.add(enemy_bullet)

        if self.shoot_sound:
            self.shoot_sound.play()

    def draw_health_bar(self, surf):
        """ Draws the boss's health bar above it onto the provided surface. """
        if self.health > 0:
            bar_length = 100
            bar_height = 10
            fill_percent = max(0, self.health / self.max_health)
            fill_length = int(bar_length * fill_percent)
            outline_rect = pygame.Rect(self.rect.centerx - bar_length // 2,
                                       self.rect.top - bar_height - 5,
                                       bar_length, bar_height)
            fill_rect = pygame.Rect(outline_rect.left, outline_rect.top,
                                    fill_length, bar_height)
            pygame.draw.rect(surf, RED, outline_rect)
            pygame.draw.rect(surf, GREEN, fill_rect)
            pygame.draw.rect(surf, WHITE, outline_rect, 2)