"""
Windows platform implementation for VirtualInput library

This module provides Windows-specific implementations using Win32 API through ctypes.
Supports all VirtualInput features including ghost coordinates and Bézier curves.

Components:
- WindowsMouse: Mouse control using SetCursorPos and mouse_event
- WindowsKeyboard: Keyboard control using keybd_event and SendInput
- WindowsUtils: Advanced Windows features and utilities

Features:
- Ghost mouse coordinates (including negative values)
- Multi-monitor support with automatic coordinate handling
- Unicode text input support
- Window management capabilities
- System metrics access
- Kernel-level input injection for maximum compatibility

Requirements:
- Windows operating system
- Python with ctypes (built-in)
- No additional dependencies required
"""

import ctypes
import sys
from typing import Optional

# Verify Windows platform
if sys.platform != 'win32':
    raise ImportError("Windows implementation can only be used on Windows systems")

# Test ctypes availability
try:
    import ctypes.wintypes
    CTYPES_AVAILABLE = True
except ImportError:
    CTYPES_AVAILABLE = False
    raise ImportError("ctypes.wintypes not available - required for Windows implementation")

# Import Windows implementations
try:
    from .mouse import WindowsMouse
    MOUSE_AVAILABLE = True
except ImportError as e:
    MOUSE_AVAILABLE = False
    _mouse_error = str(e)

try:
    from .keyboard import WindowsKeyboard
    KEYBOARD_AVAILABLE = True
except ImportError as e:
    KEYBOARD_AVAILABLE = False
    _keyboard_error = str(e)

try:
    from .utils import WindowsUtils
    UTILS_AVAILABLE = True
except ImportError as e:
    UTILS_AVAILABLE = False
    _utils_error = str(e)

# Version and platform info
PLATFORM_VERSION = "1.0.0"
PLATFORM_NAME = "Windows"
API_USED = ["Win32 API", "user32.dll", "kernel32.dll"]

def get_implementation_status() -> dict:
    """
    Get status of Windows implementations
    
    Returns:
        dict: Status of each component
    """
    status = {
        'platform': PLATFORM_NAME,
        'version': PLATFORM_VERSION,
        'ctypes_available': CTYPES_AVAILABLE,
        'components': {
            'mouse': {
                'available': MOUSE_AVAILABLE,
                'error': _mouse_error if not MOUSE_AVAILABLE else None
            },
            'keyboard': {
                'available': KEYBOARD_AVAILABLE,
                'error': _keyboard_error if not KEYBOARD_AVAILABLE else None
            },
            'utils': {
                'available': UTILS_AVAILABLE,
                'error': _utils_error if not UTILS_AVAILABLE else None
            }
        },
        'features': [
            'Ghost coordinates',
            'Multi-monitor support',
            'Unicode input',
            'Bézier curves',
            'Window management',
            'System metrics'
        ]
    }
    
    return status

def create_mouse() -> Optional['WindowsMouse']:
    """
    Create Windows mouse instance
    
    Returns:
        WindowsMouse instance or None if not available
    """
    if MOUSE_AVAILABLE:
        return WindowsMouse()
    return None

def create_keyboard() -> Optional['WindowsKeyboard']:
    """
    Create Windows keyboard instance
    
    Returns:
        WindowsKeyboard instance or None if not available
    """
    if KEYBOARD_AVAILABLE:
        return WindowsKeyboard()
    return None

def create_utils() -> Optional['WindowsUtils']:
    """
    Create Windows utils instance
    
    Returns:
        WindowsUtils instance or None if not available
    """
    if UTILS_AVAILABLE:
        return WindowsUtils()
    return None

def test_windows_apis() -> dict:
    """
    Test Windows API availability
    
    Returns:
        dict: Test results for each API function
    """
    results = {}
    
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        # Test basic mouse functions
        try:
            point = ctypes.wintypes.POINT()
            results['GetCursorPos'] = bool(user32.GetCursorPos(ctypes.byref(point)))
        except Exception as e:
            results['GetCursorPos'] = f"Error: {e}"
        
        try:
            results['SetCursorPos'] = bool(user32.SetCursorPos(point.x, point.y))
        except Exception as e:
            results['SetCursorPos'] = f"Error: {e}"
        
        # Test keyboard functions
        try:
            user32.keybd_event(0x41, 0, 0x0002, 0)  # Test key up event for 'A'
            results['keybd_event'] = True
        except Exception as e:
            results['keybd_event'] = f"Error: {e}"
        
        # Test system metrics
        try:
            width = user32.GetSystemMetrics(0)
            results['GetSystemMetrics'] = width > 0
        except Exception as e:
            results['GetSystemMetrics'] = f"Error: {e}"
        
    except Exception as e:
        results['overall_error'] = str(e)
    
    return results

def get_windows_version() -> dict:
    """
    Get Windows version information
    
    Returns:
        dict: Windows version details
    """
    try:
        import platform
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
    except Exception as e:
        return {'error': str(e)}

# Export main components
__all__ = [
    # Main classes
    'WindowsMouse',
    'WindowsKeyboard', 
    'WindowsUtils',
    
    # Factory functions
    'create_mouse',
    'create_keyboard',
    'create_utils',
    
    # Information functions
    'get_implementation_status',
    'test_windows_apis',
    'get_windows_version',
    
    # Constants
    'PLATFORM_VERSION',
    'PLATFORM_NAME',
    'API_USED',
    
    # Availability flags
    'MOUSE_AVAILABLE',
    'KEYBOARD_AVAILABLE',
    'UTILS_AVAILABLE'
]

# Initialize message
if MOUSE_AVAILABLE and KEYBOARD_AVAILABLE:
    print(f"Windows implementation loaded successfully - Ghost Mouse & Bézier Curves ready")
else:
    print("Warning: Some Windows components failed to load")
    if not MOUSE_AVAILABLE:
        print(f"  Mouse: {_mouse_error}")
    if not KEYBOARD_AVAILABLE:
        print(f"  Keyboard: {_keyboard_error}")
    if not UTILS_AVAILABLE:
        print(f"  Utils: {_utils_error}")