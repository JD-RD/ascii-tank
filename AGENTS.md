# AGENTS.md - ASCII Tank

## Project Overview
Battle City-inspired ASCII tank game built with Python + pygame. Runs in a dedicated window with ASCII character rendering. Supports keyboard and 8bitDo SN30 Pro gamepad.

## Project Structure
```
ascii-tank/
├── main.py          # Entry point (if __name__ == "__main__")
├── game.py          # Game engine: main loop, state machine, rendering, event handling
├── config.py        # All constants: display, colors, tiles, directions, speeds, gamepad
├── sprites.py       # ASCII sprite definitions (single-char, color pairs)
├── player.py        # Player tank: input, movement, shooting
├── enemy.py         # Enemy AI: pathfinding, shooting, direction choice
├── bullet.py        # Bullet movement and wall collision/destruction
├── level.py         # Level class and level factory functions
├── requirements.txt # Python dependencies
├── run.sh           # Launcher script (activates venv, runs main.py)
└── venv/            # Python virtual environment (do not commit)
```

## Commands

### Run the game
```bash
./run.sh
# or:
source venv/bin/activate && python3 main.py
```

### Install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Create virtual environment (first time)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Testing
Pytest test suite is set up (43 tests in `tests/test_game.py`):
```bash
source venv/bin/activate
pip install pytest
pytest tests/          # Run all tests
pytest tests/test_file.py  # Run single test file
pytest tests/test_file.py::test_name  # Run single test
```

### Linting / Formatting
No linter/formatter is currently configured. Recommended additions:
```bash
pip install ruff
ruff check .           # Lint
ruff format .          # Format
```

## Code Style

### Imports
- Standard library imports first, then third-party (`pygame`), then local modules
- Use explicit imports from `config` rather than `from config import *`
- Group imports: stdlib, pygame, local modules — separated by blank lines

### Formatting
- 4-space indentation (no tabs)
- Max line length: 100 characters (relaxed for long string literals in rendering)
- Use `ruff format` if available
- Two blank lines between top-level functions/classes, one between methods

### Naming Conventions
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `PLAYER_MOVE_INTERVAL`, `TILE_BRICK`)
- **Classes**: `PascalCase` (e.g., `Player`, `Enemy`, `Bullet`, `Level`, `Game`)
- **Variables/parameters**: `snake_case` (e.g., `move_counter`, `shoot_cooldown`)
- **Private methods**: `_leading_underscore` (e.g., `_draw_level`, `_check_collisions`)
- **Direction tuples**: `DIR_UP`, `DIR_DOWN`, `DIR_LEFT`, `DIR_RIGHT` — values are `(dx, dy)`
- **Tile types**: Integer constants `TILE_EMPTY = 0`, `TILE_BRICK = 1`, etc.

### Types
No type annotations are currently used. If adding them:
- Use standard Python type hints (`int`, `str`, `list`, `Optional`, etc.)
- Annotate function parameters and return types
- `pygame.Rect`, `pygame.Surface`, `pygame.Joystick` for pygame types

### Architecture Patterns
- **Grid-based movement**: All entities move on integer grid coordinates, not pixels. Speed is controlled via frame-interval counters (`move_counter` vs `MOVE_INTERVAL`), not per-frame pixel offsets.
- **Single-char sprites**: Each entity renders as one ASCII character to fit exactly one grid cell. No multi-line sprites.
- **Game states**: `menu` → `playing` → `game_over` / `level_complete` → loop back. State machine in `Game.run()`.
- **Collision**: Exact grid position matching (`bullet.x == enemy.x and bullet.y == enemy.y`).
- **Entity interface**: Game entities share common patterns: `active` bool, `x`/`y` grid coords, `direction` tuple, `move_counter`, `update()` method, `hit()` method.

### Error Handling
- No exceptions are raised in game logic — use guard clauses and early returns
- `pygame.quit(); sys.exit()` on QUIT event or ESC from menu
- Gamepad is optional — all gamepad access is guarded with `if gamepad:` checks
- Out-of-bounds tile access returns `TILE_STEEL` (safe default)

### Gamepad (8bitDo SN30 Pro)
- D-Pad is read via `joystick.get_hat(0)` (SDL hat events)
- Shoot button is `joystick.get_button(2)` (X button)
- Start button (`GAMEPAD_BTN_START`) used for menu navigation
- SN30 Pro works in DInput mode by default on Linux; no special driver needed

### Adding New Features
- New tile types: add `TILE_*` constant in `config.py`, entry in `TILE_CHARS` in `sprites.py`, logic in `Level` methods
- New entity class: follow `active`/`x`/`y`/`direction`/`update()`/`hit()` pattern
- New levels: add factory function to `level.py`, append to `LEVELS` list
- New game states: add branch in `Game.run()` and corresponding `_run_*` method
- Enemy AI: see [AI.md](AI.md) for pathfinding behavior and common issues

### Pause Menu
- Pause menu is a state (`pause_menu`) triggered by `ESC`/`P` on keyboard or `GAMEPAD_BTN_SELECT` on gamepad
