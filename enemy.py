"""Enemy tank AI with improved pathfinding and awareness."""

import random
import time
from collections import deque
from config import (
    ENEMY_MOVE_INTERVAL,
    ENEMY_SHOOT_COOLDOWN,
    ENEMY_DIRECTION_CHANGE_CHANCE,
    DIR_UP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT,
    TILE_BASE,
)
from bullet import Bullet

OPPOSITE = {DIR_UP: DIR_DOWN, DIR_DOWN: DIR_UP, DIR_LEFT: DIR_RIGHT, DIR_RIGHT: DIR_LEFT}
PERPENDICULAR = {
    DIR_UP: [DIR_LEFT, DIR_RIGHT],
    DIR_DOWN: [DIR_LEFT, DIR_RIGHT],
    DIR_LEFT: [DIR_UP, DIR_DOWN],
    DIR_RIGHT: [DIR_UP, DIR_DOWN],
}


class Enemy:
    def __init__(self, x, y, enemy_id=0, target_base=False):
        self.x = x
        self.y = y
        self.id = enemy_id
        self.direction = DIR_DOWN
        self.active = True
        self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
        self.move_counter = 0
        self.move_timer = time.time()
        self.move_interval = ENEMY_MOVE_INTERVAL
        self.stuck_counter = 0
        self.last_pos = (x, y)
        self.target_base = target_base
        self.base_pos = None
        self._base_found = False

    def update(self, level, player, all_bullets):
        if not self.active:
            return None

        if self.target_base and not self._base_found:
            self._find_base(level)
            self._base_found = True

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.move_counter += 1
        if self.move_counter < ENEMY_MOVE_INTERVAL:
            return None

        self.move_counter = 0

        now = time.time()
        if now - self.move_timer > self.move_interval:
            self.move_timer = now
            if self._is_stuck():
                self._escape_stuck(level)
            else:
                self._choose_direction(level, player, all_bullets)

        dx, dy = self.direction
        new_x = self.x + dx
        new_y = self.y + dy

        if level.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            if random.random() < ENEMY_DIRECTION_CHANGE_CHANCE:
                self._choose_direction(level, player, all_bullets)
        else:
            self._choose_direction(level, player, all_bullets)

        if self.shoot_cooldown <= 0:
            if self.target_base and self.base_pos:
                if self._can_hit_pos(self.base_pos[0], self.base_pos[1]):
                    self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
                    return Bullet(self.x, self.y, self.direction, "enemy")
            elif player.active:
                if self._can_hit_player(player):
                    self.shoot_cooldown = ENEMY_SHOOT_COOLDOWN
                    return Bullet(self.x, self.y, self.direction, "enemy")

        return None

    def _find_base(self, level):
        for y in range(level.rows):
            for x in range(level.cols):
                if level.grid[y][x] == TILE_BASE:
                    self.base_pos = (x, y)
                    return
        self.base_pos = (level.cols // 2, level.rows - 3)

    def _is_stuck(self):
        if (self.x, self.y) == self.last_pos:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.last_pos = (self.x, self.y)
        return self.stuck_counter >= 3

    def _escape_stuck(self, level):
        self.stuck_counter = 0
        perp = PERPENDICULAR.get(self.direction, [DIR_LEFT, DIR_RIGHT])
        random.shuffle(perp)
        for d in perp:
            dx, dy = d
            if level.is_walkable(self.x + dx, self.y + dy):
                self.direction = d
                return
        for d in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]:
            if d != OPPOSITE.get(self.direction) and level.is_walkable(self.x + d[0], self.y + d[1]):
                self.direction = d
                return
        rev = OPPOSITE.get(self.direction)
        if rev and level.is_walkable(self.x + rev[0], self.y + rev[1]):
            self.direction = rev

    def _choose_direction(self, level, player, all_bullets):
        if self.target_base:
            if not self.base_pos:
                self._find_base(level)
            if self.base_pos and player.active:
                if random.random() < 0.7:
                    best_dir = self._bfs_toward(level, self.base_pos)
                    if best_dir:
                        self.direction = best_dir
                        return
                else:
                    best_dir = self._bfs_toward_player(level, player)
                    if best_dir:
                        self.direction = best_dir
                        return
            elif self.base_pos:
                best_dir = self._bfs_toward(level, self.base_pos)
                if best_dir:
                    self.direction = best_dir
                    return

            self._smart_move(level, player, all_bullets)
        else:
            if not player.active:
                self._random_valid_move(level)
                return

            best_dir = self._bfs_toward_player(level, player)
            if best_dir:
                self.direction = best_dir
            else:
                self._smart_move(level, player, all_bullets)

    def _bfs_toward(self, level, target, max_depth=80):
        start = (self.x, self.y)
        queue = deque([(start, None)])
        visited = set([start])
        best_dir = None
        best_dist = abs(self.x - target[0]) + abs(self.y - target[1])

        while queue and len(visited) <= max_depth:
            (cx, cy), first_dir = queue.popleft()

            if abs(cx - target[0]) <= 1 and abs(cy - target[1]) <= 1:
                return first_dir

            for dx, dy in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) not in visited and level.is_walkable(nx, ny):
                    visited.add((nx, ny))
                    next_dir = first_dir if first_dir else (dx, dy)
                    queue.append(((nx, ny), next_dir))

                    dist = abs(nx - target[0]) + abs(ny - target[1])
                    if dist < best_dist:
                        best_dist = dist
                        best_dir = next_dir

        if best_dir and level.is_walkable(self.x + best_dir[0], self.y + best_dir[1]):
            return best_dir

        best_dir = None
        best_dist = 9999
        for dx, dy in [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]:
            nx, ny = self.x + dx, self.y + dy
            if level.is_walkable(nx, ny):
                dist = abs(nx - target[0]) + abs(ny - target[1])
                if dist < best_dist:
                    best_dist = dist
                    best_dir = (dx, dy)

        return best_dir

    def _bfs_toward_player(self, level, player, max_depth=20):
        return self._bfs_toward(level, (player.x, player.y), max_depth)

    def _smart_move(self, level, player, all_bullets):
        directions = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]
        random.shuffle(directions)

        target = self.base_pos if self.target_base else (player.x, player.y)
        best = None
        best_score = -999

        for d in directions:
            dx, dy = d
            nx, ny = self.x + dx, self.y + dy
            if not level.is_walkable(nx, ny):
                continue

            score = 0
            dist = abs(nx - target[0]) + abs(ny - target[1])
            score -= dist

            if d == self.direction:
                score += 5

            if d != OPPOSITE.get(self.direction):
                score += 2

            enemy_penalty = sum(
                10 for e in all_bullets
                if hasattr(e, 'owner') and e.owner == "player" and abs(nx - e.x) <= 3 and abs(ny - e.y) <= 3
            )
            score -= enemy_penalty

            if score > best_score:
                best_score = score
                best = d

        if best:
            self.direction = best

    def _random_valid_move(self, level):
        directions = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]
        random.shuffle(directions)
        for d in directions:
            dx, dy = d
            if level.is_walkable(self.x + dx, self.y + dy):
                self.direction = d
                return

    def _can_hit_player(self, player):
        return self._can_hit_pos(player.x, player.y)

    def _can_hit_pos(self, tx, ty):
        if self.direction == DIR_UP:
            return self.x == tx and ty < self.y
        elif self.direction == DIR_DOWN:
            return self.x == tx and ty > self.y
        elif self.direction == DIR_LEFT:
            return self.y == ty and tx < self.x
        elif self.direction == DIR_RIGHT:
            return self.y == ty and tx > self.x
        return False

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
