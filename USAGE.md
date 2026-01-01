# Usage Guide

tilepygame provides a simple framework for building top-down 2D tile-based games with Pygame-ce and Tiled maps.

## Quick Start

```python
from tilepygame import Game, Internals, TileMap, MapObject

game = Game(width=800, height=600, title="My Game", fps=60)
tilemap = game.load_tilemap("path/to/map.tmx")

def game_loop(g: Internals) -> None:
    # Your game logic here
    # The tilemap is already rendered - draw your sprites on top
    pass

game.run(game_loop)
```

## Core Concepts

### Game Loop

The `Game` class handles initialization, the main loop, and rendering. You provide a callback that runs each frame:

```python
def game_loop(g: Internals) -> None:
    dt = g.dt  # Delta time in seconds

    # Update game state
    player.update(dt)

    # Draw sprites (tilemap already rendered)
    player.draw(g.screen, g.camera.offset)
```

The `Internals` object provides access to:
- `screen` - The pygame Surface to draw on
- `camera` - The Camera instance
- `tilemap` - The loaded TileMap (if any)
- `dt` - Delta time since last frame
- `width`, `height` - Screen dimensions

### Loading Tiled Maps

```python
tilemap = game.load_tilemap("map.tmx")

# Map dimensions
print(tilemap.width, tilemap.height)        # In tiles
print(tilemap.pixel_width, tilemap.pixel_height)  # In pixels
print(tilemap.tile_width, tilemap.tile_height)    # Tile size
```

### Camera

The camera handles smooth scrolling and stays within map bounds:

```python
# Follow a target (centers on the position)
g.camera.follow(player.x, player.y)

# Adjust smoothing (0.0 = very smooth, 1.0 = instant, default 0.1)
g.camera.smoothing = 0.15

# Snap instantly to target (useful for initial positioning)
g.camera.snap_to_target()

# Get offset for rendering sprites
offset = g.camera.offset  # (x, y) tuple
screen_x = world_x - offset[0]
screen_y = world_y - offset[1]

# Manually set camera bounds (automatically set when loading a tilemap)
g.camera.set_bounds(0, 0, map_pixel_width, map_pixel_height)

# Remove camera bounds to allow free scrolling
g.camera.clear_bounds()
```

### Coordinate Conversions

Convert between screen, world, and tile coordinates:

```python
# Screen (mouse) to world coordinates
world_x, world_y = g.screen_to_world(mouse_x, mouse_y)

# World to screen (for custom drawing)
screen_x, screen_y = g.world_to_screen(entity.x, entity.y)

# World to tile coordinates
tile_x, tile_y = g.world_to_tile(world_x, world_y)

# Tile to world (top-left corner of tile)
world_x, world_y = g.tile_to_world(tile_x, tile_y)

# Screen to tile (useful for click-on-tile detection)
tile_x, tile_y = g.screen_to_tile(mouse_x, mouse_y)

# Tile to screen (useful for drawing tile highlights)
screen_x, screen_y = g.tile_to_screen(tile_x, tile_y)
```

## Working with Tiled Object Layers

Object layers in Tiled can define spawn points, collision zones, triggers, and more.

### Spawn Points

```python
spawn = tilemap.get_object_by_name("Objects", "Player Spawn")
if spawn:
    player = Player(spawn.x, spawn.y)
```

### Iterating Objects

```python
# Get all objects in a layer
for obj in tilemap.get_objects("Enemies"):
    spawn_enemy(obj.x, obj.y, obj.type)

# Filter by type
for trigger in tilemap.get_objects_by_type("Triggers", "door"):
    doors.append(Door(trigger.rect, trigger.properties))
```

### Collision Rectangles

```python
# Get all collision rects from an object layer
collision_rects = tilemap.get_collision_rects("Collisions")

# Check collision
for rect in collision_rects:
    if player.rect.colliderect(rect):
        handle_collision()
```

### MapObject Properties

Each `MapObject` has:
- `name`, `type` - From Tiled
- `x`, `y`, `width`, `height` - Position and size
- `properties` - Custom properties dict from Tiled
- `rect` - Convenience property returning a pygame.Rect

## Animated Sprites

### From Folder Structure

Organize frames in folders by animation name:

```
player/
  idle/
    01.png
    02.png
  run/
    01.png
    02.png
    03.png
```

```python
from tilepygame import AnimatedSprite

player = AnimatedSprite.from_folder("assets/player", frame_duration=0.1)
player.play("idle")

# In game loop
player.update(dt)
screen.blit(player.image, player.rect)
```

### From Spritesheet

```python
from tilepygame import load_spritesheet, AnimatedSprite

frames = load_spritesheet("spritesheet.png", frame_width=32, frame_height=32)

sprite = AnimatedSprite()
sprite.add_animation("walk", frames, frame_duration=0.1, loop=True)
sprite.play("walk")
```

### Loading Frames Manually

For more control, use the lower-level loading functions:

```python
from tilepygame import load_frames_folder, load_animations_folder

# Load frames from a single folder (e.g., assets/player/idle/)
idle_frames = load_frames_folder("assets/player/idle")

# Load all animations from a folder structure at once
# Returns dict[str, list[Surface]] mapping animation names to frames
animations = load_animations_folder("assets/player")
# animations = {"idle": [...], "run": [...], ...}
```

### Animation Control

```python
sprite.play("run")              # Switch animation
sprite.play("attack", restart=True)  # Force restart
sprite.stop()                   # Pause on current frame

if not sprite.is_playing:
    sprite.play("idle")
```

## Rendering Specific Layers

Render layers selectively for layering effects:

```python
# Render only specific layers
tilemap.render(screen, camera.offset, layers=["Ground", "Walls"])

# Or render one layer at a time
tilemap.render_layer(screen, "Background", camera.offset)
draw_entities()
tilemap.render_layer(screen, "Foreground", camera.offset)
```

## Tile Properties

Access custom properties set on tiles in Tiled:

```python
props = tilemap.get_tile_properties(tile_x, tile_y, "Ground")
if props and props.get("slippery"):
    apply_ice_physics()

# Check if a tile exists
gid = tilemap.get_tile_gid(tile_x, tile_y, "Ground")
if gid != 0:
    # Tile exists at this position
    pass
```

## Layer Information

```python
# List all layers
all_layers = tilemap.get_layer_names()
tile_layers = tilemap.get_tile_layer_names()
object_layers = tilemap.get_object_layer_names()

# Get layer properties
props = tilemap.get_layer_properties("Ground")
```
