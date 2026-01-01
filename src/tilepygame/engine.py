from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import sys

import pygame

from .camera import Camera
from .tilemap import TileMap


@dataclass
class Internals:
    """Game state passed to the game loop each frame."""
    width: int
    height: int
    screen: pygame.Surface
    camera: Camera
    tilemap: TileMap | None = None
    dt: float = 0.0
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> tuple[float, float]:
        """Convert screen coordinates to world coordinates using camera offset."""
        return screen_x + self.camera.x, screen_y + self.camera.y
    
    def world_to_screen(self, world_x: float, world_y: float) -> tuple[float, float]:
        """Convert world coordinates to screen coordinates using camera offset."""
        return world_x - self.camera.x, world_y - self.camera.y
    
    def world_to_tile(self, world_x: float, world_y: float) -> tuple[int, int] | None:
        """Convert world coordinates to tile coordinates. Returns None if no tilemap."""
        if self.tilemap is None:
            return None
        return (
            int(world_x // self.tilemap.tile_width),
            int(world_y // self.tilemap.tile_height)
        )
    
    def tile_to_world(self, tile_x: int, tile_y: int) -> tuple[float, float] | None:
        """Convert tile coordinates to world coordinates (top-left of tile). Returns None if no tilemap."""
        if self.tilemap is None:
            return None
        return (
            float(tile_x * self.tilemap.tile_width),
            float(tile_y * self.tilemap.tile_height)
        )
    
    def screen_to_tile(self, screen_x: float, screen_y: float) -> tuple[int, int] | None:
        """Convert screen coordinates to tile coordinates. Returns None if no tilemap."""
        world = self.screen_to_world(screen_x, screen_y)
        return self.world_to_tile(*world)
    
    def tile_to_screen(self, tile_x: int, tile_y: int) -> tuple[float, float] | None:
        """Convert tile coordinates to screen coordinates. Returns None if no tilemap."""
        world = self.tile_to_world(tile_x, tile_y)
        if world is None:
            return None
        return self.world_to_screen(*world)


class Game:
    """
    Main game engine class.
    
    Handles the game loop, rendering, and tilemap integration.
    """
    
    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Tile-based Game",
        fps: int = 60
    ):
        pygame.init()
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        
        self._clock = pygame.time.Clock()
        self._fps = fps
        
        self._internals = Internals(
            width=width,
            height=height,
            screen=self._screen,
            camera=Camera(width, height)
        )
    
    @property
    def internals(self) -> Internals:
        """Access to game state for setup and runtime."""
        return self._internals
    
    def load_tilemap(self, path: str) -> TileMap:
        """
        Load a Tiled map from a TMX file.
        
        Automatically sets camera bounds to the map dimensions.
        
        Args:
            path: Path to the .tmx file
            
        Returns:
            The loaded TileMap instance
        """
        tilemap = TileMap(path)
        self._internals.tilemap = tilemap
        self._internals.camera.set_bounds(
            0, 0,
            tilemap.pixel_width,
            tilemap.pixel_height
        )
        return tilemap
    
    def run(self, game_loop: Callable[[Internals], None]) -> None:
        """
        Start the game loop.
        
        Args:
            game_loop: A function that receives Internals and runs each frame.
                       The tilemap is rendered before this callback, so any
                       drawing done here will appear on top of the map.
        """
        while True:
            dt = self._clock.tick(self._fps) / 1000.0
            self._internals.dt = dt
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            if self._internals.tilemap:
                self._internals.tilemap.update(dt)
            
            self._internals.camera.update(dt)
            
            self._screen.fill((0, 0, 0))
            
            if self._internals.tilemap:
                self._internals.tilemap.render(
                    self._screen,
                    self._internals.camera.offset
                )
            
            game_loop(self._internals)
            
            pygame.display.flip()
