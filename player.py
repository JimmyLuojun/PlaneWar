# /Users/junluo/Desktop/PlaneWar/player.py
import pygame
from settings import *
from bullet import Bullet

class Player(pygame.sprite.Sprite):
    """ Represents the player's spaceship. """
    def __init__(self, player_img, shoot_sound, shield_up_sound, shield_down_sound, powerup_sound, bomb_sound):
        super().__init__()
        self.image_orig = player_img
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 20)

        # --- ADDED score initialization ---
        self.score = 0

        # Timing
        self.last_shot_time = pygame.time.get_ticks()
        self.shoot_delay = PLAYER_SHOOT_DELAY

        # Power-ups
        self.powerup_type = None
        self.powerup_end_time = 0
        self.shield_active = False
        self.shield_end_time = 0
        self.bomb_count = 1 # Start with 1 bomb (or set to 0 if preferred)

        # Shield Visuals
        self.shield_visual_radius = max(self.rect.width, self.rect.height) // 2 + 8
        self.shield_visual_color = SHIELD_VISUAL_COLOR

        # Sounds
        self.shoot_sound = shoot_sound
        self.shield_up_sound = shield_up_sound
        self.shield_down_sound = shield_down_sound
        self.powerup_sound = powerup_sound
        self.bomb_sound = bomb_sound

    def shoot(self):
        """ Creates and returns new bullet sprites based on power-up status. """
        now = pygame.time.get_ticks()
        if now - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = now
            new_bullets = []
            if self.powerup_type == 'double_shot':
                bullet_left = Bullet(self.rect.centerx - 10, self.rect.top)
                bullet_right = Bullet(self.rect.centerx + 10, self.rect.top)
                new_bullets.extend([bullet_left, bullet_right])
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                new_bullets.append(bullet)

            if self.shoot_sound:
                try:
                    self.shoot_sound.play()
                except pygame.error as e:
                    print(f"Warning: Could not play shoot sound: {e}")
            return new_bullets
        return []

    def update(self):
        """ Updates player state: position, power-up timers, visuals. """
        now = pygame.time.get_ticks()

        # Check power-up timers
        if self.powerup_type == 'double_shot' and now > self.powerup_end_time:
            print("Double shot效果结束")
            self.powerup_type = None
        if self.shield_active and now > self.shield_end_time:
            print("护盾效果结束")
            self.shield_active = False
            if self.shield_down_sound:
                 try:
                     self.shield_down_sound.play()
                 except pygame.error as e:
                     print(f"Warning: Could not play shield down sound: {e}")

        # Update position based on mouse
        mouse_pos = pygame.mouse.get_pos()
        self.rect.centerx = mouse_pos[0]
        self.rect.centery = mouse_pos[1]

        # Keep player on screen
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH: self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT: self.rect.bottom = SCREEN_HEIGHT

        # Apply shield visual if active
        self.image = self.image_orig.copy() # Reset to base image
        if self.shield_active:
            try:
                # Draw semi-transparent circle onto the image
                center = self.image.get_rect().center
                pygame.draw.circle(self.image, self.shield_visual_color, center, self.shield_visual_radius, 3)
            except TypeError: # Handle potential issue if color doesn't have alpha
                 pygame.draw.circle(self.image, CYAN, center, self.shield_visual_radius, 3) # Fallback color

    def activate_powerup(self, type):
        """ Activates the effect of a collected power-up. """
        print(f"激活道具: {type}")
        now = pygame.time.get_ticks()
        if type == 'double_shot':
            self.powerup_type = type
            self.powerup_end_time = now + POWERUP_DURATION
        elif type == 'shield':
            self.shield_active = True
            self.shield_end_time = now + SHIELD_DURATION
            if self.shield_up_sound:
                 try:
                     self.shield_up_sound.play()
                 except pygame.error as e:
                     print(f"Warning: Could not play shield up sound: {e}")
        elif type == 'bomb':
            self.bomb_count += 1
            print(f"获得炸弹! 当前数量: {self.bomb_count}")

        if self.powerup_sound:
            try:
                self.powerup_sound.play()
            except pygame.error as e:
                print(f"Warning: Could not play powerup sound: {e}")

    # --- MODIFIED use_bomb ---
    def use_bomb(self, enemies_group):
        """
        Uses one bomb if available, destroying all enemies in the provided group.
        Returns the number of enemies killed (used by run_game for scoring).
        """
        killed_count = 0
        if self.bomb_count > 0:
            print("使用炸弹！清屏！")
            self.bomb_count -= 1
            # Iterate safely if modifying group during iteration (killing sprites)
            for enemy in enemies_group.sprites():
                 enemy.kill()
                 killed_count += 1

            print(f"炸弹消灭了 {killed_count} 个普通敌机。剩余炸弹: {self.bomb_count}")
            if self.bomb_sound:
                 try:
                     self.bomb_sound.play()
                 except pygame.error as e:
                     print(f"Warning: Could not play bomb sound: {e}")
        else:
            print("没有炸弹可用!")
        # run_game will handle adding score based on killed_count
        return killed_count