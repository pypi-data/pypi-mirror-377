"""
Windows mouse implementation using Win32 API
SUpports ghost mouse functionality with unlimited coordinate range
"""

import ctypes
import ctypes.wintypes
import time
import random
from typing import Tuple
from ...core.base_classes import BaseMouse
from ...core.exceptions import MouseError
from ...core.utils import get_screen_size

class WindowsMouse(BaseMouse):
    """
    WWindows-specific mouse implementation using Win32 API
    Supports ghost coordinates and Bezier curves
    """

    def __init__(self):
        super().__init__()
        # load windows API functions
        self.user32=ctypes.windll.user32
        self.kernel32=ctypes.windll.kernel32

        # Mouse button constants
        self.BUTTON_MAP = {
            'left': {
                'down': 0x0002,    # MOUSEEVENTF_LEFTDOWN
                'up': 0x0004       # MOUSEEVENTF_LEFTUP
            },
            'right': {
                'down': 0x0008,    # MOUSEEVENTF_RIGHTDOWN  
                'up': 0x0010       # MOUSEEVENTF_RIGHTUP
            },
            'middle': {
                'down': 0x0020,    # MOUSEEVENTF_MIDDLEDOWN
                'up': 0x0040       # MOUSEEVENTF_MIDDLEUP
            }
        }

        # Track pressed buttons
        self.pressed_buttons = set()
        self.screen_size= get_screen_size() # (w,h)
        # Get screen dimensions for reference
        self.screen_width = self.user32.GetSystemMetrics(0)   # SM_CXSCREEN
        self.screen_height = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN

    
    def move(self, x:int, y:int):
        """
        Move mouse to absolute coordinates using SetCursorPos
        SUPPORTS GHOST COORDINATES -No restrictions!
        """
        try:
            
            # SetCursorPos works with negative coordinates!
            # Windows handles multi-monitor and off-screen coordinates automatically
            
            result=self.user32.SetCursorPos(int(x),int(y))

            if result:
                self.last_position = (x,y)
                return True
            else:
                error_code = self.kernel32.GetLastError()
                raise MouseError(f"SetCursorPos failed with error code: {error_code}", (x, y))
                
        except Exception as e:
            raise MouseError(f"Failed to move mouse to ({x}, {y}): {str(e)}", (x, y))
    
    def move_relative(self, dx:int, dy:int):
        """
        Move mouse relative to current position
        """
        try:
            current_x, current_y= self.get_position()
            
            new_x = current_x + dx
            new_y = current_y + dy

            return self.move(new_x,new_y)
        
        except Exception as e:
            raise MouseError(f"Failed to move mouse relatively by ({dx},{dy}): {str(e)}")
    
    def click(self, button:str = 'left')->bool:
        """
        click mouse button at current position
        """
        try:
            if button not in self.BUTTON_MAP:
                raise MouseError(f"Invalid button: {button}")
            
            button_codes = self.BUTTON_MAP[button]

             # Send mouse down event
            self.user32.mouse_event(button_codes['down'], 0, 0, 0, 0)
            
            # Human-like click duration
            time.sleep(random.uniform(0.01, 0.03))
            
            # Send mouse up event  
            self.user32.mouse_event(button_codes['up'], 0, 0, 0, 0)
            
            return True
            
        except Exception as e:
            raise MouseError(f"Failed to click {button} button: {str(e)}")
    
    def double_click(self, button: str = 'left') -> bool:
        """
        Double-click mouse button
        """
        try:
            self.click(button)
            time.sleep(random.uniform(0.05, 0.1))  # Human-like delay between clicks
            self.click(button)
            return True
        except Exception as e:
            raise MouseError(f"Failed to double-click {button} button: {str(e)}")
    
    def press_and_hold(self, button: str = 'left') -> bool:
        """
        Press and hold mouse button
        """
        try:
            if button not in self.BUTTON_MAP:
                raise MouseError(f"Invalid button: {button}")
            
            button_codes = self.BUTTON_MAP[button]
            
            # Send mouse down event only
            self.user32.mouse_event(button_codes['down'], 0, 0, 0, 0)
            
            # Track pressed button
            self.pressed_buttons.add(button)
            
            return True
            
        except Exception as e:
            raise MouseError(f"Failed to press and hold {button} button: {str(e)}")
    
    def release(self, button: str = 'left') -> bool:
        """
        Release held mouse button
        """
        try:
            if button not in self.BUTTON_MAP:
                raise MouseError(f"Invalid button: {button}")
            
            button_codes = self.BUTTON_MAP[button]
            
            # Send mouse up event only
            self.user32.mouse_event(button_codes['up'], 0, 0, 0, 0)
            
            # Remove from pressed buttons
            self.pressed_buttons.discard(button)
            
            return True
            
        except Exception as e:
            raise MouseError(f"Failed to release {button} button: {str(e)}")
    
    def scroll(self, direction: str, clicks: int = 1) -> bool:
        """
        Scroll mouse wheel
        """
        try:
            if direction.lower() == 'up':
                wheel_delta = 120 * clicks
            elif direction.lower() == 'down':
                wheel_delta = -120 * clicks
            else:
                raise MouseError(f"Invalid scroll direction: {direction}")
            
            # MOUSEEVENTF_WHEEL = 0x0800
            self.user32.mouse_event(0x0800, 0, 0, wheel_delta, 0)
            
            return True
            
        except Exception as e:
            raise MouseError(f"Failed to scroll {direction}: {str(e)}")
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get current mouse cursor position
        Works with ghost coordinates too!
        """
        try:
            # Create POINT structure
            point = ctypes.wintypes.POINT()
            
            # Get cursor position
            if self.user32.GetCursorPos(ctypes.byref(point)):
                return (point.x, point.y)
            else:
                error_code = self.kernel32.GetLastError()
                raise MouseError(f"GetCursorPos failed with error code: {error_code}")
                
        except Exception as e:
            raise MouseError(f"Failed to get mouse position: {str(e)}")
    
    
    
    def is_button_pressed(self, button: str) -> bool:
        """
        Check if mouse button is currently pressed
        """
        return button in self.pressed_buttons
