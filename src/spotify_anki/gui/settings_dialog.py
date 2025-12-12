"""Settings dialog for configuring the Music Player addon.

This module provides the SettingsDialog class, which allows users to:
    - Configure keyboard shortcuts (toggle, play/pause, next, previous, volume)
    - Set default music service (YouTube Music, YouTube, etc.)
    - Add custom service URLs
    - Restore default settings

The dialog uses a modern dark theme consistent with the main widget design.
All changes are saved immediately to the config.json file.

Architecture:
    - Form-based layout with grouped sections (Shortcuts, Services)
    - QKeySequenceEdit for keyboard shortcut capture
    - QComboBox for service selection
    - Direct config read/write on save
    - Input validation for shortcuts and URLs

Typical usage:
    >>> from gui.settings_dialog import SettingsDialog
    >>> dialog = SettingsDialog(parent=mw)
    >>> if dialog.exec():
    ...     print("Settings saved!")
"""

from aqt.qt import (
    QDialog, QVBoxLayout, QFormLayout,
    QLabel, QPushButton, QKeySequenceEdit, QComboBox,
    QGroupBox, QDialogButtonBox, QMessageBox, QKeySequence
)
from ..core.config import config


class SettingsDialog(QDialog):
    """Configuration dialog for Music Player addon settings.
    
    A modal dialog that allows users to configure all addon settings including
    keyboard shortcuts, default service, and custom service URLs. Changes are
    saved to config.json when the user clicks Save.
    
    The dialog is organized into sections:
        - Keyboard Shortcuts: Configure all shortcut keys
        - Music Service: Select default service and add custom URLs
        - Action Buttons: Save, Cancel, Restore Defaults
    
    All QKeySequenceEdit fields validate that shortcuts don't conflict.
    The service selector includes built-in services plus custom URLs.
    
    Attributes:
        shortcut_toggle: QKeySequenceEdit for widget toggle shortcut.
        shortcut_playpause: QKeySequenceEdit for play/pause shortcut.
        shortcut_next: QKeySequenceEdit for next track shortcut.
        shortcut_previous: QKeySequenceEdit for previous track shortcut.
        shortcut_volume_up: QKeySequenceEdit for volume up shortcut.
        shortcut_volume_down: QKeySequenceEdit for volume down shortcut.
        service_combo: QComboBox for service selection.
    
    Note:
        Uses config module for persistence. All shortcut changes require
        addon reload to take effect.
    
    Examples:
        >>> dialog = SettingsDialog(parent=mw)
        >>> result = dialog.exec()
        >>> if result == QDialog.DialogCode.Accepted:
        ...     print("Settings saved!")
    """
    
    def __init__(self, parent=None):
        """Initialize the settings dialog.
        
        Creates dialog window, applies dark theme, sets up UI components,
        and loads current settings from config.
        
        Args:
            parent: Optional parent Qt widget, typically Anki's main window.
        
        Side Effects:
            - Sets window title and minimum width
            - Applies dark theme stylesheet
            - Creates all UI components (_setup_ui)
            - Loads current config values (_load_settings)
        
        Examples:
            >>> dialog = SettingsDialog(parent=mw)
            >>> dialog.show()
        """
        super().__init__(parent)
        self.setWindowTitle("Music Player Settings")
        self.setMinimumWidth(550)
        self._apply_dark_theme()
        self._setup_ui()
        self._load_settings()
    
    def _apply_dark_theme(self):
        """Apply dark theme stylesheet to entire dialog.
        
        Sets up a modern dark theme with green accents matching the main
        widget design. Styles QDialog, QLabel, QGroupBox, and other
        standard Qt widgets used in the form.
        
        Side Effects:
            - Applies stylesheet to self (QDialog)
            - Sets background, text colors, borders, etc.
        
        Note:
            Called once during __init__. Additional widget-specific styles
            are applied in _create_shortcut_group and _create_service_group.
        """
        self.setStyleSheet("""
            QDialog {
                background: #1E1E1E;
            }
            QLabel {
                color: #E0E0E0;
            }
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid rgba(29, 185, 84, 0.3);
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 18px;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                background: rgba(29, 185, 84, 0.15);
                border-radius: 4px;
                color: #1ED760;
            }
        """)
    
    def _setup_ui(self):
        """Set up the user interface components.
        
        Creates the main layout and all UI sections:
            - Keyboard shortcuts group with all shortcut editors
            - Music service group with selector and custom URL button
            - Button box with Save, Cancel, Restore Defaults
        
        Side Effects:
            - Creates QVBoxLayout as main layout
            - Calls _create_shortcut_group() and _create_service_group()
            - Creates and connects button box
            - Sets layout on dialog
        
        Note:
            Should only be called once during initialization.
        """
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("♫ Music Player Configuration")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: 700;
            padding: 16px;
            color: #1ED760;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title)
        
        # Shortcuts group
        layout.addWidget(self._create_shortcuts_group())
        
        # General settings group
        layout.addWidget(self._create_general_group())
        
        # Info label
        layout.addWidget(self._create_info_label())
        
        # Reset button
        layout.addWidget(self._create_reset_button())
        
        # Dialog buttons
        layout.addWidget(self._create_dialog_buttons())
        
        self.setLayout(layout)
    
    def _create_shortcuts_group(self):
        """Create keyboard shortcuts configuration group."""
        group = QGroupBox("Keyboard Shortcuts")
        layout = QFormLayout()
        
        self.play_pause_edit = QKeySequenceEdit()
        self.play_pause_edit.setToolTip("Press the key combination you want to use")
        layout.addRow("Play/Pause:", self.play_pause_edit)
        
        self.next_edit = QKeySequenceEdit()
        self.next_edit.setToolTip("Press the key combination you want to use")
        layout.addRow("Next Track:", self.next_edit)
        
        self.previous_edit = QKeySequenceEdit()
        self.previous_edit.setToolTip("Press the key combination you want to use")
        layout.addRow("Previous Track:", self.previous_edit)
        
        self.toggle_edit = QKeySequenceEdit()
        self.toggle_edit.setToolTip("Press the key combination to toggle widget visibility")
        layout.addRow("Toggle Widget:", self.toggle_edit)
        
        group.setLayout(layout)
        group.setStyleSheet("""
            QKeySequenceEdit {
                background: rgba(45, 45, 45, 0.8);
                border: 1px solid rgba(29, 185, 84, 0.3);
                border-radius: 6px;
                padding: 8px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QKeySequenceEdit:focus {
                border: 1px solid rgba(30, 231, 96, 0.7);
                background: rgba(55, 55, 55, 0.9);
            }
        """)
        return group
    
    def _create_general_group(self):
        """Create general settings configuration group."""
        group = QGroupBox("General Settings")
        layout = QFormLayout()
        
        self.service_combo = QComboBox()
        self.service_combo.addItems(["youtube_music", "youtube"])
        self.service_combo.setToolTip("Default music service when widget opens")
        self.service_combo.setStyleSheet("""
            QComboBox {
                background: rgba(45, 45, 45, 0.8);
                border: 1px solid rgba(29, 185, 84, 0.3);
                border-radius: 6px;
                padding: 8px;
                color: #FFFFFF;
                font-size: 13px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid rgba(30, 231, 96, 0.6);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #1DB954;
            }
            QComboBox QAbstractItemView {
                background: #2D2D2D;
                color: #FFFFFF;
                selection-background-color: rgba(29, 185, 84, 0.8);
                border: 1px solid rgba(29, 185, 84, 0.5);
                border-radius: 4px;
            }
        """)
        layout.addRow("Default Service:", self.service_combo)
        
        group.setLayout(layout)
        return group
    
    def _create_info_label(self):
        """Create informational label about applying changes."""
        label = QLabel(
            "💡 Changes take effect after reloading the addon or restarting Anki.\n"
            "Use Tools → Reload Music Player Addon for instant apply."
        )
        label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            font-size: 12px;
            padding: 12px;
            background: rgba(29, 185, 84, 0.08);
            border-radius: 6px;
            border-left: 3px solid rgba(29, 185, 84, 0.5);
        """)
        label.setWordWrap(True)
        return label
    
    def _create_reset_button(self):
        """Create reset to defaults button."""
        btn = QPushButton("⟲ Reset to Defaults")
        btn.clicked.connect(self._reset_to_defaults)
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(61, 61, 61, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                padding: 10px 20px;
                color: #E0E0E0;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(77, 77, 77, 0.8);
                border: 1px solid rgba(29, 185, 84, 0.5);
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background: rgba(45, 45, 45, 0.9);
            }
        """)
        return btn
    
    def _create_dialog_buttons(self):
        """Create OK/Cancel dialog buttons."""
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet("""
            QDialogButtonBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 231, 96, 0.8), stop:1 rgba(29, 185, 84, 0.8));
                border: 1px solid rgba(30, 231, 96, 0.5);
                border-radius: 6px;
                padding: 10px 24px;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(42, 255, 128, 0.9), stop:1 rgba(30, 231, 96, 0.9));
                border: 1px solid rgba(30, 231, 96, 0.8);
            }
            QDialogButtonBox QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(23, 163, 74, 0.9), stop:1 rgba(15, 116, 53, 0.9));
            }
            QDialogButtonBox QPushButton[text="Cancel"] {
                background: rgba(61, 61, 61, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            QDialogButtonBox QPushButton[text="Cancel"]:hover {
                background: rgba(77, 77, 77, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.25);
            }
        """)
        return buttons
    
    def _load_settings(self):
        """Load current settings into the form."""
        play_pause = config.get('shortcut_play_pause', 'Space')
        self.play_pause_edit.setKeySequence(QKeySequence(play_pause))
        
        next_track = config.get('shortcut_next', 'Shift+Right')
        self.next_edit.setKeySequence(QKeySequence(next_track))
        
        previous_track = config.get('shortcut_previous', 'Shift+Left')
        self.previous_edit.setKeySequence(QKeySequence(previous_track))
        
        toggle_widget = config.get('shortcut_toggle', 'Ctrl+Shift+M')
        self.toggle_edit.setKeySequence(QKeySequence(toggle_widget))
        
        default_service = config.get('default_service', 'youtube_music')
        index = self.service_combo.findText(default_service)
        if index >= 0:
            self.service_combo.setCurrentIndex(index)
    
    def _save_and_close(self):
        """Validate and save settings."""
        # Get all shortcuts
        play_pause = self.play_pause_edit.keySequence().toString()
        next_track = self.next_edit.keySequence().toString()
        previous = self.previous_edit.keySequence().toString()
        toggle = self.toggle_edit.keySequence().toString()
        
        # Validate all shortcuts are set
        if not all([play_pause, next_track, previous, toggle]):
            QMessageBox.warning(
                self,
                "Invalid Shortcuts",
                "All shortcuts must be set. Please configure all keyboard shortcuts."
            )
            return
        
        # Validate uniqueness
        shortcuts = [play_pause, next_track, previous, toggle]
        if len(shortcuts) != len(set(shortcuts)):
            QMessageBox.warning(
                self,
                "Duplicate Shortcuts",
                "Each shortcut must be unique. Please use different key combinations."
            )
            return
        
        # Save settings
        config.set('shortcut_play_pause', play_pause)
        config.set('shortcut_next', next_track)
        config.set('shortcut_previous', previous)
        config.set('shortcut_toggle', toggle)
        config.set('default_service', self.service_combo.currentText())
        
        if config.save():
            QMessageBox.information(
                self,
                "✓ Settings Saved",
                "Settings saved successfully!\n\n"
                "Use Tools → Reload Music Player Addon to apply changes immediately,\n"
                "or restart Anki."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Save Failed",
                "Failed to save settings. Please check permissions."
            )
    
    def _reset_to_defaults(self):
        """Reset all settings to default values."""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            config.reset_to_defaults()
            self._load_settings()
            QMessageBox.information(
                self,
                "Reset Complete",
                "Settings have been reset to defaults."
            )
