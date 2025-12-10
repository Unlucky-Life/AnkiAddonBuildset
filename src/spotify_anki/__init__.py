"""
Spotify Anki Addon

Allows you to control Spotify playback from within the Anki reviewer.
Features a toggleable widget with play/pause controls.
"""

from typing import Optional
from aqt import mw
from aqt.qt import QAction

from .spotify_widget import SpotifyWidget
from .hooks import register_hooks, setup_reviewer_shortcut

# Global reference to the widget
spotify_widget: Optional[SpotifyWidget] = None


def show_spotify_widget() -> None:
    """Create and show the Spotify widget if it doesn't exist."""
    global spotify_widget

    if not spotify_widget:
        spotify_widget = SpotifyWidget()
        spotify_widget.setParent(mw)
        spotify_widget.setWindowFlags(spotify_widget.windowFlags())
        update_widget_position()
        spotify_widget.show()
        spotify_widget.raise_()


def hide_spotify_widget() -> None:
    """Hide and destroy the Spotify widget."""
    global spotify_widget

    if spotify_widget:
        spotify_widget.close()
        spotify_widget.setParent(None)
        spotify_widget = None


def toggle_spotify_widget() -> None:
    """Toggle the Spotify widget visibility."""
    global spotify_widget

    if spotify_widget:
        if spotify_widget.isVisible():
            spotify_widget.hide()
        else:
            spotify_widget.show()
            spotify_widget.raise_()
    else:
        show_spotify_widget()


def update_widget_position() -> None:
    """Update the widget position based on screen size."""
    global spotify_widget

    if not spotify_widget or not mw:
        return

    # Position in bottom-right corner
    mw_width = mw.width()
    mw_height = mw.height()
    widget_width = 250
    widget_height = 200
    margin = 20

    x = mw_width - widget_width - margin
    y = mw_height - widget_height - margin
    
    spotify_widget.move(x, y)


def setup_menu() -> None:
    """Add menu item to Anki's Tools menu."""
    action = QAction("Toggle Spotify Widget", mw)
    action.triggered.connect(toggle_spotify_widget)
    mw.form.menuTools.addAction(action)


# Set up the reviewer shortcut for toggling the widget
setup_reviewer_shortcut(toggle_spotify_widget)

# Register all hooks
register_hooks(setup_menu)
