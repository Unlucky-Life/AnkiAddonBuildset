"""
Spotify Anki Addon

Allows you to control Spotify playback from within the Anki reviewer.
Features a toggleable widget with play/pause controls.
"""

try:
    from aqt import mw, gui_hooks
    from aqt.qt import QAction, QKeySequence
    from aqt.utils import showInfo
    from .spotify_widget import SpotifyWidget
except Exception as e:
    # If imports fail (outside Anki or dependencies missing), keep as no-op
    mw = None
    gui_hooks = None
    showInfo = None
    print(f"[spotify_anki] Import error: {e}")


# Global reference to the widget
spotify_widget = None


def toggle_spotify_widget():
    """Toggle the visibility of the Spotify control widget in the reviewer."""
    global spotify_widget
    
    if showInfo:
        showInfo("[DEBUG] toggle_spotify_widget called")
    
    if not mw:
        if showInfo:
            showInfo("[DEBUG] mw is None")
        return
    
    # Get the reviewer if it exists
    reviewer = getattr(mw, 'reviewer', None)
    if not reviewer:
        if showInfo:
            showInfo("[DEBUG] Reviewer not found. Please open the reviewer first.")
        return
    
    if showInfo:
        showInfo(f"[DEBUG] Reviewer found: {reviewer}")
    
    # Create widget if it doesn't exist
    if spotify_widget is None:
        try:
            if showInfo:
                showInfo("[DEBUG] Creating new widget...")
            spotify_widget = SpotifyWidget(reviewer.web)
            if showInfo:
                showInfo(f"[DEBUG] Widget created: {spotify_widget}")
        except Exception as e:
            if showInfo:
                showInfo(f"[DEBUG] Error creating widget: {e}")
            print(f"[spotify_anki] Error creating widget: {e}")
            return
    
    # Toggle visibility
    if spotify_widget.isVisible():
        if showInfo:
            showInfo("[DEBUG] Hiding widget")
        spotify_widget.hide()
    else:
        if showInfo:
            showInfo("[DEBUG] Showing widget")
        spotify_widget.show()


def setup_menu_action():
    """Add a menu action to toggle the Spotify widget."""
    if not mw:
        return
    
    try:
        # Create action in Tools menu
        action = QAction("Toggle Spotify Widget", mw)
        action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        action.triggered.connect(toggle_spotify_widget)
        
        # Add to Tools menu
        mw.form.menuTools.addAction(action)
    except Exception as e:
        print(f"[spotify_anki] Error setting up menu: {e}")


def on_reviewer_shown():
    """Hook called when reviewer is shown - ensure widget is attached."""
    global spotify_widget
    
    if not mw:
        return
    
    reviewer = getattr(mw, 'reviewer', None)
    if not reviewer:
        return
    
    # Create widget if needed and was previously visible
    if spotify_widget is None or not spotify_widget.parent():
        try:
            # Create new widget instance when entering reviewer
            spotify_widget = SpotifyWidget(reviewer.web)
            # Start hidden by default
            spotify_widget.hide()
        except Exception as e:
            print(f"[spotify_anki] Error in reviewer shown hook: {e}")


# Register menu action when addon loads
if mw:
    setup_menu_action()

# Register hooks
if gui_hooks:
    try:
        # Hook when reviewer is shown to ensure widget is ready
        gui_hooks.reviewer_did_show_question.append(lambda _: on_reviewer_shown())
    except Exception as e:
        print(f"[spotify_anki] Error registering hooks: {e}")
