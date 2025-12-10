# Spotify Anki Addon

Control Spotify playback directly from the Anki reviewer with a toggleable floating widget.

## Features

- **Toggleable Widget**: Show/hide a floating music player with `Ctrl+Shift+S` or via `Tools → Toggle Spotify Widget`
- **Multiple Services**: Switch between Spotify and YouTube Music
- **Full Web Player**: Complete web interface with login support - use your existing accounts!
- **Global Keyboard Shortcuts**: Control playback from anywhere in Anki (even when widget is hidden):
  - **Space**: Play/Pause
  - **Shift+Right Arrow**: Next track
  - **Shift+Left Arrow**: Previous track
  - **Ctrl+Shift+S**: Toggle widget visibility
- **Button Controls**: On-screen buttons for play/pause, next, and previous
- **Draggable Widget**: Position the player anywhere on your screen
- **Dark Theme**: Clean, dark-themed interface that matches music services

## Installation

### Step 1: Install the Addon

1. Download or clone this repository
2. Copy the `spotify_anki` folder to your Anki addons directory:
   - **Windows**: `%APPDATA%\Anki2\addons21\`
   - **Mac**: `~/Library/Application Support/Anki2/addons21/`
   - **Linux**: `~/.local/share/Anki2/addons21/`
3. Restart Anki

### Step 2: No Setup Required!

That's it! No dependencies, no API credentials needed.

### Step 3: Start Using!

1. Open Anki
2. Go to `Tools → Toggle Spotify Widget` (or press `Ctrl+Shift+S`)
3. The music player will appear
4. Choose **Spotify** or **YouTube Music** from the dropdown
5. Log in to your account in the web player
6. Start playing music!
7. Use keyboard shortcuts (Space, Shift+←/→) or on-screen buttons to control playback

## Usage

### Opening the Widget

- **Keyboard shortcut**: `Ctrl+Shift+S`
- **Menu**: `Tools → Toggle Spotify Widget`

The widget will appear in the bottom-right of the reviewer screen.

### Controls

**Keyboard Shortcuts** (work anywhere in Anki when widget is open):
- **Space**: Play/Pause current track
- **Shift+Right Arrow** (→): Next track
- **Shift+Left Arrow** (←): Previous track

**On-Screen Buttons**:
- **⏯ Button**: Play or pause
- **⏭ Button**: Next track
- **⏮ Button**: Previous track
- **Service Dropdown**: Switch between Spotify and YouTube Music
- **✕ Button**: Hide widget (press `Ctrl+Shift+S` to show again)

**Menu Actions**:
- **Tools → Toggle Spotify Widget**: Show/hide the widget
- **Tools → Spotify Addon Settings**: Customize keyboard shortcuts and preferences
- **Tools → Reload Spotify Addon**: Hot reload the addon without restarting Anki (useful for development)

## Customizing Shortcuts

You can customize all keyboard shortcuts through the settings:

1. Go to `Tools → Spotify Addon Settings`
2. Click on each shortcut field
3. Press the key combination you want to use
4. Click OK to save
5. Use `Tools → Reload Spotify Addon` or restart Anki to apply changes

**Available shortcuts to customize:**
- Play/Pause (default: Space)
- Next Track (default: Shift+Right)
- Previous Track (default: Shift+Left)
- Toggle Widget (default: Ctrl+Shift+S - cannot be changed in settings)

**Important**: All shortcuts work **everywhere in Anki**, not just when the widget is focused. This means you can:
- Control playback while studying (Space to play/pause, Shift+← / Shift+→ for next/previous)
- Control playback while the widget is hidden
- Control playback from any Anki screen (Decks, Cards, etc.)

You can also set the default music service (Spotify or YouTube Music).

### Switching Services

1. Use the dropdown in the header to select **Spotify** or **YouTube Music**
2. The player will reload with the selected service
3. Log in if needed
4. Your preference is remembered while the widget is open

### Changing What Plays

Just use the normal web interface:
- **Spotify**: Search and browse playlists, albums, artists, podcasts
- **YouTube Music**: Search for songs, create playlists, explore music

### Tips

- **Drag Widget**: Click and drag the header area (top bar with title) to reposition
- **Hide While Studying**: Press `Ctrl+Shift+S` to quickly hide/show the player
- **Keyboard Control**: Use Space and Shift+Arrow keys to control playback without touching the mouse
- **Multiple Services**: YouTube Music works great with free accounts!
- **Login Persistence**: Your login session is automatically saved - you won't need to log in again!
- **Stay Logged In**: Cookies and session data are stored in the addon's `web_profile/` folder
- **Full Features**: All normal web player features work (search, playlists, queue, etc.)

## Troubleshooting

### Widget Doesn't Appear

- Make sure you're in the **Reviewer** screen (studying cards)
- Try pressing `Ctrl+Shift+S` again
- Restart Anki

### Player Shows Blank/White Screen

- Make sure you have an internet connection
- Check if QWebEngineView is installed (comes with modern Anki versions)
- Try switching to YouTube Music to see if it loads

### Keyboard Shortcuts Not Working

- Make sure the widget is visible and has focus
- Click once on the widget to give it focus
- The shortcuts (Space, Shift+←/→) should then work

### Need to Log In Again

- Login data is stored in `web_profile/` folder
- If you need to clear login data, close Anki and delete the `web_profile/` folder in the addon directory
- Then log in again when you open the widget

### Can't Hear Music

**For Spotify:**
- Spotify Web Player requires Premium for full playback
- Free accounts only get 30-second previews
- Make sure you're logged in to a Premium account

**For YouTube Music:**
- Works with free accounts!
- Make sure you're logged in
- Check your system volume

### Want Full Playback Without Premium?

- Use **YouTube Music** instead! Select it from the dropdown
- YouTube Music works fully with free accounts
- Still supports all keyboard shortcuts

## File Structure

```
spotify_anki/
├── __init__.py                 # Main addon entry point
├── spotify_web_widget.py       # Web-based Spotify embed widget
├── spotify_widget.py           # API-based widget (legacy)
├── spotify_controller.py       # Spotify API integration (optional)
├── http_server.py             # HTTP API server (optional)
├── hooks.py                   # Anki hooks integration
├── manifest.json              # Addon metadata
├── requirements.txt           # Python dependencies (optional)
├── README.md                  # This file
├── HTTP_API.md               # HTTP API documentation (optional)
└── spotipy/                   # Bundled Spotify library (optional)
```

## Privacy & Security

- Uses official Spotify and YouTube Music web players (same as their websites)
- Login sessions are saved locally in `web_profile/` folder (cookies and local storage)
- No credentials stored in plain text - handled securely by the web engine
- No data sent to third parties
- All playback happens through Spotify's/YouTube's servers
- You can clear login data by deleting the `web_profile/` folder

## Limitations

- Requires internet connection
- Widget only appears in the reviewer screen (not main window or deck browser)
- **Spotify requires Premium** for full playback (free accounts get 30-second previews)
- **YouTube Music works with free accounts!**
- Playback controlled through web interface and keyboard shortcuts

## Development

Built using:
- **Anki API**: `aqt.gui_hooks` for reviewer integration
- **PyQt6/QWebEngineView**: For embedded web content
- **JavaScript Injection**: For controlling web player buttons

### Hot Reload

During development, you can reload the addon without restarting Anki:

1. Make changes to the addon code
2. Go to `Tools → Reload Spotify Addon`
3. The addon will reload all modules and recreate the widget if it was visible
4. Much faster than restarting Anki!

### Customization

You can customize the default service by editing `spotify_web_widget.py`:
```python
self.current_service = "spotify"  # or "youtube"
```

Customize URLs:
```python
self.spotify_url = "https://open.spotify.com"
self.youtube_url = "https://music.youtube.com"
```

## License

See main repository LICENSE file.

## Credits

- Built with the [Anki Addon Buildset](https://github.com/Unlucky-Life/AnkiAddonBuildset)
- Uses [Spotipy](https://github.com/spotipy-dev/spotipy) for Spotify integration

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Include error messages from `Tools → Add-ons → View Add-on Console`

Happy studying with Spotify! 🎵📚
