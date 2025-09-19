"""
Custom exceptions for the VirtualInput library
Provides specific error types for better error handling
"""

class VirtualInputError(Exception):
    """
    Base exception for all VirtualInput library errors
    All other exceptions inherit from this one
    """
    def __init__(self, message: str, error_code: int = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self):
        if self.error_code:
            return f"VirtualInputError [{self.error_code}]: {self.message}"
        return f"VirtualInputError: {self.message}"


class PlatformNotSupportedError(VirtualInputError):
    """
    Raised when trying to use the library on an unsupported platform
    """
    def __init__(self, platform: str):
        message = f"Platform '{platform}' is not supported. Supported platforms: Windows, macOS"
        super().__init__(message, error_code=1001)
        self.platform = platform


class KeyboardError(VirtualInputError):
    """
    Raised when there's an error with keyboard operations
    """
    def __init__(self, message: str, keycode: str = None):
        super().__init__(message, error_code=2000)
        self.keycode = keycode


class MouseError(VirtualInputError):
    """
    Raised when there's an error with mouse operations
    """
    def __init__(self, message: str, coordinates: tuple = None):
        super().__init__(message, error_code=3000)
        self.coordinates = coordinates


class InvalidKeycodeError(KeyboardError):
    """
    Raised when an invalid keycode is provided
    """
    def __init__(self, keycode: str):
        message = f"Invalid keycode: '{keycode}'. Use KeyCode constants or valid key names."
        super().__init__(message, keycode)
        self.error_code = 2001


class InvalidCoordinatesError(MouseError):
    """
    Raised when invalid coordinates are provided
    """
    def __init__(self, coordinates: tuple):
        message = f"Invalid coordinates: {coordinates}. Coordinates must be non-negative integers."
        super().__init__(message, coordinates)
        self.error_code = 3001


class PermissionError(VirtualInputError):
    """
    Raised when the application doesn't have required permissions
    """
    def __init__(self, platform: str, required_permission: str):
        message = f"Permission denied on {platform}. Required: {required_permission}"
        super().__init__(message, error_code=4000)
        self.platform = platform
        self.required_permission = required_permission