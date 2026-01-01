# tilepygame

A Pygame-ce wrapper for building top-down 2D tile-based games with Tiled map support.

## Features

- **Tiled Integration** - Load and render TMX maps with tile layers, object layers, and custom properties
- **Camera System** - Smooth following, bounds clamping, and coordinate conversion helpers
- **Animated Sprites** - Load animations from spritesheets or folder structures
- **Simple Game Loop** - Minimal boilerplate to get a game running

## Installation

Requires Python 3.11+

```bash
# Clone the repository
git clone <repo-url>
cd topdown_rpg_pygame

# Install dependencies with uv
uv sync

# Or with pip
pip install pygame-ce pytmx
```

## Quick Start

```python
from tilepygame import Game, Internals

game = Game(width=800, height=600, title="My Game")
tilemap = game.load_tilemap("map.tmx")

# Get spawn point from Tiled object layer
spawn = tilemap.get_object_by_name("Objects", "Player Spawn")

def game_loop(g: Internals) -> None:
    # Handle input, update game state
    player.update(g.dt)

    # Camera follows player
    g.camera.follow(player.x, player.y)

    # Draw sprites (tilemap already rendered)
    player.draw(g.screen, g.camera.offset)

game.run(game_loop)
```

## Documentation

See [USAGE.md](USAGE.md) for detailed documentation on:
- Camera and coordinate systems
- Working with Tiled object layers
- Animated sprites
- Layer rendering

## Example

Run the click-to-move example:

```bash
uv run python examples/click_to_move/main.py
```

## Dependencies

- [pygame-ce](https://pyga.me/) - Community edition of Pygame
- [pytmx](https://github.com/bitcraft/pytmx) - Tiled TMX map loader
