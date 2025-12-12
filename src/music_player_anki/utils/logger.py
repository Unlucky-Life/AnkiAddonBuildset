"""Logging utilities for the Music Player addon.

This module provides centralized logging functionality for debugging and
error tracking. Logs are written to a file in the addon directory with
timestamps and severity levels.

Typical usage:
    >>> from utils.logger import log_info, log_error
    >>> log_info("Widget created successfully")
    >>> log_error("Failed to load profile", exception=e)
"""

import logging
import os
from datetime import datetime
from aqt import mw


class MusicPlayerLogger:
    """Centralized logger for the Music Player addon.
    
    Provides logging functionality with file output and console output.
    Logs include timestamps, severity levels, and optional exception traces.
    """
    
    _logger = None
    _log_file_path = None
    
    @classmethod
    def get_logger(cls):
        """Get or create the logger instance.
        
        Returns:
            logging.Logger: Configured logger instance.
        """
        if cls._logger is None:
            cls._setup_logger()
        return cls._logger
    
    @classmethod
    def _setup_logger(cls):
        """Set up the logger with file and console handlers."""
        # Create logger
        cls._logger = logging.getLogger("MusicPlayerAnki")
        cls._logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if cls._logger.handlers:
            return
        
        # Create log file path
        addon_dir = os.path.join(mw.pm.addonFolder(), 'music_player_anki')
        os.makedirs(addon_dir, exist_ok=True)
        cls._log_file_path = os.path.join(addon_dir, 'music_player.log')
        
        # Create file handler
        file_handler = logging.FileHandler(cls._log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler (only show warnings and errors)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)
        
        cls._logger.info("=" * 60)
        cls._logger.info(f"Music Player Addon - Logging started")
        cls._logger.info(f"Log file: {cls._log_file_path}")
        cls._logger.info("=" * 60)
    
    @classmethod
    def get_log_file_path(cls):
        """Get the path to the log file.
        
        Returns:
            str: Absolute path to the log file.
        """
        if cls._log_file_path is None:
            cls._setup_logger()
        return cls._log_file_path


# Convenience functions
def log_debug(message):
    """Log a debug message."""
    MusicPlayerLogger.get_logger().debug(message)


def log_info(message):
    """Log an info message."""
    MusicPlayerLogger.get_logger().info(message)


def log_warning(message):
    """Log a warning message."""
    MusicPlayerLogger.get_logger().warning(message)


def log_error(message, exception=None):
    """Log an error message with optional exception.
    
    Args:
        message: Error message to log.
        exception: Optional exception object to include traceback.
    """
    logger = MusicPlayerLogger.get_logger()
    if exception:
        logger.error(f"{message}: {str(exception)}", exc_info=True)
    else:
        logger.error(message)


def get_log_file_path():
    """Get the path to the log file.
    
    Returns:
        str: Absolute path to the log file.
    """
    return MusicPlayerLogger.get_log_file_path()
