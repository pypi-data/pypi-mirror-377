"""
Utility functions shared across all platform implementations
"""

import platform
import re
import time
import math
import random
from typing import Tuple, List, Union
from .exceptions import InvalidCoordinatesError, InvalidKeycodeError
from .keycodes import VALID_KEYS, VALID_SCROLL_DIRECTIONS, VALID_MOUSE_BUTTONS

def get_platform() -> str:
    """
    Get the current platform in a normalized format

    Returns:
        str: 'windows', 'macos', or 'linux'
    """
    system = platform.system().lower()

    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unknown'
    
def validate_coordinates(x: Union[int, float], y: Union[int, float]) -> Tuple[int, int]:
    """
    Validate and normalize screen coordinates
    Ghost mouse - no restrictions!

    Args:
        x: X coordinate
        y: Y coordinate
    
    Returns:
        Tuple[int, int]: validated (x, y) coordinates
    
    Raises:
        InvalidCoordinatesError: If coordinates are invalid
    """
    try:
        x = int(x)
        y = int(y)

        # No restrictions whatsoever - let the ghost mouse roam free!
        return (x, y)

    except (ValueError, TypeError):
        raise InvalidCoordinatesError((x, y))
    
def normalize_keycode(keycode: str) -> str:
    """
    Normalize a keycode to standard format

    Args:
        keycode: The keycode to normalize
    
    Returns:
        str: Normalized keycode
    
    Raises:
        InvalidKeycodeError: If keycode is invalid
    """
    if not isinstance(keycode, str):
        raise InvalidKeycodeError(str(keycode))
    
    normalized = keycode.lower().strip()

    # Handle common aliases
    aliases = {
        'return': 'enter',
        'esc': 'escape',
        'control': 'ctrl',
        'command': 'cmd',
        'windows': 'win',
        'wheel': 'middle',
        'back': 'x1',
        'forward': 'x2'
    }

    normalized = aliases.get(normalized, normalized)
    
    # Validate the keycode
    if normalized not in VALID_KEYS:
        raise InvalidKeycodeError(keycode)
    
    return normalized

def validate_mouse_button(button: str) -> str:
    """
    Validate and normalize mouse button name
    
    Args:
        button: The button name to validate
        
    Returns:
        str: Normalized button name
        
    Raises:
        ValueError: If button name is invalid
    """
    if not isinstance(button, str):
        raise ValueError(f"Button must be a string, got {type(button)}")
    
    normalized = button.lower().strip()
    
    if normalized not in VALID_MOUSE_BUTTONS:
        raise ValueError(f"Invalid mouse button: '{button}'. Valid buttons: {VALID_MOUSE_BUTTONS}")
    
    return normalized

def validate_scroll_direction(direction: str) -> str:
    """
    Validate and normalize scroll direction
    
    Args:
        direction: The scroll direction to validate
        
    Returns:
        str: Normalized direction
        
    Raises:
        ValueError: If direction is invalid
    """
    if not isinstance(direction, str):
        raise ValueError(f"Direction must be a string, got {type(direction)}")
    
    normalized = direction.lower().strip()
    
    if normalized not in VALID_SCROLL_DIRECTIONS:
        raise ValueError(f"Invalid scroll direction: '{direction}'. Valid directions: {VALID_SCROLL_DIRECTIONS}")
    
    return normalized

def parse_hotkey_combination(hotkey_string: str) -> List[str]:
    """
    Parse a hotkey string like "ctrl+c" into individual keys
    
    Args:
        hotkey_string: String like "ctrl+c", "cmd+shift+a", etc.
        
    Returns:
        List[str]: List of individual normalized keycodes
        
    Raises:
        InvalidKeycodeError: If any key in the combination is invalid
    """
    if not isinstance(hotkey_string, str):
        raise InvalidKeycodeError(str(hotkey_string))
    
    # Split by + and normalize each key
    keys = []
    for key in hotkey_string.split('+'):
        normalized_key = normalize_keycode(key.strip())
        keys.append(normalized_key)
    
    return keys

def get_screen_size() -> Tuple[int, int]:
    """
    Get screen resolution
    Cross-platform implementation using tkinter
    
    Returns:
        Tuple[int, int]: (width, height) in pixels
    """
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return (width, height)
    except ImportError:
        # Fallback if tkinter is not available
        return (1920, 1080)

def clamp_coordinates(x: int, y: int, screen_width: int = None, screen_height: int = None) -> Tuple[int, int]:
    """
    Clamp coordinates to screen boundaries
    Note: For ghost mouse, DON'T want to use this function
    
    Args:
        x: X coordinate
        y: Y coordinate
        screen_width: Screen width (auto-detected if None)
        screen_height: Screen height (auto-detected if None)
        
    Returns:
        Tuple[int, int]: Clamped coordinates
    """
    if screen_width is None or screen_height is None:
        screen_width, screen_height = get_screen_size()
    
    x = max(0, min(x, screen_width - 1))
    y = max(0, min(y, screen_height - 1))
    
    return (x, y)

def generate_typing_delays(text: str, base_delay: float = 0.05) -> List[float]:
    """
    Generate realistic typing delays for natural text input
    
    Args:
        text: The text that will be typed
        base_delay: Base delay between keystrokes
        
    Returns:
        List[float]: List of delays for each character
    """
    delays = []
    
    for i, char in enumerate(text):
        delay = base_delay
        
        # Longer delays after punctuation
        if i > 0 and text[i-1] in '.!?':
            delay *= 3
        
        # Shorter delays for common letter combinations
        if i > 0 and char.isalpha() and text[i-1].isalpha():
            delay *= 0.8
        
        # Add some randomness
        delay *= random.uniform(0.7, 1.3)
        
        delays.append(delay)
    
    return delays

def calculate_movement_speed(distance: float, human_factor: float = 0.5) -> float:
    """
    Calculate realistic movement duration based on distance and human behavior
    
    Args:
        distance: Distance to travel in pixels
        human_factor: How human-like the speed should be (0.0 = robot, 1.0 = very human)
        
    Returns:
        Duration in seconds
    """
    # Base speed: humans move at roughly 1000-2000 pixels per second
    base_speed = 1500  # pixels per second
    
    # Shorter movements are proportionally slower (human acceleration)
    if distance < 100:
        base_speed *= 0.6
    elif distance > 500:
        base_speed *= 1.3
    
    # Add human variation
    speed_variation = random.uniform(0.7, 1.4) if human_factor > 0.3 else 1.0
    actual_speed = base_speed * speed_variation
    
    # Calculate duration
    duration = distance / actual_speed
    
    # Minimum and maximum bounds
    return max(0.1, min(3.0, duration))

def add_mouse_tremor(x: int, y: int, intensity: float = 0.5) -> Tuple[int, int]:
    """
    Add slight tremor to mouse coordinates for human-like behavior
    
    Args:
        x, y: Original coordinates
        intensity: Tremor strength (0.0 = none, 1.0 = noticeable)
        
    Returns:
        Adjusted (x, y) coordinates
    """
    if intensity <= 0:
        return (x, y)
    
    # Very small random offsets
    tremor_x = random.randint(-int(intensity * 2), int(intensity * 2))
    tremor_y = random.randint(-int(intensity * 2), int(intensity * 2))
    
    return (x + tremor_x, y + tremor_y)

def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """
    Calculate Euclidean distance between two points
    
    Args:
        x1, y1: First point coordinates
        x2, y2: Second point coordinates
        
    Returns:
        float: Distance in pixels
    """
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def interpolate_linear(start_x: int, start_y: int, end_x: int, end_y: int, 
                      t: float) -> Tuple[int, int]:
    """
    Linear interpolation between two points
    
    Args:
        start_x, start_y: Start point
        end_x, end_y: End point  
        t: Interpolation factor (0.0 = start, 1.0 = end)
        
    Returns:
        Tuple[int, int]: Interpolated coordinates
    """
    x = int(start_x + (end_x - start_x) * t)
    y = int(start_y + (end_y - start_y) * t)
    return (x, y)

def generate_human_like_path(start_x: int, start_y: int, end_x: int, end_y: int,
                           human_factor: float = 0.1) -> List[Tuple[int, int]]:
    """
    Generate a more complex human-like path with multiple waypoints
    
    Args:
        start_x, start_y: Starting coordinates
        end_x, end_y: Ending coordinates
        human_factor: How "human" the movement should be (0.0 = robot, 1.0 = very human)
        
    Returns:
        List of (x, y) coordinates as waypoints
    """
    waypoints = []
    distance = calculate_distance(start_x, start_y, end_x, end_y)
    
    if distance > 200 and human_factor > 0.3:
        # Add 1-2 intermediate waypoints for very human-like movement
        
        # Add a waypoint about 1/3 of the way
        wp1_x = start_x + int((end_x - start_x) * 0.3) + random.randint(-20, 20)
        wp1_y = start_y + int((end_y - start_y) * 0.3) + random.randint(-20, 20)
        waypoints.append((wp1_x, wp1_y))
        
        if distance > 400:  # Very long movement, add second waypoint
            wp2_x = start_x + int((end_x - start_x) * 0.7) + random.randint(-15, 15)
            wp2_y = start_y + int((end_y - start_y) * 0.7) + random.randint(-15, 15)
            waypoints.append((wp2_x, wp2_y))
    
    return waypoints

def validate_duration(duration: float, min_duration: float = 0.1, max_duration: float = 10.0) -> float:
    """
    Validate and clamp duration values
    
    Args:
        duration: Duration to validate
        min_duration: Minimum allowed duration
        max_duration: Maximum allowed duration
        
    Returns:
        float: Clamped duration
    """
    return max(min_duration, min(duration, max_duration))

def normalize_angle(angle: float) -> float:
    """
    Normalize an angle to the range [0, 2π]
    
    Args:
        angle: Angle in radians
        
    Returns:
        float: Normalized angle
    """
    return angle % (2 * math.pi)

def is_point_in_rect(x: int, y: int, rect_x: int, rect_y: int, 
                    rect_width: int, rect_height: int) -> bool:
    """
    Check if a point is inside a rectangle
    
    Args:
        x, y: Point coordinates
        rect_x, rect_y: Rectangle top-left corner
        rect_width, rect_height: Rectangle dimensions
        
    Returns:
        bool: True if point is inside rectangle
    """
    return (rect_x <= x <= rect_x + rect_width and 
            rect_y <= y <= rect_y + rect_height)