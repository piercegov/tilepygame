# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**tilepygame** is a Pygame-ce wrapper library for building top-down 2D tile-based games. It provides abstractions for tilemaps, cameras, and animated sprites on top of pygame-ce and pytmx.

## Commands

```bash
# Install dependencies (uses uv with Python 3.11)
uv sync

# Run the example game
uv run python examples/click_to_move/main.py
```

## Architecture

The library is in `src/tilepygame/` with these core modules:

- **engine.py** - `Game` class that runs the main loop and `Internals` dataclass passed to the game loop callback. The game loop automatically renders the tilemap before calling the user's callback (user draws on top).

- **tilemap.py** - `TileMap` wrapper around pytmx for loading/rendering Tiled .tmx files. Provides access to tile layers, object layers (spawn points, collisions), and tile properties.

- **camera.py** - `Camera` with smooth following, bounds clamping, and offset calculation for rendering.

- **sprites.py** - `AnimatedSprite` extending pygame.sprite.Sprite with named animations, plus helpers to load frames from spritesheets or folder structures.

## Key Patterns

**Game Loop**: Users pass a callback to `Game.run()` that receives `Internals`. The tilemap renders automatically; the callback draws sprites and handles input.

**Coordinate Systems**: `Internals` provides conversion helpers: `screen_to_world`, `world_to_screen`, `world_to_tile`, `tile_to_world`, `screen_to_tile`, `tile_to_screen`.

**Object Layers**: Use `TileMap.get_objects()`, `get_objects_by_type()`, or `get_object_by_name()` to query Tiled object layers for spawn points, triggers, and collisions.
