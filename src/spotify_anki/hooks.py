"""
Hooks registration for Spotify Anki addon.
Handles all Anki hook integration and keyboard shortcuts.
"""

import sys
import traceback
from typing import Callable

from aqt import mw, gui_hooks
from aqt.qt import QKeySequence, QShortcut, Qt
from aqt.reviewer import Reviewer
from anki.hooks import wrap

# Module name for reloading
_MAIN_MODULE_NAME = "spotify_anki"

# Keyboard shortcut
TOGGLE_SHORTCUT: str = "ctrl+shift+s"

# Global shortcuts storage
_global_shortcuts = []


def _get_main_module():
    """Get the main addon module from sys.modules."""
    return sys.modules.get(_MAIN_MODULE_NAME)


def on_reviewer_show(card) -> None:
    """Handle when a new card is shown in the reviewer."""
    main_module = _get_main_module()
    if not main_module:
        return
    
    try:
        spotify_widget = main_module.spotify_widget
        
        # Show widget if it was previously visible
        if spotify_widget and not spotify_widget.isVisible():
            # Widget exists but hidden, keep it that way
            pass
        elif not spotify_widget:
            # Widget doesn't exist, don't create it automatically
            # User will toggle it manually with shortcut
            pass
        
        # Update position in case window was resized
        if spotify_widget:
            main_module.update_widget_position()
        
    except Exception as e:
        print(f"[spotify_anki] Error in reviewer show hook: {e}")
        traceback.print_exc()


def cleanup_widget(state: str, old_state: str) -> None:
    """Clean up the widget when leaving review state."""
    main_module = _get_main_module()
    if not main_module:
        return
    
    try:
        spotify_widget = getattr(main_module, 'spotify_widget', None)
        
        # Hide widget when leaving review mode
        if state != "review" and spotify_widget:
            spotify_widget.hide()
    
    except Exception as e:
        print(f"[spotify_anki] Error in cleanup hook: {e}")
        traceback.print_exc()


def setup_reviewer_shortcut(toggle_callback: Callable[[], None]) -> None:
    """Set up the reviewer shortcut by wrapping Reviewer._shortcutKeys."""
    
    def _shortcutKeys_wrap(self, _old):
        """Wrap Reviewer._shortcutKeys to add the toggle shortcut."""
        original = _old(self)
        original.append((TOGGLE_SHORTCUT, lambda: toggle_callback()))
        return original
    
    # Wrap the Reviewer's shortcut keys function
    Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, _shortcutKeys_wrap, 'around')


def reload_addon() -> None:
    """Reload the addon and recreate the widget."""
    main_module = _get_main_module()
    if not main_module:
        return
    
    try:
        # Get the current widget
        spotify_widget = getattr(main_module, 'spotify_widget', None)
        
        # Close and clean up existing widget
        if spotify_widget:
            was_visible = spotify_widget.isVisible()
            spotify_widget.close()
            spotify_widget.setParent(None)
            main_module.spotify_widget = None
            
            # If widget was visible, recreate it
            if was_visible and mw.state == "review":
                main_module.show_spotify_widget()
        
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
                    print(f"[spotify_anki] Error reloading {module_name}: {e}")
        
        print("[spotify_anki] Addon reloaded successfully!")
        
    except Exception as e:
        print(f"[spotify_anki] Error reloading addon: {e}")
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
    from .config import config
    
    # Get configured shortcuts
    toggle_seq = TOGGLE_SHORTCUT
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
