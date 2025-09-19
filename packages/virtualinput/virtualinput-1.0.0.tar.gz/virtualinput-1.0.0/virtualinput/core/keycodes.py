"""
Universal keycode mappings that work across all platform 
These constant provide a consisten  interface regardless of the underlying OS
"""

class KeyCode:
    """
    Universal key cides that work across all platform 
    Use these constants instead of platform-specific codes
    """

    # Letter (lowercase for consisitency)
    A = 'a'
    B = 'b'
    C = 'c'
    D = 'd'
    E = 'e'
    F = 'f'
    G = 'g'
    H = 'h'
    I = 'i'
    J = 'j'
    K = 'k'
    L = 'l'
    M = 'm'
    N = 'n'
    O = 'o'
    P = 'p'
    Q = 'q'
    R = 'r'
    S = 's'
    T = 't'
    U = 'u'
    V = 'v'
    W = 'w'
    X = 'x'
    Y = 'y'
    Z = 'z'

    # Numbers
    KEY_0 = '0'
    KEY_1 = '1'
    KEY_2 = '2'
    KEY_3 = '3'
    KEY_4 = '4'
    KEY_5 = '5'
    KEY_6 = '6'
    KEY_7 = '7'
    KEY_8 = '8'
    KEY_9 = '9'

    # Function keys
    F1 = 'f1'
    F2 = 'f2'
    F3 = 'f3'
    F4 = 'f4'
    F5 = 'f5'
    F6 = 'f6'
    F7 = 'f7'
    F8 = 'f8'
    F9 = 'f9'
    F10 = 'f10'
    F11 = 'f11'
    F12 = 'f12'
    
    # Arrow keys
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
    
    # Modifier keys
    CTRL = 'ctrl'
    CONTROL = 'ctrl'  # Alias
    ALT = 'alt'
    SHIFT = 'shift'
    CMD = 'cmd'      # macOS Command key
    COMMAND = 'cmd'  # Alias
    WIN = 'win'      # Windows key
    WINDOWS = 'win'  # Alias
    
    # Special keys
    ENTER = 'enter'
    RETURN = 'enter'    # Alias
    SPACE = 'space'
    TAB = 'tab'
    ESCAPE = 'escape'
    ESC = 'escape'      # Alias
    BACKSPACE = 'backspace'
    DELETE = 'delete'
    INSERT = 'insert'
    HOME = 'home'
    END = 'end'
    PAGE_UP = 'page_up'
    PAGE_DOWN = 'page_down'
    
    # Punctuation and symbols
    SEMICOLON = ';'
    EQUALS = '='
    COMMA = ','
    MINUS = '-'
    PERIOD = '.'
    SLASH = '/'
    BACKTICK = '`'
    LEFT_BRACKET = '['
    BACKSLASH = '\\'
    RIGHT_BRACKET = ']'
    QUOTE = "'"
    
    # Numpad keys
    NUMPAD_0 = 'numpad_0'
    NUMPAD_1 = 'numpad_1'
    NUMPAD_2 = 'numpad_2'
    NUMPAD_3 = 'numpad_3'
    NUMPAD_4 = 'numpad_4'
    NUMPAD_5 = 'numpad_5'
    NUMPAD_6 = 'numpad_6'
    NUMPAD_7 = 'numpad_7'
    NUMPAD_8 = 'numpad_8'
    NUMPAD_9 = 'numpad_9'
    NUMPAD_MULTIPLY = 'numpad_*'
    NUMPAD_ADD = 'numpad_+'
    NUMPAD_SUBTRACT = 'numpad_-'
    NUMPAD_DECIMAL = 'numpad_.'
    NUMPAD_DIVIDE = 'numpad_/'
    
    # Lock keys
    CAPS_LOCK = 'caps_lock'
    NUM_LOCK = 'num_lock'
    SCROLL_LOCK = 'scroll_lock'
    
    # Media keys
    VOLUME_UP = 'volume_up'
    VOLUME_DOWN = 'volume_down'
    VOLUME_MUTE = 'volume_mute'
    MEDIA_PLAY_PAUSE = 'media_play_pause'
    MEDIA_NEXT = 'media_next'
    MEDIA_PREVIOUS = 'media_previous'
    MEDIA_STOP = 'media_stop'

class MouseButton:
    """
    Universal mouse button constants
    """
    LEFT = 'left'
    RIGHT = 'right'
    MIDDLE = 'middle'
    WHEEL = 'middle'     # Alias for middle button
    X1 = 'x1'           # Back button (if available)
    X2 = 'x2'           # Forward button (if available)
    BACK = 'x1'         # Alias
    FORWARD = 'x2'      # Alias


class ScrollDirection:
    """
    Scroll direction constants
    """
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'       # Horizontal scrolling (if supported)
    RIGHT = 'right'     # Horizontal scrolling (if supported)

# Helper dictionaries for validation and conversion
VALID_KEYS = {
    # Get all KeyCode attributes that don't start with underscore
    key for key in dir(KeyCode) 
    if not key.startswith('_') and isinstance(getattr(KeyCode, key), str)
}

VALID_MOUSE_BUTTONS = {
    MouseButton.LEFT, MouseButton.RIGHT, MouseButton.MIDDLE,
    MouseButton.X1, MouseButton.X2
}

VALID_SCROLL_DIRECTIONS = {
    ScrollDirection.UP, ScrollDirection.DOWN,
    ScrollDirection.LEFT, ScrollDirection.RIGHT
}

# Modifier keys for hotkey combinations
MODIFIER_KEYS = {
    KeyCode.CTRL, KeyCode.ALT, KeyCode.SHIFT, 
    KeyCode.CMD, KeyCode.WIN
}