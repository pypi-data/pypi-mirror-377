"""
Input recorder for capturing and replaying mouse and keyboard actions
"""

import time
import json
from typing import List, Dict, Any, Optional, Callable
from .keyboard import VirtualKeyboard
from .mouse import VirtualMouse
from .core.exceptions import VirtualInputError
import threading

class InputAction:
    """Represents a single input action (mouse or keyboard)"""
    
    def __init__(self, action_type: str, timestamp: float, **kwargs):
        self.action_type = action_type  # 'mouse_move', 'mouse_click', 'key_press', etc.
        self.timestamp = timestamp
        self.data = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary for serialization"""
        return {
            'action_type': self.action_type,
            'timestamp': self.timestamp,
            'data': self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InputAction':
        """Create action from dictionary"""
        return cls(
            action_type=data['action_type'],
            timestamp=data['timestamp'],
            **data['data']
        )

class InputRecorder:
    """
    Records mouse and keyboard actions for later playback
    Can record real user input or programmed sequences
    """
    
    def __init__(self):
        self.actions: List[InputAction] = []
        self.is_recording = False
        self.recording_start_time = 0.0
        self.mouse = VirtualMouse()
        self.keyboard = VirtualKeyboard()
        self._recording_thread = None
        self._stop_recording = threading.Event()
    
    def start_recording(self) -> bool:
        """
        Start recording input actions
        
        Returns:
            bool: True if recording started successfully
        """
        if self.is_recording:
            return False
        
        self.actions.clear()
        self.is_recording = True
        self.recording_start_time = time.time()
        self._stop_recording.clear()
        
        print("Recording started. Press Ctrl+C to stop or call stop_recording()")
        return True
    
    def stop_recording(self) -> bool:
        """
        Stop recording input actions
        
        Returns:
            bool: True if recording stopped successfully
        """
        if not self.is_recording:
            return False
        
        self.is_recording = False
        self._stop_recording.set()
        
        if self._recording_thread and self._recording_thread.is_alive():
            self._recording_thread.join(timeout=1.0)
        
        print(f"Recording stopped. Captured {len(self.actions)} actions.")
        return True
    
    def record_mouse_move(self, x: int, y: int) -> bool:
        """Record a mouse movement action"""
        if not self.is_recording:
            return False
        
        timestamp = time.time() - self.recording_start_time
        action = InputAction('mouse_move', timestamp, x=x, y=y)
        self.actions.append(action)
        return True
    
    def record_mouse_click(self, x: int, y: int, button: str = 'left') -> bool:
        """Record a mouse click action"""
        if not self.is_recording:
            return False
        
        timestamp = time.time() - self.recording_start_time
        action = InputAction('mouse_click', timestamp, x=x, y=y, button=button)
        self.actions.append(action)
        return True
    
    def record_mouse_drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                         button: str = 'left') -> bool:
        """Record a mouse drag action"""
        if not self.is_recording:
            return False
        
        timestamp = time.time() - self.recording_start_time
        action = InputAction('mouse_drag', timestamp, 
                           start_x=start_x, start_y=start_y, 
                           end_x=end_x, end_y=end_y, button=button)
        self.actions.append(action)
        return True
    
    def record_mouse_scroll(self, x: int, y: int, direction: str, clicks: int = 1) -> bool:
        """Record a mouse scroll action"""
        if not self.is_recording:
            return False
        
        timestamp = time.time() - self.recording_start_time
        action = InputAction('mouse_scroll', timestamp, 
                           x=x, y=y, direction=direction, clicks=clicks)
        self.actions.append(action)
        return True
    
    def record_key_press(self, keycode: str) -> bool:
        """Record a key press action"""
        if not self.is_recording:
            return False
        
        timestamp = time.time() - self.recording_start_time
        action = InputAction('key_press', timestamp, keycode=keycode)
        self.actions.append(action)
        return True
    
    def record_key_type(self, text: str) -> bool:
        """Record a text typing action"""
        if not self.is_recording:
            return False
        
        timestamp = time.time() - self.recording_start_time
        action = InputAction('key_type', timestamp, text=text)
        self.actions.append(action)
        return True
    
    def record_hotkey(self, *keys: str) -> bool:
        """Record a hotkey combination"""
        if not self.is_recording:
            return False
        
        timestamp = time.time() - self.recording_start_time
        action = InputAction('hotkey', timestamp, keys=list(keys))
        self.actions.append(action)
        return True
    
    def record_pause(self, duration: float) -> bool:
        """Record a pause/delay"""
        if not self.is_recording:
            return False
        
        timestamp = time.time() - self.recording_start_time
        action = InputAction('pause', timestamp, duration=duration)
        self.actions.append(action)
        return True
    
    def get_recording_duration(self) -> float:
        """Get total duration of current recording"""
        if not self.actions:
            return 0.0
        return self.actions[-1].timestamp
    
    def get_action_count(self) -> int:
        """Get number of recorded actions"""
        return len(self.actions)
    
    def get_action_summary(self) -> Dict[str, int]:
        """Get summary of action types in recording"""
        summary = {}
        for action in self.actions:
            action_type = action.action_type
            summary[action_type] = summary.get(action_type, 0) + 1
        return summary
    
    def save_recording(self, filename: str) -> bool:
        """
        Save recording to JSON file
        
        Args:
            filename: Path to save file
            
        Returns:
            bool: True if saved successfully
        """
        try:
            recording_data = {
                'version': '1.0',
                'total_duration': self.get_recording_duration(),
                'action_count': len(self.actions),
                'created_at': time.time(),
                'actions': [action.to_dict() for action in self.actions]
            }
            
            with open(filename, 'w') as f:
                json.dump(recording_data, f, indent=2)
            
            print(f"Recording saved to {filename}")
            return True
        except Exception as e:
            print(f"Failed to save recording: {e}")
            return False
    
    def load_recording(self, filename: str) -> bool:
        """
        Load recording from JSON file
        
        Args:
            filename: Path to load file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            with open(filename, 'r') as f:
                recording_data = json.load(f)
            
            # Clear current actions
            self.actions.clear()
            
            # Load actions
            for action_data in recording_data.get('actions', []):
                action = InputAction.from_dict(action_data)
                self.actions.append(action)
            
            print(f"Recording loaded from {filename}")
            print(f"Loaded {len(self.actions)} actions, duration: {self.get_recording_duration():.2f}s")
            return True
        except Exception as e:
            print(f"Failed to load recording: {e}")
            return False
    
    def replay_recording(self, speed_multiplier: float = 1.0, 
                        use_bezier: bool = True, 
                        on_action_callback: Optional[Callable[[InputAction], None]] = None) -> bool:
        """
        Replay the recorded actions
        
        Args:
            speed_multiplier: Speed to replay (1.0 = normal, 2.0 = 2x speed, 0.5 = half speed)
            use_bezier: Use Bézier curves for mouse movements
            on_action_callback: Optional callback function called before each action
            
        Returns:
            bool: True if replay completed successfully
        """
        if not self.actions:
            print("No recording to replay")
            return False
        
        print(f"Starting replay of {len(self.actions)} actions...")
        print("Press Ctrl+C to stop replay")
        
        try:
            last_timestamp = 0.0
            
            for i, action in enumerate(self.actions):
                # Calculate delay since last action
                delay = (action.timestamp - last_timestamp) / speed_multiplier
                if delay > 0:
                    time.sleep(delay)
                
                # Call callback if provided
                if on_action_callback:
                    on_action_callback(action)
                
                # Execute the action
                success = self._execute_action(action, use_bezier)
                if not success:
                    print(f"Failed to execute action {i + 1}: {action.action_type}")
                
                last_timestamp = action.timestamp
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    progress = (i + 1) / len(self.actions) * 100
                    print(f"Replay progress: {progress:.1f}%")
            
            print("Replay completed successfully")
            return True
            
        except KeyboardInterrupt:
            print("Replay interrupted by user")
            return False
        except Exception as e:
            print(f"Replay failed: {e}")
            return False
    
    def _execute_action(self, action: InputAction, use_bezier: bool = True) -> bool:
        """Execute a single recorded action"""
        try:
            if action.action_type == 'mouse_move':
                if use_bezier:
                    return self.mouse.move_bezier(action.data['x'], action.data['y'], duration=0.3)
                else:
                    return self.mouse.move(action.data['x'], action.data['y'])
            
            elif action.action_type == 'mouse_click':
                # Move to position and click
                if use_bezier:
                    self.mouse.move_bezier(action.data['x'], action.data['y'], duration=0.3)
                else:
                    self.mouse.move(action.data['x'], action.data['y'])
                time.sleep(0.05)  # Small delay before clicking
                return self.mouse.click(action.data.get('button', 'left'))
            
            elif action.action_type == 'mouse_drag':
                return self.mouse.drag_bezier(
                    action.data['start_x'], action.data['start_y'],
                    action.data['end_x'], action.data['end_y'],
                    action.data.get('button', 'left')
                ) if use_bezier else self.mouse.drag(
                    action.data['start_x'], action.data['start_y'],
                    action.data['end_x'], action.data['end_y'],
                    action.data.get('button', 'left')
                )
            
            elif action.action_type == 'mouse_scroll':
                # Move to position and scroll
                self.mouse.move(action.data['x'], action.data['y'])
                return self.mouse.scroll(action.data['direction'], action.data.get('clicks', 1))
            
            elif action.action_type == 'key_press':
                return self.keyboard.press(action.data['keycode'])
            
            elif action.action_type == 'key_type':
                return self.keyboard.type(action.data['text'])
            
            elif action.action_type == 'hotkey':
                return self.keyboard.hotkey(*action.data['keys'])
            
            elif action.action_type == 'pause':
                time.sleep(action.data['duration'])
                return True
            
            else:
                print(f"Unknown action type: {action.action_type}")
                return False
                
        except Exception as e:
            print(f"Error executing action {action.action_type}: {e}")
            return False
    
    def create_loop_recording(self, loop_count: int = -1, 
                            loop_delay: float = 1.0) -> bool:
        """
        Replay recording in a loop
        
        Args:
            loop_count: Number of loops (-1 = infinite)
            loop_delay: Delay between loops in seconds
            
        Returns:
            bool: True if completed successfully
        """
        if not self.actions:
            print("No recording to loop")
            return False
        
        current_loop = 0
        print(f"Starting loop replay (loops: {'infinite' if loop_count == -1 else loop_count})")
        
        try:
            while loop_count == -1 or current_loop < loop_count:
                current_loop += 1
                print(f"Loop {current_loop}")
                
                success = self.replay_recording()
                if not success:
                    return False
                
                if loop_count == -1 or current_loop < loop_count:
                    time.sleep(loop_delay)
            
            print("Loop replay completed")
            return True
            
        except KeyboardInterrupt:
            print("Loop replay interrupted by user")
            return False
    
    def create_macro(self, name: str) -> 'Macro':
        """
        Create a macro from current recording
        
        Args:
            name: Name for the macro
            
        Returns:
            Macro: Macro object that can be saved and executed
        """
        return Macro(name, self.actions.copy())
    
    def optimize_recording(self) -> bool:
        """
        Optimize recording by removing redundant actions and smoothing movements
        
        Returns:
            bool: True if optimization completed
        """
        if not self.actions:
            return False
        
        original_count = len(self.actions)
        optimized_actions = []
        
        i = 0
        while i < len(self.actions):
            action = self.actions[i]
            
            # Combine consecutive mouse moves
            if action.action_type == 'mouse_move':
                # Look ahead for more mouse moves
                last_move = action
                j = i + 1
                while j < len(self.actions) and self.actions[j].action_type == 'mouse_move':
                    last_move = self.actions[j]
                    j += 1
                
                # Only keep the last mouse move in sequence
                optimized_actions.append(last_move)
                i = j
            else:
                optimized_actions.append(action)
                i += 1
        
        self.actions = optimized_actions
        print(f"Optimization complete: {original_count} -> {len(self.actions)} actions")
        return True
    
    def get_recording_stats(self) -> Dict[str, Any]:
        """Get detailed statistics about the recording"""
        if not self.actions:
            return {}
        
        stats = {
            'total_actions': len(self.actions),
            'duration': self.get_recording_duration(),
            'action_types': self.get_action_summary(),
            'average_actions_per_second': len(self.actions) / max(self.get_recording_duration(), 1),
            'first_action': self.actions[0].action_type if self.actions else None,
            'last_action': self.actions[-1].action_type if self.actions else None
        }
        
        # Calculate mouse movement distance
        total_distance = 0
        last_x, last_y = None, None
        for action in self.actions:
            if action.action_type == 'mouse_move':
                x, y = action.data['x'], action.data['y']
                if last_x is not None and last_y is not None:
                    distance = ((x - last_x) ** 2 + (y - last_y) ** 2) ** 0.5
                    total_distance += distance
                last_x, last_y = x, y
        
        stats['total_mouse_distance'] = total_distance
        
        return stats

class Macro:
    """A saved macro that can be executed multiple times"""
    
    def __init__(self, name: str, actions: List[InputAction]):
        self.name = name
        self.actions = actions
        self.created_at = time.time()
        self.mouse = VirtualMouse()
        self.keyboard = VirtualKeyboard()
    
    def execute(self, speed_multiplier: float = 1.0, use_bezier: bool = True) -> bool:
        """Execute the macro"""
        recorder = InputRecorder()
        recorder.actions = self.actions
        return recorder.replay_recording(speed_multiplier, use_bezier)
    
    def save_to_file(self, filename: str) -> bool:
        """Save macro to file"""
        recorder = InputRecorder()
        recorder.actions = self.actions
        return recorder.save_recording(filename)
    
    @classmethod
    def load_from_file(cls, filename: str, name: str = None) -> Optional['Macro']:
        """Load macro from file"""
        recorder = InputRecorder()
        if recorder.load_recording(filename):
            macro_name = name or f"Macro_{int(time.time())}"
            return cls(macro_name, recorder.actions)
        return None
    
    def get_info(self) -> Dict[str, Any]:
        """Get macro information"""
        return {
            'name': self.name,
            'action_count': len(self.actions),
            'duration': self.actions[-1].timestamp if self.actions else 0,
            'created_at': self.created_at
        }