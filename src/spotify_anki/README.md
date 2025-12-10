# Spotify Anki Addon

Control Spotify playback directly from the Anki reviewer with a toggleable floating widget.

## Features

- **Toggleable Widget**: Show/hide a floating control widget with `Ctrl+Shift+S` or via `Tools → Toggle Spotify Widget`
- **Playback Control**: Play, pause, skip tracks without leaving Anki
- **Real-time Updates**: See currently playing track and artist
- **Draggable Widget**: Position the widget anywhere on your screen
- **Minimal UI**: Clean, Spotify-themed interface that doesn't distract from studying

## Installation

### Step 1: Install the Addon

1. Download or clone this repository
2. Copy the `spotify_anki` folder to your Anki addons directory:
   - **Windows**: `%APPDATA%\Anki2\addons21\`
   - **Mac**: `~/Library/Application Support/Anki2/addons21/`
   - **Linux**: `~/.local/share/Anki2/addons21/`
3. Restart Anki

### Step 2: Install Python Dependencies

**Note:** This addon comes with `spotipy` bundled in the folder, so you may not need to install anything! If you encounter import errors, try one of these methods:

#### Method 1: Using Anki's Python (Recommended)

**Windows:**
```powershell
cd "$env:APPDATA\Anki2\addons21\spotify_anki"
& "C:\Program Files\Anki\python.exe" -m pip install spotipy
```

**Mac/Linux:**
```bash
cd ~/.local/share/Anki2/addons21/spotify_anki
/Applications/Anki.app/Contents/MacOS/python -m pip install spotipy
```

#### Method 2: Using requirements.txt

**Windows:**
```powershell
cd "$env:APPDATA\Anki2\addons21\spotify_anki"
& "C:\Program Files\Anki\python.exe" -m pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd ~/.local/share/Anki2/addons21/spotify_anki
/Applications/Anki.app/Contents/MacOS/python -m pip install -r requirements.txt
```

#### Method 3: Verify Bundled Library

The `spotipy` folder should already be in the addon directory. If it's missing, try installing directly:

**Windows PowerShell:**
```powershell
& "C:\Program Files\Anki\python.exe" -m pip install spotipy
```

**Mac/Linux:**
```bash
/Applications/Anki.app/Contents/MacOS/python -m pip install spotipy
```

Or using your system Python (may not work with Anki):
```bash
pip install spotipy
```

### Step 3: Configure Spotify API

To use this addon, you need Spotify API credentials:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **"Create App"**
4. Fill in:
   - **App name**: `Anki Spotify Control` (or any name)
   - **App description**: `Control Spotify from Anki`
   - **Redirect URI**: `http://localhost:8888/callback` ⚠️ **Important!**
5. Click **"Save"**
6. Copy your **Client ID** and **Client Secret**

### Step 4: Configure the Addon

1. Open Anki
2. Go to `Tools → Toggle Spotify Widget` (or press `Ctrl+Shift+S`)
3. Click **"⚙ Settings"** in the widget
4. Paste your Client ID and Client Secret
5. Make sure Redirect URI is: `http://localhost:8888/callback`
6. Click **"OK"**
7. A browser window will open asking you to authorize the app
8. Click **"Agree"** to authorize
9. You'll be redirected to a page (may show an error - that's OK!)
10. Go back to Anki - the widget should now show "No Active Device"

## Usage

### Opening the Widget

- **Keyboard shortcut**: `Ctrl+Shift+S`
- **Menu**: `Tools → Toggle Spotify Widget`

The widget will appear in the bottom-right of the reviewer screen.

### Controls

- **▶/⏸ Button**: Play or pause current track
- **⏮ Button**: Previous track
- **⏭ Button**: Next track
- **⚙ Settings**: Configure Spotify API credentials
- **✕ Hide**: Hide the widget (use `Ctrl+Shift+S` to show again)

### Tips

- **Start Spotify**: Make sure Spotify is open and playing on any device (phone, computer, etc.)
- **Drag Widget**: Click and drag anywhere on the widget to reposition it
- **Hide While Studying**: Press `Ctrl+Shift+S` to quickly hide/show the widget
- **Works Across Devices**: Control playback on any Spotify Connect device

## Troubleshooting

### "Not Configured" Message

- Click **Settings** and enter your Spotify API credentials
- Make sure you completed the authorization step

### "No Active Device" Message

- Open Spotify on your computer or phone
- Start playing any song
- The widget should detect the active device within a few seconds

### Widget Doesn't Appear

- Make sure you're in the **Reviewer** screen (studying cards)
- Try pressing `Ctrl+Shift+S` again
- Restart Anki

### Import Errors

- Make sure `spotipy` is installed in Anki's Python environment
- Check the Anki console (`Tools → Add-ons → View Add-on Console`) for error messages

### Authorization Issues

- Make sure the Redirect URI in your Spotify app settings is **exactly**: `http://localhost:8888/callback`
- Try deleting `.spotify_cache` file in the `spotify_anki` folder and re-authorizing

## File Structure

```
spotify_anki/
├── __init__.py                 # Main addon entry point
├── spotify_controller.py       # Spotify API integration
├── spotify_widget.py           # UI widget implementation
├── manifest.json              # Addon metadata
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── spotify_config.json        # Config (created after setup)
```

## Privacy & Security

- Your Spotify credentials are stored locally in `spotify_config.json`
- The addon only requests permissions to read and control playback
- No data is sent to any third parties
- Authorization tokens are cached locally in `.spotify_cache`

## Limitations

- Requires active Spotify Premium account (free accounts have limited API access)
- Requires internet connection
- Widget only appears in the reviewer screen (not main window or deck browser)

## Development

Built using:
- **Anki API**: `aqt.gui_hooks` for reviewer integration
- **PyQt6**: For UI widgets
- **Spotipy**: Python library for Spotify Web API

### Customization

You can customize the widget appearance by editing the `setStyleSheet()` calls in `spotify_widget.py`.

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
