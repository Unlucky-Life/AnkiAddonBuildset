"""Main music player widget with web view and playback controls.

This module defines the MusicWidget class, which provides the primary user
interface for the music player addon. It combines:
    - Embedded web browser (QWebEngineView) for music services
    - Playback control buttons (play/pause, next, previous, volume)
    - Service selector dropdown (YouTube Music, YouTube, etc.)
    - Ad blocking via JavaScript injection
    - Draggable, frameless window design

The widget is designed to stay on top of Anki while studying, allowing users
to control music without leaving the review interface.

Architecture:
    - Web view loads music service URLs (YouTube Music by default)
    - JavaScript injected to control playback and block ads
    - Controls send keyboard events to web page (k for pause, shift+n for next)
    - Frameless window with custom drag behavior for positioning

Typical usage:
    >>> from gui.music_widget import MusicWidget
    >>> widget = MusicWidget(parent=mw)
    >>> widget.show()
    >>> widget.move(100, 100)  # Position on screen
"""

import os
from aqt import mw
from aqt.qt import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    Qt, QUrl, QComboBox, QKeySequence
)

try:
    from aqt.qt import QWebEngineView, QWebEngineSettings, QWebEngineProfile, QWebEnginePage, QWebEngineScript
except ImportError:
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile, QWebEnginePage, QWebEngineScript
    except ImportError:
        QWebEngineView = None
        QWebEngineSettings = None
        QWebEngineProfile = None
        QWebEnginePage = None
        QWebEngineScript = None

from ..core.config import config
from ..utils.constants import SERVICES, WIDGET_WIDTH, WIDGET_HEIGHT, HEADER_HEIGHT, CONTROLS_HEIGHT, PRIMARY_BUTTON_SIZE, SECONDARY_BUTTON_SIZE
from ..utils.styles import Styles
from ..utils.javascript import JavaScriptInjector
from ..utils.logger import log_info, log_error, log_debug


class MusicWidget(QWidget):
    """Main music player widget with embedded web browser.
    
    A frameless, draggable Qt widget that embeds a web browser (QWebEngineView)
    for playing music from various streaming services. Features include:
        - Service switching (YouTube Music, YouTube, etc.)
        - Playback controls (play/pause, next, previous, volume)
        - Ad blocking via JavaScript injection
        - Custom positioning and always-on-top behavior
    
    The widget uses JavaScript to interact with the web player, sending
    keyboard events to control playback. It injects ad-blocking scripts
    at page load and maintains them with a MutationObserver.
    
    Attributes:
        controller: Optional player controller (legacy, not currently used).
        current_service: Name of currently loaded service (str).
        custom_urls: List of custom service URLs from config.
        drag_position: QPoint for tracking window drag operations.
        web_view: QWebEngineView displaying the music service.
    
    Note:
        The widget requires QWebEngineView (comes with PyQt6 or can be
        installed separately). Falls back gracefully if unavailable.
    
    Examples:
        >>> widget = MusicWidget(parent=mw)
        >>> widget.show()
        >>> widget.move(100, 100)
        >>> widget.load_service('youtube_music')
    """
    
    def __init__(self, controller=None, parent=None):
        """Initialize the music widget.
        
        Sets up the widget with default service, loads custom URLs from config,
        and initializes the UI components (web view, controls, etc.).
        
        Args:
            controller: Optional player controller for API-based control
                (kept for backward compatibility, not currently used).
            parent: Optional parent Qt widget. Should typically be Anki's
                main window (mw) to ensure proper lifecycle management.
        
        Side Effects:
            - Reads configuration (default_service, custom_urls)
            - Creates all UI components via _setup_ui()
            - Sets frameless window flags
        
        Examples:
            >>> widget = MusicWidget(parent=mw)
            >>> widget = MusicWidget(controller=my_controller, parent=mw)
        """
        super().__init__(parent)
        log_info("Initializing Music Widget")
        try:
            self.controller = controller
            self.current_service = config.get('default_service', 'youtube_music')
            self.custom_urls = config.get('custom_urls', [])
            self.drag_position = None
            self._setup_ui()
            log_info("Music Widget initialized successfully")
        except Exception as e:
            log_error("Failed to initialize Music Widget", e)
            raise
    
    def _setup_ui(self):
        """Set up the user interface components.
        
        Creates and arranges all UI elements:
            - Header with title and service selector
            - Web view for displaying music service
            - Control buttons (play/pause, next, previous, volume)
            - Close button
        
        Also applies stylesheets and loads the initial service.
        
        Side Effects:
            - Creates QVBoxLayout with header, web view, and controls
            - Applies modern dark theme stylesheets via Styles class
            - Calls _create_header(), _create_web_view(), _create_controls()
            - Loads the current service into web view
        
        Note:
            Should only be called once during initialization.
        """
        self.resize(WIDGET_WIDTH, WIDGET_HEIGHT)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add header
        layout.addWidget(self._create_header())
        
        # Add loading bar
        from aqt.qt import QProgressBar
        self.loading_bar = QProgressBar()
        self.loading_bar.setMaximum(100)
        self.loading_bar.setFixedHeight(3)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setStyleSheet("""
            QProgressBar {
                background: transparent;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1DB954, stop:1 #1FE870);
            }
        """)
        self.loading_bar.hide()
        layout.addWidget(self.loading_bar)
        
        # Add web view
        if QWebEngineView:
            layout.addWidget(self._create_web_view())
        else:
            layout.addWidget(self._create_fallback())
        
        # Add controls
        layout.addWidget(self._create_controls())
        
        self.setLayout(layout)
    
    def _create_header(self):
        """Create the header with title, service selector, and close button."""
        header = QWidget()
        header.setFixedHeight(HEADER_HEIGHT)
        header.setStyleSheet(Styles.header())
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 8, 16, 8)
        header_layout.setSpacing(12)
        
        # Title
        title = QLabel("♫ Music Player")
        title.setStyleSheet(Styles.title_label())
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Service selector
        self.service_combo = self._create_service_combo()
        header_layout.addWidget(self.service_combo)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet(Styles.close_button())
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        return header
    
    def _create_service_combo(self):
        """Create the service selection combo box."""
        combo = QComboBox()
        
        # Add supported services
        services = [SERVICES[key]['name'] for key in ['youtube_music', 'youtube']]
        
        # Add custom URLs
        for custom_url in self.custom_urls:
            services.append(custom_url.get('name', 'Custom'))
        
        combo.addItems(services)
        
        # Set default selection
        default_service = config.get('default_service', 'youtube_music')
        if default_service == 'youtube':
            combo.setCurrentIndex(1)
        
        combo.setStyleSheet(Styles.service_combo())
        combo.setToolTip("Switch music service")
        combo.currentTextChanged.connect(self._on_service_changed)
        
        return combo
    
    def _create_web_view(self):
        """Create the web engine view with persistent profile.
        
        Sets up a persistent QWebEngineProfile that stores:
            - Login cookies and sessions (so you stay logged in)
            - Local storage data
            - HTTP cache for faster loading
            
        The profile is stored in the addon folder and persists across
        Anki restarts, so you won't need to log in again.
        """
        # Set up persistent profile for saving login sessions
        try:
            # Get addon root folder from package __init__.py location
            import music_player_anki
            addon_root = os.path.dirname(music_player_anki.__file__)
            profile_path = os.path.join(addon_root, 'web_profile')
            os.makedirs(profile_path, exist_ok=True)
            
            log_info(f"Addon root: {addon_root}")
            log_info(f"Profile path: {profile_path}")
            
            # CRITICAL: Use a NAMED profile to avoid off-the-record mode
            # Named profiles are persistent by default
            self.profile = QWebEngineProfile("MusicPlayerProfile", parent=self)
            
            # Set paths BEFORE creating any pages
            self.profile.setPersistentStoragePath(profile_path)
            self.profile.setCachePath(os.path.join(profile_path, 'cache'))
            
            # Force persistent cookies
            self.profile.setPersistentCookiesPolicy(
                QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
            )
            
            # Configure profile settings
            self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
            self.profile.setHttpCacheMaximumSize(100 * 1024 * 1024)  # 100MB
            self.profile.setHttpAcceptLanguage("en-US,en;q=0.9")
            
            # Log profile configuration
            log_info("Profile configured:")
            log_info(f"  Storage path: {self.profile.persistentStoragePath()}")
            log_info(f"  Cache path: {self.profile.cachePath()}")
            log_info(f"  Is off-the-record: {self.profile.isOffTheRecord()}")
            
            if self.profile.isOffTheRecord():
                log_error("WARNING: Profile is off-the-record - cookies will NOT be saved!")
            else:
                log_info("✓ Profile is persistent - cookies will be saved!")
        except Exception as e:
            log_error("Failed to configure web profile", e)
            raise
        
        # Create page AFTER profile is fully configured
        page = QWebEnginePage(self.profile, self)
        page.loadStarted.connect(self._on_load_started)
        page.loadProgress.connect(self._on_load_progress)
        page.loadFinished.connect(self._on_page_loaded)
        
        # Create web view
        self.web_view = QWebEngineView()
        self.web_view.setPage(page)
        
        # Configure settings for best compatibility
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        
        # Load initial service
        url = SERVICES.get(self.current_service, SERVICES['youtube_music'])['url']
        self.web_view.setUrl(QUrl(url))
        
        return self.web_view
    
    def _create_fallback(self):
        """Create fallback widget when WebEngine is unavailable."""
        fallback = QLabel("Web player requires QWebEngineView")
        fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fallback.setStyleSheet(Styles.fallback_label())
        return fallback
    
    def _create_controls(self):
        """Create the playback control footer."""
        controls = QWidget()
        controls.setFixedHeight(CONTROLS_HEIGHT)
        controls.setStyleSheet(Styles.controls_footer())
        
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(16, 4, 16, 4)
        controls_layout.setSpacing(12)
        
        # Add stretch on left
        controls_layout.addStretch()
        
        # Previous button
        prev_btn = QPushButton("⏮")
        prev_btn.setFixedSize(140, 48)
        prev_btn.setToolTip("Previous")
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_btn.setStyleSheet(Styles.glass_button())
        prev_btn.clicked.connect(self.previous_track)
        controls_layout.addWidget(prev_btn)

        # Play / Pause button
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(156, 48)
        self.play_pause_btn.setToolTip("Play/Pause")
        self.play_pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.play_pause_btn.setStyleSheet(Styles.glass_button())
        self.play_pause_btn.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_pause_btn)

        # Next button
        next_btn = QPushButton("⏭")
        next_btn.setFixedSize(140, 48)
        next_btn.setToolTip("Next")
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.setStyleSheet(Styles.glass_button())
        next_btn.clicked.connect(self.next_track)
        controls_layout.addWidget(next_btn)
        
        # Volume down button
        vol_down_btn = QPushButton("🔉")
        vol_down_btn.setFixedSize(48, 48)
        vol_down_btn.setToolTip("Volume Down")
        vol_down_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        vol_down_btn.setStyleSheet(Styles.glass_button())
        vol_down_btn.clicked.connect(self.volume_down)
        controls_layout.addWidget(vol_down_btn)
        
        # Volume up button
        vol_up_btn = QPushButton("🔊")
        vol_up_btn.setFixedSize(48, 48)
        vol_up_btn.setToolTip("Volume Up")
        vol_up_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        vol_up_btn.setStyleSheet(Styles.glass_button())
        vol_up_btn.clicked.connect(self.volume_up)
        controls_layout.addWidget(vol_up_btn)

        controls_layout.addStretch()

        return controls
    
    def _create_button(self, text, tooltip, primary=False):
        """
        Create a control button.
        
        Args:
            text: Button text (emoji)
            tooltip: Tooltip text
            primary: True for primary button (play/pause), False for secondary
        
        Returns:
            QPushButton configured with appropriate style
        """
        btn = QPushButton(text)
        size = PRIMARY_BUTTON_SIZE if primary else SECONDARY_BUTTON_SIZE
        btn.setFixedSize(size, size)
        btn.setToolTip(tooltip)
        btn.setStyleSheet(Styles.primary_button() if primary else Styles.secondary_button())
        return btn
    
    def _handle_console_message(self, level, message, lineNumber, sourceID):
        """Handle JavaScript console messages for debugging."""
        if any(keyword in message.lower() for keyword in ['player', 'error']):
            print(f"[Music Player Console] {message}")
    
    def _on_load_started(self):
        """Handle page load start."""
        if hasattr(self, 'loading_bar'):
            self.loading_bar.setValue(0)
            self.loading_bar.show()
    
    def _on_load_progress(self, progress):
        """Handle page load progress."""
        if hasattr(self, 'loading_bar'):
            self.loading_bar.setValue(progress)
    
    def _on_page_loaded(self, ok):
        """Handle page load completion."""
        if hasattr(self, 'loading_bar'):
            self.loading_bar.hide()
        
        if not ok or not hasattr(self, 'web_view'):
            return
    
    def _on_service_changed(self, service_name):
        """Handle service selection change."""
        if not hasattr(self, 'web_view') or not self.web_view:
            return
        
        # Map display name to service key
        if service_name == "YouTube Music":
            self.current_service = "youtube_music"
            url = SERVICES['youtube_music']['url']
        elif service_name == "YouTube":
            self.current_service = "youtube"
            url = SERVICES['youtube']['url']
        else:
            # Custom URL
            for custom_url in self.custom_urls:
                if custom_url.get('name') == service_name:
                    self.current_service = "custom"
                    url = custom_url.get('url', '')
                    break
            else:
                return
        
        self.web_view.setUrl(QUrl(url))
    
    # Playback control methods
    
    def toggle_playback(self):
        """Toggle play/pause."""
        try:
            if hasattr(self, 'web_view'):
                log_debug("Executing play/pause JavaScript")
                self.web_view.page().runJavaScript(JavaScriptInjector.get_play_pause_js())
            else:
                log_error("Cannot toggle playback: web_view not available")
        except Exception as e:
            log_error("Error toggling playback", e)
    
    def next_track(self):
        """Skip to next track."""
        try:
            if hasattr(self, 'web_view'):
                log_debug("Executing next track JavaScript")
                self.web_view.page().runJavaScript(JavaScriptInjector.get_next_track_js())
            else:
                log_error("Cannot skip to next: web_view not available")
        except Exception as e:
            log_error("Error skipping to next track", e)
    
    def previous_track(self):
        """Skip to previous track."""
        try:
            if hasattr(self, 'web_view'):
                log_debug("Executing previous track JavaScript")
                self.web_view.page().runJavaScript(JavaScriptInjector.get_previous_track_js())
            else:
                log_error("Cannot skip to previous: web_view not available")
        except Exception as e:
            log_error("Error skipping to previous track", e)
    
    def volume_up(self):
        """Increase volume."""
        try:
            if hasattr(self, 'web_view'):
                log_debug("Executing volume up JavaScript")
                self.web_view.page().runJavaScript(JavaScriptInjector.get_volume_up_js())
            else:
                log_error("Cannot increase volume: web_view not available")
        except Exception as e:
            log_error("Error increasing volume", e)
    
    def volume_down(self):
        """Decrease volume."""
        try:
            if hasattr(self, 'web_view'):
                log_debug("Executing volume down JavaScript")
                self.web_view.page().runJavaScript(JavaScriptInjector.get_volume_down_js())
            else:
                log_error("Cannot decrease volume: web_view not available")
        except Exception as e:
            log_error("Error decreasing volume", e)
    
    # Event handlers
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts within the widget.
        
        Only handles widget-specific shortcuts like Space for play/pause.
        Global shortcuts (Ctrl+Shift+*) are handled at the application level
        and will work even when widget doesn't have focus.
        """
        # Only handle Space key when widget has focus
        if event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            self.toggle_playback()
            event.accept()
            return
        
        # Let all other keys bubble up to global shortcuts
        event.ignore()
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() <= HEADER_HEIGHT:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to end dragging."""
        self.drag_position = None
        super().mouseReleaseEvent(event)
