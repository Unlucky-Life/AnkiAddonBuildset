"""Anki integration hooks for the Music Player addon.

This module manages all integration points between the addon and Anki's
event system. It handles:
    - Widget visibility management during state transitions
    - Global keyboard shortcut registration
    - Reviewer-specific shortcuts injection
    - Addon reload functionality for development

The hooks ensure the music widget appears/disappears at appropriate times
and responds to user actions correctly throughout the Anki workflow.

Key Responsibilities:
    - Show/hide widget based on Anki state (review vs other)
    - Register global shortcuts via QShortcut
    - Inject reviewer shortcuts via Reviewer._shortcutKeys wrapping
    - Handle addon reloading without restarting Anki

Architecture:
    - Uses weak references to main module to avoid circular imports
    - Stores global shortcuts to prevent garbage collection
    - Wraps Anki methods non-invasively using anki.hooks.wrap

Typical usage (called from __init__.py):
    >>> from . import hooks
    >>> hooks.setup_reviewer_shortcut(toggle_widget_callback)
    >>> hooks.register_hooks()
"""

import sys
import traceback
from typing import Callable

from aqt import mw, gui_hooks
from aqt.qt import QKeySequence, QShortcut, Qt
from aqt.reviewer import Reviewer
from anki.hooks import wrap

from .utils.logger import log_info, log_error, log_debug

_MAIN_MODULE_NAME = "music_player_anki"
_global_shortcuts = []


def _get_main_module():
    """Get reference to the main addon module.
    
    Uses sys.modules to retrieve the main addon module without direct import,
    avoiding circular dependencies. Returns None if module not loaded.
    
    Returns:
        module: The music_player_anki module if loaded, None otherwise.
    
    Examples:
        >>> main = _get_main_module()
        >>> if main:
        ...     widget = main.music_widget
    """
    return sys.modules.get(_MAIN_MODULE_NAME)


def on_reviewer_show(card) -> None:
    """Handle reviewer show event to update widget position.
    
    Called by Anki when a card is shown in the reviewer. Updates the music
    widget's position to ensure it's correctly placed on screen.
    
    Args:
        card: The Anki card being shown (required by hook signature).
    
    Side Effects:
        - Calls update_widget_position() on main module if widget exists
        - Logs errors to console if issues occur
    
    Examples:
        >>> gui_hooks.reviewer_did_show_question.append(on_reviewer_show)
    """
    main_module = _get_main_module()
    if not main_module:
        return
    try:
        music_widget = main_module.music_widget
        if music_widget:
            main_module.update_widget_position()
    except Exception as e:
        log_error(f"Error in reviewer show hook: {e}", e)
        traceback.print_exc()


def cleanup_widget(state: str, old_state: str) -> None:
    """Hide widget when leaving review state.
    
    Called by Anki when the application state changes. Hides the music widget
    if the new state is not 'review', ensuring it only appears during study.
    
    Args:
        state: The new Anki state (e.g., 'review', 'deckBrowser', 'overview').
        old_state: The previous Anki state.
    
    Side Effects:
        - Hides music_widget if state != 'review'
        - Logs errors to console if issues occur
    
    Examples:
        >>> gui_hooks.state_did_change.append(cleanup_widget)
    """
    main_module = _get_main_module()
    if not main_module:
        return
    try:
        music_widget = getattr(main_module, 'music_widget', None)
        if state != "review" and music_widget:
            music_widget.hide()
    except Exception as e:
        log_error(f"Error in cleanup hook: {e}", e)
        traceback.print_exc()


def setup_reviewer_shortcut(toggle_callback: Callable[[], None]) -> None:
    """Set up keyboard shortcut for toggling widget in reviewer.
    
    Wraps Reviewer._shortcutKeys to inject custom toggle shortcut. This allows
    the widget toggle to work within the review interface using the configured
    keyboard shortcut (default: Ctrl+Shift+M).
    
    Args:
        toggle_callback: Function to call when shortcut is pressed.
    
    Side Effects:
        - Wraps Reviewer._shortcutKeys method
        - Adds toggle shortcut to reviewer's shortcut list
        - Reads 'shortcut_toggle' from config
    
    Note:
        Uses anki.hooks.wrap to non-invasively modify Anki's behavior.
        The shortcut only works while in review mode.
    
    Examples:
        >>> setup_reviewer_shortcut(lambda: print("Toggled!"))
    """
    def _shortcutKeys_wrap(self, _old):
        original = _old(self)
        from .core.config import config
        toggle_seq = config.get('shortcut_toggle', 'Ctrl+Shift+M')
        original.append((toggle_seq, lambda: toggle_callback()))
        return original
    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, _shortcutKeys_wrap, 'around')

def register_hooks(setup_menu_callback: Callable[[], None]) -> None:
    """Register all Anki hooks for the addon."""
    
    # Register reviewer hooks
    gui_hooks.reviewer_did_show_question.append(on_reviewer_show)
    
    # Register state change hooks
    gui_hooks.state_did_change.append(cleanup_widget)
    
    # Register initialization hooks
    gui_hooks.main_window_did_init.append(setup_menu_callback)


def setup_global_shortcuts(
    toggle_callback: Callable[[], None],
    play_pause_callback: Callable[[], None],
    next_callback: Callable[[], None],
    prev_callback: Callable[[], None],
    volume_up_callback: Callable[[], None],
    volume_down_callback: Callable[[], None]
) -> None:
    """
    Set up global shortcuts that work even when widget is not focused.
    These shortcuts work everywhere in Anki.
    """
    from .core.config import config
    
    log_info("Setting up global shortcuts")
    
    # Get configured shortcuts
    toggle_seq = config.get('shortcut_toggle', 'Ctrl+Shift+M')
    play_pause_seq = config.get('shortcut_play_pause', 'Ctrl+Shift+R')
    next_seq = config.get('shortcut_next', 'Ctrl+Shift+Right')
    prev_seq = config.get('shortcut_previous', 'Ctrl+Shift+Left')
    volume_up_seq = config.get('shortcut_volume_up', 'Ctrl+Shift+Up')
    volume_down_seq = config.get('shortcut_volume_down', 'Ctrl+Shift+Down')
    
    log_debug(f"Configured shortcuts:")
    log_debug(f"  Toggle: {toggle_seq}")
    log_debug(f"  Play/Pause: {play_pause_seq}")
    log_debug(f"  Next: {next_seq}")
    log_debug(f"  Previous: {prev_seq}")
    log_debug(f"  Volume Up: {volume_up_seq}")
    log_debug(f"  Volume Down: {volume_down_seq}")
    
    # Create debug wrapper to test if shortcuts are actually firing
    def debug_wrapper(name, callback):
        def wrapper():
            log_debug(f"{name} shortcut triggered!")
            try:
                callback()
            except Exception as e:
                log_error(f"Error in {name} shortcut callback", e)
                traceback.print_exc()
        return wrapper
    
    # Create global shortcuts - these work from anywhere in Anki
    
    # Toggle widget shortcut
    toggle_shortcut = QShortcut(QKeySequence(toggle_seq), mw)
    toggle_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
    toggle_shortcut.activated.connect(debug_wrapper("Toggle", toggle_callback))
    _global_shortcuts.append(toggle_shortcut)
    
    # Play/Pause shortcut
    play_pause_shortcut = QShortcut(QKeySequence(play_pause_seq), mw)
    play_pause_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
    play_pause_shortcut.activated.connect(debug_wrapper("Play/Pause", play_pause_callback))
    _global_shortcuts.append(play_pause_shortcut)
    
    # Next track shortcut
    next_shortcut = QShortcut(QKeySequence(next_seq), mw)
    next_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
    next_shortcut.activated.connect(debug_wrapper("Next", next_callback))
    _global_shortcuts.append(next_shortcut)
    
    # Previous track shortcut
    prev_shortcut = QShortcut(QKeySequence(prev_seq), mw)
    prev_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
    prev_shortcut.activated.connect(debug_wrapper("Previous", prev_callback))
    _global_shortcuts.append(prev_shortcut)
    
    # Volume up shortcut
    volume_up_shortcut = QShortcut(QKeySequence(volume_up_seq), mw)
    volume_up_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
    volume_up_shortcut.activated.connect(debug_wrapper("Volume Up", volume_up_callback))
    _global_shortcuts.append(volume_up_shortcut)
    
    # Volume down shortcut
    volume_down_shortcut = QShortcut(QKeySequence(volume_down_seq), mw)
    volume_down_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
    volume_down_shortcut.activated.connect(debug_wrapper("Volume Down", volume_down_callback))
    _global_shortcuts.append(volume_down_shortcut)
    
    log_info(f"Global shortcuts registered successfully:")
    log_info(f"  Toggle widget: {toggle_seq}")
    log_info(f"  Play/Pause: {play_pause_seq}")
    log_info(f"  Next track: {next_seq}")
    log_info(f"  Previous track: {prev_seq}")
    log_info(f"  Volume Up: {volume_up_seq}")
    log_info(f"  Volume Down: {volume_down_seq}")
