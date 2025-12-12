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

_MAIN_MODULE_NAME = "spotify_anki"
_global_shortcuts = []


def _get_main_module():
    """Get reference to the main addon module.
    
    Uses sys.modules to retrieve the main addon module without direct import,
    avoiding circular dependencies. Returns None if module not loaded.
    
    Returns:
        module: The spotify_anki module if loaded, None otherwise.
    
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
        print(f"[music_player] Error in reviewer show hook: {e}")
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
        print(f"[music_player] Error in cleanup hook: {e}")
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


def reload_addon() -> None:
    """Reload the addon without restarting Anki.
    
    Development utility that reloads all addon modules, recreates the widget,
    and restores its visibility state. Useful for testing changes without
    restarting Anki.
    
    Side Effects:
        - Closes and destroys existing widget
        - Reloads all addon modules using importlib.reload
        - Recreates widget if it was visible before reload
        - Prints status messages to console
    
    Note:
        This is primarily for development. Some state may not persist across
        reloads (e.g., web view scroll position).
    
    Examples:
        >>> from spotify_anki import hooks
        >>> hooks.reload_addon()  # Reload after code changes
    """
    main_module = _get_main_module()
    if not main_module:
        return
    
    try:
        # Get the current widget
        music_widget = getattr(main_module, 'music_widget', None)
        
        # Close and clean up existing widget
        if music_widget:
            was_visible = music_widget.isVisible()
            music_widget.close()
            music_widget.setParent(None)
            main_module.music_widget = None
            
            # If widget was visible, recreate it
            if was_visible and mw.state == "review":
                main_module.show_music_widget()
        
        # Reload all modules
        import importlib
        import sys
        
        # Get all submodules
        modules_to_reload = []
        for name, module in sys.modules.items():
            if name.startswith(_MAIN_MODULE_NAME):
                modules_to_reload.append(name)
        
        # Reload in reverse order to handle dependencies
        for module_name in reversed(modules_to_reload):
            if module_name in sys.modules:
                try:
                    importlib.reload(sys.modules[module_name])
                except Exception as e:
                    print(f"[music_player] Error reloading {module_name}: {e}")
        
        print("[music_player] Addon reloaded successfully!")
        
    except Exception as e:
        print(f"[music_player] Error reloading addon: {e}")
        import traceback
        traceback.print_exc()


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
    prev_callback: Callable[[], None]
) -> None:
    """
    Set up global shortcuts that work even when widget is not focused.
    These shortcuts work everywhere in Anki.
    """
    from .core.config import config
    
    # Get configured shortcuts
    toggle_seq = config.get('shortcut_toggle', 'Ctrl+Shift+M')
    play_pause_seq = config.get('shortcut_play_pause', 'Space')
    next_seq = config.get('shortcut_next', 'Shift+Right')
    prev_seq = config.get('shortcut_previous', 'Shift+Left')
    
    # Create global shortcuts - these work from anywhere in Anki
    
    # Toggle widget shortcut (Ctrl+Shift+S)
    toggle_shortcut = QShortcut(QKeySequence(toggle_seq), mw)
    toggle_shortcut.activated.connect(toggle_callback)
    _global_shortcuts.append(toggle_shortcut)
    
    # Play/Pause shortcut (only works outside of text input areas)
    play_pause_shortcut = QShortcut(QKeySequence(play_pause_seq), mw)
    play_pause_shortcut.activated.connect(play_pause_callback)
    _global_shortcuts.append(play_pause_shortcut)
    
    # Next track shortcut (Shift+Right)
    next_shortcut = QShortcut(QKeySequence(next_seq), mw)
    next_shortcut.activated.connect(next_callback)
    _global_shortcuts.append(next_shortcut)
    
    # Previous track shortcut (Shift+Left)
    prev_shortcut = QShortcut(QKeySequence(prev_seq), mw)
    prev_shortcut.activated.connect(prev_callback)
    _global_shortcuts.append(prev_shortcut)
