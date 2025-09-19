"""
macOS keyboard implementation using Core Graphics (Quartz)
"""

import time
import random
from typing import List
from ...core.base_classes import BaseKeyboard
from ...core.exceptions import KeyboardError, InvalidKeycodeError
from ...core.keycodes import KeyCode

try:
    import Quartz
    from Quartz import (
        CGEventCreateKeyboardEvent, CGEventPost, CGEventSetFlags,
        kCGHIDEventTap, kCGEventFlagMaskCommand, kCGEventFlagMaskControl,
        kCGEventFlagMaskAlternate, kCGEventFlagMaskShift
    )
    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False

class MacOSKeyboard(BaseKeyboard):
    """
    macOS-specific keyboard implementation using Core Graphics (Quartz)
    """
    
    def __init__(self):
        super().__init__()
        
        if not QUARTZ_AVAILABLE:
            raise KeyboardError("Quartz framework not available. Install pyobjc: pip install pyobjc")
        
        # macOS key code mappings (different from Windows!)
        self.key_code_map = {
            # Letters
            'a': 0x00, 'b': 0x0B, 'c': 0x08, 'd': 0x02, 'e': 0x0E,
            'f': 0x03, 'g': 0x05, 'h': 0x04, 'i': 0x22, 'j': 0x26,
            'k': 0x28, 'l': 0x25, 'm': 0x2E, 'n': 0x2D, 'o': 0x1F,
            'p': 0x23, 'q': 0x0C, 'r': 0x0F, 's': 0x01, 't': 0x11,
            'u': 0x20, 'v': 0x09, 'w': 0x0D, 'x': 0x07, 'y': 0x10, 'z': 0x06,
            
            # Numbers
            '0': 0x1D, '1': 0x12, '2': 0x13, '3': 0x14, '4': 0x15,
            '5': 0x17, '6': 0x16, '7': 0x1A, '8': 0x1C, '9': 0x19,
            
            # Function keys
            'f1': 0x7A, 'f2': 0x78, 'f3': 0x63, 'f4': 0x76, 'f5': 0x60,
            'f6': 0x61, 'f7': 0x62, 'f8': 0x64, 'f9': 0x65, 'f10': 0x6D,
            'f11': 0x67, 'f12': 0x6F,
            
            # Special keys
            'enter': 0x24, 'space': 0x31, 'tab': 0x30, 'escape': 0x35,
            'backspace': 0x33, 'delete': 0x75, 'insert': 0x72,  # Insert = Help on Mac
            'home': 0x73, 'end': 0x77, 'page_up': 0x74, 'page_down': 0x79,
            
            # Arrow keys
            'up': 0x7E, 'down': 0x7D, 'left': 0x7B, 'right': 0x7C,
            
            # Modifier keys (handled specially)
            'cmd': 0x37, 'ctrl': 0x3B, 'alt': 0x3A, 'shift': 0x38,
            
            # Lock keys
            'caps_lock': 0x39,
            
            # Punctuation
            'semicolon': 0x29, 'equals': 0x18, 'comma': 0x2B,
            'minus': 0x1B, 'period': 0x2F, 'slash': 0x2C,
            'backtick': 0x32, 'left_bracket': 0x21, 'backslash': 0x2A,
            'right_bracket': 0x1E, 'quote': 0x27,
        }
        
        # Modifier flag mappings
        self.modifier_flags = {
            'cmd': kCGEventFlagMaskCommand,
            'ctrl': kCGEventFlagMaskControl,
            'alt': kCGEventFlagMaskAlternate,
            'shift': kCGEventFlagMaskShift
        }
    
    def _get_key_code(self, keycode: str) -> int:
        """Get macOS key code for keycode"""
        keycode = keycode.lower()
        if keycode not in self.key_code_map:
            raise InvalidKeycodeError(keycode)
        return self.key_code_map[keycode]
    
    def press(self, keycode: str) -> bool:
        """
        Press and immediately release a key
        """
        try:
            key_code = self._get_key_code(keycode)
            
            # Create key down event
            key_down = CGEventCreateKeyboardEvent(None, key_code, True)
            if key_down is None:
                raise KeyboardError(f"Failed to create key down event for '{keycode}'")
            
            # Create key up event
            key_up = CGEventCreateKeyboardEvent(None, key_code, False)
            if key_up is None:
                raise KeyboardError(f"Failed to create key up event for '{keycode}'")
            
            # Post events with human-like timing
            CGEventPost(kCGHIDEventTap, key_down)
            time.sleep(random.uniform(0.01, 0.03))
            CGEventPost(kCGHIDEventTap, key_up)
            
            return True
            
        except Exception as e:
            raise KeyboardError(f"Failed to press key '{keycode}': {str(e)}", keycode)
    
    def press_and_hold(self, keycode: str) -> bool:
        """
        Press and hold a key
        """
        try:
            key_code = self._get_key_code(keycode)
            
            # Create and post key down event
            key_down = CGEventCreateKeyboardEvent(None, key_code, True)
            if key_down is None:
                raise KeyboardError(f"Failed to create key down event for '{keycode}'")
            
            CGEventPost(kCGHIDEventTap, key_down)
            
            # Track pressed key
            self.pressed_keys.add(keycode.lower())
            
            return True
            
        except Exception as e:
            raise KeyboardError(f"Failed to press and hold key '{keycode}': {str(e)}", keycode)
    
    def release(self, keycode: str) -> bool:
        """
        Release a held key
        """
        try:
            key_code = self._get_key_code(keycode)
            
            # Create and post key up event
            key_up = CGEventCreateKeyboardEvent(None, key_code, False)
            if key_up is None:
                raise KeyboardError(f"Failed to create key up event for '{keycode}'")
            
            CGEventPost(kCGHIDEventTap, key_up)
            
            # Remove from pressed keys
            self.pressed_keys.discard(keycode.lower())
            
            return True
            
        except Exception as e:
            raise KeyboardError(f"Failed to release key '{keycode}': {str(e)}", keycode)
    
    def type(self, text: str, delay: float = 0.01) -> bool:
        """
        Type a string of text with human-like timing
        """
        try:
            for char in text:
                char_lower = char.lower()
                
                if char_lower in self.key_code_map:
                    # Handle mapped characters
                    if char.isupper() and char.isalpha():
                        # Type uppercase letter with shift
                        self._type_with_shift(char_lower)
                    else:
                        # Type normally
                        self.press(char_lower)
                else:
                    # Handle unicode characters
                    self._type_unicode_char(char)
                
                # Human-like typing delay with variation
                actual_delay = delay * random.uniform(0.5, 1.5)
                time.sleep(actual_delay)
            
            return True
            
        except Exception as e:
            raise KeyboardError(f"Failed to type text: {str(e)}")
    
    def _type_with_shift(self, keycode: str):
        """Type a character with shift held"""
        key_code = self._get_key_code(keycode)
        
        # Create events with shift flag
        key_down = CGEventCreateKeyboardEvent(None, key_code, True)
        key_up = CGEventCreateKeyboardEvent(None, key_code, False)
        
        # Set shift flag
        CGEventSetFlags(key_down, kCGEventFlagMaskShift)
        CGEventSetFlags(key_up, kCGEventFlagMaskShift)
        
        # Post events
        CGEventPost(kCGHIDEventTap, key_down)
        time.sleep(0.01)
        CGEventPost(kCGHIDEventTap, key_up)
    
    def _type_unicode_char(self, char: str):
        """
        Type a unicode character
        On macOS, this is more complex and might require different approaches
        """
        # For now, try to find closest ASCII equivalent or skip
        # A full implementation would use NSString and input method services
        pass
    
    def hotkey(self, *keys: str) -> bool:
        """
        Press multiple keys simultaneously (e.g., cmd+c)
        """
        try:
            # Separate modifiers from regular keys
            modifiers = []
            regular_keys = []
            
            for key in keys:
                key_lower = key.lower()
                if key_lower in self.modifier_flags:
                    modifiers.append(key_lower)
                else:
                    regular_keys.append(key_lower)
            
            # Build modifier flags
            modifier_flag = 0
            for mod in modifiers:
                modifier_flag |= self.modifier_flags[mod]
            
            # Press regular keys with modifiers
            for key in regular_keys:
                key_code = self._get_key_code(key)
                
                # Create events with modifier flags
                key_down = CGEventCreateKeyboardEvent(None, key_code, True)
                key_up = CGEventCreateKeyboardEvent(None, key_code, False)
                
                if modifier_flag:
                    CGEventSetFlags(key_down, modifier_flag)
                    CGEventSetFlags(key_up, modifier_flag)
                
                # Post events
                CGEventPost(kCGHIDEventTap, key_down)
                time.sleep(0.01)
                CGEventPost(kCGHIDEventTap, key_up)
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            raise KeyboardError(f"Failed to execute hotkey combination: {str(e)}")
    
    def is_pressed(self, keycode: str) -> bool:
        """
        Check if a key is currently pressed
        This is more limited on macOS compared to Windows
        """
        try:
            # On macOS, checking key state is more complex
            # For now, just check our internal tracking
            return keycode.lower() in self.pressed_keys
        except Exception:
            return False