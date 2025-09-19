"""
Windows keyboard implementation using Win32 API
"""

import ctypes
import ctypes.wintypes
import time
import random
from typing import List
from ...core.base_classes import BaseKeyboard
from ...core.exceptions import KeyboardError, InvalidKeycodeError
from ...core.keycodes import KeyCode

class WindowsKeyboard(BaseKeyboard):
    """
    Windows-specific keyboard implementation using Win32 API
    """
    
    def __init__(self):
        super().__init__()
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Windows Virtual Key Code mappings
        self.vk_code_map = {
            # Letters
            'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
            'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
            'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
            'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
            'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59, 'z': 0x5A,
            
            # Numbers
            '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
            '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
            
            # Function keys
            'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73, 'f5': 0x74,
            'f6': 0x75, 'f7': 0x76, 'f8': 0x77, 'f9': 0x78, 'f10': 0x79,
            'f11': 0x7A, 'f12': 0x7B,
            
            # Special keys
            'enter': 0x0D, 'space': 0x20, 'tab': 0x09, 'escape': 0x1B,
            'backspace': 0x08, 'delete': 0x2E, 'insert': 0x2D,
            'home': 0x24, 'end': 0x23, 'page_up': 0x21, 'page_down': 0x22,
            
            # Arrow keys
            'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
            
            # Modifier keys
            'ctrl': 0x11, 'alt': 0x12, 'shift': 0x10, 'win': 0x5B,
            
            # Lock keys
            'caps_lock': 0x14, 'num_lock': 0x90, 'scroll_lock': 0x91,
            
            # Numpad
            'numpad_0': 0x60, 'numpad_1': 0x61, 'numpad_2': 0x62, 'numpad_3': 0x63,
            'numpad_4': 0x64, 'numpad_5': 0x65, 'numpad_6': 0x66, 'numpad_7': 0x67,
            'numpad_8': 0x68, 'numpad_9': 0x69, 'numpad_*': 0x6A, 'numpad_+': 0x6B,
            'numpad_-': 0x6D, 'numpad_.': 0x6E, 'numpad_/': 0x6F,
            
            # Punctuation
            'semicolon': 0xBA, 'equals': 0xBB, 'comma': 0xBC,
            'minus': 0xBD, 'period': 0xBE, 'slash': 0xBF,
            'backtick': 0xC0, 'left_bracket': 0xDB, 'backslash': 0xDC,
            'right_bracket': 0xDD, 'quote': 0xDE,
        }
    
    def _get_vk_code(self, keycode: str) -> int:
        """Get Windows Virtual Key code for keycode"""
        keycode = keycode.lower()
        if keycode not in self.vk_code_map:
            raise InvalidKeycodeError(keycode)
        return self.vk_code_map[keycode]
    
    def press(self, keycode: str) -> bool:
        """
        Press and immediately release a key
        """
        try:
            vk_code = self._get_vk_code(keycode)
            
            # Key down
            self.user32.keybd_event(vk_code, 0, 0, 0)
            
            # Human-like press duration
            time.sleep(random.uniform(0.01, 0.03))
            
            # Key up (KEYEVENTF_KEYUP = 0x0002)
            self.user32.keybd_event(vk_code, 0, 0x0002, 0)
            
            return True
            
        except Exception as e:
            raise KeyboardError(f"Failed to press key '{keycode}': {str(e)}", keycode)
    
    def press_and_hold(self, keycode: str) -> bool:
        """
        Press and hold a key
        """
        try:
            vk_code = self._get_vk_code(keycode)
            
            # Key down only
            self.user32.keybd_event(vk_code, 0, 0, 0)
            
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
            vk_code = self._get_vk_code(keycode)
            
            # Key up (KEYEVENTF_KEYUP = 0x0002)
            self.user32.keybd_event(vk_code, 0, 0x0002, 0)
            
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
                
                if char_lower in self.vk_code_map:
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
        try:
            # Press shift
            self.press_and_hold('shift')
            time.sleep(0.01)
            
            # Press the key
            self.press(keycode)
            
            # Release shift
            self.release('shift')
            
        except Exception as e:
            raise KeyboardError(f"Failed to type with shift '{keycode}': {str(e)}")
    
    def _type_unicode_char(self, char: str):
        """
        Type a unicode character using SendInput
        """
        try:
            # Convert character to unicode code point
            unicode_value = ord(char)
            
            # Use SendInput with UNICODE flag for better unicode support
            INPUT_KEYBOARD = 1
            KEYEVENTF_UNICODE = 0x0004
            KEYEVENTF_KEYUP = 0x0002
            
            # Define INPUT structure
            class INPUT(ctypes.Structure):
                _fields_ = [("type", ctypes.c_ulong),
                           ("ki", ctypes.c_ulong * 6)]
            
            # Key down
            input_down = INPUT()
            input_down.type = INPUT_KEYBOARD
            input_down.ki[4] = unicode_value  # Unicode character
            input_down.ki[3] = KEYEVENTF_UNICODE
            
            # Key up  
            input_up = INPUT()
            input_up.type = INPUT_KEYBOARD
            input_up.ki[4] = unicode_value
            input_up.ki[3] = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
            
            # Send the inputs
            self.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
            time.sleep(0.01)
            self.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))
            
        except Exception as e:
            # Fallback to regular key press if unicode fails
            pass
    
    def hotkey(self, *keys: str) -> bool:
        """
        Press multiple keys simultaneously
        """
        try:
            # Press all keys in order
            for key in keys:
                self.press_and_hold(key)
                time.sleep(0.01)  # Small delay between presses
            
            # Hold for a moment
            time.sleep(0.05)
            
            # Release all keys in reverse order
            for key in reversed(keys):
                self.release(key)
                time.sleep(0.01)
            
            return True
            
        except Exception as e:
            raise KeyboardError(f"Failed to execute hotkey combination: {str(e)}")
    
    def is_pressed(self, keycode: str) -> bool:
        """
        Check if a key is currently pressed
        """
        try:
            vk_code = self._get_vk_code(keycode)
            
            # GetAsyncKeyState returns the state of the key
            state = self.user32.GetAsyncKeyState(vk_code)
            
            # Check if the high bit is set (key is pressed)
            return bool(state & 0x8000)
            
        except Exception:
            return False