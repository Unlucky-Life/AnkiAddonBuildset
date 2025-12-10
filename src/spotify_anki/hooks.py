"""
Hooks registration for Spotify Anki addon.
Handles all Anki hook integration and keyboard shortcuts.
"""

import sys
import traceback
from typing import Callable

from aqt import mw, gui_hooks
from aqt.reviewer import Reviewer
from anki.hooks import wrap

# Module name for reloading
_MAIN_MODULE_NAME = "spotify_anki"

# Keyboard shortcut
TOGGLE_SHORTCUT: str = "ctrl+shift+s"


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


def register_hooks(setup_menu_callback: Callable[[], None]) -> None:
    """Register all Anki hooks for the addon."""
    
    # Register reviewer hooks
    gui_hooks.reviewer_did_show_question.append(on_reviewer_show)
    
    # Register state change hooks
    gui_hooks.state_did_change.append(cleanup_widget)
    
    # Register initialization hooks
    gui_hooks.main_window_did_init.append(setup_menu_callback)
