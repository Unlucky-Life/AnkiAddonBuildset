"""Centralized stylesheet definitions for the Music Player addon UI.

This module contains all Qt stylesheet (CSS-like) definitions used throughout
the addon's graphical interface. Centralizing styles ensures:
    - Consistent look and feel across all components
    - Easy theme modifications (single point of change)
    - Reduced code duplication
    - Better maintainability

The styles implement a modern, minimalistic dark theme with green accents
inspired by music streaming services. All colors use RGBA for smooth
transparency effects and modern glassmorphism aesthetics.

Color Scheme:
    - Primary: Green (#1ED760, #1DB954) - Action and emphasis
    - Background: Dark grays (#1E1E1E to #4D4D4D) - Layers and depth
    - Text: White to gray (#FFFFFF to #CCCCCC) - Hierarchy
    - Danger: Red (#E74C3C) - Close/destructive actions

Typical usage example:
    >>> from utils.styles import Styles
    >>> button.setStyleSheet(Styles.primary_button())
    >>> header.setStyleSheet(Styles.header())
"""


class Styles:
    """Container for all stylesheet definitions used in the addon.
    
    This class provides static methods that return Qt stylesheet strings for
    various UI components. All methods are static as they don't require instance
    state and act as simple factories for stylesheet strings.
    
    The class also defines color constants for consistency across styles. These
    colors implement a dark theme with green accents.
    
    Color Constants:
        PRIMARY_GREEN: Main accent color for active elements
        PRIMARY_GREEN_HOVER: Lighter green for hover states
        PRIMARY_GREEN_DARK: Darker green for pressed states
        DARK_BG: Main dark background
        DARKER_BG: Even darker for gradients
        MEDIUM_BG: Medium dark for secondary backgrounds
        LIGHT_BG: Light dark for hover states
        LIGHTER_BG: Lighter for active hover states
        TEXT_PRIMARY: Primary text color (white)
        TEXT_SECONDARY: Secondary text color (light gray)
        TEXT_TERTIARY: Tertiary text color (medium gray)
        DANGER_RED: Red for destructive actions
        DANGER_RED_DARK: Darker red for pressed states
    
    Note:
        All stylesheet methods return complete, ready-to-use Qt stylesheet
        strings that can be directly applied to widgets using setStyleSheet().
    
    Examples:
        >>> button = QPushButton()
        >>> button.setStyleSheet(Styles.primary_button())
        >>> header = QWidget()
        >>> header.setStyleSheet(Styles.header())
    """
    
    # Colors
    PRIMARY_GREEN = "#1ED760"
    PRIMARY_GREEN_HOVER = "#1FE870"
    PRIMARY_GREEN_DARK = "#1DB954"
    DARK_BG = "#1E1E1E"
    DARKER_BG = "#1a1a1a"
    MEDIUM_BG = "#2D2D2D"
    LIGHT_BG = "#3D3D3D"
    LIGHTER_BG = "#4D4D4D"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#E0E0E0"
    TEXT_TERTIARY = "#CCCCCC"
    DANGER_RED = "#E74C3C"
    DANGER_RED_DARK = "#C0392B"
    
    @staticmethod
    def header():
        """Get stylesheet for the header widget.
        
        Creates a horizontal gradient background with a subtle green bottom border.
        Used for the top section containing the title and service selector.
        
        Returns:
            str: Qt stylesheet string with gradient background and border.
        
        Examples:
            >>> header_widget.setStyleSheet(Styles.header())
        """
        return """
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1a1a, stop:0.5 #242424, stop:1 #1a1a1a);
            border-bottom: 1px solid rgba(29, 185, 84, 0.3);
        """
    
    @staticmethod
    def title_label():
        """Get stylesheet for the title label.
        
        Styles the main title text with the primary green color, bold weight,
        and slight letter spacing for modern appearance.
        
        Returns:
            str: Qt stylesheet string for title text styling.
        
        Examples:
            >>> title_label.setStyleSheet(Styles.title_label())
        """
        return """
            color: #1ED760;
            font-weight: 600;
            font-size: 15px;
            letter-spacing: 0.5px;
        """
    
    @staticmethod
    def service_combo():
        """Get stylesheet for the service selection combo box.
        
        Styles a dropdown menu with dark background, rounded corners, and
        green hover effects. Includes styling for the dropdown arrow and
        the popup menu items.
        
        Returns:
            str: Qt stylesheet string for QComboBox styling.
        
        Examples:
            >>> service_combo.setStyleSheet(Styles.service_combo())
        """
        return """
            QComboBox {
                background: rgba(61, 61, 61, 0.6);
                border: 1px solid rgba(29, 185, 84, 0.4);
                border-radius: 6px;
                padding: 6px 12px;
                color: #FFFFFF;
                min-width: 140px;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 1px solid rgba(30, 231, 96, 0.7);
                background: rgba(77, 77, 77, 0.7);
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #1DB954;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: #1E1E1E;
                color: #FFFFFF;
                selection-background-color: rgba(29, 185, 84, 0.8);
                selection-color: #FFFFFF;
                border: 1px solid rgba(29, 185, 84, 0.5);
                border-radius: 4px;
                outline: none;
            }
        """
    
    @staticmethod
    def close_button():
        """Close button stylesheet."""
        return """
            QPushButton {
                background: rgba(61, 61, 61, 0.5);
                border: 1px solid transparent;
                border-radius: 6px;
                color: #CCCCCC;
                font-size: 18px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(231, 76, 60, 0.8);
                border: 1px solid rgba(231, 76, 60, 0.6);
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background: rgba(192, 57, 43, 0.9);
            }
        """
    
    @staticmethod
    def controls_footer():
        """Controls footer stylesheet."""
        return """
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1a1a, stop:0.5 #1e1e1e, stop:1 #1a1a1a);
            border-top: 1px solid rgba(29, 185, 84, 0.25);
        """
    
    @staticmethod
    def primary_button():
        """Primary control button (play/pause) stylesheet."""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1FE870, stop:1 #1DB954);
                border: 2px solid rgba(30, 231, 96, 0.5);
                border-radius: 23px;
                color: #FFFFFF;
                font-size: 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2AFF80, stop:1 #1ED760);
                border: 2px solid rgba(30, 231, 96, 0.8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #17A34A, stop:1 #0F7435);
            }
        """
    
    @staticmethod
    def secondary_button():
        """Secondary control button (prev/next) stylesheet."""
        return """
            QPushButton {
                background: rgba(61, 61, 61, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #E0E0E0;
                font-size: 20px;
            }
            QPushButton:hover {
                background: rgba(77, 77, 77, 0.8);
                border: 1px solid rgba(29, 185, 84, 0.6);
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background: rgba(45, 45, 45, 0.9);
                border: 1px solid rgba(29, 185, 84, 0.8);
            }
        """
    
    @staticmethod
    def fallback_label():
        """Fallback label when WebEngine is unavailable."""
        return "color:#FFF;background:#1E1E1E;padding:20px;"
