"""
Configuration management for Spotify Anki addon.
Handles settings storage and retrieval.
"""

import json
from pathlib import Path
from aqt import mw


class Config:
    """Manages addon configuration."""
    
    # Default settings
    DEFAULTS = {
        'shortcut_play_pause': 'Space',
        'shortcut_next': 'Shift+Right',
        'shortcut_previous': 'Shift+Left',
        'default_service': 'spotify',
        'widget_width': 450,
        'widget_height': 600,
    }
    
    def __init__(self):
        """Initialize configuration."""
        self.config_file = self._get_config_path()
        self.settings = self.load()
    
    def _get_config_path(self):
        """Get the path to the config file."""
        if mw:
            addon_dir = Path(mw.pm.addonFolder()) / 'spotify_anki'
            addon_dir.mkdir(exist_ok=True)
            return addon_dir / 'config.json'
        return Path('config.json')
    
    def load(self):
        """Load settings from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.DEFAULTS, **settings}
            except Exception as e:
                print(f"[spotify_anki] Error loading config: {e}")
        
        return self.DEFAULTS.copy()
    
    def save(self):
        """Save settings to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"[spotify_anki] Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value."""
        self.settings[key] = value
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.settings = self.DEFAULTS.copy()
        self.save()


# Global config instance
config = Config()
