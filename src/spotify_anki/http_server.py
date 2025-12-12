"""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

try:
    from . import spotipy
    from .spotipy.oauth2 import SpotifyOAuth
except ImportError:
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
    except ImportError:
        spotipy = None
        SpotifyOAuth = None


class SpotifyServerHandler(BaseHTTPRequestHandler):
    controller = None
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/callback':
            self.handle_oauth_callback(parsed_path.query)
            return
        if path == '/status':
            self.handle_status()
            return
        if path == '/current':
            self.handle_current_track()
            return
        
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        response = {'success': False, 'message': 'Unknown command'}
        
        if path == '/play':
            result = self.controller.play() if self.controller else False
            response = {'success': result, 'message': 'Playing' if result else 'Failed to play'}
        
        elif path == '/pause':
            result = self.controller.pause() if self.controller else False
            response = {'success': result, 'message': 'Paused' if result else 'Failed to pause'}
        
        elif path == '/toggle':
            result = self.controller.toggle_playback() if self.controller else False
            response = {'success': result, 'message': 'Toggled' if result else 'Failed to toggle'}
        
        elif path == '/next':
            result = self.controller.next_track() if self.controller else False
            response = {'success': result, 'message': 'Next track' if result else 'Failed to skip'}
        
        elif path == '/previous':
            result = self.controller.previous_track() if self.controller else False
            response = {'success': result, 'message': 'Previous track' if result else 'Failed to go back'}
        
        # Send JSON response
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_oauth_callback(self, query):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        
        html = """
        <html>
        <head><title>Spotify Authorization</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>✓ Authorization Successful!</h1>
            <p>You can close this window and return to Anki.</p>
            <p style="color: #1DB954;">Spotify is now connected.</p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def handle_status(self):
        """Return current playback status."""
        if not self.controller or not self.controller.is_configured():
            response = {'configured': False, 'playing': False}
        else:
            is_playing = self.controller.is_playing()
            response = {'configured': True, 'playing': is_playing}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_current_track(self):
        """Return current track information."""
        if not self.controller or not self.controller.is_configured():
            response = {'error': 'Not configured'}
        else:
            track_info = self.controller.get_current_track_info()
            response = track_info if track_info else {'error': 'No track playing'}
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


class SpotifyHTTPServer:
    """HTTP server for Spotify playback control."""
    
    def __init__(self, controller, host='localhost', port=8888):
        """
        Initialize the HTTP server.
        
        Args:
            controller: SpotifyController instance
            host: Server host (default: localhost)
            port: Server port (default: 8888)
        """
        self.controller = controller
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.running = False
    
    def start(self):
        """Start the HTTP server in a background thread."""
        if self.running:
            return
        
        # Set the controller in the handler class
        SpotifyServerHandler.controller = self.controller
        
        try:
            self.server = HTTPServer((self.host, self.port), SpotifyServerHandler)
            self.running = True
            
            # Run server in background thread
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            print(f"[spotify_anki] HTTP server started on http://{self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[spotify_anki] Failed to start HTTP server: {e}")
            return False
    
    def _run_server(self):
        """Run the server (called in background thread)."""
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"[spotify_anki] Server error: {e}")
    
    def stop(self):
        """Stop the HTTP server."""
        if not self.running:
            return
        
        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            self.running = False
            print("[spotify_anki] HTTP server stopped")
        except Exception as e:
            print(f"[spotify_anki] Error stopping server: {e}")
    
    def is_running(self):
        """Check if server is running."""
        return self.running
