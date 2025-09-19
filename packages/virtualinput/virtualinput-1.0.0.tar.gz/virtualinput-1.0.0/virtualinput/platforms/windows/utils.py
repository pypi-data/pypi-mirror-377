"""
Windows-specific utility functions
"""

import ctypes
import ctypes.wintypes
from typing import List, Tuple, Dict

class WindowsUtils:
    """
    Windows-specific utility functions for advanced operations
    """
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
    
    def get_window_under_cursor(self) -> int:
        """
        Get handle of window under cursor
        
        Returns:
            int: Window handle (HWND)
        """
        point = ctypes.wintypes.POINT()
        self.user32.GetCursorPos(ctypes.byref(point))
        return self.user32.WindowFromPoint(point)
    
    def get_screen_dimensions(self) -> Tuple[int, int]:
        """
        Get primary screen dimensions using Windows API
        
        Returns:
            Tuple[int, int]: (width, height) in pixels
        """
        width = self.user32.GetSystemMetrics(0)   # SM_CXSCREEN
        height = self.user32.GetSystemMetrics(1)  # SM_CYSCREEN
        return (width, height)
    
    def get_all_monitor_dimensions(self) -> List[Dict]:
        """
        Get all monitor dimensions (including negative coordinate spaces)
        This is useful for ghost mouse operations across multiple monitors
        
        Returns:
            List[Dict]: List of monitor information dictionaries
        """
        monitors = []
        
        def monitor_enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
            # Get monitor info
            monitor_info = ctypes.wintypes.RECT()
            ctypes.memmove(ctypes.byref(monitor_info), lprcMonitor, ctypes.sizeof(ctypes.wintypes.RECT))
            
            monitors.append({
                'left': monitor_info.left,
                'top': monitor_info.top, 
                'right': monitor_info.right,
                'bottom': monitor_info.bottom,
                'width': monitor_info.right - monitor_info.left,
                'height': monitor_info.bottom - monitor_info.top
            })
            return True
        
        # Define the callback function type
        MonitorEnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, 
                                           ctypes.wintypes.HMONITOR,
                                           ctypes.wintypes.HDC,
                                           ctypes.POINTER(ctypes.wintypes.RECT),
                                           ctypes.wintypes.LPARAM)
        
        try:
            # Enumerate all monitors
            self.user32.EnumDisplayMonitors(None, None, MonitorEnumProc(monitor_enum_proc), 0)
        except Exception:
            # Fallback to primary monitor
            width, height = self.get_screen_dimensions()
            monitors = [{
                'left': 0, 'top': 0, 'right': width, 'bottom': height,
                'width': width, 'height': height
            }]
        
        return monitors
    
    def is_coordinate_on_any_monitor(self, x: int, y: int) -> bool:
        """
        Check if coordinate is on any monitor (including negative coordinates)
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            bool: True if coordinate is on any monitor
        """
        try:
            point = ctypes.wintypes.POINT(x, y)
            monitor = self.user32.MonitorFromPoint(point, 1)  # MONITOR_DEFAULTTONULL
            return monitor != 0
        except Exception:
            return False
    
    def get_window_title(self, hwnd: int) -> str:
        """
        Get window title by handle
        
        Args:
            hwnd: Window handle
            
        Returns:
            str: Window title
        """
        try:
            title = ctypes.create_unicode_buffer(512)
            self.user32.GetWindowTextW(hwnd, title, 512)
            return title.value
        except Exception:
            return ""
    
    def get_window_title_under_cursor(self) -> str:
        """
        Get title of window under cursor
        
        Returns:
            str: Window title
        """
        hwnd = self.get_window_under_cursor()
        return self.get_window_title(hwnd)
    
    def minimize_window(self, hwnd: int) -> bool:
        """
        Minimize a window
        
        Args:
            hwnd: Window handle
            
        Returns:
            bool: True if successful
        """
        try:
            return bool(self.user32.ShowWindow(hwnd, 6))  # SW_MINIMIZE
        except Exception:
            return False
    
    def maximize_window(self, hwnd: int) -> bool:
        """
        Maximize a window
        
        Args:
            hwnd: Window handle
            
        Returns:
            bool: True if successful
        """
        try:
            return bool(self.user32.ShowWindow(hwnd, 3))  # SW_MAXIMIZE
        except Exception:
            return False
    
    def restore_window(self, hwnd: int) -> bool:
        """
        Restore a window to normal state
        
        Args:
            hwnd: Window handle
            
        Returns:
            bool: True if successful
        """
        try:
            return bool(self.user32.ShowWindow(hwnd, 1))  # SW_RESTORE
        except Exception:
            return False
    
    def is_window_maximized(self, hwnd: int) -> bool:
        """
        Check if window is maximized
        
        Args:
            hwnd: Window handle
            
        Returns:
            bool: True if maximized
        """
        try:
            placement = ctypes.wintypes.WINDOWPLACEMENT()
            placement.length = ctypes.sizeof(ctypes.wintypes.WINDOWPLACEMENT)
            
            if self.user32.GetWindowPlacement(hwnd, ctypes.byref(placement)):
                return placement.showCmd == 3  # SW_SHOWMAXIMIZED
            return False
        except Exception:
            return False
    
    def get_window_rect(self, hwnd: int) -> Tuple[int, int, int, int]:
        """
        Get window rectangle coordinates
        
        Args:
            hwnd: Window handle
            
        Returns:
            Tuple[int, int, int, int]: (left, top, right, bottom)
        """
        try:
            rect = ctypes.wintypes.RECT()
            if self.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return (rect.left, rect.top, rect.right, rect.bottom)
            return (0, 0, 0, 0)
        except Exception:
            return (0, 0, 0, 0)
    
    def set_window_position(self, hwnd: int, x: int, y: int, width: int = None, height: int = None) -> bool:
        """
        Set window position and optionally size
        
        Args:
            hwnd: Window handle
            x: New X position
            y: New Y position
            width: New width (optional)
            height: New height (optional)
            
        Returns:
            bool: True if successful
        """
        try:
            if width is None or height is None:
                # Get current size if not specified
                left, top, right, bottom = self.get_window_rect(hwnd)
                if width is None:
                    width = right - left
                if height is None:
                    height = bottom - top
            
            # SWP_NOZORDER | SWP_NOACTIVATE = 0x0010 | 0x0004
            flags = 0x0014
            return bool(self.user32.SetWindowPos(hwnd, 0, x, y, width, height, flags))
        except Exception:
            return False
    
    def find_window_by_title(self, title: str) -> int:
        """
        Find window by title (partial match)
        
        Args:
            title: Window title to search for
            
        Returns:
            int: Window handle (0 if not found)
        """
        try:
            return self.user32.FindWindowW(None, title)
        except Exception:
            return 0
    
    def get_foreground_window(self) -> int:
        """
        Get handle of currently active (foreground) window
        
        Returns:
            int: Window handle
        """
        try:
            return self.user32.GetForegroundWindow()
        except Exception:
            return 0
    
    def set_foreground_window(self, hwnd: int) -> bool:
        """
        Bring window to foreground
        
        Args:
            hwnd: Window handle
            
        Returns:
            bool: True if successful
        """
        try:
            return bool(self.user32.SetForegroundWindow(hwnd))
        except Exception:
            return False
    
    def get_cursor_info(self) -> Dict:
        """
        Get detailed cursor information
        
        Returns:
            Dict: Cursor information including position and visibility
        """
        try:
            # Get cursor position
            point = ctypes.wintypes.POINT()
            position_success = self.user32.GetCursorPos(ctypes.byref(point))
            
            # Get cursor visibility
            cursor_info = ctypes.Structure()
            cursor_info._fields_ = [("cbSize", ctypes.c_uint32), ("flags", ctypes.c_uint32)]
            cursor_info.cbSize = ctypes.sizeof(cursor_info)
            
            info_success = self.user32.GetCursorInfo(ctypes.byref(cursor_info))
            
            return {
                'position': (point.x, point.y) if position_success else (0, 0),
                'visible': bool(cursor_info.flags & 0x00000001) if info_success else True,
                'position_success': bool(position_success),
                'info_success': bool(info_success)
            }
        except Exception:
            return {
                'position': (0, 0),
                'visible': True,
                'position_success': False,
                'info_success': False
            }
    
    def hide_cursor(self) -> bool:
        """
        Hide the mouse cursor
        
        Returns:
            bool: True if successful
        """
        try:
            count = self.user32.ShowCursor(False)
            return count < 0  # Cursor is hidden when count < 0
        except Exception:
            return False
    
    def show_cursor(self) -> bool:
        """
        Show the mouse cursor
        
        Returns:
            bool: True if successful
        """
        try:
            count = self.user32.ShowCursor(True)
            return count >= 0  # Cursor is visible when count >= 0
        except Exception:
            return False
    
    def get_system_metrics(self, metric: int) -> int:
        """
        Get system metrics
        
        Args:
            metric: System metric constant (SM_*)
            
        Returns:
            int: Metric value
        """
        try:
            return self.user32.GetSystemMetrics(metric)
        except Exception:
            return 0
    
    def get_virtual_screen_rect(self) -> Tuple[int, int, int, int]:
        """
        Get virtual screen rectangle (all monitors combined)
        
        Returns:
            Tuple[int, int, int, int]: (left, top, width, height)
        """
        try:
            left = self.get_system_metrics(76)    # SM_XVIRTUALSCREEN
            top = self.get_system_metrics(77)     # SM_YVIRTUALSCREEN
            width = self.get_system_metrics(78)   # SM_CXVIRTUALSCREEN
            height = self.get_system_metrics(79)  # SM_CYVIRTUALSCREEN
            return (left, top, width, height)
        except Exception:
            # Fallback to primary screen
            width, height = self.get_screen_dimensions()
            return (0, 0, width, height)