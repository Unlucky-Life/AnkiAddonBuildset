"""
Spotify API integration module.

Uses spotipy library to interact with Spotify Web API.
Handles authentication and playback control.
"""

import os
import json
from pathlib import Path

try:
    # Try to import from local bundled spotipy first
    from . import spotipy
    from .spotipy.oauth2 import SpotifyOAuth
except ImportError:
    try:
        # Fallback to globally installed spotipy
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
    except ImportError:
        spotipy = None
        SpotifyOAuth = None


class SpotifyController:
    """Manages Spotify API connection and playback control."""
    
    def __init__(self, config_dir):
        """
        Initialize Spotify controller.
        
        Args:
            config_dir: Directory to store config and cache files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "spotify_config.json"
        self.cache_file = self.config_dir / ".spotify_cache"
        
        self.sp = None
        self.config = self._load_config()
        
        if spotipy and self.config.get('client_id') and self.config.get('client_secret'):
            self._initialize_spotify()
    
    def _load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[spotify_anki] Error loading config: {e}")
        
        # Default config
        return {
            'client_id': '',
            'client_secret': '',
            'redirect_uri': 'http://localhost:8888/callback'
        }
    
    def save_config(self, client_id, client_secret, redirect_uri='http://localhost:8888/callback'):
        """Save Spotify API credentials."""
        self.config = {
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            # Initialize after saving
            if spotipy:
                self._initialize_spotify()
            return True
        except Exception as e:
            print(f"[spotify_anki] Error saving config: {e}")
            return False
    
    def _initialize_spotify(self):
        """Initialize Spotify API client with OAuth."""
        if not spotipy:
            print("[spotify_anki] spotipy not installed. Run: pip install spotipy")
            return
        
        try:
            scope = "user-read-playback-state,user-modify-playback-state"
            
            auth_manager = SpotifyOAuth(
                client_id=self.config['client_id'],
                client_secret=self.config['client_secret'],
                redirect_uri=self.config['redirect_uri'],
                scope=scope,
                cache_path=str(self.cache_file)
            )
            
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
        except Exception as e:
            print(f"[spotify_anki] Spotify initialization error: {e}")
            self.sp = None
    
    def is_configured(self):
        """Check if Spotify is configured and connected."""
        return self.sp is not None
    
    def get_current_playback(self):
        """Get current playback state."""
        if not self.sp:
            return None
        
        try:
            return self.sp.current_playback()
        except Exception as e:
            print(f"[spotify_anki] Error getting playback: {e}")
            return None
    
    def is_playing(self):
        """Check if Spotify is currently playing."""
        playback = self.get_current_playback()
        return playback and playback.get('is_playing', False)
    
    def play(self):
        """Resume playback."""
        if not self.sp:
            return False
        
        try:
            self.sp.start_playback()
            return True
        except Exception as e:
            print(f"[spotify_anki] Error starting playback: {e}")
            return False
    
    def pause(self):
        """Pause playback."""
        if not self.sp:
            return False
        
        try:
            self.sp.pause_playback()
            return True
        except Exception as e:
            print(f"[spotify_anki] Error pausing playback: {e}")
            return False
    
    def toggle_playback(self):
        """Toggle between play and pause."""
        if self.is_playing():
            return self.pause()
        else:
            return self.play()
    
    def next_track(self):
        """Skip to next track."""
        if not self.sp:
            return False
        
        try:
            self.sp.next_track()
            return True
        except Exception as e:
            print(f"[spotify_anki] Error skipping track: {e}")
            return False
    
    def previous_track(self):
        """Go to previous track."""
        if not self.sp:
            return False
        
        try:
            self.sp.previous_track()
            return True
        except Exception as e:
            print(f"[spotify_anki] Error going to previous track: {e}")
            return False
    
    def get_current_track_info(self):
        """Get information about the currently playing track."""
        playback = self.get_current_playback()
        if not playback or not playback.get('item'):
            return None
        
        item = playback['item']
        artists = ', '.join([artist['name'] for artist in item.get('artists', [])])
        
        return {
            'name': item.get('name', 'Unknown'),
            'artist': artists,
            'album': item.get('album', {}).get('name', 'Unknown'),
            'is_playing': playback.get('is_playing', False),
            'progress_ms': playback.get('progress_ms', 0),
            'duration_ms': item.get('duration_ms', 0)
        }
