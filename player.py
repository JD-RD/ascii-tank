"""Player tank class."""

import pygame
from config import (
    PLAYER_MOVE_INTERVAL,
    PLAYER_SHOOT_COOLDOWN,
    PLAYER_LIVES,
    GAMEPAD_DEADZONE,
    DIR_UP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT,
)
from bullet import Bullet


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = DIR_UP
        self.lives = PLAYER_LIVES
        self.shoot_cooldown = 0
        self.move_counter = 0
        self.active = True
        self.shielded = False
        self.shield_timer = 0
        self.speed_boost = 0
        self.base_move_interval = PLAYER_MOVE_INTERVAL

    def get_move_interval(self):
        if self.speed_boost > 0:
            return max(2, self.base_move_interval // 2)
        return self.base_move_interval

    def update(self, keys, level, gamepad=None):
        if not self.active:
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.speed_boost > 0:
            self.speed_boost -= 1

        if self.shielded:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shielded = False

        self.move_counter += 1
        if self.move_counter < self.get_move_interval():
            return

        self.move_counter = 0

        dx, dy = 0, 0

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
            self.direction = DIR_UP
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            self.direction = DIR_DOWN
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            self.direction = DIR_LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            self.direction = DIR_RIGHT

        if gamepad:
            if gamepad.get_numhats() > 0:
                hat = gamepad.get_hat(0)
                if hat[1] > 0:
                    dy = -1
                    self.direction = DIR_UP
                elif hat[1] < 0:
                    dy = 1
                    self.direction = DIR_DOWN
                elif hat[0] < 0:
                    dx = -1
                    self.direction = DIR_LEFT
                elif hat[0] > 0:
                    dx = 1
                    self.direction = DIR_RIGHT

            if gamepad.get_numaxes() >= 2:
                axis_x = gamepad.get_axis(0)
                axis_y = gamepad.get_axis(1)
                if abs(axis_x) > GAMEPAD_DEADZONE or abs(axis_y) > GAMEPAD_DEADZONE:
                    if abs(axis_x) > abs(axis_y):
                        if axis_x < 0:
                            dx = -1
                            self.direction = DIR_LEFT
                        else:
                            dx = 1
                            self.direction = DIR_RIGHT
                    else:
                        if axis_y < 0:
                            dy = -1
                            self.direction = DIR_UP
                        else:
                            dy = 1
                            self.direction = DIR_DOWN

        if dx != 0 or dy != 0:
            new_x = self.x + dx
            new_y = self.y + dy
            if level.is_walkable(new_x, new_y):
                self.x = new_x
                self.y = new_y

    def shoot(self, keys, gamepad=None):
        if not self.active or self.shoot_cooldown > 0:
            return None

        shoot_pressed = keys[pygame.K_SPACE]
        if gamepad:
            shoot_pressed = shoot_pressed or gamepad.get_button(0)

        if shoot_pressed:
            self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
            return Bullet(self.x, self.y, self.direction, "player")

        return None

    def hit(self):
        if self.shielded:
            self.shielded = False
            self.shield_timer = 0
            return
        self.lives -= 1
        if self.lives <= 0:
            self.active = False

    def get_direction_name(self):
        if self.direction == DIR_UP:
            return "up"
        elif self.direction == DIR_DOWN:
            return "down"
        elif self.direction == DIR_LEFT:
            return "left"
        return "right"
