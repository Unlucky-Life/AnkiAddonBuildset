"""
Spotify Anki Addon

Allows you to control Spotify playback from within the Anki reviewer.
Features a toggleable widget with play/pause controls.
"""

from typing import Optional
from aqt import mw
from aqt.qt import QAction

from .spotify_web_widget import SpotifyWebWidget
from .hooks import register_hooks, setup_reviewer_shortcut, setup_global_shortcuts

# Global reference to the widget
spotify_widget: Optional[SpotifyWebWidget] = None


def show_spotify_widget() -> None:
    """Create and show the Spotify widget if it doesn't exist."""
    global spotify_widget

    if not spotify_widget:
        spotify_widget = SpotifyWebWidget()
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


def play_pause_from_global() -> None:
    """Play/pause from global shortcut (works even if widget is hidden)."""
    global spotify_widget
    
    if not spotify_widget:
        show_spotify_widget()
    
    if spotify_widget:
        spotify_widget.toggle_playback()


def next_track_from_global() -> None:
    """Next track from global shortcut (works even if widget is hidden)."""
    global spotify_widget
    
    if not spotify_widget:
        show_spotify_widget()
    
    if spotify_widget:
        spotify_widget.next_track()


def previous_track_from_global() -> None:
    """Previous track from global shortcut (works even if widget is hidden)."""
    global spotify_widget
    
    if not spotify_widget:
        show_spotify_widget()
    
    if spotify_widget:
        spotify_widget.previous_track()


def update_widget_position() -> None:
    """Update the widget position based on screen size."""
    global spotify_widget

    if not spotify_widget or not mw:
        return

    # Position in bottom-right corner
    mw_width = mw.width()
    mw_height = mw.height()
    widget_width = 450
    widget_height = 600
    margin = 20

    x = mw_width - widget_width - margin
    y = mw_height - widget_height - margin
    
    spotify_widget.move(x, y)


def setup_menu() -> None:
    """Add menu items to Anki's Tools menu."""
    # Toggle widget action
    action = QAction("Toggle Spotify Widget", mw)
    action.triggered.connect(toggle_spotify_widget)
    mw.form.menuTools.addAction(action)
    
    # Settings action
    from .settings_dialog import SettingsDialog
    settings_action = QAction("Spotify Addon Settings...", mw)
    settings_action.triggered.connect(lambda: SettingsDialog(mw).exec())
    mw.form.menuTools.addAction(settings_action)
    
    # Reload addon action
    from .hooks import reload_addon
    reload_action = QAction("Reload Spotify Addon", mw)
    reload_action.triggered.connect(reload_addon)
    mw.form.menuTools.addAction(reload_action)


# Set up the reviewer shortcut for toggling the widget
setup_reviewer_shortcut(toggle_spotify_widget)

# Set up global shortcuts that work everywhere in Anki
setup_global_shortcuts(
    toggle_callback=toggle_spotify_widget,
    play_pause_callback=play_pause_from_global,
    next_callback=next_track_from_global,
    prev_callback=previous_track_from_global
)

# Register all hooks
register_hooks(setup_menu)
