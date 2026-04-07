# TODO

## High Priority
- [x] Fix enemy shooting logic (shoots too frequently)
- [x] Add proper gamepad axis support (left stick) as alternative to D-Pad
- [x] Improve collision detection for bullets vs entities (proximity-based)
- [x] Add sound effects for shooting, explosions, and enemy destruction
- [x] Add test suite with pytest (43 tests covering Level, Player, Enemy, Bullet)

## Medium Priority
- [x] Add base defense mechanic (game over if base is destroyed)
- [x] Add pause menu (P key, ESC, or Select button)
- [x] Add high score persistence
- [x] Add multiple levels with increasing difficulty (3 levels)
- [x] Refactor level generation to data-driven approach (_build_level + helpers)
- [x] Improve enemy AI (BFS pathfinding, stuck detection, line-of-fire shooting)
- [x] Add power-ups (speed boost, shield, extra lives, freeze enemies)

## Low Priority
- [ ] Add animated sprites (multi-frame ASCII)
- [ ] Add particle effects for explosions
- [ ] Add multiplayer support (2 players)
- [ ] Add level editor
- [ ] Add configuration file for keybindings and gamepad mappings
- [ ] Add ruff linter/formatter to project
