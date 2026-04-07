import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()

from config import (
    TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_TREE, TILE_BASE,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    PLAYER_MOVE_INTERVAL, ENEMY_MOVE_INTERVAL, BULLET_MOVE_INTERVAL,
    GRID_WIDTH, GRID_HEIGHT,
)
from level import Level, make_level_1
from player import Player
from enemy import Enemy
from bullet import Bullet


@pytest.fixture
def simple_level():
    grid = [[TILE_EMPTY] * 20 for _ in range(20)]
    grid[5][5] = TILE_BRICK
    grid[5][6] = TILE_BRICK
    grid[6][5] = TILE_STEEL
    grid[7][7] = TILE_WATER
    grid[8][8] = TILE_TREE
    grid[18][10] = TILE_BASE
    return Level(grid, spawn_points={"player": (10, 19), "enemies": [(5, 2), (10, 2), (15, 2)]})


class TestLevel:
    def test_get_tile_empty(self, simple_level):
        assert simple_level.get_tile(0, 0) == TILE_EMPTY

    def test_get_tile_brick(self, simple_level):
        assert simple_level.get_tile(5, 5) == TILE_BRICK

    def test_get_tile_steel(self, simple_level):
        assert simple_level.get_tile(5, 6) == TILE_STEEL

    def test_get_tile_out_of_bounds(self, simple_level):
        assert simple_level.get_tile(99, 99) == TILE_STEEL

    def test_is_walkable_empty(self, simple_level):
        assert simple_level.is_walkable(0, 0) is True

    def test_is_walkable_tree(self, simple_level):
        assert simple_level.is_walkable(8, 8) is True

    def test_is_walkable_brick(self, simple_level):
        assert simple_level.is_walkable(5, 5) is False

    def test_is_walkable_steel(self, simple_level):
        assert simple_level.is_walkable(6, 5) is False

    def test_is_walkable_water(self, simple_level):
        assert simple_level.is_walkable(7, 7) is False

    def test_is_shootable_brick(self, simple_level):
        assert simple_level.is_shootable(5, 5) is True

    def test_is_shootable_steel(self, simple_level):
        assert simple_level.is_shootable(6, 5) is True

    def test_is_shootable_base(self, simple_level):
        assert simple_level.is_shootable(10, 18) is True

    def test_is_shootable_empty(self, simple_level):
        assert simple_level.is_shootable(0, 0) is False

    def test_is_destroyable_brick(self, simple_level):
        assert simple_level.is_destroyable(5, 5) is True

    def test_is_destroyable_base(self, simple_level):
        assert simple_level.is_destroyable(10, 18) is True

    def test_is_destroyable_steel(self, simple_level):
        assert simple_level.is_destroyable(5, 6) is False

    def test_set_tile(self, simple_level):
        simple_level.set_tile(0, 0, TILE_BRICK)
        assert simple_level.get_tile(0, 0) == TILE_BRICK

    def test_set_tile_out_of_bounds(self, simple_level):
        simple_level.set_tile(99, 99, TILE_BRICK)
        assert simple_level.get_tile(99, 99) == TILE_STEEL


class TestMakeLevel1:
    def test_level_created(self):
        level = make_level_1()
        assert isinstance(level, Level)

    def test_dimensions(self):
        level = make_level_1()
        assert level.rows == GRID_HEIGHT
        assert level.cols == GRID_WIDTH

    def test_border_walls(self):
        level = make_level_1()
        for x in range(level.cols):
            assert level.get_tile(x, 0) == TILE_STEEL
            assert level.get_tile(x, level.rows - 1) == TILE_STEEL
        for y in range(level.rows):
            assert level.get_tile(0, y) == TILE_STEEL
            assert level.get_tile(level.cols - 1, y) == TILE_STEEL

    def test_spawn_points_exist(self):
        level = make_level_1()
        assert "player" in level.spawn_points
        assert "enemies" in level.spawn_points
        assert len(level.spawn_points["enemies"]) > 0

    def test_base_exists(self):
        level = make_level_1()
        px, py = level.spawn_points["player"]
        base_x = level.cols // 2
        base_y = level.rows - 3
        assert level.get_tile(base_x, base_y) == TILE_BASE


class TestPlayer:
    def test_init(self):
        p = Player(10, 10)
        assert p.x == 10
        assert p.y == 10
        assert p.direction == DIR_UP
        assert p.active is True
        assert p.lives == 3
        assert p.shoot_cooldown == 0
        assert p.move_counter == 0

    def test_hit_reduces_lives(self, simple_level):
        p = Player(10, 10)
        p.hit()
        assert p.lives == 2
        assert p.active is True

    def test_hit_kills_at_zero(self, simple_level):
        p = Player(10, 10)
        p.lives = 1
        p.hit()
        assert p.lives == 0
        assert p.active is False

    def test_direction_names(self):
        p = Player(10, 10)
        p.direction = DIR_UP
        assert p.get_direction_name() == "up"
        p.direction = DIR_DOWN
        assert p.get_direction_name() == "down"
        p.direction = DIR_LEFT
        assert p.get_direction_name() == "left"
        p.direction = DIR_RIGHT
        assert p.get_direction_name() == "right"

    def test_movement_respects_interval(self, simple_level):
        p = Player(10, 10)
        keys = {pygame.K_UP: True, pygame.K_DOWN: False,
                pygame.K_LEFT: False, pygame.K_RIGHT: False,
                pygame.K_w: False, pygame.K_s: False,
                pygame.K_a: False, pygame.K_d: False}
        for _ in range(PLAYER_MOVE_INTERVAL - 1):
            p.update(keys, simple_level)
        assert p.y == 10
        p.update(keys, simple_level)
        assert p.y == 9

    def test_shoot_returns_bullet(self, simple_level):
        p = Player(10, 10)
        keys = {pygame.K_SPACE: True}
        bullet = p.shoot(keys)
        assert bullet is not None
        assert isinstance(bullet, Bullet)
        assert bullet.owner == "player"

    def test_shoot_respects_cooldown(self, simple_level):
        p = Player(10, 10)
        keys = {pygame.K_SPACE: True}
        p.shoot(keys)
        assert p.shoot(keys) is None

    def test_inactive_player_cannot_shoot(self, simple_level):
        p = Player(10, 10)
        p.active = False
        keys = {pygame.K_SPACE: True}
        assert p.shoot(keys) is None


class TestEnemy:
    def test_init(self):
        e = Enemy(5, 5)
        assert e.x == 5
        assert e.y == 5
        assert e.direction == DIR_DOWN
        assert e.active is True
        assert e.shoot_cooldown == 90

    def test_hit_kills(self):
        e = Enemy(5, 5)
        e.hit()
        assert e.active is False

    def test_direction_names(self):
        e = Enemy(5, 5)
        e.direction = DIR_UP
        assert e.get_direction_name() == "up"
        e.direction = DIR_DOWN
        assert e.get_direction_name() == "down"
        e.direction = DIR_LEFT
        assert e.get_direction_name() == "left"
        e.direction = DIR_RIGHT
        assert e.get_direction_name() == "right"

    def test_inactive_enemy_does_nothing(self, simple_level):
        e = Enemy(5, 5)
        e.active = False
        player = Player(10, 10)
        assert e.update(simple_level, player, []) is None

    def test_enemy_moves_on_interval(self, simple_level):
        e = Enemy(3, 3)
        e.shoot_cooldown = 999
        player = Player(10, 10)
        for _ in range(ENEMY_MOVE_INTERVAL - 1):
            e.update(simple_level, player, [])
        assert e.y == 3
        e.update(simple_level, player, [])
        assert e.y == 4


class TestBullet:
    def test_init(self):
        b = Bullet(10, 10, DIR_UP, "player")
        assert b.x == 10
        assert b.y == 10
        assert b.direction == DIR_UP
        assert b.owner == "player"
        assert b.active is True

    def test_bullet_moves_on_interval(self, simple_level):
        b = Bullet(10, 10, DIR_UP, "player")
        for _ in range(BULLET_MOVE_INTERVAL - 1):
            b.update(simple_level)
        assert b.y == 10
        b.update(simple_level)
        assert b.y == 9

    def test_bullet_hits_brick(self, simple_level):
        b = Bullet(5, 4, DIR_DOWN, "player")
        for _ in range(BULLET_MOVE_INTERVAL):
            result = b.update(simple_level)
        assert b.active is False
        assert result is not None
        assert result[0] == "hit_wall"

    def test_bullet_hits_steel(self, simple_level):
        b = Bullet(5, 5, DIR_DOWN, "player")
        for _ in range(BULLET_MOVE_INTERVAL):
            result = b.update(simple_level)
        assert b.active is False
        assert result is not None
        assert result[0] == "hit_wall"

    def test_bullet_destroys_brick(self, simple_level):
        b = Bullet(5, 4, DIR_DOWN, "player")
        for _ in range(BULLET_MOVE_INTERVAL):
            b.update(simple_level)
        assert simple_level.get_tile(5, 5) == TILE_EMPTY

    def test_bullet_does_not_destroy_steel(self, simple_level):
        b = Bullet(5, 4, DIR_DOWN, "player")
        for _ in range(BULLET_MOVE_INTERVAL):
            b.update(simple_level)
        assert simple_level.get_tile(5, 6) == TILE_STEEL

    def test_inactive_bullet_does_nothing(self, simple_level):
        b = Bullet(10, 10, DIR_UP, "player")
        b.active = False
        assert b.update(simple_level) is None
