# Spotify Anki Addon Modifications Summary

## Changes Made

### 1. **Added Zoom Controls to Web Widget**
   - **File**: [spotify_web_widget.py](src/music_player_anki/spotify_web_widget.py)
   - **Changes**:
     - Changed from fixed window size (450x600) to resizable (500x700)
     - Added `zoom_level` instance variable to track zoom state
     - Added two zoom buttons in the header: "🔍-" (zoom out) and "🔍+" (zoom in)
     - Zoom range: 0.5x to 2.0x
     - New methods:
       - `zoom_in()`: Increases zoom by 0.1, max 2.0x
       - `zoom_out()`: Decreases zoom by 0.1, min 0.5x
     - Uses `setZoomFactor()` on the QWebEngineView

### 2. **Enabled External Browser Login**
   - **File**: [spotify_controller.py](src/music_player_anki/spotify_controller.py)
   - **New Methods**:
     - `open_spotify_login_in_browser()`: Opens Spotify OAuth login URL in user's default web browser
       - Users can now authenticate without embedding a web view
       - Automatically handles the OAuth flow via browser
       - Shows success/error messages via console
     - `check_and_refresh_token()`: Validates and refreshes cached authentication token
   - **New Imports**: Added `webbrowser` module for opening browser links

### 3. **Added Login Button to Widget**
   - **File**: [spotify_web_widget.py](src/music_player_anki/spotify_web_widget.py)
   - **Changes**:
     - Added green "🔐 Login" button in widget header (next to zoom controls)
     - Button opens Spotify login in the user's default web browser
     - Shows tooltip: "Login to Spotify in your browser"
     - New method: `open_browser_login()` - triggers browser-based OAuth flow
     - Shows Anki tooltip message when login is initiated or if API credentials are missing

### 4. **Updated Widget Initialization**
   - **File**: [spotify_web_widget.py](src/music_player_anki/spotify_web_widget.py)
   - **Changes**:
     - Modified `__init__()` to accept optional `controller` parameter
     - Allows sharing SpotifyController instance between widgets
     - Falls back to creating a new controller if not provided

### 5. **Updated Module Initialization**
   - **File**: [__init__.py](src/music_player_anki/__init__.py)
   - **Changes**:
     - Added `get_spotify_controller()` function to manage controller lifecycle
     - Added global `spotify_controller` variable
     - Modified `show_spotify_widget()` to create controller and pass it to widget
     - Ensures single controller instance is shared across the addon

## User Benefits

1. **Better Website Viewing**: Users can now zoom in/out to better view the Spotify web interface within Anki
2. **External Authentication**: Users can authenticate with Spotify using their default web browser, which:
   - Handles complex authentication flows better
   - Supports 2FA and other security features
   - Doesn't require embedding the full authentication UI in Anki
3. **Cleaner UI**: Login button provides quick access to authentication without navigating

## Technical Details

### Zoom Implementation
- Uses Qt's `setZoomFactor()` method on QWebEngineView
- Zoom level is per-widget instance
- Range: 50% to 200% (0.5x to 2.0x)

### Browser-Based OAuth
- Leverages Python's `webbrowser` module for cross-platform compatibility
- Spotify OAuth redirect URI must be configured to `http://localhost:8888/callback`
- Token is cached locally for subsequent authentication
- Works on Windows, macOS, and Linux

## Configuration Requirements

Users must still configure:
- **Client ID**: From Spotify Developer Dashboard
- **Client Secret**: From Spotify Developer Dashboard
- **Redirect URI**: Should be `http://localhost:8888/callback`

These can be configured through the addon's settings dialog in Anki.

## Backward Compatibility

All changes are backward compatible:
- Existing embedded web view functionality remains intact
- New features are opt-in (users choose to use zoom or external login)
- Controller can be initialized without a widget
- Zoom level defaults to 1.0 (no zoom)
