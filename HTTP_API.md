# HTTP Server API Reference

The Spotify Anki addon now includes an HTTP server running on `http://localhost:8888` that allows controlling Spotify playback via HTTP requests.

## Endpoints

### GET Endpoints

#### `/status`
Get current playback status.

**Response:**
```json
{
  "configured": true,
  "playing": true
}
```

#### `/current`
Get current track information.

**Response:**
```json
{
  "name": "Song Name",
  "artist": "Artist Name",
  "album": "Album Name",
  "is_playing": true,
  "progress_ms": 45000,
  "duration_ms": 180000
}
```

#### `/callback`
OAuth callback endpoint (used during Spotify authorization).

---

### POST Endpoints

#### `/play`
Resume playback.

**Response:**
```json
{
  "success": true,
  "message": "Playing"
}
```

#### `/pause`
Pause playback.

**Response:**
```json
{
  "success": true,
  "message": "Paused"
}
```

#### `/toggle`
Toggle between play and pause.

**Response:**
```json
{
  "success": true,
  "message": "Toggled"
}
```

#### `/next`
Skip to next track.

**Response:**
```json
{
  "success": true,
  "message": "Next track"
}
```

#### `/previous`
Go to previous track.

**Response:**
```json
{
  "success": true,
  "message": "Previous track"
}
```

---

## Usage Examples

### Command Line (PowerShell)

```powershell
# Get status
Invoke-RestMethod -Uri "http://localhost:8888/status" -Method GET

# Get current track
Invoke-RestMethod -Uri "http://localhost:8888/current" -Method GET

# Play
Invoke-RestMethod -Uri "http://localhost:8888/play" -Method POST

# Pause
Invoke-RestMethod -Uri "http://localhost:8888/pause" -Method POST

# Toggle play/pause
Invoke-RestMethod -Uri "http://localhost:8888/toggle" -Method POST

# Next track
Invoke-RestMethod -Uri "http://localhost:8888/next" -Method POST

# Previous track
Invoke-RestMethod -Uri "http://localhost:8888/previous" -Method POST
```

### Command Line (curl)

```bash
# Get status
curl http://localhost:8888/status

# Get current track
curl http://localhost:8888/current

# Play
curl -X POST http://localhost:8888/play

# Pause
curl -X POST http://localhost:8888/pause

# Toggle play/pause
curl -X POST http://localhost:8888/toggle

# Next track
curl -X POST http://localhost:8888/next

# Previous track
curl -X POST http://localhost:8888/previous
```

### JavaScript/Browser

```javascript
// Get current track
fetch('http://localhost:8888/current')
  .then(response => response.json())
  .then(data => console.log(data));

// Toggle playback
fetch('http://localhost:8888/toggle', { method: 'POST' })
  .then(response => response.json())
  .then(data => console.log(data));

// Next track
fetch('http://localhost:8888/next', { method: 'POST' })
  .then(response => response.json())
  .then(data => console.log(data));
```

### Python

```python
import requests

# Get status
response = requests.get('http://localhost:8888/status')
print(response.json())

# Get current track
response = requests.get('http://localhost:8888/current')
print(response.json())

# Play
response = requests.post('http://localhost:8888/play')
print(response.json())

# Toggle playback
response = requests.post('http://localhost:8888/toggle')
print(response.json())
```

---

## Use Cases

1. **External Scripts**: Control Spotify from other applications or scripts
2. **Automation**: Integrate with task automation tools
3. **Stream Deck / Macro Keys**: Map physical buttons to control playback
4. **Browser Extensions**: Control Spotify from browser shortcuts
5. **Mobile Apps**: Control from phone apps on same network

---

## Security Notes

- Server runs on **localhost only** (not accessible from network)
- No authentication required (safe since it's localhost)
- CORS enabled for browser access
- OAuth tokens stored locally in `.spotify_cache`

---

## Server Lifecycle

- **Starts**: When the Spotify widget is created
- **Stops**: When the widget is closed
- **Port**: 8888 (default)
- **Auto-restart**: Automatically restarts when widget is toggled

---

## Troubleshooting

**Port already in use:**
- Close other applications using port 8888
- Or modify the port in `spotify_widget.py`

**Connection refused:**
- Make sure the Spotify widget is open (server only runs when widget exists)
- Check Anki console for error messages

**Commands not working:**
- Ensure Spotify is configured (Client ID/Secret set)
- Make sure Spotify is open and playing on a device
- Check `/status` endpoint to verify configuration
