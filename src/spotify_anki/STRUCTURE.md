# Music Player Anki Addon - Code Structure

## Overview

The codebase has been refactored into a clean, modular structure following best practices for maintainability and readability.

## Directory Structure

```
spotify_anki/
├── __init__.py              # Main entry point and addon initialization
├── hooks.py                 # Anki hooks integration
├── config.py                # Legacy config (use core/config.py instead)
├── settings_dialog.py       # Legacy settings (use gui/settings_dialog.py instead)
├── spotify_web_widget.py    # Legacy widget (use gui/music_widget.py instead)
├── spotify_controller.py    # Legacy controller (use core/player_controller.py instead)
│
├── core/                    # Core business logic
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   └── player_controller.py # Player control logic
│
├── gui/                     # GUI components
│   ├── __init__.py
│   ├── music_widget.py     # Main music player widget
│   └── settings_dialog.py  # Settings configuration dialog
│
└── utils/                   # Utility modules
    ├── __init__.py
    ├── constants.py        # Constants and enumerations
    ├── styles.py           # Centralized UI styles
    └── javascript.py       # JavaScript injection utilities
```

## Module Descriptions

### Core (`core/`)

**`config.py`**
- Manages addon configuration and settings
- Handles JSON file persistence
- Provides default values
- Thread-safe singleton instance

**`player_controller.py`**
- Simplified player controller
- Maintains compatibility with existing code
- No API-based control (all control via JavaScript injection)

### GUI (`gui/`)

**`music_widget.py`**
- Main widget with embedded web browser
- Supports YouTube Music and YouTube
- Frameless, draggable window
- Playback controls (play/pause, next, previous)
- Ad blocking for YouTube services
- Keyboard shortcuts support

**`settings_dialog.py`**
- Dark-themed settings dialog
- Keyboard shortcut configuration
- Service selection (YouTube Music/YouTube)
- Input validation
- Reset to defaults functionality

### Utils (`utils/`)

**`constants.py`**
- Service URLs and metadata
- Widget dimensions
- Button sizes
- Keyboard shortcut mappings

**`styles.py`**
- Centralized stylesheet definitions
- Color constants
- Component-specific styles (header, buttons, controls, etc.)
- Ensures consistent UI across the addon

**`javascript.py`**
- JavaScript code for web player control
- Ad blocker scripts (CSS and DOM manipulation)
- Playback control scripts (play/pause, next, previous)
- MutationObserver for dynamic ad removal

## Key Features

### 1. Clean Separation of Concerns
- **Core**: Business logic and data management
- **GUI**: User interface components
- **Utils**: Reusable utilities and constants

### 2. Modern Design Patterns
- Singleton pattern for config
- Factory methods for button creation
- Private methods (`_method_name`) for internal logic
- Type hints throughout

### 3. Enhanced Maintainability
- Clear module responsibilities
- Well-documented classes and methods
- Centralized styles and constants
- Easy to extend and modify

### 4. Performance Optimizations
- Efficient ad blocking with early CSS injection
- Minimal DOM manipulation
- Optimized button sizes and layouts
- HTTP caching (100MB)

## Usage

### Importing Components

```python
# Import from gui
from .gui import MusicWidget, SettingsDialog

# Import from core
from .core import config, PlayerController

# Import from utils
from .utils import SERVICES, Styles, JavaScriptInjector
```

### Creating the Widget

```python
# Simple instantiation
widget = MusicWidget(controller=None, parent=mw)
widget.show()
```

### Accessing Configuration

```python
from .core import config

# Get setting
default_service = config.get('default_service', 'youtube_music')

# Set setting
config.set('default_service', 'youtube')

# Save to disk
config.save()
```

### Using Styles

```python
from .utils import Styles

# Apply style to widget
button.setStyleSheet(Styles.primary_button())
```

## Migration from Legacy Code

The refactored code maintains backward compatibility with the legacy structure:

- `spotify_web_widget.py` → `gui/music_widget.py`
- `settings_dialog.py` → `gui/settings_dialog.py`
- `config.py` → `core/config.py`
- `spotify_controller.py` → `core/player_controller.py`

All imports in `__init__.py` have been updated to use the new structure.

## Development Guidelines

### Adding New Features

1. **New GUI Component**: Add to `gui/` directory
2. **New Business Logic**: Add to `core/` directory
3. **New Utility**: Add to `utils/` directory

### Code Style

- Use type hints for all function parameters and returns
- Document all public methods with docstrings
- Use private methods (`_method_name`) for internal logic
- Follow PEP 8 naming conventions

### Testing

Test the addon by:
1. Loading in Anki
2. Toggling the widget (Ctrl+Shift+M)
3. Testing playback controls
4. Checking settings dialog
5. Verifying keyboard shortcuts

## Dependencies

- **Anki**: 24.06.3+
- **Python**: 3.9.18+
- **Qt**: 6.6.2+
- **PyQt**: 6.6.1+
- **QWebEngine**: Required for web player

## Future Improvements

Potential areas for enhancement:
- [ ] Add unit tests
- [ ] Add custom URL management UI
- [ ] Add volume control
- [ ] Add playlist support
- [ ] Add theme customization
- [ ] Add more keyboard shortcuts
- [ ] Add mini player mode
