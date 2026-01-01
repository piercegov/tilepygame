from __future__ import annotations

import re
from pathlib import Path

import pygame


def load_spritesheet(
    source: str | pygame.Surface,
    frame_width: int,
    frame_height: int
) -> list[pygame.Surface]:
    """
    Load animation frames from a horizontal spritesheet.
    
    Args:
        source: Path to the spritesheet image or an existing pygame Surface
        frame_width: Width of each frame in pixels
        frame_height: Height of each frame in pixels
        
    Returns:
        List of pygame Surfaces, one per frame (left-to-right)
    """
    if isinstance(source, str):
        sheet = pygame.image.load(source).convert_alpha()
    else:
        sheet = source
    
    sheet_width = sheet.get_width()
    frames: list[pygame.Surface] = []
    
    x = 0
    while x + frame_width <= sheet_width:
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (x, 0, frame_width, frame_height))
        frames.append(frame)
        x += frame_width
    
    return frames


def _natural_sort_key(path: Path) -> tuple[int, str]:
    """Sort key that handles numeric filenames naturally (1, 2, 10 instead of 1, 10, 2)."""
    match = re.match(r"(\d+)", path.stem)
    if match:
        return (int(match.group(1)), path.stem)
    return (0, path.stem)


def load_frames_folder(path: str) -> list[pygame.Surface]:
    """
    Load animation frames from a folder of numbered images.
    
    Expects files like 01.png, 02.png, etc. or 1.png, 2.png, etc.
    Files are sorted numerically.
    
    Args:
        path: Path to folder containing frame images
        
    Returns:
        List of pygame Surfaces in numeric order
    """
    folder = Path(path)
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp"}
    
    image_files = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]
    image_files.sort(key=_natural_sort_key)
    
    return [pygame.image.load(str(f)).convert_alpha() for f in image_files]


def load_animations_folder(path: str) -> dict[str, list[pygame.Surface]]:
    """
    Load multiple animations from a directory structure.
    
    Expects a folder with subdirectories, where each subdirectory is an
    animation containing numbered frame images:
    
        path/
            idle/
                01.png
                02.png
            run/
                01.png
                02.png
                03.png
    
    Args:
        path: Path to the root folder containing animation subdirectories
        
    Returns:
        Dict mapping animation names to lists of frame Surfaces
    """
    folder = Path(path)
    animations: dict[str, list[pygame.Surface]] = {}
    
    for subdir in sorted(folder.iterdir()):
        if subdir.is_dir():
            animations[subdir.name] = load_frames_folder(str(subdir))
    
    return animations


class AnimatedSprite(pygame.sprite.Sprite):
    """
    A sprite with support for multiple named animations.
    
    Extends pygame.sprite.Sprite with animation playback capabilities.
    """
    
    def __init__(self) -> None:
        super().__init__()
        self._animations: dict[str, _Animation] = {}
        self._current_animation: str | None = None
        self._current_frame: int = 0
        self._elapsed: float = 0.0
        self._playing: bool = False
        
        self._image: pygame.Surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect: pygame.Rect = self._image.get_rect()
    
    @classmethod
    def from_folder(
        cls,
        path: str,
        frame_duration: float = 0.1,
        loop: bool = True
    ) -> AnimatedSprite:
        """
        Create an AnimatedSprite from a folder structure.
        
        Args:
            path: Path to folder with animation subdirectories
            frame_duration: Default duration per frame in seconds
            loop: Whether animations should loop by default
            
        Returns:
            New AnimatedSprite with all animations loaded
        """
        sprite = cls()
        animations = load_animations_folder(path)
        
        for name, frames in animations.items():
            sprite.add_animation(name, frames, frame_duration, loop)
        
        return sprite
    
    def add_animation(
        self,
        name: str,
        frames: list[pygame.Surface],
        frame_duration: float = 0.1,
        loop: bool = True
    ) -> None:
        """
        Add a named animation.
        
        Args:
            name: Name to identify this animation
            frames: List of pygame Surfaces for each frame
            frame_duration: Time per frame in seconds
            loop: Whether the animation should loop
        """
        self._animations[name] = _Animation(
            frames=frames,
            frame_duration=frame_duration,
            loop=loop
        )
        
        if self._current_animation is None and frames:
            self._current_animation = name
            self._image = frames[0]
            self.rect = self._image.get_rect(topleft=self.rect.topleft)
    
    def play(self, name: str, restart: bool = False) -> None:
        """
        Play a named animation.
        
        Args:
            name: Name of the animation to play
            restart: If True, restart from frame 0 even if already playing this animation
        """
        if name not in self._animations:
            return
        
        if name != self._current_animation or restart:
            self._current_animation = name
            self._current_frame = 0
            self._elapsed = 0.0
            self._update_image()
        
        self._playing = True
    
    def stop(self) -> None:
        """Stop the current animation."""
        self._playing = False
    
    def update(self, dt: float) -> None:
        """
        Update the animation state.
        
        Args:
            dt: Delta time in seconds since last update
        """
        if not self._playing or self._current_animation is None:
            return
        
        anim = self._animations.get(self._current_animation)
        if anim is None or not anim.frames:
            return
        
        self._elapsed += dt
        
        while self._elapsed >= anim.frame_duration:
            self._elapsed -= anim.frame_duration
            self._current_frame += 1
            
            if self._current_frame >= len(anim.frames):
                if anim.loop:
                    self._current_frame = 0
                else:
                    self._current_frame = len(anim.frames) - 1
                    self._playing = False
                    break
        
        self._update_image()
    
    def _update_image(self) -> None:
        """Update the image Surface to the current frame."""
        if self._current_animation is None:
            return
        
        anim = self._animations.get(self._current_animation)
        if anim is None or not anim.frames:
            return
        
        old_center = self.rect.center
        self._image = anim.frames[self._current_frame]
        self.rect = self._image.get_rect(center=old_center)
    
    @property
    def image(self) -> pygame.Surface:
        """The current frame Surface."""
        return self._image
    
    @property
    def current_animation(self) -> str | None:
        """Name of the current animation, or None if no animation is set."""
        return self._current_animation
    
    @property
    def is_playing(self) -> bool:
        """Whether an animation is currently playing."""
        return self._playing


class _Animation:
    """Internal class to store animation data."""
    
    __slots__ = ("frames", "frame_duration", "loop")
    
    def __init__(
        self,
        frames: list[pygame.Surface],
        frame_duration: float,
        loop: bool
    ) -> None:
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop

