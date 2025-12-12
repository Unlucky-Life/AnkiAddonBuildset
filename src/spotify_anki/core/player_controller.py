"""Player controller for managing music playback.

This module provides a simplified player controller that maintains compatibility
with legacy code while the actual playback control has been migrated to JavaScript
injection in the web view.

Historical Context:
    Originally, this module interfaced with the Spotify API for playback control.
    However, API-based control caused conflicts with the web player and required
    Premium accounts. The functionality has been replaced with direct JavaScript
    manipulation of the web player interface.

Current Purpose:
    - Maintain API compatibility with older code
    - Provide a placeholder for potential future enhancements
    - Serve as a configuration storage location

The controller intentionally returns False for all control methods to signal
that JavaScript-based control should be used instead.

Note:
    All actual playback control is handled by the MusicWidget class via
    JavaScript injection. This controller is maintained only for compatibility.
"""

import os
from aqt import mw


class PlayerController:
    """
    Simplified player controller.
    Currently used only for maintaining compatibility with existing code.
    All actual playback control is done via JavaScript injection in the widget.
    """
    
    def __init__(self, config_dir=None):
        """Initialize the player controller.
        
        Creates the configuration directory if it doesn't exist. The directory
        can be used to store tokens, credentials, or other persistent state
        related to music services.
        
        Args:
            config_dir (str, optional): Path to the configuration directory.
                If None, defaults to 'spotify_anki' in the Anki addon folder.
        
        Side Effects:
            - Creates the config_dir directory if it doesn't exist
            - Sets self.config_dir attribute
        
        Examples:
            >>> controller = PlayerController()  # Uses default path
            >>> controller = PlayerController('/custom/path')  # Custom path
        """
        self.config_dir = config_dir or os.path.join(mw.pm.addonFolder(), 'spotify_anki')
        os.makedirs(self.config_dir, exist_ok=True)
    
    def is_configured(self):
        """Check if the controller is configured for API-based control.
        
        Returns:
            bool: Always returns False since API-based control is disabled.
        
        Note:
            This method exists for compatibility with code that checks whether
            API control is available. Since we've moved to JavaScript-based
            control, this always returns False.
        
        Examples:
            >>> controller.is_configured()
            False
        """
        return False
    
    def toggle_playback(self):
        """Toggle playback state via API.
        
        Returns:
            bool: Always returns False to indicate JavaScript control should
                be used instead.
        
        Note:
            This method does NOT actually control playback. It exists only
            for API compatibility. Callers should check the return value and
            fall back to JavaScript-based control.
        
        Examples:
            >>> if not controller.toggle_playback():
            ...     # Use JavaScript control
            ...     web_view.page().runJavaScript(play_pause_script)
        """
        return False
    
    def next_track(self):
        """Skip to the next track via API.
        
        Returns:
            bool: Always returns False to indicate JavaScript control should
                be used instead.
        
        Note:
            This method does NOT actually skip to the next track. It exists
            only for API compatibility. Callers should check the return value
            and fall back to JavaScript-based control.
        
        Examples:
            >>> if not controller.next_track():
            ...     # Use JavaScript control
            ...     web_view.page().runJavaScript(next_track_script)
        """
        return False
    
    def previous_track(self):
        """Skip to the previous track via API.
        
        Returns:
            bool: Always returns False to indicate JavaScript control should
                be used instead.
        
        Note:
            This method does NOT actually skip to the previous track. It
            exists only for API compatibility. Callers should check the
            return value and fall back to JavaScript-based control.
        
        Examples:
            >>> if not controller.previous_track():
            ...     # Use JavaScript control
            ...     web_view.page().runJavaScript(previous_track_script)
        """
        return False
