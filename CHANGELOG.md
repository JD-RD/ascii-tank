# Changelog

## [Unreleased]

### Added
- Initial project setup with pygame
- ASCII tank game inspired by Battle City (NES)
- Player tank with keyboard (WASD/Arrows) and 8bitDo SN30 Pro gamepad support
- Enemy AI with basic pathfinding toward player
- Bullet system with wall collision and destruction
- Level system with brick, steel, water, tree, and base tiles
- Game states: menu, playing, game_over, level_complete
- HUD displaying lives and score
- `run.sh` launcher script with venv activation
- `AGENTS.md` for development guidelines

### Changed
- Switched from per-frame pixel speeds to frame-interval counters for playable movement speeds
- Simplified sprites from multi-line ASCII to single characters to prevent cell overlap
- Collision detection uses exact grid position matching
