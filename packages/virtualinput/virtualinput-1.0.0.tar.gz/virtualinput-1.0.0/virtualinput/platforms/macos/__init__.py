"""
macOS platform implementation for VirtualInput library

This module provides macOS-specific implementations using Core Graphics (Quartz) 
and Cocoa frameworks through pyobjc bindings.

Components:
- MacOSMouse: Mouse control using CGEventCreateMouseEvent and CGEventPost
- MacOSKeyboard: Keyboard control using CGEventCreateKeyboardEvent
- MacOSUtils: macOS-specific utilities and application management

Features:
- Ghost mouse coordinates (including negative values)
- Multi-monitor support with automatic coordinate handling
- Accessibility framework integration
- Application management (activate, hide, unhide)
- System notifications and clipboard access
- Kernel-level input injection through Core Graphics

Requirements:
- macOS operating system
- pyobjc package (pip install pyobjc)
- Accessibility permissions for input simulation
"""

import sys
import platform as plt
from typing import Optional, Dict, Any

# Verify macOS platform
if plt.system() != 'Darwin':
    raise ImportError("macOS implementation can only be used on macOS systems")

# Test pyobjc availability
try:
    import Cocoa
    import Quartz
    PYOBJC_AVAILABLE = True
    PYOBJC_VERSION = getattr(Cocoa, '__version__', 'Unknown')
except ImportError:
    PYOBJC_AVAILABLE = False
    PYOBJC_VERSION = None

# Import macOS implementations with error handling
try:
    from .mouse import MacOSMouse
    MOUSE_AVAILABLE = True
    _mouse_error = None
except ImportError as e:
    MOUSE_AVAILABLE = False
    _mouse_error = str(e)

try:
    from .keyboard import MacOSKeyboard
    KEYBOARD_AVAILABLE = True
    _keyboard_error = None
except ImportError as e:
    KEYBOARD_AVAILABLE = False
    _keyboard_error = str(e)

try:
    from .utils import MacOSUtils
    UTILS_AVAILABLE = True
    _utils_error = None
except ImportError as e:
    UTILS_AVAILABLE = False
    _utils_error = str(e)

# Platform information
PLATFORM_VERSION = "1.0.0"
PLATFORM_NAME = "macOS"
API_USED = ["Core Graphics", "Quartz", "Cocoa"]
REQUIRED_PACKAGES = ["pyobjc-framework-Cocoa", "pyobjc-framework-Quartz"]

def get_implementation_status() -> Dict[str, Any]:
    """
    Get status of macOS implementations
    
    Returns:
        dict: Status of each component and requirements
    """
    status = {
        'platform': PLATFORM_NAME,
        'version': PLATFORM_VERSION,
        'macos_version': plt.mac_ver()[0],
        'pyobjc_available': PYOBJC_AVAILABLE,
        'pyobjc_version': PYOBJC_VERSION,
        'accessibility_permissions': check_accessibility_permissions(),
        'components': {
            'mouse': {
                'available': MOUSE_AVAILABLE,
                'error': _mouse_error
            },
            'keyboard': {
                'available': KEYBOARD_AVAILABLE,
                'error': _keyboard_error
            },
            'utils': {
                'available': UTILS_AVAILABLE,
                'error': _utils_error
            }
        },
        'features': [
            'Ghost coordinates',
            'Multi-monitor support',
            'Accessibility integration',
            'Bézier curves',
            'Application management',
            'System notifications',
            'Clipboard access'
        ],
        'requirements': {
            'packages': REQUIRED_PACKAGES,
            'permissions': ['Accessibility']
        }
    }
    
    return status

def check_accessibility_permissions() -> bool:
    """
    Check if accessibility permissions are granted
    
    Returns:
        bool: True if permissions are available
    """
    if not PYOBJC_AVAILABLE:
        return False
    
    try:
        import Quartz
        # Try to create a simple event to test permissions
        event = Quartz.CGEventCreate(None)
        return event is not None
    except Exception:
        return False

def request_accessibility_permissions() -> bool:
    """
    Guide user to enable accessibility permissions
    
    Returns:
        bool: True if request was successful
    """
    try:
        import subprocess
        
        # Try to open System Preferences to Privacy settings
        result = subprocess.run([
            'osascript', '-e',
            'tell application "System Preferences" to reveal anchor "Privacy_Accessibility" of pane id "com.apple.preference.security"'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("System Preferences opened to Accessibility settings.")
            print("Please add your Python application to the list and enable the checkbox.")
            return True
        else:
            print("Please manually open System Preferences > Security & Privacy > Privacy > Accessibility")
            print("Add your Python application and enable the checkbox.")
            return False
            
    except Exception as e:
        print(f"Could not open System Preferences: {e}")
        print("Please manually enable accessibility permissions:")
        print("System Preferences > Security & Privacy > Privacy > Accessibility")
        return False

def create_mouse() -> Optional['MacOSMouse']:
    """
    Create macOS mouse instance
    
    Returns:
        MacOSMouse instance or None if not available
    """
    if MOUSE_AVAILABLE:
        return MacOSMouse()
    return None

def create_keyboard() -> Optional['MacOSKeyboard']:
    """
    Create macOS keyboard instance
    
    Returns:
        MacOSKeyboard instance or None if not available
    """
    if KEYBOARD_AVAILABLE:
        return MacOSKeyboard()
    return None

def create_utils() -> Optional['MacOSUtils']:
    """
    Create macOS utils instance
    
    Returns:
        MacOSUtils instance or None if not available
    """
    if UTILS_AVAILABLE:
        return MacOSUtils()
    return None

def test_macos_apis() -> Dict[str, Any]:
    """
    Test macOS API availability and functionality
    
    Returns:
        dict: Test results for each API component
    """
    results = {}
    
    if not PYOBJC_AVAILABLE:
        results['error'] = "pyobjc not available"
        return results
    
    try:
        import Quartz
        
        # Test event creation
        try:
            event = Quartz.CGEventCreate(None)
            results['CGEventCreate'] = event is not None
        except Exception as e:
            results['CGEventCreate'] = f"Error: {e}"
        
        # Test mouse event creation
        try:
            mouse_event = Quartz.CGEventCreateMouseEvent(
                None, Quartz.kCGEventMouseMoved, (100, 100), Quartz.kCGMouseButtonLeft
            )
            results['CGEventCreateMouseEvent'] = mouse_event is not None
        except Exception as e:
            results['CGEventCreateMouseEvent'] = f"Error: {e}"
        
        # Test keyboard event creation
        try:
            key_event = Quartz.CGEventCreateKeyboardEvent(None, 0x00, True)  # 'A' key
            results['CGEventCreateKeyboardEvent'] = key_event is not None
        except Exception as e:
            results['CGEventCreateKeyboardEvent'] = f"Error: {e}"
        
    except ImportError as e:
        results['Quartz_import'] = f"Error: {e}"
    
    try:
        import Cocoa
        
        # Test screen access
        try:
            screen = Cocoa.NSScreen.mainScreen()
            results['NSScreen'] = screen is not None
        except Exception as e:
            results['NSScreen'] = f"Error: {e}"
        
        # Test workspace access
        try:
            workspace = Cocoa.NSWorkspace.sharedWorkspace()
            results['NSWorkspace'] = workspace is not None
        except Exception as e:
            results['NSWorkspace'] = f"Error: {e}"
    
    except ImportError as e:
        results['Cocoa_import'] = f"Error: {e}"
    
    return results

def get_macos_version() -> Dict[str, Any]:
    """
    Get macOS version and system information
    
    Returns:
        dict: macOS version details
    """
    try:
        mac_ver = plt.mac_ver()
        return {
            'system': plt.system(),
            'version': mac_ver[0],
            'version_info': mac_ver[1],
            'machine': plt.machine(),
            'processor': plt.processor(),
            'python_version': plt.python_version(),
            'architecture': plt.architecture()
        }
    except Exception as e:
        return {'error': str(e)}

def install_instructions() -> str:
    """
    Get installation instructions for macOS
    
    Returns:
        str: Installation instructions
    """
    return """
macOS Installation Instructions:

1. Install pyobjc:
   pip install pyobjc
   
   Or install specific frameworks:
   pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz

2. Enable Accessibility Permissions:
   - Open System Preferences
   - Go to Security & Privacy > Privacy > Accessibility
   - Add your Python application or Terminal to the list
   - Check the checkbox to enable

3. Verify installation:
   python -c "import virtualinput; print(virtualinput.get_platform_info())"

Note: Some applications may require additional permissions or 
System Integrity Protection to be disabled for full functionality.
"""

# Export main components
__all__ = [
    # Main classes
    'MacOSMouse',
    'MacOSKeyboard',
    'MacOSUtils',
    
    # Factory functions
    'create_mouse',
    'create_keyboard', 
    'create_utils',
    
    # Permission and setup functions
    'check_accessibility_permissions',
    'request_accessibility_permissions',
    'install_instructions',
    
    # Information functions
    'get_implementation_status',
    'test_macos_apis',
    'get_macos_version',
    
    # Constants
    'PLATFORM_VERSION',
    'PLATFORM_NAME',
    'API_USED',
    'REQUIRED_PACKAGES',
    
    # Availability flags
    'PYOBJC_AVAILABLE',
    'MOUSE_AVAILABLE',
    'KEYBOARD_AVAILABLE',
    'UTILS_AVAILABLE'
]

# Initialization messages and checks
if PYOBJC_AVAILABLE:
    if MOUSE_AVAILABLE and KEYBOARD_AVAILABLE:
        accessibility_ok = check_accessibility_permissions()
        if accessibility_ok:
            print(f"macOS implementation loaded successfully - Ghost Mouse & Bézier Curves ready")
        else:
            print("macOS implementation loaded but accessibility permissions required")
            print("Run: virtualinput.platforms.macos.request_accessibility_permissions()")
    else:
        print("Warning: Some macOS components failed to load")
        if not MOUSE_AVAILABLE:
            print(f"  Mouse: {_mouse_error}")
        if not KEYBOARD_AVAILABLE:
            print(f"  Keyboard: {_keyboard_error}")
else:
    print("pyobjc not available. Install with: pip install pyobjc")
    print("For installation help, run: virtualinput.platforms.macos.install_instructions()")