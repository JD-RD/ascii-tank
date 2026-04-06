# ASCII Tank

A Battle City (NES) inspired tank game rendered entirely in ASCII characters. Built with Python and pygame, featuring full support for keyboard and 8bitDo SN30 Pro gamepad on Linux.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![pygame](https://img.shields.io/badge/pygame-2.5+-red.svg)

## Features

- **ASCII graphics** — tanks, walls, bullets, and explosions rendered as single characters
- **Keyboard controls** — WASD or Arrow keys to move, Space to shoot
- **Gamepad support** — 8bitDo SN30 Pro (D-Pad + A button) works out of the box on Linux
- **Destructible terrain** — brick walls crumble under fire, steel walls hold firm
- **Enemy AI** — tanks that track your position and fire back
- **Multiple tile types** — brick, steel, water (impassable), trees (concealment), and the base to defend
- **Lives & scoring** — classic arcade-style gameplay loop

## Screenshots

```
ASCII TANK
A Battle City Tribute

  ^  ← Your tank (green)
  A  ← Enemy tank (red)
  #  ← Brick wall (destructible)
  @  ← Steel wall (indestructible)
  ~  ← Water (impassable)
  %  ← Trees (concealment)
  &  ← Base (defend it!)
  *  ← Bullet
  X  ← Explosion
```

## Quick Start

### Prerequisites

- Python 3.8+
- pygame 2.5+
- Linux (tested on Linux Mint)

### Install & Run

```bash
# Clone the repo
git clone https://github.com/<your-username>/ascii-tank.git
cd ascii-tank

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the game
./run.sh
```

## Controls

| Action | Keyboard | 8bitDo SN30 Pro |
|--------|----------|-----------------|
| Move | WASD / Arrow Keys | D-Pad |
| Shoot | Space | A Button |
| Start Game | Enter | A / Start |
| Pause | ESC | — |

## Project Structure

```
ascii-tank/
├── main.py          # Entry point
├── game.py          # Game engine: main loop, state machine, rendering
├── config.py        # Constants: display, colors, tiles, speeds, gamepad
├── sprites.py       # ASCII sprite definitions
├── player.py        # Player tank: input, movement, shooting
├── enemy.py         # Enemy AI: pathfinding, shooting
├── bullet.py        # Bullet movement and wall collision
├── level.py         # Level class and factory functions
├── requirements.txt # Dependencies
├── run.sh           # Launcher script
├── AGENTS.md        # Development guidelines for AI agents
├── CHANGELOG.md     # Version history
└── TODO.md          # Planned features and improvements
```

## Architecture

- **Grid-based movement** — entities move on integer grid coordinates using frame-interval counters
- **Single-char sprites** — each entity is one ASCII character fitting exactly one grid cell
- **State machine** — `menu` → `playing` → `game_over` / `level_complete` → loop
- **Exact collision** — grid position matching for bullet-to-entity hits

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT
