"""
Spotify Widget UI for Anki Reviewer.

Creates a floating widget with play/pause controls that appears
in the Anki reviewer window.
"""

try:
    from aqt import mw
    from aqt.qt import (
        QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
        Qt, QTimer, QDialog, QLineEdit, QFormLayout, QDialogButtonBox
    )
    from .spotify_controller import SpotifyController
except Exception as e:
    print(f"[spotify_anki] Widget import error: {e}")
    QWidget = object
    mw = None


class ConfigDialog(QDialog):
    """Dialog for configuring Spotify API credentials."""
    
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Spotify Configuration")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the configuration dialog UI."""
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "To use Spotify integration, you need to create a Spotify app:\n\n"
            "1. Go to https://developer.spotify.com/dashboard\n"
            "2. Create a new app\n"
            "3. Add 'http://localhost:8888/callback' as a Redirect URI\n"
            "4. Copy your Client ID and Client Secret below"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Form for credentials
        form_layout = QFormLayout()
        
        self.client_id_input = QLineEdit()
        self.client_id_input.setText(self.controller.config.get('client_id', ''))
        form_layout.addRow("Client ID:", self.client_id_input)
        
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setText(self.controller.config.get('client_secret', ''))
        self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Client Secret:", self.client_secret_input)
        
        self.redirect_uri_input = QLineEdit()
        self.redirect_uri_input.setText(
            self.controller.config.get('redirect_uri', 'http://localhost:8888/callback')
        )
        form_layout.addRow("Redirect URI:", self.redirect_uri_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_config)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def save_config(self):
        """Save the configuration."""
        success = self.controller.save_config(
            self.client_id_input.text().strip(),
            self.client_secret_input.text().strip(),
            self.redirect_uri_input.text().strip()
        )
        
        if success:
            self.accept()


class SpotifyWidget(QWidget):
    """Floating widget for Spotify controls in the Anki reviewer."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize Spotify controller
        if mw:
            addon_dir = mw.pm.addonFolder()
            import os
            config_dir = os.path.join(addon_dir, 'spotify_anki')
        else:
            config_dir = '.'
        
        self.controller = SpotifyController(config_dir)
        
        # Setup UI
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second
        
        # Initial update
        self.update_display()
    
    def setup_ui(self):
        """Setup the widget UI."""
        # Make widget floating and frameless
        self.setWindowFlags(
            Qt.WindowType.Tool | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Track info label
        self.track_label = QLabel("Not Connected")
        self.track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.track_label.setStyleSheet("font-weight: bold; color: #1DB954;")
        layout.addWidget(self.track_label)
        
        # Artist info label
        self.artist_label = QLabel("")
        self.artist_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_label.setStyleSheet("color: #666;")
        layout.addWidget(self.artist_label)
        
        # Control buttons layout
        controls_layout = QHBoxLayout()
        
        # Previous button
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setFixedSize(40, 40)
        self.prev_btn.clicked.connect(self.previous_track)
        controls_layout.addWidget(self.prev_btn)
        
        # Play/Pause button
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(50, 50)
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        self.play_pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #1DB954;
                color: white;
                border-radius: 25px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #1ED760;
            }
        """)
        controls_layout.addWidget(self.play_pause_btn)
        
        # Next button
        self.next_btn = QPushButton("⏭")
        self.next_btn.setFixedSize(40, 40)
        self.next_btn.clicked.connect(self.next_track)
        controls_layout.addWidget(self.next_btn)
        
        layout.addLayout(controls_layout)
        
        # Settings button
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self.show_settings)
        layout.addWidget(settings_btn)
        
        # Close button
        close_btn = QPushButton("✕ Hide")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # Style the widget
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #1DB954;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        # Set initial size and position
        self.setFixedSize(250, 200)
        if parent and hasattr(parent, 'width'):
            # Position in bottom-right corner
            self.move(parent.width() - 270, parent.height() - 220)
        else:
            self.move(100, 100)
    
    def toggle_playback(self):
        """Toggle play/pause."""
        if not self.controller.is_configured():
            self.show_settings()
            return
        
        self.controller.toggle_playback()
        # Update display immediately
        QTimer.singleShot(100, self.update_display)
    
    def next_track(self):
        """Skip to next track."""
        if not self.controller.is_configured():
            self.show_settings()
            return
        
        self.controller.next_track()
        QTimer.singleShot(500, self.update_display)
    
    def previous_track(self):
        """Go to previous track."""
        if not self.controller.is_configured():
            self.show_settings()
            return
        
        self.controller.previous_track()
        QTimer.singleShot(500, self.update_display)
    
    def update_display(self):
        """Update the display with current track info."""
        if not self.controller.is_configured():
            self.track_label.setText("Not Configured")
            self.artist_label.setText("Click Settings to setup")
            self.play_pause_btn.setText("▶")
            return
        
        track_info = self.controller.get_current_track_info()
        
        if track_info:
            # Update track name
            track_name = track_info['name']
            if len(track_name) > 30:
                track_name = track_name[:27] + "..."
            self.track_label.setText(track_name)
            
            # Update artist
            artist_name = track_info['artist']
            if len(artist_name) > 30:
                artist_name = artist_name[:27] + "..."
            self.artist_label.setText(artist_name)
            
            # Update play/pause button
            if track_info['is_playing']:
                self.play_pause_btn.setText("⏸")
            else:
                self.play_pause_btn.setText("▶")
        else:
            self.track_label.setText("No Active Device")
            self.artist_label.setText("Open Spotify")
            self.play_pause_btn.setText("▶")
    
    def show_settings(self):
        """Show the configuration dialog."""
        dialog = ConfigDialog(self.controller, self)
        if dialog.exec():
            # Refresh display after configuration
            self.update_display()
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
