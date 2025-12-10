"""
Settings dialog for Spotify Anki addon.
Allows users to customize keyboard shortcuts and preferences.
"""

from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QKeySequenceEdit, QComboBox,
    QGroupBox, QDialogButtonBox, QMessageBox, Qt
)
from .config import config


class SettingsDialog(QDialog):
    """Settings dialog for customizing addon preferences."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spotify Addon Settings")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings dialog UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Spotify Anki Addon Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Keyboard Shortcuts Group
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QFormLayout()
        
        # Play/Pause shortcut
        self.play_pause_edit = QKeySequenceEdit()
        self.play_pause_edit.setToolTip("Press the key combination you want to use")
        shortcuts_layout.addRow("Play/Pause:", self.play_pause_edit)
        
        # Next track shortcut
        self.next_edit = QKeySequenceEdit()
        self.next_edit.setToolTip("Press the key combination you want to use")
        shortcuts_layout.addRow("Next Track:", self.next_edit)
        
        # Previous track shortcut
        self.previous_edit = QKeySequenceEdit()
        self.previous_edit.setToolTip("Press the key combination you want to use")
        shortcuts_layout.addRow("Previous Track:", self.previous_edit)
        
        shortcuts_group.setLayout(shortcuts_layout)
        layout.addWidget(shortcuts_group)
        
        # General Settings Group
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout()
        
        # Default service
        self.service_combo = QComboBox()
        self.service_combo.addItems(["spotify", "youtube"])
        self.service_combo.setToolTip("Default music service when widget opens")
        general_layout.addRow("Default Service:", self.service_combo)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # Info label
        info_label = QLabel(
            "Note: Changes take effect after reloading the addon or restarting Anki.\n"
            "Use Tools → Reload Spotify Addon for instant apply."
        )
        info_label.setStyleSheet("color: #666; font-size: 11px; padding: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        layout.addWidget(reset_btn)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_and_close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Load current settings into the dialog."""
        # Load shortcuts
        from aqt.qt import QKeySequence
        
        play_pause = config.get('shortcut_play_pause', 'Space')
        self.play_pause_edit.setKeySequence(QKeySequence(play_pause))
        
        next_track = config.get('shortcut_next', 'Shift+Right')
        self.next_edit.setKeySequence(QKeySequence(next_track))
        
        previous_track = config.get('shortcut_previous', 'Shift+Left')
        self.previous_edit.setKeySequence(QKeySequence(previous_track))
        
        # Load default service
        default_service = config.get('default_service', 'spotify')
        index = self.service_combo.findText(default_service)
        if index >= 0:
            self.service_combo.setCurrentIndex(index)
    
    def save_and_close(self):
        """Save settings and close dialog."""
        # Get shortcuts as strings
        play_pause = self.play_pause_edit.keySequence().toString()
        next_track = self.next_edit.keySequence().toString()
        previous = self.previous_edit.keySequence().toString()
        
        # Validate shortcuts are not empty
        if not play_pause or not next_track or not previous:
            QMessageBox.warning(
                self,
                "Invalid Shortcuts",
                "All shortcuts must be set. Please configure all keyboard shortcuts."
            )
            return
        
        # Check for duplicate shortcuts
        shortcuts = [play_pause, next_track, previous]
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
        config.set('default_service', self.service_combo.currentText())
        
        if config.save():
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings saved successfully!\n\n"
                "Use Tools → Reload Spotify Addon to apply changes immediately,\n"
                "or restart Anki."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Save Failed",
                "Failed to save settings. Please check permissions."
            )
    
    def reset_to_defaults(self):
        """Reset all settings to default values."""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            config.reset_to_defaults()
            self.load_settings()
            QMessageBox.information(
                self,
                "Reset Complete",
                "Settings have been reset to defaults."
            )
