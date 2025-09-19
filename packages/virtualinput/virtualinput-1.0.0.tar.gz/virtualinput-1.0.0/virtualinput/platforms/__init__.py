"""
Platform-specific implementations for VirtualInput library

This module contains platform-specific implementations for different operating systems.
Each platform has its own subdirectory with mouse, keyboard, and utility implementations.

Supported platforms:
- Windows: Uses Win32 API via ctypes
- macOS: Uses Core Graphics and Cocoa frameworks

The main library automatically detects the platform and loads the appropriate implementation.
"""

import platform
from typing import Optional, Type
from ..core.base_classes import BaseMouse, BaseKeyboard
from ..core.exceptions import PlatformNotSupportedError

# Platform detection
CURRENT_PLATFORM = platform.system()

def get_platform_name() -> str:
    """
    Get normalized platform name
    
    Returns:
        str: 'windows', 'macos', or 'unknown'
    """
    system = CURRENT_PLATFORM.lower()
    
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    else:
        return 'unknown'

def get_mouse_implementation() -> Type[BaseMouse]:
    """
    Get the appropriate mouse implementation for current platform
    
    Returns:
        Type[BaseMouse]: Platform-specific mouse class
        
    Raises:
        PlatformNotSupportedError: If platform is not supported
    """
    platform_name = get_platform_name()
    
    if platform_name == 'windows':
        try:
            from .windows.mouse import WindowsMouse
            return WindowsMouse
        except ImportError as e:
            raise PlatformNotSupportedError(f"Windows mouse implementation failed: {e}")
    
    elif platform_name == 'macos':
        try:
            from .macos.mouse import MacOSMouse
            return MacOSMouse
        except ImportError as e:
            raise PlatformNotSupportedError(f"macOS mouse implementation failed. Install pyobjc: pip install pyobjc")
    
    else:
        raise PlatformNotSupportedError(f"Platform '{CURRENT_PLATFORM}' is not supported")

def get_keyboard_implementation() -> Type[BaseKeyboard]:
    """
    Get the appropriate keyboard implementation for current platform
    
    Returns:
        Type[BaseKeyboard]: Platform-specific keyboard class
        
    Raises:
        PlatformNotSupportedError: If platform is not supported
    """
    platform_name = get_platform_name()
    
    if platform_name == 'windows':
        try:
            from .windows.keyboard import WindowsKeyboard
            return WindowsKeyboard
        except ImportError as e:
            raise PlatformNotSupportedError(f"Windows keyboard implementation failed: {e}")
    
    elif platform_name == 'macos':
        try:
            from .macos.keyboard import MacOSKeyboard
            return MacOSKeyboard
        except ImportError as e:
            raise PlatformNotSupportedError(f"macOS keyboard implementation failed. Install pyobjc: pip install pyobjc")
    
    else:
        raise PlatformNotSupportedError(f"Platform '{CURRENT_PLATFORM}' is not supported")

def get_platform_utils():
    """
    Get platform-specific utilities
    
    Returns:
        Platform-specific utils class or None if not available
    """
    platform_name = get_platform_name()
    
    try:
        if platform_name == 'windows':
            from .windows.utils import WindowsUtils
            return WindowsUtils()
        elif platform_name == 'macos':
            from .macos.utils import MacOSUtils
            return MacOSUtils()
    except ImportError:
        pass
    
    return None

def is_platform_supported(platform_name: str = None) -> bool:
    """
    Check if a platform is supported
    
    Args:
        platform_name: Platform to check (None = current platform)
        
    Returns:
        bool: True if platform is supported
    """
    if platform_name is None:
        platform_name = get_platform_name()
    
    return platform_name.lower() in ['windows', 'macos']

def get_platform_features() -> dict:
    """
    Get features available on current platform
    
    Returns:
        dict: Available features for current platform
    """
    platform_name = get_platform_name()
    
    base_features = [
        'mouse_movement',
        'mouse_clicking', 
        'mouse_scrolling',
        'keyboard_typing',
        'keyboard_hotkeys',
        'ghost_coordinates',
        'bezier_curves'
    ]
    
    if platform_name == 'windows':
        return {
            'platform': 'Windows',
            'features': base_features + [
                'multi_monitor_support',
                'window_management',
                'system_metrics',
                'unicode_input'
            ],
            'apis_used': ['Win32 API', 'ctypes'],
            'dependencies': ['Built-in (ctypes)']
        }
    
    elif platform_name == 'macos':
        return {
            'platform': 'macOS',
            'features': base_features + [
                'accessibility_integration',
                'application_management', 
                'notification_system',
                'clipboard_access'
            ],
            'apis_used': ['Core Graphics', 'Cocoa'],
            'dependencies': ['pyobjc']
        }
    
    else:
        return {
            'platform': 'Unsupported',
            'features': [],
            'apis_used': [],
            'dependencies': []
        }

# Export commonly used functions
__all__ = [
    'get_platform_name',
    'get_mouse_implementation',
    'get_keyboard_implementation', 
    'get_platform_utils',
    'is_platform_supported',
    'get_platform_features',
    'CURRENT_PLATFORM'
]