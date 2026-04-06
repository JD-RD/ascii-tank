"""Map/level definitions."""

from config import (
    GRID_WIDTH,
    GRID_HEIGHT,
    TILE_EMPTY,
    TILE_BRICK,
    TILE_STEEL,
    TILE_WATER,
    TILE_TREE,
    TILE_BASE,
)


class Level:
    """Represents a game level with a tile grid."""

    def __init__(self, grid, spawn_points=None):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.spawn_points = spawn_points or []

    def get_tile(self, x, y):
        if 0 <= y < self.rows and 0 <= x < self.cols:
            return self.grid[y][x]
        return TILE_STEEL

    def set_tile(self, x, y, tile):
        if 0 <= y < self.rows and 0 <= x < self.cols:
            self.grid[y][x] = tile

    def is_walkable(self, x, y):
        tile = self.get_tile(x, y)
        return tile in (TILE_EMPTY, TILE_TREE)

    def is_shootable(self, x, y):
        tile = self.get_tile(x, y)
        return tile in (TILE_BRICK, TILE_STEEL, TILE_BASE)

    def is_destroyable(self, x, y):
        tile = self.get_tile(x, y)
        return tile in (TILE_BRICK, TILE_BASE)


def make_level_1():
    """Create the first level - classic Battle City layout."""
    cols = GRID_WIDTH
    rows = GRID_HEIGHT
    grid = [[TILE_EMPTY] * cols for _ in range(rows)]

    # Border walls (steel)
    for x in range(cols):
        grid[0][x] = TILE_STEEL
        grid[rows - 1][x] = TILE_STEEL
    for y in range(rows):
        grid[y][0] = TILE_STEEL
        grid[y][cols - 1] = TILE_STEEL

    # Internal brick walls in a pattern
    brick_layouts = [
        # Horizontal walls
        ((8, 6), 12, TILE_BRICK),
        ((28, 6), 12, TILE_BRICK),
        ((8, 14), 6, TILE_BRICK),
        ((22, 14), 6, TILE_BRICK),
        ((34, 14), 6, TILE_BRICK),
        ((14, 22), 8, TILE_BRICK),
        ((28, 22), 8, TILE_BRICK),
        ((6, 30), 10, TILE_BRICK),
        ((24, 30), 10, TILE_BRICK),
        # Vertical walls
        ((10, 8), 4, TILE_BRICK, True),
        ((38, 8), 4, TILE_BRICK, True),
        ((16, 16), 4, TILE_BRICK, True),
        ((32, 16), 4, TILE_BRICK, True),
        ((12, 24), 4, TILE_BRICK, True),
        ((36, 24), 4, TILE_BRICK, True),
    ]

    for item in brick_layouts:
        sx, sy = item[0]
        length = item[1]
        tile_type = item[2]
        vertical = item[3] if len(item) > 3 else False
        for i in range(length):
            if vertical:
                ny = sy + i
                if ny < rows - 1:
                    grid[ny][sx] = tile_type
            else:
                nx = sx + i
                if nx < cols - 1:
                    grid[sy][nx] = tile_type

    # Steel obstacles
    steel_layouts = [
        ((20, 10), 4, TILE_STEEL),
        ((26, 10), 4, TILE_STEEL),
        ((18, 18), 2, TILE_STEEL, True),
        ((30, 18), 2, TILE_STEEL, True),
    ]

    for item in steel_layouts:
        sx, sy = item[0]
        length = item[1]
        tile_type = item[2]
        vertical = item[3] if len(item) > 3 else False
        for i in range(length):
            if vertical:
                ny = sy + i
                if ny < rows - 1:
                    grid[ny][sx] = tile_type
            else:
                nx = sx + i
                if nx < cols - 1:
                    grid[sy][nx] = tile_type

    # Water patches
    water_layouts = [
        ((4, 18), 4, TILE_WATER),
        ((44, 18), 4, TILE_WATER),
        ((20, 26), 8, TILE_WATER),
    ]

    for item in water_layouts:
        sx, sy = item[0]
        length = item[1]
        tile_type = item[2]
        vertical = item[3] if len(item) > 3 else False
        for i in range(length):
            if vertical:
                ny = sy + i
                if ny < rows - 1:
                    grid[ny][sx] = tile_type
            else:
                nx = sx + i
                if nx < cols - 1:
                    grid[sy][nx] = tile_type

    # Tree patches
    tree_layouts = [
        ((14, 8), 4, TILE_TREE),
        ((32, 8), 4, TILE_TREE),
        ((10, 26), 6, TILE_TREE),
        ((34, 26), 6, TILE_TREE),
    ]

    for item in tree_layouts:
        sx, sy = item[0]
        length = item[1]
        tile_type = item[2]
        vertical = item[3] if len(item) > 3 else False
        for i in range(length):
            if vertical:
                ny = sy + i
                if ny < rows - 1:
                    grid[ny][sx] = tile_type
            else:
                nx = sx + i
                if nx < cols - 1:
                    grid[sy][nx] = tile_type

    # Base (protected by brick walls)
    base_x = cols // 2
    base_y = rows - 3
    grid[base_y][base_x] = TILE_BASE
    # Brick wall around base
    for dx in range(-2, 3):
        grid[base_y][base_x + dx] = TILE_BRICK
    grid[base_y - 1][base_x - 2] = TILE_BRICK
    grid[base_y - 1][base_x + 2] = TILE_BRICK

    # Spawn points: player at bottom center, enemies at top
    spawn_points = {
        "player": (base_x, base_y + 1),
        "enemies": [
            (4, 2),
            (cols // 2, 2),
            (cols - 5, 2),
        ],
    }

    return Level(grid, spawn_points)


LEVELS = [make_level_1]
