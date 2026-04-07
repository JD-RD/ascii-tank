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
    GAMEPAD_BTN_X,
    GAMEPAD_BTN_Y,
    GAMEPAD_BTN_START,
    GAMEPAD_BTN_SELECT,
    ENEMY_COUNT,
    TILE_BASE,
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
from sounds import make_shoot_sound, make_explosion_sound, make_hit_sound
from highscore import load_highscore, save_highscore, get_leaderboard
from powerups import (
    PowerUp, spawn_powerup, POWERUP_SPEED, POWERUP_SHIELD,
    POWERUP_LIFE, POWERUP_FREEZE, POWERUP_SPAWN_INTERVAL,
    POWERUP_DURATION,
)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
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
        self.paused = False
        self.base_destroyed = False
        self.highscore = load_highscore()
        self.powerups = []
        self.powerup_timer = 0
        self.frozen_enemies = set()
        self.freeze_timer = 0
        self.player_name = ""
        self.sounds = {
            "shoot": make_shoot_sound(),
            "explosion": make_explosion_sound(),
            "hit": make_hit_sound(),
        }

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
            elif self.state == "name_input":
                self._run_name_input()
            elif self.state == "playing":
                self._run_game()
            elif self.state == "game_over":
                self._run_game_over()
            elif self.state == "level_complete":
                self._run_level_complete()
            elif self.state == "pause_menu":
                self._run_pause_menu()
            elif self.state == "leaderboard":
                self._run_leaderboard()

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
                        self.state = "name_input"
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.gamepad:
                        if event.button == GAMEPAD_BTN_A or event.button == GAMEPAD_BTN_START:
                            self.state = "name_input"

            self.clock.tick(FPS)

    def _draw_menu(self):
        title = self.font.render("ASCII TANK", True, GREEN)
        subtitle = self.font_small.render("A Battle City Tribute", True, DARK_GRAY)
        start = self.font.render("Press ENTER or A/START to Start", True, YELLOW)
        controls = self.font_small.render("WASD/Arrows: Move | SPACE/A: Shoot", True, CYAN)
        controls2 = self.font_small.render("SN30 Pro: D-Pad: Move | A: Shoot", True, CYAN)
        hs = self.font_small.render(f"High Score: {self.highscore}", True, YELLOW)

        tw, th = title.get_size()
        self.screen.blit(title, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(subtitle, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 4 + 40))
        self.screen.blit(hs, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 4 + 70))
        self.screen.blit(start, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(controls, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(controls2, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2 + 80))

    def _run_name_input(self):
        name = ""
        blink = True
        blink_timer = 0
        letter_index = 0
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        while self.state == "name_input":
            self.screen.fill(BLACK)
            prompt = self.font.render("Enter your name (4 chars):", True, CYAN)
            display = name + ("_" if blink else " ")
            name_surf = self.font.render(f">> {display} <<", True, GREEN)

            # Virtual keyboard at bottom
            keyboard_y = SCREEN_HEIGHT - 60
            # Current selected letter
            current_char = letters[letter_index]
            current_line = f"Select: {current_char} | Confirm: A/START"
            key_surf = self.font_small.render(current_line, True, YELLOW)
            pygame.draw.rect(self.screen, DARK_GRAY, (0, keyboard_y - 5, SCREEN_WIDTH, 60), 2)

            pw, _ = prompt.get_size()
            self.screen.blit(prompt, ((SCREEN_WIDTH - pw) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(name_surf, ((SCREEN_WIDTH - pw) // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(key_surf, ((SCREEN_WIDTH - pw) // 2, keyboard_y))
            pygame.display.flip()

            blink_timer += 1
            if blink_timer % 30 == 0:
                blink = not blink

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(name) >= 1:
                        self.player_name = name[:4].upper()
                        self._start_level(0)
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "menu"
                    elif len(name) < 4 and event.unicode.isalpha():
                        name += event.unicode.upper()
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.gamepad and event.button in (GAMEPAD_BTN_A, GAMEPAD_BTN_START):
                        if len(name) >= 1:
                            self.player_name = name[:4].upper()
                            self._start_level(0)
                if event.type == pygame.JOYHATMOTION:
                    if self.gamepad:
                        hat = self.gamepad.get_hat(GAMEPAD_HAT_INDEX)
                        if hat[0] != 0 or hat[1] != 0:
                            if hat[0] > 0:  # Right
                                letter_index = (letter_index + 1) % len(letters)
                            elif hat[0] < 0:  # Left
                                letter_index = (letter_index - 1) % len(letters)
                            elif hat[1] < 0:  # Down
                                letter_index = (letter_index + 5) % len(letters)
                            elif hat[1] > 0:  # Up
                                letter_index = (letter_index - 5) % len(letters)
                        # Trigger backspace with home button or combo
                if event.type == pygame.JOYBUTTONDOWN and event.button == GAMEPAD_BTN_B:
                    name = name[:-1]

            self.clock.tick(FPS)

    def _run_pause_menu(self):
        selected = 0
        options = ["Resume", "Leaderboard", "Quit to Menu"]
        while self.state == "pause_menu":
            self.screen.fill(BLACK)
            title = self.font.render("PAUSED", True, CYAN)
            tw, _ = title.get_size()
            self.screen.blit(title, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 4))

            for i, opt in enumerate(options):
                color = YELLOW if i == selected else DARK_GRAY
                text = self.font.render(opt, True, color)
                self.screen.blit(text, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2 + i * 40))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._handle_pause_option(selected)
                    elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.paused = False
                        self.state = "playing"
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.gamepad:
                        if event.button == GAMEPAD_BTN_A or event.button == GAMEPAD_BTN_START:
                            self._handle_pause_option(selected)
                        elif event.button == GAMEPAD_BTN_SELECT:
                            self.paused = False
                            self.state = "playing"
                        elif event.button == GAMEPAD_BTN_Y:
                            selected = (selected - 1) % len(options)
                        elif event.button == GAMEPAD_BTN_B:
                            selected = (selected + 1) % len(options)

            self.clock.tick(FPS)

    def _handle_pause_option(self, idx):
        if idx == 0:
            self.paused = False
            self.state = "playing"
        elif idx == 1:
            self.state = "leaderboard"
        elif idx == 2:
            self.state = "menu"

    def _run_leaderboard(self):
        entries = get_leaderboard()
        while self.state == "leaderboard":
            self.screen.fill(BLACK)
            title = self.font.render("LEADERBOARD", True, CYAN)
            tw, _ = title.get_size()
            self.screen.blit(title, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 5))

            for i, entry in enumerate(entries[:10]):
                color = YELLOW if i == 0 else WHITE
                text = self.font.render(f"{i+1}. {entry['name']:4s}  {entry['score']}", True, color)
                self.screen.blit(text, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 3 + i * 30))

            if not entries:
                empty = self.font_small.render("No scores yet", True, DARK_GRAY)
                self.screen.blit(empty, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2))

            back = self.font_small.render("Press ESC or ENTER to go back", True, DARK_GRAY)
            self.screen.blit(back, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT - 60))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        if self.paused:
                            self.state = "pause_menu"
                        else:
                            self.state = "menu"
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.gamepad and event.button == GAMEPAD_BTN_A:
                        if self.paused:
                            self.state = "pause_menu"
                        else:
                            self.state = "menu"

            self.clock.tick(FPS)

    def _start_level(self, num):
        self.level_num = num
        level_factory = LEVELS[num % len(LEVELS)]
        self.level = level_factory()
        px, py = self.level.spawn_points["player"]
        self.player = Player(px, py)
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self.powerups = []
        self.powerup_timer = 0
        self.frozen_enemies = set()
        self.freeze_timer = 0
        self.paused = False
        self.base_destroyed = False
        self._spawn_enemies()
        self.state = "playing"

    def _spawn_enemies(self):
        spawn_points = self.level.spawn_points.get("enemies", [])
        for i in range(ENEMY_COUNT):
            sx, sy = spawn_points[i % len(spawn_points)]
            target_base = i % 2 == 0 or self.level_num >= 2
            self.enemies.append(Enemy(sx, sy, i, target_base=target_base))

    def _run_game(self):
        while self.state == "playing":
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = True
                        self.state = "pause_menu"
                    elif event.key == pygame.K_p:
                        self.paused = True
                        self.state = "pause_menu"
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.gamepad and event.button == GAMEPAD_BTN_SELECT:
                        self.paused = True

            if self.player and self.player.active:
                self.player.update(keys, self.level, self.gamepad)
                new_bullet = self.player.shoot(keys, self.gamepad)
                if new_bullet:
                    self.bullets.append(new_bullet)
                    self.sounds["shoot"].play()

            for enemy in self.enemies:
                if enemy.active and id(enemy) not in self.frozen_enemies:
                    new_bullet = enemy.update(self.level, self.player, self.bullets)
                    if new_bullet:
                        self.bullets.append(new_bullet)

            self._update_bullets()
            self._check_collisions()
            self._update_explosions()
            self._update_powerups()
            self._check_powerup_collection()

            if self.freeze_timer > 0:
                self.freeze_timer -= 1

            if self.player and not self.player.active:
                self.state = "game_over"

            if self.base_destroyed:
                self.state = "game_over"

            if all(not e.active for e in self.enemies):
                self.state = "level_complete"

            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    def _update_powerups(self):
        self.powerup_timer += 1
        if self.powerup_timer >= POWERUP_SPAWN_INTERVAL and len(self.powerups) < 3:
            self.powerup_timer = 0
            pu = spawn_powerup(self.level)
            if pu:
                self.powerups.append(pu)

        self.powerups = [p for p in self.powerups if p.active and not p.is_expired()]

        if self.freeze_timer <= 0:
            self.frozen_enemies.clear()

    def _check_powerup_collection(self):
        if not self.player or not self.player.active:
            return

        for pu in self.powerups:
            if not pu.active:
                continue
            if abs(self.player.x - pu.x) <= 1 and abs(self.player.y - pu.y) <= 1:
                pu.active = False
                self._apply_powerup(pu)

    def _apply_powerup(self, pu):
        if pu.ptype == POWERUP_SPEED:
            self.player.speed_boost = POWERUP_DURATION
        elif pu.ptype == POWERUP_SHIELD:
            self.player.shielded = True
            self.player.shield_timer = POWERUP_DURATION
        elif pu.ptype == POWERUP_LIFE:
            self.player.lives = min(self.player.lives + 1, 5)
        elif pu.ptype == POWERUP_FREEZE:
            self.freeze_timer = POWERUP_DURATION
            self.frozen_enemies = {id(e) for e in self.enemies if e.active}

    def _run_paused(self):
        self.screen.fill(BLACK)
        text = self.font.render("PAUSED", True, CYAN)
        cont = self.font_small.render("Press P to Resume", True, DARK_GRAY)
        tw, _ = text.get_size()
        self.screen.blit(text, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(cont, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    self.paused = False
            if event.type == pygame.JOYBUTTONDOWN:
                if self.gamepad and event.button == GAMEPAD_BTN_SELECT:
                    self.paused = False

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
                    if len(result) > 2 and result[2] == TILE_BASE:
                        self.base_destroyed = True
                        self.sounds["explosion"].play()

        self.bullets = [b for b in self.bullets if b.active]

    def _check_collisions(self):
        for bullet in self.bullets:
            if not bullet.active:
                continue

            if bullet.owner == "player":
                for enemy in self.enemies:
                    if enemy.active and abs(bullet.x - enemy.x) <= 1 and abs(bullet.y - enemy.y) <= 1:
                        bullet.active = False
                        enemy.hit()
                        self.score += 100
                        self.explosions.append({
                            "x": enemy.x,
                            "y": enemy.y,
                            "timer": 20,
                        })
                        self.sounds["explosion"].play()
                        break
            elif bullet.owner == "enemy":
                if self.player and self.player.active and abs(bullet.x - self.player.x) <= 1 and abs(bullet.y - self.player.y) <= 1:
                    bullet.active = False
                    self.player.hit()
                    self.explosions.append({
                        "x": self.player.x,
                        "y": self.player.y,
                        "timer": 20,
                    })
                    self.sounds["hit"].play()

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

        for pu in self.powerups:
            if pu.active:
                self._draw_powerup(pu)

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

    def _draw_powerup(self, pu):
        char, color = pu.get_char()
        self._draw_char(char, color, pu.x * CELL_SIZE, pu.y * CELL_SIZE)

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

        indicators = []
        if self.player and self.player.shielded:
            indicators.append("[SHIELD]")
        if self.player and self.player.speed_boost > 0:
            indicators.append("[SPEED]")
        if self.freeze_timer > 0:
            indicators.append("[FREEZE]")
        if indicators:
            text = self.font_small.render(" ".join(indicators), True, CYAN)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 5))

    def _run_game_over(self):
        save_highscore(self.player_name or "????", self.score)
        self.highscore = load_highscore()

        while self.state == "game_over":
            self.screen.fill(BLACK)
            text = self.font.render("GAME OVER", True, RED)
            score = self.font.render(f"Final Score: {self.score}", True, YELLOW)
            hs = self.font.render(f"High Score: {self.highscore}", True, YELLOW)
            restart = self.font.render("Press ENTER to Restart", True, GREEN)

            tw, _ = text.get_size()
            self.screen.blit(text, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(score, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(hs, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(restart, ((SCREEN_WIDTH - tw) // 2, SCREEN_HEIGHT // 2 + 80))
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
