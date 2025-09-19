"""
Main keyboard interface that automatically detects platform and uses appropriate implementation
"""

import platform
from .core.base_classes import BaseKeyboard
from .core.exceptions import PlatformNotSupportedError, KeyboardError
from .core.keycodes import KeyCode
from typing import List

class VirtualKeyboard:
    """
    Cross-platform virtual keyboard that automatically detects your operating system
    and uses the appropriate implementation (Windows or macOS)
    """
    
    def __init__(self):
        """Initialize the keyboard with platform-specific implementation"""
        self._implementation = self._get_platform_implementation()
    
    def _get_platform_implementation(self) -> BaseKeyboard:
        """
        Get the appropriate keyboard implementation for the current platform
        
        Returns:
            BaseKeyboard: Platform-specific keyboard implementation
            
        Raises:
            PlatformNotSupportedError: If platform is not supported
        """
        system = platform.system()
        
        if system == "Windows":
            try:
                from .platforms.windows.keyboard import WindowsKeyboard
                return WindowsKeyboard()
            except ImportError as e:
                raise PlatformNotSupportedError(f"Windows keyboard implementation failed: {e}")
        
        elif system == "Darwin":  # macOS
            try:
                from .platforms.macos.keyboard import MacOSKeyboard
                return MacOSKeyboard()
            except ImportError as e:
                raise PlatformNotSupportedError(f"macOS keyboard implementation failed. Install pyobjc: pip install pyobjc")
        
        else:
            raise PlatformNotSupportedError(f"Platform '{system}' is not supported yet. Supported platforms: Windows, macOS")
    
    def press(self, keycode: str) -> bool:
        """
        Press and immediately release a key
        
        Args:
            keycode: The key to press (use KeyCode constants for consistency)
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            keyboard.press(KeyCode.A)
            keyboard.press('enter')
            keyboard.press('f1')
        """
        return self._implementation.press(keycode)
    
    def press_and_hold(self, keycode: str) -> bool:
        """
        Press and hold a key down
        
        Args:
            keycode: The key to press and hold
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            keyboard.press_and_hold('shift')
            # Do other operations while shift is held
            keyboard.release('shift')
        """
        return self._implementation.press_and_hold(keycode)
    
    def release(self, keycode: str) -> bool:
        """
        Release a previously held key
        
        Args:
            keycode: The key to release
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self._implementation.release(keycode)
    
    def type(self, text: str, delay: float = 0.01) -> bool:
        """
        Type a string of text with realistic human-like timing
        
        Args:
            text: The text to type
            delay: Base delay between keystrokes in seconds (will have human-like variation)
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            keyboard.type("Hello, World!")
            keyboard.type("This is slower typing", delay=0.1)
        """
        return self._implementation.type(text, delay)
    
    def hotkey(self, *keys: str) -> bool:
        """
        Press multiple keys simultaneously (like Ctrl+C, Ctrl+Shift+S)
        
        Args:
            *keys: Variable number of keys to press together
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            keyboard.hotkey('ctrl', 'c')        # Copy
            keyboard.hotkey('ctrl', 'shift', 's')  # Save As
            keyboard.hotkey('alt', 'tab')       # Alt+Tab
        """
        return self._implementation.hotkey(*keys)
    
    def is_pressed(self, keycode: str) -> bool:
        """
        Check if a key is currently being pressed
        
        Args:
            keycode: The key to check
            
        Returns:
            bool: True if the key is pressed, False otherwise
            
        Example:
            if keyboard.is_pressed('shift'):
                print("Shift is currently held down")
        """
        return self._implementation.is_pressed(keycode)
    
    def release_all(self) -> bool:
        """
        Release all currently held keys
        Useful for cleanup or emergency key release
        
        Returns:
            bool: True if successful, False otherwise
        """
        return self._implementation.release_all()
    
    def get_pressed_keys(self) -> set:
        """
        Get set of currently pressed keys
        
        Returns:
            set: Set of currently pressed key codes
        """
        return self._implementation.pressed_keys.copy()
    
    def type_with_hotkeys(self, text: str, delay: float = 0.01) -> bool:
        """
        Type text that may contain hotkey combinations
        Format: Use {ctrl+c} for hotkeys within text
        
        Args:
            text: Text with optional hotkey combinations
            delay: Delay between operations
            
        Returns:
            bool: True if successful
            
        Example:
            keyboard.type_with_hotkeys("Hello {ctrl+a} World")
            # Types "Hello ", presses Ctrl+A, then types " World"
        """
        try:
            import re
            
            # Find all hotkey patterns like {ctrl+c}
            pattern = r'\{([^}]+)\}'
            parts = re.split(pattern, text)
            
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Regular text
                    if part:
                        self.type(part, delay)
                else:
                    # Hotkey combination
                    keys = [key.strip() for key in part.split('+')]
                    self.hotkey(*keys)
                
                if delay > 0:
                    import time
                    time.sleep(delay)
            
            return True
        except Exception:
            return False
    
    def type_special_chars(self, text: str, delay: float = 0.01) -> bool:
        """
        Type text including special characters and symbols
        Handles unicode characters properly
        
        Args:
            text: Text including special characters
            delay: Delay between keystrokes
            
        Returns:
            bool: True if successful
        """
        return self._implementation.type(text, delay)
    
    def simulate_real_typing(self, text: str, wpm: int = 60) -> bool:
        """
        Simulate realistic human typing speed
        
        Args:
            text: Text to type
            wpm: Words per minute (average human typing speed)
            
        Returns:
            bool: True if successful
            
        Example:
            keyboard.simulate_real_typing("This types at 40 WPM", wpm=40)
        """
        try:
            # Calculate delay based on WPM
            # Average word length is 5 characters, so chars per minute = wpm * 5
            chars_per_minute = wpm * 5
            base_delay = 60.0 / chars_per_minute  # seconds per character
            
            return self.type(text, base_delay)
        except Exception:
            return False
    
    def get_platform_info(self) -> dict:
        """
        Get information about the current platform and implementation
        
        Returns:
            dict: Platform information
        """
        return {
            'platform': platform.system(),
            'implementation': type(self._implementation).__name__,
            'supported_features': [
                'press', 'press_and_hold', 'release', 'type', 'hotkey', 
                'is_pressed', 'release_all'
            ]
        }