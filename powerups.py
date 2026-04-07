"""Power-up system."""

import random
import time
from config import (
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
)

POWERUP_SPEED = 0
POWERUP_SHIELD = 1
POWERUP_LIFE = 2
POWERUP_FREEZE = 3

POWERUP_CHARS = {
    POWERUP_SPEED: (">>", (0, 255, 255)),
    POWERUP_SHIELD: ("[]", (0, 128, 255)),
    POWERUP_LIFE: ("++", (255, 0, 255)),
    POWERUP_FREEZE: ("**", (255, 255, 255)),
}

POWERUP_DURATION = 600
POWERUP_SPAWN_INTERVAL = 1200


class PowerUp:
    def __init__(self, x, y, ptype):
        self.x = x
        self.y = y
        self.ptype = ptype
        self.active = True
        self.spawn_time = time.time()

    def get_char(self):
        return POWERUP_CHARS.get(self.ptype, ("??", (255, 255, 255)))

    def is_expired(self):
        return time.time() - self.spawn_time > 30


def spawn_powerup(level):
    empty_cells = []
    for y in range(1, level.rows - 1):
        for x in range(1, level.cols - 1):
            if level.is_walkable(x, y):
                empty_cells.append((x, y))

    if not empty_cells:
        return None

    x, y = random.choice(empty_cells)
    ptype = random.choice([POWERUP_SPEED, POWERUP_SHIELD, POWERUP_LIFE, POWERUP_FREEZE])
    return PowerUp(x, y, ptype)
