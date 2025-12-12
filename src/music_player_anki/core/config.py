"""Configuration management for Music Player addon.

This module provides a centralized configuration management system for the Music Player
addon. It handles loading, saving, and accessing user settings with a JSON-based
persistence layer.

The configuration system supports:
    - Keyboard shortcut customization
    - Default service selection (YouTube Music/YouTube)
    - Widget dimensions
    - Custom URL management
    - Automatic migration from legacy settings

All settings are stored in a JSON file in the addon's data directory and are
automatically merged with default values to ensure compatibility across updates.

Typical usage example:
    >>> from core.config import config
    >>> shortcut = config.get('shortcut_play_pause', 'Space')
    >>> config.set('default_service', 'youtube')
    >>> config.save()
"""

import json
from pathlib import Path
from aqt import mw


class Config:
    """Manages addon configuration with JSON persistence.
    
    This class implements a singleton-like configuration manager that handles
    loading, saving, and accessing user settings. Settings are stored in a JSON
    file within the addon's data directory and are automatically merged with
    default values to ensure all required keys exist.
    
    The configuration system is designed to be:
        - Thread-safe for reads (writes should be done from main thread)
        - Backward compatible (new defaults are added automatically)
        - User-friendly (invalid configs fall back to defaults)
    
    Attributes:
        DEFAULTS (dict): Default configuration values. These are used when no
            configuration file exists or when required keys are missing.
        config_file (Path): Path to the JSON configuration file.
        settings (dict): Current configuration dictionary with all settings.
    
    Examples:
        >>> config = Config()
        >>> play_pause = config.get('shortcut_play_pause', 'Space')
        >>> config.set('default_service', 'youtube_music')
        >>> config.save()
    """
    
    # Default settings
    DEFAULTS = {
        'shortcut_play_pause': 'Ctrl+Shift+R',
        'shortcut_next': 'Ctrl+Shift+Right',
        'shortcut_previous': 'Ctrl+Shift+Left',
        'shortcut_toggle': 'Ctrl+Shift+M',
        'shortcut_volume_up': 'Ctrl+Shift+Up',
        'shortcut_volume_down': 'Ctrl+Shift+Down',
        'default_service': 'youtube_music',
        'widget_width': 700,
        'widget_height': 550,
        'custom_urls': [],  # List of dicts with 'name' and 'url' keys
    }
    
    def __init__(self):
        """Initialize the configuration manager.
        
        Determines the configuration file path and loads existing settings
        from disk. If no configuration file exists, defaults are used.
        
        Side Effects:
            - Sets self.config_file to the configuration file path
            - Loads settings from disk into self.settings
            - May create the addon directory if it doesn't exist
        """
        self.config_file = self._get_config_path()
        self.settings = self.load()
    
    def _get_config_path(self):
        """Get the path to the configuration file.
        
        Constructs the full path to config.json within the addon's data directory.
        If the Anki main window is available, uses the profile's addon folder.
        Otherwise, falls back to a local config.json file (mainly for testing).
        
        Returns:
            Path: Path object pointing to config.json in the addon directory.
        
        Side Effects:
            - May create the addon directory if it doesn't exist (via mkdir)
        
        Note:
            The directory name 'music_player_anki' is retained for backward compatibility
            even though the addon is now called "Music Player".
        """
        if mw:
            addon_dir = Path(mw.pm.addonFolder()) / 'music_player_anki'
            addon_dir.mkdir(exist_ok=True)
            return addon_dir / 'config.json'
        return Path('config.json')
    
    def load(self):
        """Load settings from the configuration file.
        
        Reads the JSON configuration file and merges it with DEFAULTS to ensure
        all required keys exist. If the file doesn't exist or cannot be read,
        returns a copy of DEFAULTS.
        
        Returns:
            dict: Configuration dictionary with all settings. This is always a
                complete configuration (defaults + user settings) even if the
                file is missing or malformed.
        
        Note:
            User settings take precedence over defaults. New default keys added
            in updates are automatically included even if not in the saved file.
            
            Errors during file reading are logged but don't raise exceptions -
            the function returns defaults instead.
        
        Examples:
            >>> settings = config.load()
            >>> print(settings['default_service'])
            'youtube_music'
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.DEFAULTS, **settings}
            except Exception as e:
                print(f"[music_player] Error loading config: {e}")
        
        return self.DEFAULTS.copy()
    
    def save(self):
        """Save current settings to the configuration file.
        
        Writes the current settings dictionary to disk as formatted JSON with
        2-space indentation for readability.
        
        Returns:
            bool: True if save was successful, False if an error occurred.
        
        Note:
            Errors during file writing are logged to console but don't raise
            exceptions. The return value indicates success/failure.
            
            File permissions issues or disk space problems may cause save to fail.
        
        Examples:
            >>> config.set('default_service', 'youtube')
            >>> if config.save():
            ...     print("Settings saved successfully")
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"[music_player] Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a configuration value by key.
        
        Retrieves the value for the specified configuration key. If the key
        doesn't exist, returns the provided default value.
        
        Args:
            key (str): The configuration key to look up. Should match a key
                in DEFAULTS or a user-defined key.
            default: The value to return if the key doesn't exist. Defaults
                to None.
        
        Returns:
            The value associated with the key, or the default value if the
            key is not found.
        
        Examples:
            >>> shortcut = config.get('shortcut_play_pause', 'Space')
            >>> service = config.get('default_service')
        """
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value.
        
        Updates the value for the specified configuration key. This only updates
        the in-memory settings dictionary - call save() to persist to disk.
        
        Args:
            key (str): The configuration key to set. Can be any string, though
                it's recommended to use keys defined in DEFAULTS.
            value: The value to associate with the key. Can be any JSON-serializable
                type (str, int, bool, list, dict, etc.).
        
        Note:
            Changes are not persisted until save() is called. Multiple set()
            calls can be made before saving to batch updates.
        
        Examples:
            >>> config.set('default_service', 'youtube_music')
            >>> config.set('shortcut_toggle', 'Ctrl+M')
            >>> config.save()  # Persist all changes
        """
        self.settings[key] = value
    
    def reset_to_defaults(self):
        """Reset all settings to their default values.
        
        Replaces the current settings with a fresh copy of DEFAULTS and
        immediately saves to disk. This permanently removes all custom
        settings.
        
        Side Effects:
            - Replaces self.settings with a copy of DEFAULTS
            - Saves the configuration file immediately
            - All user customizations are permanently lost
        
        Warning:
            This operation cannot be undone. All custom settings including
            keyboard shortcuts and service preferences will be lost.
        
        Examples:
            >>> config.reset_to_defaults()
            # All settings restored to defaults and saved
        """
        self.settings = self.DEFAULTS.copy()
        self.save()


# Global config instance
config = Config()

