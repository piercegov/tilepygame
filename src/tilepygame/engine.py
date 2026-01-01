from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import sys

import pygame

from .tilemap import TileMap


@dataclass
class Internals:
    """Game state passed to the game loop each frame."""
    width: int
    height: int
    screen: pygame.Surface
    dt: float = 0.0
    camera_offset: tuple[float, float] = (0, 0)


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
        self._tilemap: TileMap | None = None
        
        self._internals = Internals(
            width=width,
            height=height,
            screen=self._screen
        )
    
    @property
    def tilemap(self) -> TileMap | None:
        """The currently loaded tilemap."""
        return self._tilemap
    
    def load_tilemap(self, path: str) -> TileMap:
        """
        Load a Tiled map from a TMX file.
        
        Args:
            path: Path to the .tmx file
            
        Returns:
            The loaded TileMap instance
        """
        self._tilemap = TileMap(path)
        return self._tilemap
    
    def set_camera_offset(self, x: float, y: float) -> None:
        """
        Set the camera offset for tilemap rendering.
        
        Args:
            x: Camera x offset
            y: Camera y offset
        """
        self._internals.camera_offset = (x, y)
    
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
            
            if self._tilemap:
                self._tilemap.update(dt)
            
            game_loop(self._internals)
            
            self._render()
    
    def _render(self) -> None:
        """Internal render method called each frame."""
        self._screen.fill((0, 0, 0))
        
        if self._tilemap:
            self._tilemap.render(self._screen, self._internals.camera_offset)
        
        pygame.display.flip()
