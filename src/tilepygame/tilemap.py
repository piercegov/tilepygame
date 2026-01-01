from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Any

import pygame
from pytmx.util_pygame import load_pygame
from pytmx import TiledMap, TiledObjectGroup, TiledTileLayer


@dataclass
class MapObject:
    """Represents a Tiled object (collision box, spawn point, trigger, etc.)."""
    name: str
    type: str
    x: float
    y: float
    width: float
    height: float
    properties: dict[str, Any]
    
    @property
    def rect(self) -> pygame.Rect:
        """Get a pygame Rect for this object."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class TileMap:
    """
    Wrapper around pytmx for loading and rendering Tiled maps.
    
    Supports:
    - Multiple tile layers
    - Object layers (collision, spawn points, triggers)
    - Tile animations
    - Custom properties on tiles, objects, and layers
    """
    
    def __init__(self, path: str):
        """
        Load a Tiled map from a TMX file.
        
        Args:
            path: Path to the .tmx file
        """
        self._tmx: TiledMap = load_pygame(path)
        self._animation_time: float = 0.0
    
    @property
    def width(self) -> int:
        """Map width in tiles."""
        return self._tmx.width
    
    @property
    def height(self) -> int:
        """Map height in tiles."""
        return self._tmx.height
    
    @property
    def tile_width(self) -> int:
        """Width of each tile in pixels."""
        return self._tmx.tilewidth
    
    @property
    def tile_height(self) -> int:
        """Height of each tile in pixels."""
        return self._tmx.tileheight
    
    @property
    def pixel_width(self) -> int:
        """Total map width in pixels."""
        return self.width * self.tile_width
    
    @property
    def pixel_height(self) -> int:
        """Total map height in pixels."""
        return self.height * self.tile_height
    
    def update(self, dt: float) -> None:
        """
        Update tile animations.
        
        Args:
            dt: Delta time in seconds since last update
        """
        self._animation_time += dt
    
    def render(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[float, float] = (0, 0),
        layers: list[str] | None = None
    ) -> None:
        """
        Render the tilemap to a surface.
        
        Args:
            surface: The pygame surface to render to
            camera_offset: (x, y) offset for camera scrolling
            layers: Optional list of layer names to render. If None, renders all visible tile layers.
        """
        offset_x, offset_y = camera_offset
        
        for layer in self._tmx.visible_layers:
            if not isinstance(layer, TiledTileLayer):
                continue
            
            if layers is not None and layer.name not in layers:
                continue
            
            for x, y, surface_img in layer.tiles():
                if surface_img is None:
                    continue
                
                pos_x = x * self.tile_width - offset_x
                pos_y = y * self.tile_height - offset_y
                
                surface.blit(surface_img, (pos_x, pos_y))
    
    def render_layer(
        self,
        surface: pygame.Surface,
        layer_name: str,
        camera_offset: tuple[float, float] = (0, 0)
    ) -> None:
        """
        Render a specific tile layer.
        
        Args:
            surface: The pygame surface to render to
            layer_name: Name of the layer to render
            camera_offset: (x, y) offset for camera scrolling
        """
        self.render(surface, camera_offset, layers=[layer_name])
    
    def draw_grid(
        self,
        surface: pygame.Surface,
        camera_offset: tuple[float, float] = (0, 0),
        color: tuple[int, int, int, int] = (255, 255, 255, 60)
    ) -> None:
        """
        Draw tile border grid for visualization.
        
        Args:
            surface: The pygame surface to render to
            camera_offset: (x, y) offset for camera scrolling
            color: RGBA color tuple for grid lines
        """
        tw = self.tile_width
        th = self.tile_height
        cam_x, cam_y = camera_offset
        screen_w, screen_h = surface.get_size()

        start_tile_x = max(0, int(cam_x // tw))
        start_tile_y = max(0, int(cam_y // th))
        end_tile_x = min(self.width, int((cam_x + screen_w) // tw) + 1)
        end_tile_y = min(self.height, int((cam_y + screen_h) // th) + 1)

        grid_surface = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

        for tx in range(start_tile_x, end_tile_x + 1):
            screen_x = int(tx * tw - cam_x)
            pygame.draw.line(grid_surface, color, (screen_x, 0), (screen_x, screen_h))

        for ty in range(start_tile_y, end_tile_y + 1):
            screen_y = int(ty * th - cam_y)
            pygame.draw.line(grid_surface, color, (0, screen_y), (screen_w, screen_y))

        surface.blit(grid_surface, (0, 0))
    
    def get_layer_names(self) -> list[str]:
        """Get names of all layers in the map."""
        return [layer.name for layer in self._tmx.layers]
    
    def get_tile_layer_names(self) -> list[str]:
        """Get names of all tile layers."""
        return [
            layer.name for layer in self._tmx.layers
            if isinstance(layer, TiledTileLayer)
        ]
    
    def get_object_layer_names(self) -> list[str]:
        """Get names of all object layers."""
        return [
            layer.name for layer in self._tmx.layers
            if isinstance(layer, TiledObjectGroup)
        ]
    
    def get_objects(self, layer_name: str) -> Iterator[MapObject]:
        """
        Get all objects from an object layer.
        
        Args:
            layer_name: Name of the object layer
            
        Yields:
            MapObject instances for each object in the layer
        """
        layer = self._tmx.get_layer_by_name(layer_name)
        
        if not isinstance(layer, TiledObjectGroup):
            return
        
        for obj in layer:
            yield MapObject(
                name=obj.name or "",
                type=obj.type or "",
                x=obj.x,
                y=obj.y,
                width=obj.width or 0,
                height=obj.height or 0,
                properties=dict(obj.properties) if obj.properties else {}
            )
    
    def get_objects_by_type(self, layer_name: str, obj_type: str) -> Iterator[MapObject]:
        """
        Get objects of a specific type from an object layer.
        
        Args:
            layer_name: Name of the object layer
            obj_type: Type of objects to filter by
            
        Yields:
            MapObject instances matching the specified type
        """
        for obj in self.get_objects(layer_name):
            if obj.type == obj_type:
                yield obj
    
    def get_object_by_name(self, layer_name: str, name: str) -> MapObject | None:
        """
        Get a specific object by name.
        
        Args:
            layer_name: Name of the object layer
            name: Name of the object to find
            
        Returns:
            MapObject if found, None otherwise
        """
        for obj in self.get_objects(layer_name):
            if obj.name == name:
                return obj
        return None
    
    def get_tile_properties(
        self,
        x: int,
        y: int,
        layer_name: str
    ) -> dict[str, Any] | None:
        """
        Get custom properties for a tile at a specific position.
        
        Args:
            x: Tile x coordinate
            y: Tile y coordinate
            layer_name: Name of the tile layer
            
        Returns:
            Dictionary of properties, or None if no tile/properties exist
        """
        layer = self._tmx.get_layer_by_name(layer_name)
        
        if not isinstance(layer, TiledTileLayer):
            return None
        
        gid = layer.data[y][x]
        if gid == 0:
            return None
        
        props = self._tmx.get_tile_properties_by_gid(gid)
        return dict(props) if props else None
    
    def get_tile_gid(self, x: int, y: int, layer_name: str) -> int:
        """
        Get the tile GID at a specific position.
        
        Args:
            x: Tile x coordinate
            y: Tile y coordinate
            layer_name: Name of the tile layer
            
        Returns:
            Tile GID (0 means empty)
        """
        layer = self._tmx.get_layer_by_name(layer_name)
        
        if not isinstance(layer, TiledTileLayer):
            return 0
        
        return layer.data[y][x]
    
    def get_layer_properties(self, layer_name: str) -> dict[str, Any]:
        """
        Get custom properties for a layer.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            Dictionary of properties
        """
        layer = self._tmx.get_layer_by_name(layer_name)
        return dict(layer.properties) if layer and layer.properties else {}
    
    def get_collision_rects(self, layer_name: str = "Collisions") -> list[pygame.Rect]:
        """
        Convenience method to get all collision rectangles from an object layer.
        
        Args:
            layer_name: Name of the collision object layer
            
        Returns:
            List of pygame Rect objects
        """
        return [obj.rect for obj in self.get_objects(layer_name)]

