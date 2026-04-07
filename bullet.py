"""Bullet class."""

from config import (
    BULLET_MOVE_INTERVAL,
    DIR_UP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT,
    TILE_BRICK,
    TILE_STEEL,
    TILE_BASE,
    TILE_EMPTY,
)


class Bullet:
    def __init__(self, x, y, direction, owner):
        self.x = x
        self.y = y
        self.direction = direction
        self.owner = owner
        self.active = True
        self.move_counter = 0

    def update(self, level):
        if not self.active:
            return None

        self.move_counter += 1
        if self.move_counter < BULLET_MOVE_INTERVAL:
            return None

        self.move_counter = 0

        dx, dy = self.direction
        self.x += dx
        self.y += dy

        if level.is_shootable(self.x, self.y):
            tile = level.get_tile(self.x, self.y)
            self.active = False
            if level.is_destroyable(self.x, self.y):
                level.set_tile(self.x, self.y, TILE_EMPTY)
            return "hit_wall", (self.x, self.y), tile

        return None
