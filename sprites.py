"""ASCII sprite definitions - single line per entity to avoid cell overlap."""


class Sprite:
    def __init__(self, text, color):
        self.text = text
        self.color = color


PLAYER_SPRITES = {
    "up": Sprite("^", (0, 255, 0)),
    "down": Sprite("v", (0, 255, 0)),
    "left": Sprite("<", (0, 255, 0)),
    "right": Sprite(">", (0, 255, 0)),
}

ENEMY_SPRITES = {
    "up": Sprite("A", (255, 0, 0)),
    "down": Sprite("V", (255, 0, 0)),
    "left": Sprite("E", (255, 0, 0)),
    "right": Sprite("E", (255, 0, 0)),
}

BULLET_SPRITE = Sprite("*", (255, 255, 0))

EXPLOSION_SPRITE = Sprite("X", (255, 165, 0))

TILE_CHARS = {
    1: ("#", (139, 69, 19)),
    2: ("@", (192, 192, 192)),
    3: ("~", (0, 100, 255)),
    4: ("%", (0, 128, 0)),
    5: ("&", (255, 215, 0)),
}
