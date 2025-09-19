"""
VirtualInput - Cross-platform virtual keyboard and mouse library
"""

"""
VirtualInput - Cross-platform virtual mouse and keyboard library

A professional-grade automation library featuring:
- Ghost mouse technology (negative coordinates support)
- Bézier curve movements for human-like behavior
- Cross-platform compatibility (Windows, macOS)
- Input recording and playback capabilities
- Kernel-level system integration

Example usage:
    from virtualinput import VirtualMouse, VirtualKeyboard
    
    mouse = VirtualMouse()
    keyboard = VirtualKeyboard()
    
    # Ghost mouse movement
    mouse.move(-100, 200)  # Off-screen coordinates
    
    # Human-like curved movement
    mouse.move_bezier(500, 300, duration=1.5, curve_intensity=0.4)
    
    # Natural typing
    keyboard.type("Hello, World!")
    keyboard.hotkey("ctrl", "c")
"""

__version__ = "1.0.0"
__author__="off.rkv"
__license__ = "rkv's workshope"
__description__ = "Cross-platform virtual mouse and keyboard with ghost coordinates and Bézier curves"

# Main classes - these are what users will import
from .mouse import VirtualMouse
from .keyboard import VirtualKeyboard
from .recorder import InputRecorder, Macro

# Core components for advanced users
from .core.keycodes import KeyCode, MouseButton, ScrollDirection
from .core.exceptions import (
    VirtualInputError, 
    PlatformNotSupportedError, 
    MouseError, 
    KeyboardError,
    InvalidKeycodeError,
    InvalidCoordinatesError
)

# Utility functions for convenience
from .core.utils import get_platform, get_screen_size

# Make these available at package level
__all__ = [
    # Main classes
    'VirtualMouse',
    'VirtualKeyboard', 
    'InputRecorder',
    'Macro',
    
    # Constants
    'KeyCode',
    'MouseButton',
    'ScrollDirection',
    
    # Exceptions
    'VirtualInputError',
    'PlatformNotSupportedError',
    'MouseError',
    'KeyboardError',
    'InvalidKeycodeError',
    'InvalidCoordinatesError',
    
    # Utilities
    'get_platform',
    'get_screen_size',
    
    # Convenience functions
    'quick_click',
    'quick_type',
    'quick_hotkey',
]

# Convenience functions for quick operations
def quick_click(x: int, y: int, button: str = 'left', use_bezier: bool = True) -> bool:
    """
    Quick function to click at coordinates without creating mouse instance
    
    Args:
        x, y: Coordinates to click at
        button: Mouse button to click
        use_bezier: Use curved movement
        
    Returns:
        bool: True if successful
        
    Example:
        import virtualinput
        virtualinput.quick_click(500, 300)
    """
    try:
        mouse = VirtualMouse()
        return mouse.click_at(x, y, button, use_bezier)
    except Exception:
        return False

def quick_type(text: str, delay: float = 0.01) -> bool:
    """
    Quick function to type text without creating keyboard instance
    
    Args:
        text: Text to type
        delay: Delay between keystrokes
        
    Returns:
        bool: True if successful
        
    Example:
        import virtualinput
        virtualinput.quick_type("Hello, World!")
    """
    try:
        keyboard = VirtualKeyboard()
        return keyboard.type(text, delay)
    except Exception:
        return False

def quick_hotkey(*keys: str) -> bool:
    """
    Quick function to send hotkey without creating keyboard instance
    
    Args:
        *keys: Keys to press simultaneously
        
    Returns:
        bool: True if successful
        
    Example:
        import virtualinput
        virtualinput.quick_hotkey("ctrl", "c")
    """
    try:
        keyboard = VirtualKeyboard()
        return keyboard.hotkey(*keys)
    except Exception:
        return False

# Library information
def get_version() -> str:
    """Get library version"""
    return __version__

def get_platform_info() -> dict:
    """Get detailed platform information"""
    import platform as plt
    
    return {
        'library_version': __version__,
        'python_version': plt.python_version(),
        'platform': plt.system(),
        'platform_release': plt.release(),
        'architecture': plt.machine(),
        'processor': plt.processor(),
        'supported_platforms': ['Windows', 'macOS'],
        'features': [
            'Ghost coordinates',
            'Bézier curves', 
            'Cross-platform',
            'Input recording',
            'Macro creation'
        ]
    }

# Startup message (optional, can be disabled)
import os
if os.environ.get('VIRTUALINPUT_QUIET') != '1':
    print(f"VirtualInput v{__version__} - Ghost Mouse & Bézier Curves Ready")
    print(f"Platform: {get_platform()}")
    
# Cleanup
del os