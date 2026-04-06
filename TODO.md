# TODO

## High Priority
- [ ] Fix enemy shooting logic (currently shoots too frequently in `enemy.py:update()`)
- [ ] Add proper gamepad axis support (left stick) as alternative to D-Pad
- [ ] Improve collision detection for bullets vs entities (currently exact grid match only)
- [ ] Add sound effects for shooting, explosions, and enemy destruction
- [ ] Add test suite with pytest

## Medium Priority
- [ ] Add multiple levels with increasing difficulty
- [ ] Add power-ups (speed boost, shield, extra lives)
- [ ] Improve enemy AI (avoid getting stuck, better pathfinding)
- [ ] Add base defense mechanic (game over if base is destroyed)
- [ ] Add pause functionality (P key or Select button)
- [ ] Add high score persistence
- [ ] Refactor level generation to use data-driven approach (JSON/text files)

## Low Priority
- [ ] Add animated sprites (multi-frame ASCII)
- [ ] Add particle effects for explosions
- [ ] Add multiplayer support (2 players)
- [ ] Add level editor
- [ ] Add configuration file for keybindings and gamepad mappings
- [ ] Add ruff linter/formatter to project
