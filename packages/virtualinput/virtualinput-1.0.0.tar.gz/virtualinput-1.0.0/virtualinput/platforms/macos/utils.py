"""
macOS-specific utility functions
"""

from typing import List, Tuple, Dict
import subprocess

# Safe imports with fallbacks
try:
    import Cocoa
    COCOA_AVAILABLE = True
except ImportError:
    COCOA_AVAILABLE = False

try:
    import Quartz
    from Quartz import CGEventCreate, CGEventGetLocation
    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False

class MacOSUtils:
    """
    macOS-specific utility functions
    """
    
    def __init__(self):
        if not COCOA_AVAILABLE and not QUARTZ_AVAILABLE:
            raise ImportError("macOS utilities require pyobjc. Install with: pip install pyobjc")
    
    def get_screen_dimensions(self) -> Tuple[int, int]:
        """
        Get primary screen dimensions
        
        Returns:
            Tuple[int, int]: (width, height) in pixels
        """
        if COCOA_AVAILABLE:
            try:
                screen = Cocoa.NSScreen.mainScreen()
                frame = screen.frame()
                return (int(frame.size.width), int(frame.size.height))
            except Exception:
                pass
        
        # Fallback to default resolution
        return (1920, 1080)
    
    def get_all_screen_dimensions(self) -> List[Dict]:
        """
        Get all screen dimensions (including negative coordinate spaces for multi-monitor)
        
        Returns:
            List[Dict]: List of screen information dictionaries
        """
        screens = []
        
        if COCOA_AVAILABLE:
            try:
                for screen in Cocoa.NSScreen.screens():
                    frame = screen.frame()
                    screens.append({
                        'x': int(frame.origin.x),
                        'y': int(frame.origin.y),
                        'width': int(frame.size.width),
                        'height': int(frame.size.height)
                    })
                return screens
            except Exception:
                pass
        
        # Fallback to single screen
        width, height = self.get_screen_dimensions()
        return [{'x': 0, 'y': 0, 'width': width, 'height': height}]
    
    def check_accessibility_permissions(self) -> bool:
        """
        Check if the app has accessibility permissions (required for input simulation)
        
        Returns:
            bool: True if permissions are granted
        """
        if QUARTZ_AVAILABLE:
            try:
                # Try to create a simple event to test permissions
                event = CGEventCreate(None)
                return event is not None
            except Exception:
                return False
        return False
    
    def request_accessibility_permissions(self):
        """
        Guide user to enable accessibility permissions
        """
        try:
            # Open System Preferences to Privacy & Security
            subprocess.run([
                'osascript', '-e',
                'tell application "System Preferences" to reveal anchor "Privacy_Accessibility" of pane id "com.apple.preference.security"'
            ], check=False)
            
            print("Please enable accessibility permissions in System Preferences:")
            print("System Preferences > Security & Privacy > Privacy > Accessibility")
            print("Add your application to the list and check the checkbox.")
        except Exception:
            print("Please manually enable accessibility permissions in System Preferences")
    
    def is_coordinate_on_screen(self, x: int, y: int) -> bool:
        """
        Check if coordinate is on any screen (including negative coordinates)
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            bool: True if coordinate is on any screen
        """
        screens = self.get_all_screen_dimensions()
        
        for screen in screens:
            if (screen['x'] <= x <= screen['x'] + screen['width'] and
                screen['y'] <= y <= screen['y'] + screen['height']):
                return True
        
        return False
    
    def get_active_application(self) -> Dict:
        """
        Get information about the currently active application
        
        Returns:
            Dict: Application information
        """
        if COCOA_AVAILABLE:
            try:
                workspace = Cocoa.NSWorkspace.sharedWorkspace()
                active_app = workspace.frontmostApplication()
                
                return {
                    'name': str(active_app.localizedName()) if active_app.localizedName() else "Unknown",
                    'bundle_id': str(active_app.bundleIdentifier()) if active_app.bundleIdentifier() else "Unknown",
                    'pid': int(active_app.processIdentifier())
                }
            except Exception:
                pass
        
        return {'name': 'Unknown', 'bundle_id': 'Unknown', 'pid': 0}
    
    def get_running_applications(self) -> List[Dict]:
        """
        Get list of running applications
        
        Returns:
            List[Dict]: List of application information
        """
        apps = []
        
        if COCOA_AVAILABLE:
            try:
                workspace = Cocoa.NSWorkspace.sharedWorkspace()
                running_apps = workspace.runningApplications()
                
                for app in running_apps:
                    # Skip background processes
                    if app.activationPolicy() == Cocoa.NSApplicationActivationPolicyRegular:
                        apps.append({
                            'name': str(app.localizedName()) if app.localizedName() else "Unknown",
                            'bundle_id': str(app.bundleIdentifier()) if app.bundleIdentifier() else "Unknown",
                            'pid': int(app.processIdentifier())
                        })
            except Exception:
                pass
        
        return apps
    
    def activate_application(self, bundle_id: str) -> bool:
        """
        Activate (bring to front) an application by bundle ID
        
        Args:
            bundle_id: Application bundle identifier (e.g., 'com.apple.finder')
            
        Returns:
            bool: True if successful
        """
        if COCOA_AVAILABLE:
            try:
                workspace = Cocoa.NSWorkspace.sharedWorkspace()
                return workspace.launchApplication_(bundle_id)
            except Exception:
                pass
        return False
    
    def hide_application(self, bundle_id: str) -> bool:
        """
        Hide an application by bundle ID
        
        Args:
            bundle_id: Application bundle identifier
            
        Returns:
            bool: True if successful
        """
        if COCOA_AVAILABLE:
            try:
                workspace = Cocoa.NSWorkspace.sharedWorkspace()
                running_apps = workspace.runningApplications()
                
                for app in running_apps:
                    if str(app.bundleIdentifier()) == bundle_id:
                        return app.hide()
            except Exception:
                pass
        return False
    
    def unhide_application(self, bundle_id: str) -> bool:
        """
        Unhide an application by bundle ID
        
        Args:
            bundle_id: Application bundle identifier
            
        Returns:
            bool: True if successful
        """
        if COCOA_AVAILABLE:
            try:
                workspace = Cocoa.NSWorkspace.sharedWorkspace()
                running_apps = workspace.runningApplications()
                
                for app in running_apps:
                    if str(app.bundleIdentifier()) == bundle_id:
                        return app.unhide()
            except Exception:
                pass
        return False
    
    def get_window_under_cursor(self) -> Dict:
        """
        Get information about window under cursor (limited on macOS due to security)
        
        Returns:
            Dict: Window information (may be limited)
        """
        # macOS has strict security around window information
        # This is a basic implementation
        active_app = self.get_active_application()
        
        return {
            'app_name': active_app['name'],
            'app_bundle_id': active_app['bundle_id'],
            'note': 'macOS limits window information access for security'
        }
    
    def take_screenshot(self, region: Tuple[int, int, int, int] = None) -> bool:
        """
        Take a screenshot using macOS screencapture
        
        Args:
            region: Optional region (x, y, width, height)
            
        Returns:
            bool: True if successful
        """
        try:
            cmd = ['screencapture', '-x']  # -x = no sound
            
            if region:
                x, y, width, height = region
                cmd.extend(['-R', f'{x},{y},{width},{height}'])
            
            cmd.append('/tmp/screenshot.png')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_system_volume(self) -> float:
        """
        Get system volume level
        
        Returns:
            float: Volume level (0.0 to 1.0)
        """
        try:
            result = subprocess.run([
                'osascript', '-e', 'output volume of (get volume settings)'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                volume = int(result.stdout.strip())
                return volume / 100.0  # Convert to 0.0-1.0 range
        except Exception:
            pass
        
        return 0.5  # Default fallback
    
    def set_system_volume(self, volume: float) -> bool:
        """
        Set system volume level
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            bool: True if successful
        """
        try:
            volume_percent = int(volume * 100)
            volume_percent = max(0, min(100, volume_percent))  # Clamp to 0-100
            
            result = subprocess.run([
                'osascript', '-e', f'set volume output volume {volume_percent}'
            ], capture_output=True, text=True)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def show_notification(self, title: str, message: str, sound: bool = False) -> bool:
        """
        Show a macOS notification
        
        Args:
            title: Notification title
            message: Notification message
            sound: Whether to play sound
            
        Returns:
            bool: True if successful
        """
        try:
            sound_option = 'with sound' if sound else ''
            script = f'display notification "{message}" with title "{title}" {sound_option}'
            
            result = subprocess.run([
                'osascript', '-e', script
            ], capture_output=True, text=True)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def get_clipboard_content(self) -> str:
        """
        Get clipboard content
        
        Returns:
            str: Clipboard text content
        """
        if COCOA_AVAILABLE:
            try:
                pasteboard = Cocoa.NSPasteboard.generalPasteboard()
                content = pasteboard.stringForType_(Cocoa.NSPasteboardTypeString)
                return str(content) if content else ""
            except Exception:
                pass
        
        # Fallback using pbpaste
        try:
            result = subprocess.run(['pbpaste'], capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else ""
        except Exception:
            return ""
    
    def set_clipboard_content(self, text: str) -> bool:
        """
        Set clipboard content
        
        Args:
            text: Text to set in clipboard
            
        Returns:
            bool: True if successful
        """
        if COCOA_AVAILABLE:
            try:
                pasteboard = Cocoa.NSPasteboard.generalPasteboard()
                pasteboard.clearContents()
                pasteboard.setString_forType_(text, Cocoa.NSPasteboardTypeString)
                return True
            except Exception:
                pass
        
        # Fallback using pbcopy
        try:
            result = subprocess.run(['pbcopy'], input=text, text=True, capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_current_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position using Quartz
        
        Returns:
            Tuple[int, int]: (x, y) coordinates
        """
        if QUARTZ_AVAILABLE:
            try:
                event = CGEventCreate(None)
                if event:
                    location = CGEventGetLocation(event)
                    return (int(location.x), int(location.y))
            except Exception:
                pass
        
        return (0, 0)  # Fallback
    
    def check_app_in_dock(self, bundle_id: str) -> bool:
        """
        Check if application is in the Dock
        
        Args:
            bundle_id: Application bundle identifier
            
        Returns:
            bool: True if app is in Dock
        """
        try:
            script = f'''
            tell application "System Events"
                set dockApps to (get bundle identifier of every application process whose background only is false)
                return "{bundle_id}" is in dockApps
            end tell
            '''
            
            result = subprocess.run([
                'osascript', '-e', script
            ], capture_output=True, text=True)
            
            return result.stdout.strip() == "true"
        except Exception:
            return False