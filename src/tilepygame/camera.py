from __future__ import annotations


class Camera:
    """
    Camera for smooth following and bounded scrolling.
    
    The camera tracks a target position and smoothly interpolates toward it.
    Bounds can be set to prevent the camera from showing areas outside the map.
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize the camera.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        self.x: float = 0.0
        self.y: float = 0.0
        self.width = width
        self.height = height
        self.zoom: float = 1.0
        self.min_zoom: float = 1.0
        self.max_zoom: float = 4.0
        self.zoom_speed: float = 0.25
        self.scroll_zoom_enabled: bool = True
        self.bounds: tuple[float, float, float, float] | None = None
        self.smoothing: float = 0.1
        
        self._target_x: float = 0.0
        self._target_y: float = 0.0
        self._follow_x: float = 0.0
        self._follow_y: float = 0.0
    
    @property
    def view_width(self) -> float:
        """Effective viewport width accounting for zoom."""
        return self.width / self.zoom
    
    @property
    def view_height(self) -> float:
        """Effective viewport height accounting for zoom."""
        return self.height / self.zoom
    
    def follow(self, target_x: float, target_y: float) -> None:
        """
        Set the target position for the camera to follow.
        
        The camera will center on this position (offset by half viewport).
        
        Args:
            target_x: Target world x coordinate
            target_y: Target world y coordinate
        """
        self._follow_x = target_x
        self._follow_y = target_y
        self._update_target()
    
    def _update_target(self) -> None:
        """Recalculate camera target from followed position and current zoom."""
        self._target_x = self._follow_x - self.view_width / 2
        self._target_y = self._follow_y - self.view_height / 2
    
    def set_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        """
        Set world bounds to clamp the camera within.
        
        Args:
            min_x: Minimum x (usually 0)
            min_y: Minimum y (usually 0)
            max_x: Maximum x (usually map pixel width)
            max_y: Maximum y (usually map pixel height)
        """
        self.bounds = (min_x, min_y, max_x, max_y)
    
    def clear_bounds(self) -> None:
        """Remove camera bounds."""
        self.bounds = None
    
    def snap_to_target(self) -> None:
        """Instantly move camera to target position (no smoothing)."""
        self.x = self._target_x
        self.y = self._target_y
        self._clamp_to_bounds()
    
    def update(self, dt: float) -> None:
        """
        Update camera position with smoothing.
        
        Args:
            dt: Delta time in seconds
        """
        smoothing_factor = 1.0 - (1.0 - self.smoothing) ** (dt * 60)
        
        self.x += (self._target_x - self.x) * smoothing_factor
        self.y += (self._target_y - self.y) * smoothing_factor
        
        self._clamp_to_bounds()
    
    def _clamp_to_bounds(self) -> None:
        """Clamp camera position to bounds if set."""
        if self.bounds is None:
            return
        
        min_x, min_y, max_x, max_y = self.bounds
        
        max_camera_x = max_x - self.view_width
        max_camera_y = max_y - self.view_height
        
        if max_camera_x < min_x:
            self.x = (min_x + max_x - self.view_width) / 2
        else:
            self.x = max(min_x, min(self.x, max_camera_x))
        
        if max_camera_y < min_y:
            self.y = (min_y + max_y - self.view_height) / 2
        else:
            self.y = max(min_y, min(self.y, max_camera_y))
    
    @property
    def offset(self) -> tuple[float, float]:
        """
        Get the current camera offset for rendering.
        
        Returns:
            (x, y) offset to subtract from world positions
        """
        return (self.x, self.y)

