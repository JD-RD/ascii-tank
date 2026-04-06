"""Main game engine."""

import pygame
import sys
import time
import random
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CELL_SIZE,
    FONT_SIZE,
    FPS,
    BLACK,
    GREEN,
    YELLOW,
    RED,
    CYAN,
    WHITE,
    DARK_GRAY,
    GAMEPAD_DEADZONE,
    GAMEPAD_HAT_INDEX,
    GAMEPAD_BTN_A,
    GAMEPAD_BTN_B,
    GAMEPAD_BTN_START,
    GAMEPAD_BTN_SELECT,
    ENEMY_COUNT,
)
from sprites import (
    PLAYER_SPRITES,
    ENEMY_SPRITES,
    BULLET_SPRITE,
    EXPLOSION_SPRITE,
    TILE_CHARS,
)
from player import Player
from enemy import Enemy
from bullet import Bullet
from level import LEVELS


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ASCII TANK")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(pygame.font.get_default_font(), FONT_SIZE)
        self.font_small = pygame.font.Font(pygame.font.get_default_font(), FONT_SIZE - 2)
        self.gamepad = self._init_gamepad()
        self.state = "menu"
        self.level = None
        self.player = None
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self.score = 0
        self.level_num = 0

    def _init_gamepad(self):
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            gp = pygame.joystick.Joystick(0)
            gp.init()
            print(f"Gamepad detected: {gp.get_name()}")
            return gp
        print("No gamepad detected. Keyboard only.")
        return None

    def run(self):
        while True:
            if self.state == "menu":
                self._run_menu()
            elif self.state == "playing":
                self._run_game()
            elif self.state == "game_over":
                self._run_game_over()
            elif self.state == "level_complete":
                self._run_level_complete()

    def _run_menu(self):
        while self.state == "menu":
            self.screen.fill(BLACK)
            self._draw_menu()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._start_level(0)
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.gamepad:
                        if event.button == GAMEPAD_BTN_A or event.button == GAMEPAD_BTN_START:
                            self._start_level(0)

            self.clock.tick(FPS)

    def _draw_menu(self):
        title = self.font.render("ASCII TANK", True, GREEN)
        subtitle = self.font_small.render("A Battle City Tribute", True, DARK_GRAY)
        start = self.font.render("Press ENTER or A to Start", True, YELLOW)
        controls = self.font_small.render("WASD/Arrows: Move | SPACE/A: Shoot", True, CYAN)
        controls2 = self.font_small.render("SN30 Pro: D-Pad: Move | A: Shoot", True, CYAN)

        tw, th = title.get_size()
        self.screen.blit(title, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(subtitle, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 4 + 40))
        self.screen.blit(start, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(controls, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(controls2, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2 + 80))

    def _start_level(self, num):
        self.level_num = num
        level_factory = LEVELS[num % len(LEVELS)]
        self.level = level_factory()
        px, py = self.level.spawn_points["player"]
        self.player = Player(px, py)
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self._spawn_enemies()
        self.state = "playing"

    def _spawn_enemies(self):
        spawn_points = self.level.spawn_points.get("enemies", [])
        for i in range(ENEMY_COUNT):
            sx, sy = spawn_points[i % len(spawn_points)]
            self.enemies.append(Enemy(sx, sy, i))

    def _run_game(self):
        while self.state == "playing":
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "menu"

            if self.player and self.player.active:
                self.player.update(keys, self.level, self.gamepad)
                new_bullet = self.player.shoot(keys, self.gamepad)
                if new_bullet:
                    self.bullets.append(new_bullet)

            for enemy in self.enemies:
                if enemy.active:
                    new_bullet = enemy.update(self.level, self.player, self.bullets)
                    if new_bullet:
                        self.bullets.append(new_bullet)

            self._update_bullets()
            self._check_collisions()
            self._update_explosions()

            if self.player and not self.player.active:
                self.state = "game_over"

            if all(not e.active for e in self.enemies):
                self.state = "level_complete"

            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    def _update_bullets(self):
        for bullet in self.bullets:
            if bullet.active:
                result = bullet.update(self.level)
                if result and result[0] == "hit_wall":
                    self.explosions.append({
                        "x": result[1][0],
                        "y": result[1][1],
                        "timer": 15,
                    })

        self.bullets = [b for b in self.bullets if b.active]

    def _check_collisions(self):
        for bullet in self.bullets:
            if not bullet.active:
                continue

            if bullet.owner == "player":
                for enemy in self.enemies:
                    if enemy.active and bullet.x == enemy.x and bullet.y == enemy.y:
                        bullet.active = False
                        enemy.hit()
                        self.score += 100
                        self.explosions.append({
                            "x": enemy.x,
                            "y": enemy.y,
                            "timer": 20,
                        })
                        break
            elif bullet.owner == "enemy":
                if self.player and self.player.active and bullet.x == self.player.x and bullet.y == self.player.y:
                    bullet.active = False
                    self.player.hit()
                    self.explosions.append({
                        "x": self.player.x,
                        "y": self.player.y,
                        "timer": 20,
                    })

    def _update_explosions(self):
        for exp in self.explosions:
            exp["timer"] -= 1
        self.explosions = [e for e in self.explosions if e["timer"] > 0]

    def _draw(self):
        self.screen.fill(BLACK)

        if self.level:
            self._draw_level()

        if self.player and self.player.active:
            self._draw_player()

        for enemy in self.enemies:
            if enemy.active:
                self._draw_enemy(enemy)

        for bullet in self.bullets:
            if bullet.active:
                self._draw_bullet(bullet)

        for exp in self.explosions:
            self._draw_explosion(exp)

        self._draw_hud()

    def _draw_level(self):
        for y in range(self.level.rows):
            for x in range(self.level.cols):
                tile = self.level.grid[y][x]
                if tile != 0:
                    if tile == 4:
                        continue
                    info = TILE_CHARS.get(tile)
                    if info:
                        char, color = info
                        self._draw_char(char, color, x * CELL_SIZE, y * CELL_SIZE)

        for y in range(self.level.rows):
            for x in range(self.level.cols):
                if self.level.grid[y][x] == 4:
                    char, color = TILE_CHARS[4]
                    self._draw_char(char, color, x * CELL_SIZE, y * CELL_SIZE)

    def _draw_player(self):
        sprite = PLAYER_SPRITES[self.player.get_direction_name()]
        self._draw_char(sprite.text, sprite.color, self.player.x * CELL_SIZE, self.player.y * CELL_SIZE)

    def _draw_enemy(self, enemy):
        sprite = ENEMY_SPRITES[enemy.get_direction_name()]
        self._draw_char(sprite.text, sprite.color, enemy.x * CELL_SIZE, enemy.y * CELL_SIZE)

    def _draw_bullet(self, bullet):
        self._draw_char(BULLET_SPRITE.text, BULLET_SPRITE.color, bullet.x * CELL_SIZE, bullet.y * CELL_SIZE)

    def _draw_explosion(self, exp):
        alpha = exp["timer"] / 20.0
        color = (int(255 * alpha), int(165 * alpha), 0)
        self._draw_char(EXPLOSION_SPRITE.text, color, exp["x"] * CELL_SIZE, exp["y"] * CELL_SIZE)

    def _draw_char(self, char, color, px, py):
        text = self.font.render(char, True, color)
        self.screen.blit(text, (px, py))

    def _draw_hud(self):
        if self.player:
            lives_text = self.font.render(f"Lives: {self.player.lives}", True, GREEN)
        else:
            lives_text = self.font.render(f"Lives: 0", True, GREEN)
        score_text = self.font.render(f"Score: {self.score}", True, YELLOW)
        self.screen.blit(lives_text, (10, 5))
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 5))

    def _run_game_over(self):
        while self.state == "game_over":
            self.screen.fill(BLACK)
            text = self.font.render("GAME OVER", True, RED)
            score = self.font.render(f"Final Score: {self.score}", True, YELLOW)
            restart = self.font.render("Press ENTER to Restart", True, GREEN)

            tw, _ = text.get_size()
            self.screen.blit(text, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(score, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2 + 60))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.score = 0
                        self._start_level(0)
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.gamepad and event.button == GAMEPAD_BTN_A:
                        self.score = 0
                        self._start_level(0)

            self.clock.tick(FPS)

    def _run_level_complete(self):
        while self.state == "level_complete":
            self.screen.fill(BLACK)
            text = self.font.render("LEVEL COMPLETE!", True, GREEN)
            score = self.font.render(f"Score: {self.score}", True, YELLOW)
            cont = self.font.render("Press ENTER for Next Level", True, CYAN)

            tw, _ = text.get_size()
            self.screen.blit(text, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(score, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(cont, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2 + 60))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._start_level(self.level_num + 1)
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.gamepad and event.button == GAMEPAD_BTN_A:
                        self._start_level(self.level_num + 1)

            self.clock.tick(FPS)
