"""
Main mouse interface that automatically detects platform and uses appropriate implementation
"""

import platform
from .core.base_classes import BaseMouse
from .core.exceptions import PlatformNotSupportedError, MouseError
from .core.keycodes import MouseButton
from typing import Tuple, List
import time

class VirtualMouse:
    """
    Cross-platform virtual mouse with ghost coordinate support and Bézier curves
    Automatically detects your operating system and uses the appropriate implementation
    """
    
    def __init__(self):
        """Initialize the mouse with platform-specific implementation"""
        self._implementation = self._get_platform_implementation()
    
    def _get_platform_implementation(self) -> BaseMouse:
        """
        Get the appropriate mouse implementation for the current platform
        
        Returns:
            BaseMouse: Platform-specific mouse implementation
            
        Raises:
            PlatformNotSupportedError: If platform is not supported
        """
        system = platform.system()
        
        if system == "Windows":
            try:
                from .platforms.windows.mouse import WindowsMouse
                return WindowsMouse()
            except ImportError as e:
                raise PlatformNotSupportedError(f"Windows mouse implementation failed: {e}")
        
        elif system == "Darwin":  # macOS
            try:
                from .platforms.macos.mouse import MacOSMouse
                return MacOSMouse()
            except ImportError as e:
                raise PlatformNotSupportedError(f"macOS mouse implementation failed. Install pyobjc: pip install pyobjc")
        
        else:
            raise PlatformNotSupportedError(f"Platform '{system}' is not supported yet. Supported platforms: Windows, macOS")
    
    def move(self, x: int, y: int) -> bool:
        """
        Move mouse to absolute coordinates
        GHOST MOUSE: Supports negative coordinates and off-screen positions!
        
        Args:
            x: X coordinate (can be negative for off-screen/hidden areas)
            y: Y coordinate (can be negative for off-screen/hidden areas)
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            mouse.move(500, 300)    # Normal screen position
            mouse.move(-100, 200)   # Ghost position (hidden off-screen left)
            mouse.move(2000, 400)   # Off-screen right
        """
        return self._implementation.move(x, y)
    
    def move_relative(self, dx: int, dy: int) -> bool:
        """
        Move mouse relative to current position
        
        Args:
            dx: Change in X position (positive = right, negative = left)
            dy: Change in Y position (positive = down, negative = up)
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            mouse.move_relative(50, 0)    # Move 50 pixels right
            mouse.move_relative(-25, 100) # Move 25 pixels left, 100 pixels down
        """
        return self._implementation.move_relative(dx, dy)
    
    def move_bezier(self, end_x: int, end_y: int, duration: float = 1.0, 
                   curve_intensity: float = 0.3) -> bool:
        """
        Move mouse in a human-like curved path using quadratic Bézier curves
        Works with ghost coordinates!
        
        Args:
            end_x: Target X coordinate (supports negative/ghost coordinates)
            end_y: Target Y coordinate (supports negative/ghost coordinates)
            duration: Time to complete movement in seconds
            curve_intensity: How curved the path should be (0.0 = straight, 1.0 = very curved)
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            mouse.move_bezier(500, 300)                           # Natural curve
            mouse.move_bezier(-200, 400, duration=2.0)           # Ghost destination with slow movement
            mouse.move_bezier(800, 200, curve_intensity=0.8)     # Very curved path
        """
        return self._implementation.move_bezier(end_x, end_y, duration, curve_intensity)
    
    def move_bezier_relative(self, dx: int, dy: int, duration: float = 1.0, 
                            curve_intensity: float = 0.3) -> bool:
        """
        Move mouse relatively using Bézier curve
        
        Args:
            dx: Relative X movement
            dy: Relative Y movement
            duration: Time to complete movement in seconds
            curve_intensity: Curve strength
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self._implementation.move_bezier_relative(dx, dy, duration, curve_intensity)
    
    def click(self, button: str = 'left') -> bool:
        """
        Click mouse button at current position
        
        Args:
            button: Which button to click ('left', 'right', 'middle')
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            mouse.click()                    # Left click
            mouse.click('right')             # Right click
            mouse.click(MouseButton.MIDDLE)  # Middle click using constant
        """
        return self._implementation.click(button)
    
    def double_click(self, button: str = 'left') -> bool:
        """
        Double-click mouse button at current position
        
        Args:
            button: Which button to double-click
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self._implementation.double_click(button)
    
    def press_and_hold(self, button: str = 'left') -> bool:
        """
        Press and hold mouse button
        
        Args:
            button: Which button to hold down
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            mouse.press_and_hold('left')
            # Move mouse while holding button (drag operation)
            mouse.move(400, 300)
            mouse.release('left')
        """
        return self._implementation.press_and_hold(button)
    
    def release(self, button: str = 'left') -> bool:
        """
        Release held mouse button
        
        Args:
            button: Which button to release
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self._implementation.release(button)
    
    def scroll(self, direction: str, clicks: int = 1) -> bool:
        """
        Scroll mouse wheel
        
        Args:
            direction: 'up' or 'down'
            clicks: Number of scroll clicks
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            mouse.scroll('up', 3)      # Scroll up 3 clicks
            mouse.scroll('down')       # Scroll down 1 click
        """
        return self._implementation.scroll(direction, clicks)
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get current mouse cursor position
        Works with ghost coordinates - can return negative values!
        
        Returns:
            Tuple[int, int]: (x, y) coordinates
            
        Example:
            x, y = mouse.get_position()
            print(f"Mouse is at ({x}, {y})")
        """
        return self._implementation.get_position()
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
            button: str = 'left') -> bool:
        """
        Drag from one position to another (straight line)
        
        Args:
            start_x, start_y: Starting coordinates
            end_x, end_y: Ending coordinates
            button: Mouse button to use for dragging
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            mouse.drag(100, 100, 400, 300)      # Drag from (100,100) to (400,300)
            mouse.drag(-50, 200, 600, 400)     # Ghost drag starting off-screen
        """
        return self._implementation.drag(start_x, start_y, end_x, end_y, button)
    
    def drag_bezier(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                   button: str = 'left', duration: float = 1.0) -> bool:
        """
        Drag using smooth Bézier curve movement
        
        Args:
            start_x, start_y: Start coordinates
            end_x, end_y: End coordinates (supports ghost coordinates)
            button: Mouse button to use for dragging
            duration: Total drag duration
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            mouse.drag_bezier(100, 100, 500, 300, duration=2.0)    # Smooth curved drag
            mouse.drag_bezier(-100, 200, 400, 300)                 # Ghost start position
        """
        return self._implementation.drag_bezier(start_x, start_y, end_x, end_y, button, duration)
    
    def click_at(self, x: int, y: int, button: str = 'left', 
                use_bezier: bool = True, duration: float = 1.0) -> bool:
        """
        Move to coordinates and click (convenience method)
        
        Args:
            x, y: Coordinates to click at (supports ghost coordinates)
            button: Mouse button to click
            use_bezier: Use curved movement instead of straight line
            duration: Movement duration if using Bézier
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            mouse.click_at(500, 300)                           # Move and click with curve
            mouse.click_at(-100, 200, button='right')         # Ghost click
            mouse.click_at(400, 300, use_bezier=False)        # Straight line movement
        """
        try:
            # Move to position
            if use_bezier:
                success = self.move_bezier(x, y, duration)
            else:
                success = self.move(x, y)
            
            if not success:
                return False
            
            # Small delay before clicking
            time.sleep(0.05)
            
            # Click
            return self.click(button)
        except Exception:
            return False
    
    def double_click_at(self, x: int, y: int, button: str = 'left', 
                       use_bezier: bool = True, duration: float = 1.0) -> bool:
        """
        Move to coordinates and double-click
        
        Args:
            x, y: Coordinates to double-click at
            button: Mouse button to double-click
            use_bezier: Use curved movement
            duration: Movement duration if using Bézier
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Move to position
            if use_bezier:
                success = self.move_bezier(x, y, duration)
            else:
                success = self.move(x, y)
            
            if not success:
                return False
            
            # Small delay before clicking
            time.sleep(0.05)
            
            # Double-click
            return self.double_click(button)
        except Exception:
            return False
    
    def is_button_pressed(self, button: str) -> bool:
        """
        Check if mouse button is currently pressed
        
        Args:
            button: Button to check
            
        Returns:
            bool: True if button is pressed
        """
        return self._implementation.is_button_pressed(button)
    
    def get_pressed_buttons(self) -> set:
        """
        Get set of currently pressed buttons
        
        Returns:
            set: Set of currently pressed button names
        """
        return getattr(self._implementation, 'pressed_buttons', set()).copy()
    
    def stealth_click(self, x: int, y: int, button: str = 'left') -> bool:
        """
        Perform stealth click by moving to ghost area first, then to target
        This makes the movement less detectable
        
        Args:
            x, y: Target coordinates
            button: Button to click
            
        Returns:
            bool: True if successful
        """
        try:
            # Get current position
            current_x, current_y = self.get_position()
            
            # Move to ghost area first (off-screen)
            ghost_x = -50
            ghost_y = current_y
            self.move_bezier(ghost_x, ghost_y, duration=0.5, curve_intensity=0.2)
            
            # Small delay
            time.sleep(0.1)
            
            # Move to target with curve
            self.move_bezier(x, y, duration=0.8, curve_intensity=0.3)
            
            # Click
            time.sleep(0.05)
            return self.click(button)
        except Exception:
            return False
    
    def natural_scroll(self, direction: str, distance: int = 3, 
                      speed: float = 0.1) -> bool:
        """
        Scroll with natural human-like timing
        
        Args:
            direction: 'up' or 'down'
            distance: Total scroll distance
            speed: Delay between scroll clicks
            
        Returns:
            bool: True if successful
        """
        try:
            import random
            
            for i in range(distance):
                # Scroll one click
                success = self.scroll(direction, 1)
                if not success:
                    return False
                
                # Human-like delay variation
                delay = speed * random.uniform(0.7, 1.3)
                time.sleep(delay)
            
            return True
        except Exception:
            return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen dimensions
        
        Returns:
            Tuple[int, int]: (width, height) in pixels
        """
        return getattr(self._implementation, 'get_screen_size', lambda: (1920, 1080))()
    
    def get_platform_info(self) -> dict:
        """
        Get information about the current platform and implementation
        
        Returns:
            dict: Platform information
        """
        return {
            'platform': platform.system(),
            'implementation': type(self._implementation).__name__,
            'ghost_coordinates': True,
            'bezier_curves': True,
            'supported_features': [
                'move', 'move_relative', 'move_bezier', 'click', 'double_click',
                'press_and_hold', 'release', 'scroll', 'drag', 'drag_bezier',
                'ghost_coordinates', 'stealth_operations'
            ]
        }