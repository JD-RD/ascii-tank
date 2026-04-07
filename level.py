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


def _build_level(bricks, steels, waters, trees, base_protected=True):
    """Build a level grid from layout lists.

    Each layout entry: ((start_x, start_y), length, vertical=False)
    """
    cols = GRID_WIDTH
    rows = GRID_HEIGHT
    grid = [[TILE_EMPTY] * cols for _ in range(rows)]

    # Border walls
    for x in range(cols):
        grid[0][x] = TILE_STEEL
        grid[rows - 1][x] = TILE_STEEL
    for y in range(rows):
        grid[y][0] = TILE_STEEL
        grid[y][cols - 1] = TILE_STEEL

    for sx, sy, length, tile_type, vertical in bricks:
        for i in range(length):
            nx, ny = (sx, sy + i) if vertical else (sx + i, sy)
            if 0 < ny < rows - 1 and 0 < nx < cols - 1:
                grid[ny][nx] = tile_type

    for sx, sy, length, tile_type, vertical in steels:
        for i in range(length):
            nx, ny = (sx, sy + i) if vertical else (sx + i, sy)
            if 0 < ny < rows - 1 and 0 < nx < cols - 1:
                grid[ny][nx] = tile_type

    for sx, sy, length, tile_type, vertical in waters:
        for i in range(length):
            nx, ny = (sx, sy + i) if vertical else (sx + i, sy)
            if 0 < ny < rows - 1 and 0 < nx < cols - 1:
                grid[ny][nx] = tile_type

    for sx, sy, length, tile_type, vertical in trees:
        for i in range(length):
            nx, ny = (sx, sy + i) if vertical else (sx + i, sy)
            if 0 < ny < rows - 1 and 0 < nx < cols - 1:
                grid[ny][nx] = tile_type

    # Base
    base_x = cols // 2
    base_y = rows - 3
    grid[base_y][base_x] = TILE_BASE
    if base_protected:
        for dx in range(-2, 3):
            if dx == 0:
                continue
            grid[base_y][base_x + dx] = TILE_BRICK
        grid[base_y - 1][base_x - 2] = TILE_BRICK
        grid[base_y - 1][base_x + 2] = TILE_BRICK

    spawn_points = {
        "player": (base_x, base_y + 1),
        "enemies": [
            (4, 2),
            (cols // 2, 2),
            (cols - 5, 2),
        ],
    }

    return Level(grid, spawn_points)


def _b(sx, sy, length, vertical=False):
    """Shorthand for brick layout entry: (sx, sy, length, tile_type, vertical)."""
    return (sx, sy, length, TILE_BRICK, vertical)


def _s(sx, sy, length, vertical=False):
    """Shorthand for steel layout entry."""
    return (sx, sy, length, TILE_STEEL, vertical)


def _w(sx, sy, length, vertical=False):
    """Shorthand for water layout entry."""
    return (sx, sy, length, TILE_WATER, vertical)


def _t(sx, sy, length, vertical=False):
    """Shorthand for tree layout entry."""
    return (sx, sy, length, TILE_TREE, vertical)


def make_level_1():
    """Level 1 - Open terrain, mostly brick walls."""
    return _build_level(
        bricks=[
            _b(8, 6, 12), _b(28, 6, 12),
            _b(8, 14, 6), _b(22, 14, 6), _b(34, 14, 6),
            _b(14, 22, 8), _b(28, 22, 8),
            _b(6, 30, 10), _b(24, 30, 10),
            _b(10, 8, 4, True), _b(38, 8, 4, True),
            _b(16, 16, 4, True), _b(32, 16, 4, True),
            _b(12, 24, 4, True), _b(36, 24, 4, True),
        ],
        steels=[
            _s(20, 10, 4), _s(26, 10, 4),
            _s(18, 18, 2, True), _s(30, 18, 2, True),
        ],
        waters=[
            _w(4, 18, 4), _w(44, 18, 4),
            _w(20, 26, 8),
        ],
        trees=[
            _t(14, 8, 4), _t(32, 8, 4),
            _t(10, 26, 6), _t(34, 26, 6),
        ],
    )


def make_level_2():
    """Level 2 - Steel maze, tighter corridors."""
    return _build_level(
        bricks=[
            _b(6, 5, 8), _b(20, 5, 8), _b(34, 5, 8),
            _b(10, 12, 6), _b(30, 12, 6),
            _b(4, 20, 10), _b(36, 20, 10),
            _b(16, 28, 6), _b(28, 28, 6),
        ],
        steels=[
            _s(14, 5, 6), _s(28, 5, 6),
            _s(6, 12, 4), _s(38, 12, 4),
            _s(18, 18, 4), _s(28, 18, 4),
            _s(12, 24, 4, True), _s(34, 24, 4, True),
            _s(22, 8, 4, True), _s(26, 8, 4, True),
            _s(8, 28, 4, True), _s(40, 28, 4, True),
        ],
        waters=[
            _w(2, 15, 6), _w(42, 15, 6),
            _w(18, 32, 12),
        ],
        trees=[
            _t(20, 14, 8),
            _t(6, 32, 6), _t(38, 32, 6),
        ],
    )


def make_level_3():
    """Level 3 - Fortress, heavy steel, open kill zones."""
    return _build_level(
        bricks=[
            _b(4, 4, 6), _b(40, 4, 6),
            _b(10, 10, 4), _b(36, 10, 4),
            _b(6, 18, 8), _b(36, 18, 8),
            _b(14, 26, 4), _b(32, 26, 4),
            _b(4, 32, 6), _b(40, 32, 6),
            _b(8, 6, 4, True), _b(40, 6, 4, True),
            _b(14, 14, 4, True), _b(34, 14, 4, True),
            _b(10, 22, 4, True), _b(38, 22, 4, True),
        ],
        steels=[
            _s(16, 4, 16),
            _s(20, 10, 8),
            _s(10, 16, 4), _s(36, 16, 4),
            _s(22, 22, 4),
            _s(18, 28, 12),
            _s(12, 8, 4, True), _s(36, 8, 4, True),
            _s(16, 16, 4, True), _s(32, 16, 4, True),
            _s(8, 24, 4, True), _s(40, 24, 4, True),
            _s(20, 30, 4, True), _s(28, 30, 4, True),
        ],
        waters=[
            _w(2, 10, 4), _w(44, 10, 4),
            _w(14, 20, 4), _w(32, 20, 4),
        ],
        trees=[
            _t(22, 6, 4),
            _t(4, 26, 4), _t(44, 26, 4),
            _t(18, 34, 4), _t(28, 34, 4),
        ],
    )


LEVELS = [make_level_1, make_level_2, make_level_3]
