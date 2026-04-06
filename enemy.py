"""Enemy tank AI."""

import random
import time
from config import (
    ENEMY_MOVE_INTERVAL,
    ENEMY_SHOOT_COOLDOWN,
    DIR_UP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT,
)
from bullet import Bullet


class Enemy:
    def __init__(self, x, y, enemy_id=0):
        self.x = x
        self.y = y
        self.id = enemy_id
        self.direction = DIR_DOWN
        self.active = True
        self.shoot_cooldown = 0
        self.move_counter = 0
        self.move_timer = time.time()
        self.move_interval = 2.0
        self.directions = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]

    def update(self, level, player, all_bullets):
        if not self.active:
            return None

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.move_counter += 1
        if self.move_counter < ENEMY_MOVE_INTERVAL:
            if self.shoot_cooldown <= 0 and player.active:
                self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
                return Bullet(self.x, self.y, self.direction, "enemy")
            return None

        self.move_counter = 0

        now = time.time()
        if now - self.move_timer > self.move_interval:
            self.move_timer = now
            self._choose_direction(level, player)

        dx, dy = self.direction
        new_x = self.x + dx
        new_y = self.y + dy

        if level.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            self._choose_direction(level, player)

        if self.shoot_cooldown <= 0 and player.active:
            self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
            return Bullet(self.x, self.y, self.direction, "enemy")

        return None

    def _choose_direction(self, level, player):
        if random.random() < 0.4 and player.active:
            if abs(player.x - self.x) > abs(player.y - self.y):
                self.direction = DIR_LEFT if player.x < self.x else DIR_RIGHT
            else:
                self.direction = DIR_UP if player.y < self.y else DIR_DOWN
        else:
            self.direction = random.choice(self.directions)

    def hit(self):
        self.active = False

    def get_direction_name(self):
        if self.direction == DIR_UP:
            return "up"
        elif self.direction == DIR_DOWN:
            return "down"
        elif self.direction == DIR_LEFT:
            return "left"
        return "right"
