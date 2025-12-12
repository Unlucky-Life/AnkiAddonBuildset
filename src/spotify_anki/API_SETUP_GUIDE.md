# Spotify API Setup & Playback Control Guide

## Understanding the Two Control Methods

This addon supports **two ways** to control Spotify:

### 1. **Web Player Control (JavaScript)** 
- Uses the embedded Spotify web player in Anki
- **No API setup required**
- Works by simulating button clicks in the web interface
- Limited functionality
- Requires you to be logged into Spotify in the web player

### 2. **API Control (Recommended)** ✨
- Uses Spotify's official Web API
- **Requires API credentials and setup** (see below)
- Full playback control across all your Spotify devices
- Can control Spotify desktop app, mobile app, web player, etc.
- More reliable and feature-rich

---

## Setting Up Spotify API Control

### Step 1: Create a Spotify Developer App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **"Create app"**
4. Fill in the form:
   - **App name**: `Anki Spotify Controller` (or any name)
   - **App description**: `Controls Spotify from Anki`
   - **Redirect URI**: `http://localhost:8888/callback` ⚠️ **IMPORTANT!**
   - Check the Terms of Service box
5. Click **"Save"**
6. On the app page, click **"Settings"**
7. Copy your **Client ID** and **Client Secret**

### Step 2: Configure the Addon

1. In Anki, open the Spotify widget
2. Click the **Settings** button (⚙)
3. Paste your **Client ID** and **Client Secret**
4. Make sure **Redirect URI** is: `http://localhost:8888/callback`
5. Click **OK**

### Step 3: Authenticate

1. Click the **"🔐 Login"** button in the widget header
2. Your default browser will open with Spotify's login page
3. **Log in to Spotify** and **authorize the app**
4. The browser will redirect and show "Authorization Successful!"
5. Return to Anki - the status indicator should now show **●** (green dot)

### Step 4: Have an Active Spotify Session

**CRITICAL:** The Spotify API requires an **active playback device**. This means:

✅ **You must have Spotify open and playing on at least one device:**
- Spotify Desktop App (Windows/Mac/Linux)
- Spotify Mobile App (iOS/Android)
- Spotify Web Player (browser)
- Smart speakers (Alexa, Google Home, etc.)
- Game consoles or other devices

❌ **API control will NOT work if:**
- No Spotify device is active
- You only logged in via the API but didn't start Spotify anywhere

---

## How to Use API Control

Once set up correctly:

1. **Start Spotify** on any device (desktop, mobile, web, etc.)
2. **Play a song** (any song, just get playback started)
3. Now in Anki, the widget controls will use the API:
   - **Play/Pause**: Controls whatever device is currently active
   - **Next/Previous**: Skips tracks on the active device
   - Works even if the widget is minimized!

### Visual Indicators

- **○** (gray circle): API not connected - using web player controls only
- **●** (green circle): API connected - using Spotify API for control!
- Button shows **"✓ API"** when connected

---

## Troubleshooting

### "No active device found"
**Solution:** Open Spotify on any device and start playing something. The API needs an active playback session to control.

### API not connecting after login
**Solution:** 
1. Check the green/gray status indicator
2. Try clicking the Login button again
3. Check Anki's console for error messages
4. Verify your Client ID and Secret are correct

### Controls not working
**Solution:**
- If API is connected (green ●): Make sure Spotify is playing on a device
- If API is not connected (gray ○): Controls will only work on the embedded web player - make sure you're logged in to Spotify in the web view

### Redirect URI error during login
**Solution:** Double-check that your Spotify app settings have the **exact** redirect URI: `http://localhost:8888/callback`

---

## Fallback Behavior

The addon is smart! It automatically:
- **Tries API control first** (if connected)
- **Falls back to web player control** (if API unavailable)

So even if your API isn't set up, the basic web controls will still work!

---

## Benefits of API Control

- ✅ Control Spotify across **all your devices**
- ✅ More **reliable** than JavaScript control
- ✅ Works with **keyboard shortcuts** even when widget is hidden
- ✅ Can control desktop/mobile Spotify apps remotely
- ✅ No need to keep web player open
- ✅ Better error handling and feedback

---

## Privacy & Security

- Your credentials are stored **locally** in your Anki addon folder
- The addon only requests permissions to read/control playback
- No data is sent anywhere except to Spotify's official API
- Your Client Secret is only used for authentication with Spotify's servers
