# Changelog

## [Unreleased]

### Added
- Gamepad Start button support for menu navigation (same as Enter key)
- Virtual keyboard for gamepad name input (D-Pad to select letters, B for backspace, A/START to confirm)
- Name input before game start (4 characters max, alpha only)
- Leaderboard with top 10 scores (persistent in `highscore.json`)
- ESC opens pause menu instead of returning to main menu
- Enemy base-targeting AI: 50% of enemies target the base in level 1, all levels 2+
- High score persistence across game over states
- Pause menu with Resume, Leaderboard, Quit to Menu options
- HUD indicators for active power-ups (SHIELD, SPEED, FREEZE)
- Power-up spawning system: speed boost, shield, extra life, and freeze enemies

### Fixed
- Gamepad name input: A button now adds selected letter, START confirms
- Gamepad Select now opens pause menu during gameplay
- Gamepad button constants: removed duplicate entries in config.py
- Enemy AI: base position now found on spawn (was previously lazy, could remain None)
- Enemy AI: added direction change chance (30%) for more dynamic movement
- Enemy AI: bullet avoidance now only checks player bullets (not own bullets)
- Enemy AI: now uses config constant ENEMY_MOVE_INTERVAL instead of hardcoded 2.0
- Enemy AI: improved BFS pathfinding (deeper search, better fallback, finds paths to player/base)
- Enemy AI: enemies now target base starting from level 2 (was level 1)
- Enemy AI: BFS fallback now finds nearest walkable tile toward target (better in maze levels)
- Enemy AI: improved BFS to track best direction found so far (not just last direction)
- Enemy shooting: removed duplicate shoot-on-wait-frame bug that fired 60 bullets/sec per enemy
- Base tile overwritten by surrounding brick wall in level generation (skipped center cell)
- Stereo audio array shape for pygame mixer (was 1D, now 2D stereo)
- Level 2/3 generation: fixed raw tuple format for brick/steel/water/tile layout helpers
- Score now persists between levels instead of resetting
- ESC during gameplay opens pause menu, not main menu
- Gamepad button constants updated with Y/X buttons for pause menu

### Testing
- Added pytest test suite with 43 tests covering Level, Player, Enemy, and Bullet classes
- Tests verify tile properties, movement intervals, shooting cooldowns, collision behavior
