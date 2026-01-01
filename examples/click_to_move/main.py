"""
Simple click-to-move example using tilepygame.

Demonstrates:
- Loading and rendering a Tiled map
- Spawning at a map object location
- Click-to-move player movement
- Camera following with smooth scrolling
"""

from __future__ import annotations

import math
from pathlib import Path

import pygame

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tilepygame import Game, Internals


class Player:
    """Simple circle player with click-to-move behavior."""
    
    def __init__(self, x: float, y: float, speed: float = 200.0):
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = speed
        self.radius = 12
        self.color = (70, 130, 180)  # Steel blue
    
    def set_target(self, x: float, y: float) -> None:
        """Set the target position to move toward."""
        self.target_x = x
        self.target_y = y
    
    def update(self, dt: float) -> None:
        """Move toward target position."""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 2:  # Stop when close enough
            move_dist = self.speed * dt
            if move_dist >= dist:
                self.x = self.target_x
                self.y = self.target_y
            else:
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist
    
    def draw(self, screen: pygame.Surface, camera_offset: tuple[float, float]) -> None:
        """Draw the player circle on screen."""
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)
        pygame.draw.circle(screen, (40, 80, 120), (screen_x, screen_y), self.radius, 2)


def main() -> None:
    assets_dir = Path(__file__).parent / "assets"
    
    game = Game(width=800, height=600, title="Click to Move", fps=60)
    tilemap = game.load_tilemap(str(assets_dir / "island.tmx"))
    
    spawn = tilemap.get_object_by_name("Objects", "Starting Point")
    if spawn:
        player = Player(spawn.x, spawn.y)
    else:
        player = Player(400, 300)
    
    game.internals.camera.follow(player.x, player.y)
    game.internals.camera.snap_to_target()
    
    was_pressed = False
    
    def game_loop(g: Internals) -> None:
        nonlocal was_pressed
        
        pressed = pygame.mouse.get_pressed()[0]
        if pressed and not was_pressed:
            mx, my = pygame.mouse.get_pos()
            world_x, world_y = g.screen_to_world(mx, my)
            player.set_target(world_x, world_y)
        was_pressed = pressed
        
        player.update(g.dt)
        
        g.camera.follow(player.x, player.y)
        
        player.draw(g.screen, g.camera.offset)
    
    game.run(game_loop)


if __name__ == "__main__":
    main()

