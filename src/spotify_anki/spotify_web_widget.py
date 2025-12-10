"""
HTML-based Spotify/YouTube widget with keyboard control.
Opens full web player with JavaScript-based playback control.
"""

from aqt import mw
from aqt.qt import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    Qt, QUrl, QComboBox, QKeySequence
)

try:
    from aqt.qt import QWebEngineView, QWebEngineSettings, QWebEngineProfile
except ImportError:
    # Fallback for older Anki versions
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile
    except ImportError:
        QWebEngineView = None
        QWebEngineSettings = None
        QWebEngineProfile = None

from .config import config


class SpotifyWebWidget(QWidget):
    """Spotify/YouTube widget with full web player and keyboard controls."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load default service from config
        self.current_service = config.get('default_service', 'spotify')
        self.spotify_url = "https://open.spotify.com"
        self.youtube_url = "https://music.youtube.com"
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI with embedded web player."""
        # Set fixed size
        self.setFixedSize(450, 600)
        
        # Make widget frameless and stay on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Widget
        )
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with title and close button
        header = QWidget()
        header.setFixedHeight(40)
        header.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                border-bottom: 2px solid #1DB954;
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        title_label = QLabel("🎵 Music Player")
        title_label.setStyleSheet("color: #1DB954; font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Service selector
        self.service_combo = QComboBox()
        self.service_combo.addItems(["Spotify", "YouTube Music"])
        # Set default service from config
        default_service = config.get('default_service', 'spotify')
        if default_service == 'youtube':
            self.service_combo.setCurrentIndex(1)
        self.service_combo.setStyleSheet("""
            QComboBox {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 5px;
                padding: 5px;
                color: #FFFFFF;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #FFFFFF;
                margin-right: 5px;
            }
        """)
        self.service_combo.currentTextChanged.connect(self.change_service)
        header_layout.addWidget(self.service_combo)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 15px;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
            }
        """)
        close_btn.clicked.connect(self.hide)
        header_layout.addWidget(close_btn)
        
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        # Check if QWebEngineView is available
        if QWebEngineView:
            # Create persistent web profile for login data
            if QWebEngineProfile:
                # Use persistent profile to save cookies and login data
                from aqt import mw
                import os
                profile_path = os.path.join(mw.pm.addonFolder(), 'spotify_anki', 'web_profile')
                os.makedirs(profile_path, exist_ok=True)
                
                self.profile = QWebEngineProfile("SpotifyAnkiProfile")
                self.profile.setPersistentStoragePath(profile_path)
                self.profile.setPersistentCookiesPolicy(
                    QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
                )
                
                # Create web view with persistent profile
                from aqt.qt import QWebEnginePage
                page = QWebEnginePage(self.profile, self)
                self.web_view = QWebEngineView()
                self.web_view.setPage(page)
            else:
                # Fallback without persistent profile
                self.web_view = QWebEngineView()
            
            # Enable features
            settings = self.web_view.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
            
            # Load appropriate service URL
            if self.current_service == 'youtube':
                self.web_view.setUrl(QUrl(self.youtube_url))
            else:
                self.web_view.setUrl(QUrl(self.spotify_url))
            
            layout.addWidget(self.web_view)
        else:
            # Fallback: show instructions if WebEngine not available
            fallback_label = QLabel(
                "Web player requires QWebEngineView.\n"
                "Please install PyQt6-WebEngine or use a newer Anki version."
            )
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback_label.setStyleSheet("""
                color: #FFFFFF;
                background-color: #1E1E1E;
                padding: 20px;
            """)
            fallback_label.setWordWrap(True)
            layout.addWidget(fallback_label)
        
        # Control buttons footer
        controls = QWidget()
        controls.setFixedHeight(60)
        controls.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                border-top: 2px solid #1DB954;
            }
        """)
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 10, 10, 10)
        
        # Previous button
        prev_btn = QPushButton("⏮")
        prev_btn.setFixedSize(45, 40)
        prev_btn.setToolTip(f"Previous Track ({config.get('shortcut_previous', 'Shift+Left')})")
        prev_btn.clicked.connect(self.previous_track)
        controls_layout.addWidget(prev_btn)
        
        # Play/Pause button
        self.play_pause_btn = QPushButton("⏯")
        self.play_pause_btn.setFixedSize(50, 40)
        self.play_pause_btn.setToolTip(f"Play/Pause ({config.get('shortcut_play_pause', 'Space')})")
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                border: 1px solid #1DB954;
                border-radius: 5px;
                color: #FFFFFF;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
        """)
        controls_layout.addWidget(self.play_pause_btn)
        
        # Next button
        next_btn = QPushButton("⏭")
        next_btn.setFixedSize(45, 40)
        next_btn.setToolTip(f"Next Track ({config.get('shortcut_next', 'Shift+Right')})")
        next_btn.clicked.connect(self.next_track)
        controls_layout.addWidget(next_btn)
        
        controls_layout.addStretch()
        
        # Help label with configured shortcuts
        play_pause = config.get('shortcut_play_pause', 'Space')
        next_key = config.get('shortcut_next', 'Shift+Right')
        prev_key = config.get('shortcut_previous', 'Shift+Left')
        help_label = QLabel(f"Keys: {play_pause}, {prev_key}/{next_key}")
        help_label.setStyleSheet("color: #B3B3B3; font-size: 10px;")
        controls_layout.addWidget(help_label)
        
        # Apply button styles
        for btn in [prev_btn, next_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D2D;
                    border: 1px solid #3D3D3D;
                    border-radius: 5px;
                    color: #FFFFFF;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #3D3D3D;
                }
            """)
        
        controls.setLayout(controls_layout)
        layout.addWidget(controls)
        
        self.setLayout(layout)
        
        # Widget background
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                border: 2px solid #1DB954;
            }
        """)
    
    def change_service(self, service_name):
        """Switch between Spotify and YouTube Music."""
        if not hasattr(self, 'web_view') or not self.web_view:
            return
        
        if service_name == "Spotify":
            self.current_service = "spotify"
            self.web_view.setUrl(QUrl(self.spotify_url))
        elif service_name == "YouTube Music":
            self.current_service = "youtube"
            self.web_view.setUrl(QUrl(self.youtube_url))
    
    def toggle_playback(self):
        """Toggle play/pause using JavaScript."""
        if not hasattr(self, 'web_view') or not self.web_view:
            return
        
        if self.current_service == "spotify":
            # Spotify web player uses specific button
            js_code = """
            (function() {
                // Try multiple selectors for Spotify's play/pause button
                var playBtn = document.querySelector('[data-testid="control-button-playpause"]') ||
                              document.querySelector('button[aria-label*="Play"]') ||
                              document.querySelector('button[aria-label*="Pause"]');
                if (playBtn) {
                    playBtn.click();
                    return 'clicked';
                }
                // Fallback: try keyboard event
                document.dispatchEvent(new KeyboardEvent('keydown', {key: ' ', keyCode: 32, which: 32}));
                return 'keyboard';
            })();
            """
        else:  # YouTube Music
            # YouTube Music keyboard shortcut
            js_code = """
            (function() {
                // Try button click first
                var playBtn = document.querySelector('.play-pause-button') ||
                              document.querySelector('[aria-label*="Play"]') ||
                              document.querySelector('[aria-label*="Pause"]');
                if (playBtn) {
                    playBtn.click();
                    return 'clicked';
                }
                // Fallback: keyboard 'k' for YouTube
                document.dispatchEvent(new KeyboardEvent('keydown', {key: 'k', keyCode: 75, which: 75}));
                return 'keyboard';
            })();
            """
        
        self.web_view.page().runJavaScript(js_code)
    
    def next_track(self):
        """Skip to next track using JavaScript."""
        if not hasattr(self, 'web_view') or not self.web_view:
            return
        
        if self.current_service == "spotify":
            js_code = """
            (function() {
                var nextBtn = document.querySelector('[data-testid="control-button-skip-forward"]') ||
                              document.querySelector('button[aria-label*="Next"]');
                if (nextBtn) {
                    nextBtn.click();
                    return 'clicked';
                }
                return 'not found';
            })();
            """
        else:  # YouTube Music
            js_code = """
            (function() {
                var nextBtn = document.querySelector('.next-button') ||
                              document.querySelector('[aria-label*="Next"]');
                if (nextBtn) {
                    nextBtn.click();
                    return 'clicked';
                }
                return 'not found';
            })();
            """
        
        self.web_view.page().runJavaScript(js_code)
    
    def previous_track(self):
        """Go to previous track using JavaScript."""
        if not hasattr(self, 'web_view') or not self.web_view:
            return
        
        if self.current_service == "spotify":
            js_code = """
            (function() {
                var prevBtn = document.querySelector('[data-testid="control-button-skip-back"]') ||
                              document.querySelector('button[aria-label*="Previous"]');
                if (prevBtn) {
                    prevBtn.click();
                    return 'clicked';
                }
                return 'not found';
            })();
            """
        else:  # YouTube Music
            js_code = """
            (function() {
                var prevBtn = document.querySelector('.previous-button') ||
                              document.querySelector('[aria-label*="Previous"]');
                if (prevBtn) {
                    prevBtn.click();
                    return 'clicked';
                }
                return 'not found';
            })();
            """
        
        self.web_view.page().runJavaScript(js_code)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        # Get configured shortcuts
        play_pause_seq = QKeySequence(config.get('shortcut_play_pause', 'Space'))
        next_seq = QKeySequence(config.get('shortcut_next', 'Shift+Right'))
        prev_seq = QKeySequence(config.get('shortcut_previous', 'Shift+Left'))
        
        # Create sequence from current event
        key = event.key()
        modifiers = event.modifiers()
        # Qt6: modifiers() returns KeyboardModifier, need to convert to int
        current_seq = QKeySequence(key | int(modifiers.value if hasattr(modifiers, 'value') else modifiers))
        
        # Check if current key matches any configured shortcut
        if current_seq.matches(play_pause_seq) == QKeySequence.SequenceMatch.ExactMatch:
            self.toggle_playback()
            event.accept()
            return
        
        if current_seq.matches(next_seq) == QKeySequence.SequenceMatch.ExactMatch:
            self.next_track()
            event.accept()
            return
        
        if current_seq.matches(prev_seq) == QKeySequence.SequenceMatch.ExactMatch:
            self.previous_track()
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Clean up when widget closes."""
        super().closeEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Only allow dragging from the header area (top 40px)
            if event.position().y() <= 40:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            if event.position().y() <= 40:
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()
