"""
macOS mouse implementation using Core Graphics (Quartz)
Supports ghost mouse functionality with unlimited coordinate range
"""

import time
import random
from typing import Tuple
from ...core.base_classes import BaseMouse
from ...core.exceptions import MouseError

try:
    import Quartz
    from Quartz import (
        CGEventCreateMouseEvent, CGEventPost, CGEventCreate,
        kCGEventMouseMoved, kCGEventLeftMouseDown, kCGEventLeftMouseUp,
        kCGEventRightMouseDown, kCGEventRightMouseUp,
        kCGEventOtherMouseDown, kCGEventOtherMouseUp,
        kCGEventScrollWheel, kCGHIDEventTap,
        kCGMouseButtonLeft, kCGMouseButtonRight, kCGMouseButtonCenter,
        CGEventCreateScrollWheelEvent, kCGScrollEventUnitPixel, CGEventGetLocation
    )
    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False

class MacOSMouse(BaseMouse):
    """
    macOS-specific mouse implementation using Quartz (Core Graphics)
    Supports ghost coordinates and Bézier curves
    """
    
    def __init__(self):
        super().__init__()
        
        if not QUARTZ_AVAILABLE:
            raise MouseError("Quartz framework not available. Install pyobjc: pip install pyobjc")
        
        # Button mappings
        self.button_map = {
            'left': {
                'down_event': kCGEventLeftMouseDown,
                'up_event': kCGEventLeftMouseUp,
                'button_id': kCGMouseButtonLeft
            },
            'right': {
                'down_event': kCGEventRightMouseDown,
                'up_event': kCGEventRightMouseUp, 
                'button_id': kCGMouseButtonRight
            },
            'middle': {
                'down_event': kCGEventOtherMouseDown,
                'up_event': kCGEventOtherMouseUp,
                'button_id': kCGMouseButtonCenter
            }
        }
        
        self.pressed_buttons = set()
        
        # Get screen dimensions
        try:
            import Cocoa
            screen = Cocoa.NSScreen.mainScreen()
            frame = screen.frame()
            self.screen_width = int(frame.size.width)
            self.screen_height = int(frame.size.height)
        except ImportError:
            self.screen_width = 1920
            self.screen_height = 1080
    
    def move(self, x: int, y: int) -> bool:
        """
        Move mouse to absolute coordinates using Core Graphics
        SUPPORTS GHOST COORDINATES - macOS handles negative coordinates!
        """
        try:
            # Create mouse moved event
            # macOS Core Graphics supports negative coordinates for multi-monitor setups
            event = CGEventCreateMouseEvent(
                None,                    # No event source
                kCGEventMouseMoved,      # Mouse moved event type
                (float(x), float(y)),    # Target coordinates (supports negative!)
                kCGMouseButtonLeft       # Button (irrelevant for move events)
            )
            
            if event is None:
                raise MouseError(f"Failed to create mouse move event for ({x}, {y})")
            
            # Post the event to the system
            CGEventPost(kCGHIDEventTap, event)
            
            # Update our position tracking
            self.last_position = (x, y)
            
            return True
            
        except Exception as e:
            raise MouseError(f"Failed to move mouse to ({x}, {y}): {str(e)}", (x, y))
    
    def move_relative(self, dx: int, dy: int) -> bool:
        """
        Move mouse relative to current position
        """
        try:
            current_x, current_y = self.get_position()
            new_x = current_x + dx
            new_y = current_y + dy
            return self.move(new_x, new_y)
        except Exception as e:
            raise MouseError(f"Failed to move mouse relatively by ({dx}, {dy}): {str(e)}")
    
    def click(self, button: str = 'left') -> bool:
        """
        Click mouse button at current position
        """
        try:
            if button not in self.button_map:
                raise MouseError(f"Invalid button: {button}")
            
            current_pos = self.get_position()
            button_info = self.button_map[button]
            
            # Create mouse down event
            down_event = CGEventCreateMouseEvent(
                None,
                button_info['down_event'],
                current_pos,
                button_info['button_id']
            )
            
            # Create mouse up event  
            up_event = CGEventCreateMouseEvent(
                None,
                button_info['up_event'],
                current_pos,
                button_info['button_id']
            )
            
            if down_event is None or up_event is None:
                raise MouseError(f"Failed to create mouse click events for {button} button")
            
            # Post events with human-like timing
            CGEventPost(kCGHIDEventTap, down_event)
            time.sleep(random.uniform(0.01, 0.03))
            CGEventPost(kCGHIDEventTap, up_event)
            
            return True
            
        except Exception as e:
            raise MouseError(f"Failed to click {button} button: {str(e)}")
    
    def double_click(self, button: str = 'left') -> bool:
        """
        Double-click mouse button
        """
        try:
            self.click(button)
            time.sleep(random.uniform(0.05, 0.1))
            self.click(button)
            return True
        except Exception as e:
            raise MouseError(f"Failed to double-click {button} button: {str(e)}")
    
    def press_and_hold(self, button: str = 'left') -> bool:
        """
        Press and hold mouse button
        """
        try:
            if button not in self.button_map:
                raise MouseError(f"Invalid button: {button}")
            
            current_pos = self.get_position()
            button_info = self.button_map[button]
            
            # Create and post mouse down event
            down_event = CGEventCreateMouseEvent(
                None,
                button_info['down_event'],
                current_pos,
                button_info['button_id']
            )
            
            if down_event is None:
                raise MouseError(f"Failed to create mouse down event for {button} button")
            
            CGEventPost(kCGHIDEventTap, down_event)
            
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
            if button not in self.button_map:
                raise MouseError(f"Invalid button: {button}")
            
            current_pos = self.get_position()
            button_info = self.button_map[button]
            
            # Create and post mouse up event
            up_event = CGEventCreateMouseEvent(
                None,
                button_info['up_event'],
                current_pos,
                button_info['button_id']
            )
            
            if up_event is None:
                raise MouseError(f"Failed to create mouse up event for {button} button")
            
            CGEventPost(kCGHIDEventTap, up_event)
            
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
                scroll_delta = clicks
            elif direction.lower() == 'down':
                scroll_delta = -clicks
            else:
                raise MouseError(f"Invalid scroll direction: {direction}")
            
            # Create scroll event
            scroll_event = CGEventCreateScrollWheelEvent(
                None,                        # Event source
                kCGScrollEventUnitPixel,     # Scroll unit
                1,                           # Number of axes (1 for vertical)
                scroll_delta                 # Scroll amount
            )
            
            if scroll_event is None:
                raise MouseError(f"Failed to create scroll event")
            
            CGEventPost(kCGHIDEventTap, scroll_event)
            
            return True
            
        except Exception as e:
            raise MouseError(f"Failed to scroll {direction}: {str(e)}")
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get current mouse cursor position
        Works with ghost coordinates!
        """
        try:
            # Get current mouse location
            event = CGEventCreate(None)
            if event is None:
                raise MouseError("Failed to create event for position query")
            
            location = CGEventGetLocation(event)
            
            return (int(location.x), int(location.y))
            
        except Exception as e:
            raise MouseError(f"Failed to get mouse position: {str(e)}")
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get primary screen dimensions
        """
        return (self.screen_width, self.screen_height)
    
    def is_button_pressed(self, button: str) -> bool:
        """
        Check if mouse button is currently pressed
        """
        return button in self.pressed_buttons