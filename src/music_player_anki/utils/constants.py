"""Constants and configuration values for the Music Player addon.

This module defines all constants used throughout the addon, including service
URLs, widget dimensions, button sizes, and keyboard shortcuts. Centralizing
these values makes it easy to modify behavior without searching through code.

Constants are organized into logical groups:
    - Service configurations (URLs and metadata)
    - UI dimensions (widget and component sizes)
    - Keyboard mappings (for JavaScript injection)

Using constants from this module ensures consistency across the addon and makes
it easier to maintain and modify behavior.

Typical usage example:
    >>> from utils.constants import SERVICES, WIDGET_WIDTH
    >>> url = SERVICES['youtube_music']['url']
    >>> widget.resize(WIDGET_WIDTH, WIDGET_HEIGHT)
"""

# Service URLs
SERVICES = {
    'youtube_music': {
        'name': 'YouTube Music',
        'url': 'https://music.youtube.com'
    },
    'youtube': {
        'name': 'YouTube',
        'url': 'https://www.youtube.com'
    }
}

# Keyboard shortcuts
KEYBOARD_SHORTCUTS = {
    'play_pause': 'k',
    'next': 'n',
    'previous': 'p'
}

# Widget dimensions
WIDGET_WIDTH = 700
WIDGET_HEIGHT = 550
HEADER_HEIGHT = 48
CONTROLS_HEIGHT = 56

# Button sizes
PRIMARY_BUTTON_SIZE = 46
SECONDARY_BUTTON_SIZE = 40
