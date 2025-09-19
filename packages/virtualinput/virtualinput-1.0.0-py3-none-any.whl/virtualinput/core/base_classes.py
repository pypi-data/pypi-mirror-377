"""
Abstract base classes that define the inerface for keyboard and mouse implementations
Every platform-specific implementation must inherit from these classes
"""
from abc import ABC, abstractmethod
from typing import Tuple, List
import time
import random
import math


class BaseKeyboard(ABC):
    """
    Abstract base class for all keyboard implementations
    Defines the standard interface that all platforms must implement
    """

    def __init__(self):
        self.pressed_keys=set() # track the currently pressed keys

    @abstractmethod
    def press(self, keycode:str)->bool:
        """
        Press and immediately release a key

        Args:
            keycode: The key to press (use KeyCode constants)
        
        Returns:
            bool:True if successful, False otherwise
        """
        pass

    @abstractmethod
    def press_and_hold(self,keycode:str)->bool:
        """
        Press a key and hold it down
        
        Args:
            keycode: The key to press and hold
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abstractmethod
    def release(self,keycode:str)->bool:
        """
        Release a previously held key

        Args:
            keycode: The key to release

        Returns:
            bool:True if successful, Flase otherwise
        """
        pass

    @abstractmethod
    def type(self, text:str,delay:float=0.01)->bool:
        """
        Type a string of text with optional delay between characters

        Args:
            text: The text to type
            delay:Deplay between keystrokes in seconds
        
        Returns:
            bool:True:if successful, False otherwise
        """
        pass

    @abstractmethod
    def hotkey(self, *keys:str)->bool:
        """
        Press multiple keys simultaneously (like ctrl+c, ctrl+shift+p)

        Args:
            *keys: Varoable number of keys to press together
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abstractmethod
    def is_pressed(self, keycode:str)->bool:
        """
        Check if a key is currently being pressed

        Args:
            keycode: The key to check
        
        Returns:
            bool: True if the key is pressed, False otherwise
        """
        pass

    
    def release_all(self)->bool:
        """
        Release all currently held keys
        This is common method that can be implemented here
        """
        try:
            for key in list(self.pressed_keys):
                self.release(key)
            
            return True
        except Exception:
            return False

# =======================================  Mouse config ======================================= #

class BaseMouse(ABC):
    """
    Abstract base class for all mouse implementations
    Defines the standard interface that all platform must implement
    """

    def __init__(self):
        self.last_position=(0,0)

    @abstractmethod
    def move(self,x:int,y:int)->bool:
        """
        Move mouse to absolute screen coordinates with some trajectory 
                    
        Args:
            x: X coordinate (pixels from left edge)
            y: Y coordinate (pixels from top edge)
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abstractmethod
    def move_relative(self,dx:int,dy:int)->bool:
        """
        Move mouse relative to current position

        Function:
            x(t) = (1 - t)^2 * x0 + 2(1 - t) * t * xc + t^2 * x1,
            y(t) = (1 - t)^2 * y0 + 2(1 - t) * t * yc + t^2 * y1, 
            t=0..1

            P0(x0,y0) inital start point, P1(x1,y1) is the End point
            C(xc,yc) is curve path 
            t-> 0 to 1

        Args:
            dx: Change in X postion (positive=right)
            dy:chnage in Y positon (positive=down)
        
        Returns:
            bool:True if successful, False otherwise
        """
        pass
    
    def move_bezier(self, end_x: int, end_y: int, duration: float = 1.0, 
               curve_intensity: float = 0.3) -> bool:
        """
        Move mouse in a human-like curved path using quadratic Bézier curve

        Args:
            end_x: Target X coordinate
            end_y: Target Y coordinate
            duration: Time to complete movement (seconds)
            curve_intensity: How curved the path should be (0.0 = straight, 1.0 = very curved)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current position from the real mouse instance
            start_x, start_y = self.get_position()

            # Calculate control point for natural curve
            control_x, control_y = self._calculate_bezier_control_point(
                start_x, start_y, end_x, end_y, curve_intensity
            )

            # Generate smooth path points
            path_points = self._generate_bezier_path(
                start_x, start_y, control_x, control_y, end_x, end_y, duration
            )

            # Execute the movement
            return self._execute_bezier_movement(path_points, duration)
        
        except Exception:
            return False

    def move_bezier_relative(self, dx: int, dy: int, duration: float = 1.0, 
                            curve_intensity: float = 0.3) -> bool:
        """
        Move mouse relatively using Bézier curve

        Args:
            dx: Relative X movement
            dy: Relative Y movement
            duration: Time to complete movement (seconds)
            curve_intensity: Curve strength

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            current_x, current_y = self.get_position()
            target_x = current_x + dx
            target_y = current_y + dy

            return self.move_bezier(target_x, target_y, duration, curve_intensity)

        except Exception:
            return False

    def drag_bezier(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                   button: str = 'left', duration: float = 1.0) -> bool:
        """
        Drag using smooth Bézier curve movement

        Args:
            start_x, start_y: Start coordinates
            end_x, end_y: End coordinates
            button: Mouse button to use for dragging
            duration: Total drag duration

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Move to start position with curve (30% of total duration)
            self.move_bezier(start_x, start_y, duration * 0.3)

            # Press and hold the button
            self.press_and_hold(button)

            # Drag along curve to end position (70% of total duration)
            result = self.move_bezier(end_x, end_y, duration * 0.7, curve_intensity=0.2)

            # Release the button
            self.release(button)

            return result

        except Exception:
            return False

    def _calculate_bezier_control_point(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                                       curve_intensity: float) -> Tuple[int, int]:
        """
        Calculate the control point for a natural-looking Bézier curve

        Args:
            start_x, start_y: Start coordinates
            end_x, end_y: End coordinates
            curve_intensity: How curved the path should be (0.0 = straight, 1.0 = very curved)

        Returns:
            Tuple[int, int]: Control point coordinates
        """
        # Calculate midpoint
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2

        # Calculate distance between start and end
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)

        # Calculate perpendicular offset for curve
        # This creates a natural arc instead of straight line
        angle = math.atan2(end_y - start_y, end_x - start_x)
        perpendicular_angle = angle + math.pi / 2

        # Add randomness for human-like behavior
        random_factor = random.uniform(0.7, 1.3)
        curve_offset = distance * curve_intensity * random_factor * 0.3

        # Apply random direction (sometimes curve left, sometimes right)
        direction = random.choice([-1, 1])
        curve_offset *= direction

        # Calculate control point
        control_x = int(mid_x + math.cos(perpendicular_angle) * curve_offset)
        control_y = int(mid_y + math.sin(perpendicular_angle) * curve_offset)

        return (control_x, control_y)

    def _generate_bezier_path(self, x0: int, y0: int, xc: int, yc: int, 
                             x1: int, y1: int, duration: float) -> List[Tuple[int, int, float]]:
        """
        Generate points along quadratic Bézier curve with timing
        Using your mathematical formula!

        Args:
            x0, y0: Start point
            xc, yc: Control point  
            x1, y1: End point
            duration: Total movement time

        Returns:
            List of (x, y, delay) tuples
        """
        # Calculate number of steps based on distance and duration
        distance = math.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        num_steps = max(10, int(distance / 5))  # At least 10 steps, more for longer distances

        path_points = []

        for i in range(num_steps + 1):
            # Parameter t goes from 0 to 1
            t = i / num_steps

            # Your Bézier curve formulas!
            x = int((1 - t)**2 * x0 + 2*(1 - t) * t * xc + t**2 * x1)
            y = int((1 - t)**2 * y0 + 2*(1 - t) * t * yc + t**2 * y1)

            # Calculate realistic delay with human-like variation
            base_delay = duration / num_steps

            # Add human-like timing variations
            if i == 0 or i == num_steps:
                # Slower at start and end (human acceleration/deceleration)
                delay = base_delay * random.uniform(1.5, 2.0)
            else:
                # Faster in middle, with random variation
                delay = base_delay * random.uniform(0.8, 1.2)

            path_points.append((x, y, delay))

        return path_points

    def _execute_bezier_movement(self, path_points: List[Tuple[int, int, float]], 
                                duration: float) -> bool:
        """
        Execute the movement along the calculated Bézier path

        Args:
            path_points: List of (x, y, delay) tuples from _generate_bezier_path
            duration: Total movement duration (not used in current implementation)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for x, y, delay in path_points:
                # Move to this point using the platform-specific move() method
                self.move(x, y)

                # Human-like pause
                time.sleep(delay)

            return True
        except Exception:
            return False

    @abstractmethod
    def click(self,button:str='left')->bool:
        """
        Click a mouse button at current position
        
        Args:
            button: Which button to click ('left', 'right', 'middle')
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abstractmethod
    def double_click(self,button:str="left")->bool:
        """
        Double-click a mouse button at current position

        Args:
            button:which button to double-click
        
        Returns:
            bool: True if successful, Flase otherwise
        """
        pass

    @abstractmethod
    def press_and_hold(self,button:str="left")->bool:
        """
        press and hold a mouse button

        Agrs:
            button: which button to hold down
        
        Returns:
            bool:True if successful, False otherwise
        """
        pass

    @abstractmethod
    def release(self,button:str="left")->bool:
        """
        Release a held mouse button

        Args:
            button:which button to relase
        
        Returns:
            bool:True if successful, False otherwise
        """
        pass

    @abstractmethod
    def scroll(self,direction:str,clicks: int=1)->bool:
        """
        scroll the mouse wheel

        Args:
            direction: "up and "down"
        
        Returns:
            bool:True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_position(self)->Tuple[int,int]:
        """
        Get current mouse postion

        Returns:
            Tuple[int,int]:(x,y) coordinates
        """
        pass

    def drag(self,start_x:int,start_y:int,end_x:int,end_y:int,button:str='left')->bool:
        """
        Drag from one position to another
        This is a common operation that can be implemented here using abstract methods
        """
        try:
            # Move to start position
            self.move(start_x, start_y)
            
            # Press and hold the button
            self.press_and_hold(button)
            
            # Move to end position (while holding)
            self.move(end_x, end_y)
            
            # Release the button
            self.release(button)
            
            return True
        except Exception:
            return False

