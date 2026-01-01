from dataclasses import dataclass
import pygame
from typing import Callable
import sys

@dataclass
class Internals:
    width: int
    height: int

class Game:
    def __init__(self, width: int = 800, height: int = 600):
        self._internals = Internals(width=width, height=height)
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Tile-based Game")

    # How should we handle the game loop?
    # Users of the framework should be able to define their own game loop, but some things are common.
    # e.g. rendering the tilemap, handling input, etc.
    def run(self, game_loop: Callable[[Internals], None]):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            game_loop(self._internals)

            self.render()

    def render(self):
        self._screen.fill((0, 0, 0))
        pygame.display.flip()

        # Will render the tilemap to the screen