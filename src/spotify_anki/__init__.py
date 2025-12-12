"""Music Player Anki Addon.

A modern, minimalistic music player widget for Anki that provides seamless integration
with YouTube Music and YouTube. The addon features a sleek, frameless interface with
comprehensive ad blocking, keyboard shortcuts, and persistent session management.

This addon allows users to:
    - Listen to music while studying in Anki
    - Control playback with keyboard shortcuts
    - Switch between YouTube Music and YouTube
    - Block advertisements automatically
    - Maintain persistent login sessions

The widget is designed to be unobtrusive, appearing in the bottom-right corner of the
Anki window and can be easily toggled on/off with a keyboard shortcut.

Attributes:
    __version__ (str): Current version of the addon.
    __author__ (str): Author or team name.
    music_widget (Optional[MusicWidget]): Global reference to the music widget instance.
    player_controller (Optional[PlayerController]): Global reference to the player controller.

Examples:
    Toggle the music widget from any Anki view:
        >>> # Press Ctrl+Shift+M (default shortcut)
    
    Control playback:
        >>> # Press Space for play/pause
        >>> # Press Shift+Right for next track
        >>> # Press Shift+Left for previous track

Note:
    Requires QWebEngineView to be available in the Qt installation.
    The addon stores persistent cookies and cache in the Anki profile directory.
"""

from typing import Optional
from aqt import mw
from aqt.qt import QAction

from .gui import MusicWidget, SettingsDialog
from .core import PlayerController
from .hooks import register_hooks, setup_reviewer_shortcut, setup_global_shortcuts

# Addon metadata
__version__ = "2.0.0"
__author__ = "Music Player Team"

# Global references
music_widget: Optional[MusicWidget] = None
player_controller: Optional[PlayerController] = None


def get_player_controller() -> PlayerController:
    """
    Get or create the player controller.
    
    Returns:
        PlayerController instance
    """
    global player_controller
    
    if not player_controller:
        import os
        addon_dir = mw.pm.addonFolder()
        config_dir = os.path.join(addon_dir, 'spotify_anki')
        player_controller = PlayerController(config_dir)
    
    return player_controller


def show_music_widget() -> None:
    """Create and show the music widget if it doesn't exist.
    
    Creates a new MusicWidget instance if one doesn't already exist, positions it
    in the bottom-right corner of the Anki main window, and makes it visible.
    The widget is parented to the main Anki window and configured with appropriate
    window flags for a frameless, always-on-top appearance.
    
    The widget will load the default service (YouTube Music or YouTube) as configured
    in the addon settings and restore any previous login session from persistent cookies.
    
    Note:
        This function is idempotent - calling it multiple times will not create
        multiple widget instances. Use toggle_music_widget() to show/hide an
        existing widget.
    
    Side Effects:
        - Sets the global music_widget variable
        - Creates a new MusicWidget instance
        - Positions the widget in the bottom-right corner
        - Makes the widget visible and brings it to front
    
    Examples:
        >>> show_music_widget()
        # Widget appears in bottom-right corner
    """
    global music_widget

    if not music_widget:
        controller = get_player_controller()
        music_widget = MusicWidget(controller=controller)
        music_widget.setParent(mw)
        music_widget.setWindowFlags(music_widget.windowFlags())
        update_widget_position()
        music_widget.show()
        music_widget.raise_()


def hide_music_widget() -> None:
    """Hide and destroy the music widget.
    
    Closes and destroys the current music widget instance if one exists,
    freeing up memory and system resources. The widget's state (including
    login session) is preserved in persistent storage and will be restored
    when the widget is shown again.
    
    Note:
        This function is safe to call even if no widget exists. It will
        simply do nothing in that case.
    
    Side Effects:
        - Closes the widget window
        - Removes the widget's parent reference
        - Sets the global music_widget variable to None
        - Triggers Qt cleanup of the widget and its resources
    
    Examples:
        >>> hide_music_widget()
        # Widget is closed and destroyed
    """
    global music_widget

    if music_widget:
        music_widget.close()
        music_widget.setParent(None)
        music_widget = None


def toggle_music_widget() -> None:
    """Toggle the music widget visibility.
    
    Shows the widget if it's currently hidden or doesn't exist, and hides it
    if it's currently visible. This is the primary function for controlling
    widget visibility and is bound to the global keyboard shortcut (default:
    Ctrl+Shift+M).
    
    The function intelligently handles three cases:
        1. Widget doesn't exist: Creates and shows a new widget
        2. Widget exists but is hidden: Shows and raises the widget
        3. Widget exists and is visible: Hides the widget
    
    Note:
        When showing an existing hidden widget, it's brought to the front
        using raise_() to ensure it's visible above other windows.
    
    Side Effects:
        - May create a new widget instance
        - Changes widget visibility state
        - May bring widget to front of window stack
    
    Examples:
        >>> toggle_music_widget()  # Shows widget if hidden
        >>> toggle_music_widget()  # Hides widget if visible
    """
    global music_widget

    if music_widget:
        if music_widget.isVisible():
            music_widget.hide()
        else:
            music_widget.show()
            music_widget.raise_()
    else:
        show_music_widget()


def play_pause_from_global() -> None:
    """Toggle play/pause state from global shortcut.
    
    Toggles the playback state of the currently loaded music service. If the
    widget doesn't exist, it will be created first. This function is bound to
    the play/pause keyboard shortcut (default: Space) and works even when the
    widget is hidden.
    
    The function executes JavaScript in the web view to:
        1. Find the play/pause button in the page
        2. Click it if found
        3. Fall back to keyboard event dispatch if button not found
    
    Note:
        The widget must be created (though not necessarily visible) for this
        function to work. Audio will continue playing even if the widget is
        hidden after creation.
    
    Side Effects:
        - May create a new widget instance if none exists
        - Executes JavaScript in the widget's web view
        - Changes playback state of the music service
    
    Examples:
        >>> play_pause_from_global()  # Starts playback if paused
        >>> play_pause_from_global()  # Pauses playback if playing
    """
    global music_widget
    
    if not music_widget:
        show_music_widget()
    
    if music_widget:
        music_widget.toggle_playback()


def next_track_from_global() -> None:
    """Skip to next track from global shortcut.
    
    Skips to the next track in the current playlist or queue. If the widget
    doesn't exist, it will be created first. This function is bound to the
    next track keyboard shortcut (default: Shift+Right) and works even when
    the widget is hidden.
    
    The function executes JavaScript in the web view to:
        1. Find the next track button in the page
        2. Click it if found
        3. Fall back to keyboard event dispatch (Shift+N) if button not found
    
    Note:
        The widget must be created (though not necessarily visible) for this
        function to work. The skip action will occur regardless of widget
        visibility.
    
    Side Effects:
        - May create a new widget instance if none exists
        - Executes JavaScript in the widget's web view
        - Advances to next track in the music service
    
    Examples:
        >>> next_track_from_global()  # Skips to next track
    """
    global music_widget
    
    if not music_widget:
        show_music_widget()
    
    if music_widget:
        music_widget.next_track()


def previous_track_from_global() -> None:
    """Skip to previous track from global shortcut.
    
    Skips to the previous track in the current playlist or queue. If the widget
    doesn't exist, it will be created first. This function is bound to the
    previous track keyboard shortcut (default: Shift+Left) and works even when
    the widget is hidden.
    
    The function executes JavaScript in the web view to:
        1. Find the previous track button in the page
        2. Click it if found
        3. Fall back to keyboard event dispatch (Shift+P) if button not found
    
    Note:
        The widget must be created (though not necessarily visible) for this
        function to work. The skip action will occur regardless of widget
        visibility.
    
    Side Effects:
        - May create a new widget instance if none exists
        - Executes JavaScript in the widget's web view
        - Returns to previous track in the music service
    
    Examples:
        >>> previous_track_from_global()  # Skips to previous track
    """
    global music_widget
    
    if not music_widget:
        show_music_widget()
    
    if music_widget:
        music_widget.previous_track()


def update_widget_position() -> None:
    """Update the widget position to bottom-right corner.
    
    Calculates the appropriate position for the music widget based on the
    current size of the Anki main window and moves the widget to the
    bottom-right corner with a fixed margin.
    
    The position is calculated as:
        - X: Main window width - widget width (700px) - margin (20px)
        - Y: Main window height - widget height (550px) - margin (20px)
    
    This function is automatically called when:
        - The widget is first created
        - The reviewer shows a new card
        - The main window is resized (if implemented)
    
    Note:
        This function is safe to call even if the widget doesn't exist or
        the main window is not available. It will simply do nothing in
        those cases.
    
    Side Effects:
        - Moves the widget window to a new position
        - Does not resize the widget (dimensions are fixed)
    
    Examples:
        >>> update_widget_position()
        # Widget moves to bottom-right corner with 20px margin
    """
    global music_widget

    if not music_widget or not mw:
        return

    # Position in bottom-right corner with margin
    mw_width = mw.width()
    mw_height = mw.height()
    widget_width = 700
    widget_height = 550
    margin = 20

    x = mw_width - widget_width - margin
    y = mw_height - widget_height - margin
    
    music_widget.move(x, y)


def setup_menu() -> None:
    """Add menu items to Anki's Tools menu.
    
    Creates and adds three menu actions to the Anki Tools menu:
        1. "Toggle Music Player" - Shows/hides the widget
        2. "Music Player Settings..." - Opens the settings dialog
        3. "Reload Music Player Addon" - Reloads the addon code
    
    These menu items provide an alternative to keyboard shortcuts for
    accessing addon functionality and are particularly useful for users
    who prefer mouse interaction or need to modify settings.
    
    The menu items are added in the order listed above and appear at the
    bottom of the Tools menu (after any existing items).
    
    Note:
        This function is called automatically during addon initialization
        via the register_hooks() function. It should not be called manually
        unless re-initializing the addon.
    
    Side Effects:
        - Adds three QAction items to mw.form.menuTools
        - Connects actions to their respective callback functions
    
    Examples:
        After calling setup_menu(), users can access:
        Tools → Toggle Music Player
        Tools → Music Player Settings...
        Tools → Reload Music Player Addon
    """
    # Toggle widget action
    toggle_action = QAction("Toggle Music Player", mw)
    toggle_action.triggered.connect(toggle_music_widget)
    mw.form.menuTools.addAction(toggle_action)
    
    # Settings action
    settings_action = QAction("Music Player Settings...", mw)
    settings_action.triggered.connect(lambda: SettingsDialog(mw).exec())
    mw.form.menuTools.addAction(settings_action)
    
    # Reload addon action
    from .hooks import reload_addon
    reload_action = QAction("Reload Music Player Addon", mw)
    reload_action.triggered.connect(reload_addon)
    mw.form.menuTools.addAction(reload_action)


# Initialize the addon
def initialize() -> None:
    """Initialize the Music Player addon.
    
    Performs all necessary setup for the addon to function correctly within
    Anki. This includes:
        1. Setting up reviewer shortcuts (toggle widget on card review)
        2. Setting up global shortcuts (work everywhere in Anki)
        3. Registering Anki hooks for lifecycle management
    
    The initialization process configures:
        - Toggle widget shortcut (default: Ctrl+Shift+M)
        - Play/pause shortcut (default: Space)
        - Next track shortcut (default: Shift+Right)
        - Previous track shortcut (default: Shift+Left)
        - Reviewer show/hide hooks
        - State change hooks
        - Menu setup hook
    
    This function is called automatically when the addon is loaded by Anki.
    It should not be called manually unless completely re-initializing the
    addon (e.g., after code reload).
    
    Note:
        Shortcuts can be customized via the Settings dialog. The defaults
        listed here can be overridden by user configuration.
    
    Side Effects:
        - Registers keyboard shortcuts with Anki
        - Registers hooks with Anki's hook system
        - Adds menu items to Tools menu
        - Modifies Reviewer._shortcutKeys via wrap()
    
    Examples:
        >>> initialize()
        # Addon is fully initialized and ready to use
    """
    # Set up reviewer shortcut for toggling widget
    setup_reviewer_shortcut(toggle_music_widget)
    
    # Set up global shortcuts that work everywhere in Anki
    setup_global_shortcuts(
        toggle_callback=toggle_music_widget,
        play_pause_callback=play_pause_from_global,
        next_callback=next_track_from_global,
        prev_callback=previous_track_from_global
    )
    
    # Register all hooks
    register_hooks(setup_menu)


# Run initialization
initialize()

