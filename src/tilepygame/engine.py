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
            game_loop: A function that receives Internals and runs each frame
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
            
            game_loop(self._internals)
            
            self._internals.camera.update(dt)
            
            self._render()
    
    def _render(self) -> None:
        """Internal render method called each frame."""
        self._screen.fill((0, 0, 0))
        
        if self._internals.tilemap:
            self._internals.tilemap.render(
                self._screen,
                self._internals.camera.offset
            )
        
        pygame.display.flip()
