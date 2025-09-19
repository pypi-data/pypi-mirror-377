"""
Core module for VirtualInput library
Contains base classes, exceptions, and shared utilities
"""

from .base_classes import BaseKeyboard, BaseMouse

from .exceptions import (
    VirtualInputError,
    PlatformNotSupportedError,
    KeyboardError,
    MouseError,
    InvalidKeycodeError,
    InvalidCoordinatesError,
    PermissionError
)
from .keycodes import (
    KeyCode,
    MouseButton,
    ScrollDirection,
    VALID_KEYS,
    VALID_MOUSE_BUTTONS,
    VALID_SCROLL_DIRECTIONS,
    MODIFIER_KEYS
)

# Import only the functions that actually exist in utils.py
from .utils import (
    get_platform,
    validate_coordinates,
    normalize_keycode,
    validate_mouse_button,
    validate_scroll_direction,
    parse_hotkey_combination,
    get_screen_size,
    generate_typing_delays,
    calculate_movement_speed,
    add_mouse_tremor,
    calculate_distance,
    interpolate_linear,
    generate_human_like_path,
    validate_duration,
    normalize_angle,
    is_point_in_rect,
    clamp_coordinates
)

__all__ = [
    # Base classes
    'BaseKeyboard',
    'BaseMouse',
    
    # Exceptions
    'VirtualInputError',
    'PlatformNotSupportedError',
    'KeyboardError',
    'MouseError',
    'InvalidKeycodeError',
    'InvalidCoordinatesError',
    'PermissionError',
    
    # Key and button constants
    'KeyCode',
    'MouseButton',
    'ScrollDirection',
    'VALID_KEYS',
    'VALID_MOUSE_BUTTONS',
    'VALID_SCROLL_DIRECTIONS',
    'MODIFIER_KEYS',
    
    # Utility functions
    'get_platform',
    'validate_coordinates',
    'normalize_keycode',
    'validate_mouse_button',
    'validate_scroll_direction',
    'parse_hotkey_combination',
    'get_screen_size',
    'generate_typing_delays',
    'calculate_movement_speed',
    'add_mouse_tremor',
    'calculate_distance',
    'interpolate_linear',
    'generate_human_like_path',
    'validate_duration',
    'normalize_angle',
    'is_point_in_rect',
    'clamp_coordinates'
]